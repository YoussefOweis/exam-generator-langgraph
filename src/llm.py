import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_llm():

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.2,
    )


def explain_mistakes(results: list[dict]) -> str:

    wrong_answers = [
        result
        for result in results
        if not result["correct"]
    ]

    if not wrong_answers:
        return "Excellent ! Toutes les réponses sont correctes."

    mistakes_text = []

    for result in wrong_answers:

        mistakes_text.append(
            f"""
Question:
{result['question']}

Student answers:
{result['user_answers']}

Correct answers:
{result['correct_answers']}

Database explanation:
{result['explanation']}
"""
        )

    prompt = f"""
Tu es un professeur spécialisé en informatique.

L'étudiant prépare le concours du Master M2I à la FS Tétouan.

Analyse ses erreurs ci-dessous.

Pour chaque question:
1. Explique pourquoi la réponse correcte est correcte.
2. Explique brièvement l'erreur de l'étudiant.
3. Donne une règle ou notion à retenir.

Sois précis et pédagogique.

Erreurs:

{"".join(mistakes_text)}
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    return response.content