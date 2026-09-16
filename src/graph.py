import random

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from .models import ExamState
from .loader import load_questions


# =========================================================
# LOAD QUESTIONS
# =========================================================

def load_questions_node(
    state: ExamState
) -> ExamState:

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
    Allocate questions proportionally according to
    the number of questions available in each type.

    Example:

        reseaux: 11
        java: 16
        c: 5

    A 16-question exam will roughly follow those
    proportions.

    The function also ensures that, whenever possible,
    every selected type gets at least one question.
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

    # -----------------------------------------------------
    # First give one question to each type when possible
    # -----------------------------------------------------

    if total_questions >= len(types):

        for question_type in types:

            allocation[question_type] = 1

        remaining = (
            total_questions - len(types)
        )

    else:

        remaining = total_questions

    # -----------------------------------------------------
    # Distribute remaining questions proportionally
    # -----------------------------------------------------

    while remaining > 0:

        candidates = [
            question_type
            for question_type in types
            if allocation[question_type]
            < counts[question_type]
        ]

        if not candidates:
            break

        total_available_for_candidates = sum(
            counts[question_type]
            for question_type in candidates
        )

        # Current deficit from proportional target
        deficits = {}

        for question_type in candidates:

            ideal = (
                total_questions
                * counts[question_type]
                / total_available
            )

            deficits[question_type] = (
                ideal
                - allocation[question_type]
            )

        selected_type = max(
            deficits,
            key=deficits.get
        )

        allocation[selected_type] += 1

        remaining -= 1

    return allocation


# =========================================================
# SELECT QUESTIONS
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

    # -----------------------------------------------------
    # Filter by selected types
    # -----------------------------------------------------

    if selected_types:

        available_questions = [
            question
            for question in all_questions
            if question["type"]
            in selected_types
        ]

    else:

        # Empty list means all types
        available_questions = all_questions

    if not available_questions:

        raise ValueError(
            "Aucune question ne correspond "
            "aux types sélectionnés."
        )

    # -----------------------------------------------------
    # Group questions by type
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Count questions
    # -----------------------------------------------------

    counts = {
        question_type: len(
            question_list
        )
        for question_type, question_list
        in questions_by_type.items()
    }

    # -----------------------------------------------------
    # Calculate proportional distribution
    # -----------------------------------------------------

    allocation = allocate_proportionally(
        counts=counts,
        total_questions=number_of_questions
    )

    # -----------------------------------------------------
    # Select questions
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Shuffle final exam
    # -----------------------------------------------------

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
# VALIDATE EXAM
# =========================================================

def validate_exam_node(
    state: ExamState
) -> ExamState:

    exam = state["exam"]

    requested = state[
        "number_of_questions"
    ]

    # -----------------------------------------------------
    # Check number of questions
    # -----------------------------------------------------

    if len(exam) != requested:

        raise ValueError(
            f"Expected {requested} questions, "
            f"but generated {len(exam)}."
        )

    # -----------------------------------------------------
    # Check duplicates
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
# CORRECT EXAM
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
        # Exact comparison
        #
        # ["B"] == ["B"]
        #
        # ["B", "D"] == ["B", "D"]
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
# EXAM GENERATION GRAPH
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
# CORRECTION GRAPH
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