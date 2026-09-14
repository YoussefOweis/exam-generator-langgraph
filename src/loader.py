import json
from pathlib import Path

from .models import Question


BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "data" / "questions.json"


def load_questions() -> list[Question]:
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(
            f"Question file not found: {QUESTIONS_FILE}"
        )

    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("questions.json must contain a JSON list.")

    questions: list[Question] = []

    for item in data:
        required_fields = [
            "id",
            "question",
            "options",
            "correct_answers",
            "explanation",
        ]

        for field in required_fields:
            if field not in item:
                raise ValueError(
                    f"Question {item.get('id', '?')} is missing '{field}'."
                )

        questions.append(
            {
                "id": int(item["id"]),
                "question": str(item["question"]),
                "options": list(item["options"]),
                "correct_answers": list(item["correct_answers"]),
                "explanation": str(item["explanation"]),
            }
        )

    return questions