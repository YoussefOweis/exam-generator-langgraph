from typing import TypedDict


class Question(TypedDict):
    id: int
    question: str
    options: list[str]
    correct_answers: list[str]
    explanation: str


class ExamState(TypedDict, total=False):
    # Configuration
    number_of_questions: int

    # Question database
    all_questions: list[Question]

    # Generated exam
    exam: list[Question]

    # Student answers
    user_answers: dict[int, list[str]]

    # Results
    results: list[dict]
    score: int

    # AI feedback
    ai_feedback: str