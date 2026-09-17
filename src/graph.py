import random

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from .loader import load_questions
from .models import ExamState


# =========================================================
# LOAD QUESTIONS NODE
# =========================================================

def load_questions_node(
    state: ExamState
) -> ExamState:
    """
    Load the complete question database.
    """

    questions = load_questions()

    return {
        "all_questions": questions
    }


# =========================================================
# PROPORTIONAL ALLOCATION
# =========================================================

def allocate_proportionally(
    counts: dict[str, int],
    total_questions: int
) -> dict[str, int]:
    """
    Allocate exam questions proportionally according
    to the number of available questions in each type.

    Whenever possible, every selected type receives
    at least one question.
    """

    if not counts:

        raise ValueError(
            "No question types are available."
        )

    total_available = sum(
        counts.values()
    )

    if total_questions > total_available:

        raise ValueError(
            f"Impossible de générer "
            f"{total_questions} questions. "
            f"Seulement {total_available} "
            f"questions sont disponibles."
        )

    types = list(counts.keys())

    allocation = {
        question_type: 0
        for question_type in types
    }

    # =====================================================
    # CASE 1:
    # Enough questions to give one to every type
    # =====================================================

    if total_questions >= len(types):

        # Give one question to each type
        for question_type in types:

            allocation[question_type] = 1

        remaining = (
            total_questions - len(types)
        )

        remaining_capacity = {
            question_type:
                counts[question_type] - 1
            for question_type in types
        }

        total_remaining_capacity = sum(
            remaining_capacity.values()
        )

        # -------------------------------------------------
        # Distribute remaining questions proportionally
        # -------------------------------------------------

        if remaining > 0:

            exact_allocations = {}

            for question_type in types:

                capacity = remaining_capacity[
                    question_type
                ]

                exact = (
                    remaining
                    * capacity
                    / total_remaining_capacity
                    if total_remaining_capacity > 0
                    else 0
                )

                exact_allocations[
                    question_type
                ] = exact

            # First take integer parts
            for question_type in types:

                extra = min(
                    int(
                        exact_allocations[
                            question_type
                        ]
                    ),
                    remaining_capacity[
                        question_type
                    ]
                )

                allocation[
                    question_type
                ] += extra

            allocated = sum(
                allocation.values()
            )

            leftover = (
                total_questions - allocated
            )

            # -------------------------------------------------
            # Distribute remaining questions using largest
            # fractional remainder
            # -------------------------------------------------

            remainders = sorted(
                types,
                key=lambda question_type:
                    exact_allocations[
                        question_type
                    ]
                    - int(
                        exact_allocations[
                            question_type
                        ]
                    ),
                reverse=True
            )

            for question_type in remainders:

                if leftover <= 0:
                    break

                if (
                    allocation[question_type]
                    < counts[question_type]
                ):

                    allocation[
                        question_type
                    ] += 1

                    leftover -= 1

    # =====================================================
    # CASE 2:
    # Fewer questions than selected types
    # =====================================================

    else:

        # Give one question to the types with the
        # largest number of available questions.
        selected_types = sorted(
            types,
            key=lambda question_type:
                counts[question_type],
            reverse=True
        )

        for question_type in selected_types[
            :total_questions
        ]:

            allocation[
                question_type
            ] = 1

    return allocation


# =========================================================
# SELECT QUESTIONS NODE
# =========================================================

def select_questions_node(
    state: ExamState
) -> ExamState:

    all_questions = state[
        "all_questions"
    ]

    number_of_questions = state[
        "number_of_questions"
    ]

    selected_types = state.get(
        "selected_types",
        []
    )

    # =====================================================
    # FILTER TYPES
    # =====================================================

    if selected_types:

        available_questions = [
            question
            for question in all_questions
            if question["type"] in selected_types
        ]

    else:

        # Empty list means all types
        available_questions = all_questions

    if not available_questions:

        raise ValueError(
            "Aucune question ne correspond "
            "aux types sélectionnés."
        )

    # =====================================================
    # GROUP QUESTIONS BY TYPE
    # =====================================================

    questions_by_type: dict[str, list] = {}

    for question in available_questions:

        question_type = question["type"]

        if question_type not in questions_by_type:

            questions_by_type[
                question_type
            ] = []

        questions_by_type[
            question_type
        ].append(question)

    # =====================================================
    # COUNT QUESTIONS
    # =====================================================

    counts = {
        question_type: len(
            question_list
        )
        for question_type, question_list
        in questions_by_type.items()
    }

    # =====================================================
    # CALCULATE PROPORTIONAL DISTRIBUTION
    # =====================================================

    allocation = allocate_proportionally(
        counts=counts,
        total_questions=number_of_questions
    )

    # =====================================================
    # SELECT RANDOM QUESTIONS
    # =====================================================

    selected_questions = []

    for question_type, number in allocation.items():

        if number <= 0:
            continue

        type_questions = questions_by_type[
            question_type
        ]

        selected = random.sample(
            type_questions,
            number
        )

        selected_questions.extend(
            selected
        )

    # =====================================================
    # SHUFFLE FINAL EXAM
    # =====================================================

    random.shuffle(
        selected_questions
    )

    return {
        "exam": selected_questions,
        "distribution": allocation,
        "user_answers": {},
        "score": 0,
        "results": [],
        "ai_feedback": ""
    }


# =========================================================
# VALIDATE EXAM NODE
# =========================================================

def validate_exam_node(
    state: ExamState
) -> ExamState:

    exam = state["exam"]

    requested = state[
        "number_of_questions"
    ]

    # -----------------------------------------------------
    # Correct number of questions
    # -----------------------------------------------------

    if len(exam) != requested:

        raise ValueError(
            f"Expected {requested} questions, "
            f"but generated {len(exam)}."
        )

    # -----------------------------------------------------
    # No duplicates
    # -----------------------------------------------------

    ids = [
        question["id"]
        for question in exam
    ]

    if len(ids) != len(set(ids)):

        raise ValueError(
            "Des questions en double ont été détectées."
        )

    return {}


# =========================================================
# CORRECT EXAM NODE
# =========================================================

def correct_exam_node(
    state: ExamState
) -> ExamState:

    exam = state["exam"]

    user_answers = state.get(
        "user_answers",
        {}
    )

    score = 0

    results = []

    for question in exam:

        question_id = question["id"]

        expected_answers = sorted(
            question["correct_answers"]
        )

        submitted_answers = sorted(
            user_answers.get(
                question_id,
                []
            )
        )

        # -------------------------------------------------
        # Exact answer comparison
        # -------------------------------------------------

        is_correct = (
            submitted_answers
            == expected_answers
        )

        if is_correct:

            score += 1

        results.append(
            {
                "question_id":
                    question_id,

                "type":
                    question["type"],

                "question":
                    question["question"],

                "options":
                    question["options"],

                "user_answers":
                    submitted_answers,

                "correct_answers":
                    expected_answers,

                "correct":
                    is_correct,

                "explanation":
                    question["explanation"]
            }
        )

    return {
        "score": score,
        "results": results
    }


# =========================================================
# BUILD EXAM GENERATION GRAPH
# =========================================================

def build_exam_graph():

    builder = StateGraph(
        ExamState
    )

    builder.add_node(
        "load_questions",
        load_questions_node
    )

    builder.add_node(
        "select_questions",
        select_questions_node
    )

    builder.add_node(
        "validate_exam",
        validate_exam_node
    )

    builder.add_edge(
        START,
        "load_questions"
    )

    builder.add_edge(
        "load_questions",
        "select_questions"
    )

    builder.add_edge(
        "select_questions",
        "validate_exam"
    )

    builder.add_edge(
        "validate_exam",
        END
    )

    return builder.compile()


# =========================================================
# BUILD CORRECTION GRAPH
# =========================================================

def build_correction_graph():

    builder = StateGraph(
        ExamState
    )

    builder.add_node(
        "correct_exam",
        correct_exam_node
    )

    builder.add_edge(
        START,
        "correct_exam"
    )

    builder.add_edge(
        "correct_exam",
        END
    )

    return builder.compile()


# =========================================================
# COMPILED GRAPHS
# =========================================================

exam_graph = build_exam_graph()

correction_graph = build_correction_graph()