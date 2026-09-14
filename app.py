import streamlit as st

from src.graph import exam_graph, correction_graph
from src.llm import explain_mistakes


st.set_page_config(
    page_title="M2I FS Tétouan Preparation",
    page_icon="🎓",
    layout="wide"
)


# ---------------------------------------------------------
# INITIAL STATE
# ---------------------------------------------------------

if "exam" not in st.session_state:
    st.session_state.exam = None

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "results" not in st.session_state:
    st.session_state.results = None

if "score" not in st.session_state:
    st.session_state.score = None

if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = None


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("🎓 M2I FS Tétouan — QCM Preparation")

st.write(
    "Préparation au concours du Master Informatique "
    "avec LangGraph."
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("Exam Configuration")

    number_of_questions = st.number_input(
        "Nombre de questions",
        min_value=1,
        max_value=50,
        value=20
    )

    generate_exam = st.button(
        "🎯 Generate Exam",
        use_container_width=True
    )

    if st.button(
        "🔄 Reset",
        use_container_width=True
    ):
        st.session_state.exam = None
        st.session_state.answers = {}
        st.session_state.results = None
        st.session_state.score = None
        st.session_state.ai_feedback = None

        st.rerun()


# ---------------------------------------------------------
# GENERATE EXAM
# ---------------------------------------------------------

if generate_exam:

    try:

        initial_state = {
            "number_of_questions": number_of_questions
        }

        result = exam_graph.invoke(
            initial_state
        )

        st.session_state.exam = result["exam"]
        st.session_state.answers = {}
        st.session_state.results = None
        st.session_state.score = None
        st.session_state.ai_feedback = None

        st.rerun()

    except Exception as e:

        st.error(
            f"Impossible de générer l'examen : {e}"
        )


# ---------------------------------------------------------
# DISPLAY EXAM
# ---------------------------------------------------------

if st.session_state.exam:

    exam = st.session_state.exam

    st.subheader(
        f"QCM — {len(exam)} questions"
    )

    st.divider()

    for index, question in enumerate(exam):

        st.markdown(
            f"### Question {index + 1}"
        )

        st.write(
            question["question"]
        )

        # -------------------------------------------------
        # Determine if single-answer or multiple-answer
        # -------------------------------------------------

        is_multiple = (
            len(question["correct_answers"]) > 1
        )

        if is_multiple:

            selected = st.multiselect(
                "Sélectionnez les réponses :",
                options=question["options"],
                key=f"question_{question['id']}"
            )

            st.session_state.answers[
                question["id"]
            ] = [
                option[0]
                for option in selected
            ]

        else:

            selected = st.radio(
                "Choisissez une réponse :",
                options=question["options"],
                key=f"question_{question['id']}"
            )

            st.session_state.answers[
                question["id"]
            ] = [
                selected[0]
            ]

        st.divider()


    # -----------------------------------------------------
    # SUBMIT
    # -----------------------------------------------------

    if st.button(
        "✅ Submit Exam",
        use_container_width=True
    ):

        correction_state = {
            "exam": exam,
            "user_answers": st.session_state.answers
        }

        result = correction_graph.invoke(
            correction_state
        )

        st.session_state.results = result["results"]
        st.session_state.score = result["score"]

        st.rerun()


# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------

if st.session_state.results is not None:

    results = st.session_state.results
    score = st.session_state.score

    total = len(results)

    percentage = (
        score / total * 100
        if total > 0
        else 0
    )

    st.header("📊 Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Score",
            f"{score}/{total}"
        )

    with col2:
        st.metric(
            "Percentage",
            f"{percentage:.1f}%"
        )

    with col3:
        st.metric(
            "Incorrect",
            total - score
        )

    st.divider()

    # -----------------------------------------------------
    # REVIEW ANSWERS
    # -----------------------------------------------------

    for index, result in enumerate(results):

        if result["correct"]:

            st.success(
                f"Question {index + 1} — Correct"
            )

        else:

            st.error(
                f"Question {index + 1} — Incorrect"
            )

            st.write(
                result["question"]
            )

            st.write(
                f"Votre réponse : "
                f"{', '.join(result['user_answers'])}"
            )

            st.write(
                f"Bonne réponse : "
                f"{', '.join(result['correct_answers'])}"
            )

            with st.expander("Voir l'explication"):

                st.write(
                    result["explanation"]
                )


    # -----------------------------------------------------
    # AI EXPLANATION
    # -----------------------------------------------------

    st.divider()

    st.subheader("🤖 AI Tutor")

    if st.button(
        "Explain my mistakes"
    ):

        with st.spinner(
            "Gemini analyse vos erreurs..."
        ):

            try:

                feedback = explain_mistakes(
                    results
                )

                st.session_state.ai_feedback = feedback

            except Exception as e:

                st.error(
                    f"Erreur Gemini : {e}"
                )


    if st.session_state.ai_feedback:

        st.markdown(
            st.session_state.ai_feedback
        )