from typing import TypedDict


class Question(TypedDict):
    id: int
    type: str
    question: str
    options: list[str]
    correct_answers: list[str]
    explanation: str


class ExamState(TypedDict, total=False):
    # -----------------------------------------------------
    # Exam configuration
    # -----------------------------------------------------

    number_of_questions: int

    # Empty list = all types
    selected_types: list[str]

    # -----------------------------------------------------
    # Question database
    # -----------------------------------------------------

    all_questions: list[Question]

    filtered_questions: list[Question]

    # -----------------------------------------------------
    # Generated exam
    # -----------------------------------------------------

    exam: list[Question]

    distribution: dict[str, int]

    # -----------------------------------------------------
    # Student answers
    # Example:
    # {
    #     1: ["C"],
    #     21: ["B", "D"]
    # }
    # -----------------------------------------------------

    user_answers: dict[int, list[str]]

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    score: int

    results: list[dict]

    # -----------------------------------------------------
    # AI
    # -----------------------------------------------------

    ai_feedback: str