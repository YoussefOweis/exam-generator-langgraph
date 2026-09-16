import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# GET GEMINI MODEL
# =========================================================

def get_llm():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        temperature=0.2
    )


# =========================================================
# DEEP QUESTION EXPLANATION
# =========================================================

def explain_question_in_depth(
    question: str,
    options: list[str],
    user_answers: list[str],
    correct_answers: list[str],
    database_explanation: str,
    question_type: str
) -> str:

    user_answer_text = (
        ", ".join(user_answers)
        if user_answers
        else "Aucune réponse"
    )

    correct_answer_text = ", ".join(
        correct_answers
    )

    options_text = "\n".join(options)

    prompt = f"""
Tu es un professeur expert en informatique.

Tu aides un étudiant qui prépare un concours
de Master en Informatique à la FS Tétouan.

Analyse cette question de QCM en profondeur.

TYPE:
{question_type}

QUESTION:
{question}

OPTIONS:
{options_text}

RÉPONSE CHOISIE PAR L'ÉTUDIANT:
{user_answer_text}

RÉPONSE CORRECTE FOURNIE PAR LA BASE DE DONNÉES:
{correct_answer_text}

EXPLICATION FOURNIE PAR LA BASE DE DONNÉES:
{database_explanation}

IMPORTANT:

- La réponse correcte de la base de données est la référence.
- Ne change jamais la réponse correcte.
- Analyse chaque proposition.
- Explique pourquoi chaque proposition est correcte
  ou incorrecte.
- Explique l'erreur éventuelle de l'étudiant.
- Développe réellement le concept informatique.

Structure ta réponse :

## 1. Comprendre la question
Explique ce que la question demande.

## 2. Analyse des propositions
Analyse chaque proposition une par une.

## 3. Pourquoi la réponse correcte est correcte
Explique le concept en profondeur.

## 4. Analyse de la réponse de l'étudiant
Explique pourquoi sa réponse est correcte ou incorrecte.

## 5. À retenir pour le concours
Donne les règles importantes à mémoriser.

## 6. Exemple pratique
Donne un exemple concret.

## 7. Mini-question
Pose une petite question similaire pour vérifier
la compréhension.

Réponds en français.
Sois précis, pédagogique et adapté à un étudiant
en préparation d'un concours informatique.
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text_parts.append(
                        item.get("text", "")
                    )

            elif isinstance(item, str):

                text_parts.append(item)

        return "\n".join(text_parts).strip()

    return str(content)