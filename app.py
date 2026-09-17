import streamlit as st

from src.graph import (
    exam_graph,
    correction_graph
)

from src.loader import (
    get_question_types
)

from src.llm import (
    stream_question_explanation
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="M2I FS Tétouan - QCM Preparation",
    page_icon="🎓",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "exam" not in st.session_state:

    st.session_state.exam = None


if "answers" not in st.session_state:

    st.session_state.answers = {}


if "results" not in st.session_state:

    st.session_state.results = None


if "score" not in st.session_state:

    st.session_state.score = None


if "distribution" not in st.session_state:

    st.session_state.distribution = {}


# ---------------------------------------------------------
# Store completed AI explanations
#
# question_id -> full explanation text
# ---------------------------------------------------------

if "ai_explanations" not in st.session_state:

    st.session_state.ai_explanations = {}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_answer_letter(
    option: str
) -> str:
    """
    Convert:

        B. Some answer

    into:

        B
    """

    return (
        option
        .split(".", 1)[0]
        .strip()
    )


def get_option_text(
    answer_letter: str,
    options: list[str]
) -> str:
    """
    Convert:

        B

    into:

        B. Complete answer
    """

    for option in options:

        if (
            get_answer_letter(option)
            == answer_letter
        ):

            return option

    return answer_letter


# =========================================================
# TITLE
# =========================================================

st.title(
    "🎓 M2I FS Tétouan — QCM Preparation"
)

st.write(
    "Préparation au concours du Master Informatique "
    "à partir de votre base de questions."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header(
        "⚙️ Configuration de l'examen"
    )

    # -----------------------------------------------------
    # LOAD TYPES
    # -----------------------------------------------------

    try:

        question_types = (
            get_question_types()
        )

    except Exception as e:

        st.error(
            f"Impossible de charger les types : {e}"
        )

        st.stop()


    # -----------------------------------------------------
    # MODE
    # -----------------------------------------------------

    mode = st.radio(
        "Mode de sélection",
        [
            "Tous les types",
            "Choisir les types"
        ]
    )


    # =====================================================
    # ALL TYPES
    # =====================================================

    if mode == "Tous les types":

        selected_types = []

        st.info(
            "Toutes les matières seront utilisées "
            "avec une répartition proportionnelle "
            "au nombre de questions disponibles."
        )


    # =====================================================
    # SELECT TYPES
    # =====================================================

    else:

        selected_types = st.multiselect(
            "Choisissez les types",
            options=question_types
        )

        if selected_types:

            st.write(
                "Types sélectionnés :"
            )

            for question_type in selected_types:

                st.write(
                    f"• {question_type}"
                )

        else:

            st.warning(
                "Sélectionnez au moins un type."
            )


    # -----------------------------------------------------
    # NUMBER OF QUESTIONS
    # -----------------------------------------------------

    number_of_questions = st.number_input(
        "Nombre de questions",
        min_value=1,
        max_value=100,
        value=20,
        step=1
    )


    # -----------------------------------------------------
    # BUTTONS
    # -----------------------------------------------------

    generate_exam = st.button(
        "🎯 Générer l'examen",
        use_container_width=True
    )

    reset = st.button(
        "🔄 Réinitialiser",
        use_container_width=True
    )


# =========================================================
# RESET
# =========================================================

if reset:

    st.session_state.exam = None

    st.session_state.answers = {}

    st.session_state.results = None

    st.session_state.score = None

    st.session_state.distribution = {}

    st.session_state.ai_explanations = {}

    st.rerun()


# =========================================================
# GENERATE EXAM
# =========================================================

if generate_exam:

    # -----------------------------------------------------
    # Validate selected types
    # -----------------------------------------------------

    if mode == "Choisir les types":

        if not selected_types:

            st.error(
                "Veuillez sélectionner au moins "
                "un type de question."
            )

            st.stop()


    try:

        # -------------------------------------------------
        # Initial state
        # -------------------------------------------------

        initial_state = {

            "number_of_questions":
                number_of_questions,

            "selected_types":
                selected_types
        }


        # -------------------------------------------------
        # LangGraph
        # -------------------------------------------------

        result = exam_graph.invoke(
            initial_state
        )


        # -------------------------------------------------
        # Save exam
        # -------------------------------------------------

        st.session_state.exam = (
            result["exam"]
        )

        st.session_state.distribution = (
            result["distribution"]
        )

        st.session_state.answers = {}

        st.session_state.results = None

        st.session_state.score = None

        st.session_state.ai_explanations = {}


        # -------------------------------------------------
        # Refresh
        # -------------------------------------------------

        st.rerun()


    except Exception as e:

        st.error(
            f"Erreur lors de la génération : {e}"
        )


# =========================================================
# EXAM DISTRIBUTION
# =========================================================

if st.session_state.exam:

    st.subheader(
        "📊 Répartition de l'examen"
    )

    distribution = (
        st.session_state.distribution
    )

    total_distribution = sum(
        distribution.values()
    )


    if distribution:

        distribution_data = []


        for (
            question_type,
            count
        ) in distribution.items():

            percentage = (
                count
                / total_distribution
                * 100
                if total_distribution > 0
                else 0
            )

            distribution_data.append(
                {
                    "Type":
                        question_type,

                    "Questions":
                        count,

                    "Pourcentage":
                        f"{percentage:.1f}%"
                }
            )


        # Full words are displayed without narrow columns.
        st.dataframe(
            distribution_data,
            use_container_width=True,
            hide_index=True
        )


    st.divider()


# =========================================================
# DISPLAY EXAM
# =========================================================

if st.session_state.exam:

    exam = st.session_state.exam


    st.subheader(
        f"📝 QCM — {len(exam)} questions"
    )


    st.write(
        "Répondez aux questions puis cliquez "
        "sur **Terminer l'examen**."
    )


    st.divider()


    # =====================================================
    # QUESTIONS
    # =====================================================

    for index, question in enumerate(
        exam
    ):

        question_number = index + 1


        st.markdown(
            f"### Question {question_number}"
        )


        st.caption(
            f"Type : {question['type']}"
        )


        # -------------------------------------------------
        # QUESTION
        # -------------------------------------------------

        st.write(
            question["question"]
        )


        # =================================================
        # MULTIPLE ANSWERS
        # =================================================

        if len(
            question["correct_answers"]
        ) > 1:

            st.caption(
                "☑️ Plusieurs réponses sont possibles."
            )


            selected_options = st.multiselect(
                "Sélectionnez les réponses :",
                options=question["options"],
                key=f"question_{question['id']}"
            )


            st.session_state.answers[
                question["id"]
            ] = [

                get_answer_letter(option)

                for option
                in selected_options
            ]


        # =================================================
        # SINGLE ANSWER
        # =================================================

        else:

            st.caption(
                "🔘 Une seule réponse est possible."
            )


            selected_option = st.radio(
                "Choisissez une réponse :",
                options=question["options"],
                key=f"question_{question['id']}"
            )


            if selected_option:

                st.session_state.answers[
                    question["id"]
                ] = [

                    get_answer_letter(
                        selected_option
                    )

                ]

            else:

                st.session_state.answers[
                    question["id"]
                ] = []


        st.divider()


    # =====================================================
    # SUBMIT
    # =====================================================

    if st.button(
        "✅ Terminer l'examen",
        use_container_width=True
    ):

        correction_state = {

            "exam":
                exam,

            "user_answers":
                st.session_state.answers
        }


        try:

            result = correction_graph.invoke(
                correction_state
            )


            st.session_state.results = (
                result["results"]
            )


            st.session_state.score = (
                result["score"]
            )


            st.rerun()


        except Exception as e:

            st.error(
                f"Erreur lors de la correction : {e}"
            )


# =========================================================
# RESULTS
# =========================================================

if st.session_state.results is not None:

    results = (
        st.session_state.results
    )

    score = (
        st.session_state.score
    )

    total = len(results)


    # -----------------------------------------------------
    # Percentage
    # -----------------------------------------------------

    percentage = (
        score
        / total
        * 100
        if total > 0
        else 0
    )


    # =====================================================
    # RESULTS HEADER
    # =====================================================

    st.header(
        "📊 Résultats"
    )


    # =====================================================
    # SCORE CARDS
    # =====================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Score",
            f"{score}/{total}"
        )


    with col2:

        st.metric(
            "Pourcentage",
            f"{percentage:.1f}%"
        )


    with col3:

        st.metric(
            "Erreurs",
            total - score
        )


    st.divider()


    # =====================================================
    # PERFORMANCE MESSAGE
    # =====================================================

    if percentage >= 80:

        st.success(
            "🎉 Excellent résultat !"
        )

    elif percentage >= 60:

        st.warning(
            "👍 Bon résultat, mais vous pouvez encore progresser."
        )

    else:

        st.error(
            "📚 Continuez à réviser les notions où "
            "vous avez fait des erreurs."
        )


    st.divider()


    # =====================================================
    # CORRECTION
    # =====================================================

    st.subheader(
        "📚 Correction"
    )


    for index, result in enumerate(
        results
    ):

        question_number = index + 1


        # =================================================
        # STATUS
        # =================================================

        if result["correct"]:

            st.success(
                f"Question {question_number} — ✅ Correct"
            )

        else:

            st.error(
                f"Question {question_number} — ❌ Incorrect"
            )


        # =================================================
        # EXPANDER
        # =================================================

        with st.expander(
            f"👁️ Voir la question {question_number}"
        ):

            # ---------------------------------------------
            # QUESTION
            # ---------------------------------------------

            st.markdown(
                f"### Question {question_number}"
            )


            st.caption(
                f"Type : {result['type']}"
            )


            st.write(
                result["question"]
            )


            st.divider()


            # =============================================
            # YOUR ANSWER
            # =============================================

            st.markdown(
                "### 🔵 Votre réponse"
            )


            if result["user_answers"]:

                for answer_letter in (
                    result["user_answers"]
                ):

                    answer_text = (
                        get_option_text(
                            answer_letter,
                            result["options"]
                        )
                    )


                    st.write(
                        f"🔵 {answer_text}"
                    )

            else:

                st.write(
                    "❌ Aucune réponse"
                )


            # =============================================
            # CORRECT ANSWER
            # =============================================

            st.markdown(
                "### 🟢 Réponse correcte"
            )


            for answer_letter in (
                result["correct_answers"]
            ):

                answer_text = (
                    get_option_text(
                        answer_letter,
                        result["options"]
                    )
                )


                st.write(
                    f"🟢 {answer_text}"
                )


            st.divider()


            # =============================================
            # DATABASE EXPLANATION
            # =============================================

            st.markdown(
                "### 💡 Explication de la base"
            )


            st.info(
                result["explanation"]
            )


            st.divider()


            # =============================================
            # GEMINI DEEP EXPLANATION
            # =============================================

            st.markdown(
                "### 🤖 Professeur IA"
            )


            question_id = (
                result["question_id"]
            )


            # -------------------------------------------------
            # Already generated?
            # -------------------------------------------------

            if question_id in (
                st.session_state.ai_explanations
            ):

                st.markdown(
                    st.session_state
                    .ai_explanations[
                        question_id
                    ]
                )


            # -------------------------------------------------
            # Generate new explanation
            # -------------------------------------------------

            else:

                explain_button = st.button(
                    "🔎 Expliquer cette question en profondeur",
                    key=f"explain_{question_id}"
                )


                if explain_button:

                    st.markdown(
                        "### 🤖 Explication détaillée"
                    )


                    try:

                        # -----------------------------------------
                        # Stream Gemini response
                        # -----------------------------------------

                        full_response = st.write_stream(
                            stream_question_explanation(

                                question=
                                    result["question"],

                                options=
                                    result["options"],

                                user_answers=
                                    result["user_answers"],

                                correct_answers=
                                    result["correct_answers"],

                                database_explanation=
                                    result["explanation"],

                                question_type=
                                    result["type"]
                            )
                        )


                        # -----------------------------------------
                        # Save complete response
                        # -----------------------------------------

                        st.session_state.ai_explanations[
                            question_id
                        ] = full_response


                    except Exception as e:

                        st.error(
                            f"Erreur lors de l'appel à Gemini : {e}"
                        )


    # =====================================================
    # RESULTS BY TYPE
    # =====================================================

    st.divider()


    st.subheader(
        "📈 Résultats par type"
    )


    type_statistics = {}


    for result in results:

        question_type = (
            result["type"]
        )


        if question_type not in (
            type_statistics
        ):

            type_statistics[
                question_type
            ] = {
                "correct": 0,
                "total": 0
            }


        type_statistics[
            question_type
        ]["total"] += 1


        if result["correct"]:

            type_statistics[
                question_type
            ]["correct"] += 1


    # -----------------------------------------------------
    # Create table
    # -----------------------------------------------------

    type_results_data = []


    for (
        question_type,
        statistics
    ) in type_statistics.items():

        correct = (
            statistics["correct"]
        )

        type_total = (
            statistics["total"]
        )

        type_percentage = (
            correct
            / type_total
            * 100
            if type_total > 0
            else 0
        )


        type_results_data.append(
            {
                "Type":
                    question_type,

                "Correct":
                    correct,

                "Total":
                    type_total,

                "Pourcentage":
                    f"{type_percentage:.1f}%"
            }
        )


    st.dataframe(
        type_results_data,
        use_container_width=True,
        hide_index=True
    )