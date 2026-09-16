
import json
from pathlib import Path

from .models import Question


# =========================================================
# QUESTION FILE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

QUESTIONS_FILE = (
    BASE_DIR
    / "data"
    / "questions.json"
)


# =========================================================
# LOAD QUESTIONS
# =========================================================

def load_questions() -> list[Question]:
    """
    Load all questions from questions.json.
    """

    if not QUESTIONS_FILE.exists():

        raise FileNotFoundError(
            f"Question file not found:\n{QUESTIONS_FILE}"
        )

    with QUESTIONS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):

        raise ValueError(
            "questions.json must contain a JSON array."
        )

    questions: list[Question] = []

    for item in data:

        required_fields = [
            "id",
            "type",
            "question",
            "options",
            "correct_answers",
            "explanation"
        ]

        for field in required_fields:

            if field not in item:

                raise ValueError(
                    f"Question {item.get('id', '?')} "
                    f"is missing field '{field}'."
                )

        questions.append(
            {
                "id": int(item["id"]),

                "type": str(
                    item["type"]
                ),

                "question": str(
                    item["question"]
                ),

                "options": list(
                    item["options"]
                ),

                "correct_answers": list(
                    item["correct_answers"]
                ),

                "explanation": str(
                    item["explanation"]
                )
            }
        )

    return questions


# =========================================================
# GET QUESTION TYPES
# =========================================================

def get_question_types() -> list[str]:
    """
    Return all unique question types.
    """

    questions = load_questions()

    types = sorted(
        {
            question["type"]
            for question in questions
        }
    )

    return types

