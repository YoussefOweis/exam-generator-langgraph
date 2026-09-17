import os

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# GET GEMINI MODEL
# =========================================================

def get_llm():

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured "
            "in the .env file."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        temperature=0.2
    )


# =========================================================
# EXTRACT TEXT FROM GEMINI CHUNK
# =========================================================

def extract_chunk_text(
    content
) -> str:
    """
    Convert Gemini/LangChain streaming content
    into plain text.

    Handles:

        "hello"

    and:

        [
            {
                "type": "text",
                "text": "hello"
            }
        ]
    """

    if isinstance(content, str):

        return content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text = item.get(
                        "text",
                        ""
                    )

                    if text:

                        text_parts.append(
                            text
                        )

            elif isinstance(item, str):

                text_parts.append(
                    item
                )

        return "".join(
            text_parts
        )

    return ""


# =========================================================
# STREAM DEEP EXPLANATION
# =========================================================

def stream_question_explanation(
    question: str,
    options: list[str],
    user_answers: list[str],
    correct_answers: list[str],
    database_explanation: str,
    question_type: str
):
    """
    Stream a deep Gemini explanation.

    The function yields only plain text strings.
    """

    user_answer_text = (
        ", ".join(
            user_answers
        )
        if user_answers
        else "Aucune réponse"
    )

    correct_answer_text = ", ".join(
        correct_answers
    )

    options_text = "\n".join(
        options
    )

    # =====================================================
    # PROMPT
    # =====================================================

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

- La réponse correcte fournie par la base de données
  est la référence.
- Ne change jamais la réponse correcte.
- Ne remplace pas la réponse de la base de données
  par une autre.
- Analyse toutes les propositions.
- Explique pourquoi chaque proposition est correcte
  ou incorrecte.
- Analyse la réponse de l'étudiant.
- Développe le concept informatique.

Structure ta réponse exactement ainsi:

## 1. Comprendre la question

Explique clairement ce que la question demande.

## 2. Analyse des propositions

Analyse chaque proposition une par une.

Pour chaque proposition:
- indique si elle est correcte ou incorrecte;
- explique pourquoi.

## 3. Pourquoi la réponse correcte est correcte

Explique le concept informatique en profondeur.

## 4. Analyse de la réponse de l'étudiant

Explique pourquoi sa réponse est correcte ou incorrecte.

## 5. À retenir pour le concours

Donne les points essentiels à mémoriser.

## 6. Exemple pratique

Donne un exemple concret permettant de comprendre
le concept.

## 7. Mini-question

Pose une petite question similaire pour vérifier
la compréhension.

Réponds en français.
Sois précis, pédagogique et adapté à un étudiant
en préparation d'un concours informatique.
"""

    # =====================================================
    # STREAM GEMINI RESPONSE
    # =====================================================

    llm = get_llm()

    for chunk in llm.stream(prompt):

        content = getattr(
            chunk,
            "content",
            ""
        )

        text = extract_chunk_text(
            content
        )

        if text:

            yield text