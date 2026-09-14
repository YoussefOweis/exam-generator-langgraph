import random

from langgraph.graph import StateGraph, START, END

from .models import ExamState, Question


def load_questions_node(state: ExamState) -> ExamState:
    """
    Load the complete question bank.

    The actual JSON loading is delegated to loader.py.
    """
    from .loader import load_questions

    questions = load_questions()

    return {
        "all_questions": questions
    }


def select_questions_node(state: ExamState) -> ExamState:
    """
    Randomly select questions for the exam.
    """

    all_questions = state["all_questions"]
    number_of_questions = state["number_of_questions"]

    if number_of_questions > len(all_questions):
        raise ValueError(
            f"Requested {number_of_questions} questions, "
            f"but only {len(all_questions)} are available."
        )

    selected_questions = random.sample(
        all_questions,
        number_of_questions
    )

    return {
        "exam": selected_questions,
        "user_answers": {},
        "results": [],
        "score": 0,
        "ai_feedback": ""
    }


def validate_exam_node(state: ExamState) -> ExamState:
    """
    Validate that the generated exam has the requested number
    of unique questions.
    """

    exam = state["exam"]
    requested = state["number_of_questions"]

    ids = [question["id"] for question in exam]

    if len(exam) != requested:
        raise ValueError("Incorrect number of questions generated.")

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate questions detected.")

    return {}


def correct_exam_node(state: ExamState) -> ExamState:
    """
    Compare student answers with the authoritative correct answers
    stored in JSON.
    """

    exam = state["exam"]
    user_answers = state.get("user_answers", {})

    results = []
    score = 0

    for question in exam:

        question_id = question["id"]

        expected = sorted(
            question["correct_answers"]
        )

        submitted = sorted(
            user_answers.get(question_id, [])
        )

        correct = submitted == expected

        if correct:
            score += 1

        results.append(
            {
                "question_id": question_id,
                "question": question["question"],
                "user_answers": submitted,
                "correct_answers": expected,
                "correct": correct,
                "explanation": question["explanation"]
            }
        )

    return {
        "score": score,
        "results": results
    }


def build_graph():

    builder = StateGraph(ExamState)

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

    builder.add_node(
        "correct_exam",
        correct_exam_node
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

    # Correction is deliberately separate from generation.
    #
    # Streamlit will call this after the student submits
    # the exam.
    return builder.compile()


def build_correction_graph():

    builder = StateGraph(ExamState)

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


exam_graph = build_graph()
correction_graph = build_correction_graph()