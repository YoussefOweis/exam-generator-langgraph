# M2I FS Tétouan — QCM Preparation System

A Python, LangGraph, Streamlit, and Gemini-based application for preparing an Informatique Master's entrance exam through a structured QCM question bank.

The application uses a JSON file as the source of truth for questions, answer choices, correct answers, question types, and explanations. LangGraph orchestrates exam generation and correction, while Gemini is called on demand to provide deeper explanations for individual questions.

## Features

- QCM generation from a local JSON question bank.
- Question classification by `type`.
- Full mock exams using a proportional distribution of available question types.
- User selection of one or several question types.
- Single-answer and multiple-answer questions.
- Randomized question selection.
- Deterministic grading using the answers stored in JSON.
- Score and percentage calculation.
- Correction review for every question.
- Display of the student's answer, correct answer, and database explanation.
- Per-type performance statistics.
- Optional Gemini deep explanation for individual questions.
- AI explanations are generated only when the user clicks the explanation button.

## Architecture

```text
                         questions.json
                              |
                              v
                    +--------------------+
                    |   Load Questions   |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    | Filter / Select    |
                    | Question Types     |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    | Proportional Exam  |
                    | Distribution       |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    |      Streamlit     |
                    |      QCM UI        |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    | Student Answers    |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    | LangGraph          |
                    | Correction         |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    | Score + Correction |
                    +---------+----------+
                              |
                              v
                 +---------------------------+
                 | Gemini - optional         |
                 | Deep explanation          |
                 +---------------------------+
```

## Project Structure

```text
projet fin stage/
│
├── app.py
│
├── data/
│   └── questions.json
│
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── loader.py
│   ├── graph.py
│   └── llm.py
│
├── .env
├── requirements.txt
└── README.md
```

`app.py` should be located in the project root, not inside `src`.

## Technologies

- Python
- LangGraph
- LangChain
- Google Gemini
- Streamlit
- JSON
- python-dotenv

## Question Database

The application expects:

```text
data/questions.json
```

The JSON is an array of question objects.

Each question has this structure:

```json
{
  "id": 1,
  "type": "reseaux",
  "question": "L’adresse MAC est :",
  "options": [
    "A. Une adresse logique de chaque carte réseau",
    "B. Une adresse dynamique et variable de chaque carte réseau",
    "C. Une adresse fixe et unique de chaque carte réseau"
  ],
  "correct_answers": [
    "C"
  ],
  "explanation": "L'adresse MAC est l'adresse physique matérielle gravée par le fabricant, unique et constante pour chaque interface réseau."
}
```

### Fields

| Field | Description |
|---|---|
| `id` | Unique question identifier |
| `type` | Subject/category of the question |
| `question` | Question text |
| `options` | List of answer choices |
| `correct_answers` | One or more correct answer letters |
| `explanation` | Explanation stored with the question |

## Question Types

The application reads the available types directly from the JSON file.

For example:

```text
reseaux
ro
algo
c
java
bdd
culture_g
```

New types can be added simply by adding questions with a new value in the `type` field.

No code change is required for the type list.

## Single-Answer Questions

A question with one correct answer:

```json
"correct_answers": [
  "C"
]
```

The interface uses a radio selection.

## Multiple-Answer Questions

A question with multiple correct answers:

```json
"correct_answers": [
  "B",
  "D"
]
```

The interface automatically uses a multiple-selection control.

The student must select exactly the correct combination.

The application compares the complete answer sets when grading.

# Exam Generation

## All Types

The user can choose:

```text
Tous les types
```

The application uses questions from all available types.

The number of questions from each type is distributed proportionally according to how many questions are available in the JSON database.

For example:

```text
Java       16 questions
Réseaux    10 questions
C            5 questions
BDD          2 questions
```

The generated exam follows those proportions as closely as possible.

## Selected Types

The user can choose:

```text
Choisir les types
```

and select:

```text
Java
Réseaux
BDD
```

Only those types are considered.

The proportional distribution is then recalculated using only the selected types.

## Randomization

Questions are selected randomly using Python.

The final exam is shuffled after questions are selected.

This means two generated exams can contain different combinations of questions.

# LangGraph Workflow

## Exam Generation Graph

```text
START
  |
  v
load_questions
  |
  v
select_questions
  |
  v
validate_exam
  |
  v
END
```

### `load_questions`

Loads the JSON database.

### `select_questions`

- filters by the selected types;
- counts questions by type;
- calculates the proportional allocation;
- randomly selects questions;
- shuffles the final exam.

### `validate_exam`

Checks the requested number of questions and duplicate question IDs.

# Correction Graph

```text
START
  |
  v
correct_exam
  |
  v
END
```

Correction is deterministic.

The application compares:

```python
student_answers == correct_answers
```

It does not ask an LLM to decide which answer is correct.

This makes the local question bank the authoritative answer key.

# Correction Interface

After submitting the exam, the application displays:

```text
Score: 24/30
Percentage: 80.0%
Errors: 6
```

Each question can be expanded with:

```text
👁️ Voir la question
```

Inside the correction the user sees:

```text
Question
Type

🔵 Votre réponse
...

🟢 Réponse correcte
...

💡 Explication de la base
...
```

The application converts answer letters such as `B` back to the full option text.

# Gemini Deep Explanation

Gemini is optional.

It is called only when the user clicks:

```text
🔎 Expliquer cette question en profondeur
```

The request contains the question, question type, all options, student's answer, correct answer from the database, and database explanation.

The prompt instructs Gemini to treat the database answer as the reference.

Gemini explains:

1. What the question is asking.
2. Every answer choice.
3. Why the correct answer is correct.
4. Why the student's answer is correct or incorrect.
5. Important concepts to memorize.
6. A practical example.
7. A mini verification question.

# API Usage

Normal QCM operation does not require Gemini:

```text
Load JSON                 → 0 API calls
Generate exam             → 0 API calls
Display questions         → 0 API calls
Correct exam              → 0 API calls
Calculate score           → 0 API calls
Show stored explanation   → 0 API calls
```

Gemini is called only when the user requests an in-depth explanation:

```text
Click "Explain in depth"
        |
        v
1 Gemini API request
```

Each question can therefore be explained independently.

# Gemini Response Handling

Depending on the installed Gemini/LangChain version, `response.content` may be either a string or structured content such as:

```python
[
    {
        "type": "text",
        "text": "..."
    }
]
```

`src/llm.py` extracts only the `text` value from structured content so the Streamlit interface displays the explanation itself rather than the raw response structure.

# Environment Setup

## 1. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\\Scripts\\activate
```

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

Recommended `requirements.txt`:

```text
langgraph
langchain
langchain-google-genai
streamlit
python-dotenv
```

# Gemini API Key

Create:

```text
.env
```

and add:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Do not commit `.env` to Git.

Recommended `.gitignore`:

```text
.env
.venv/
__pycache__/
*.pyc
```

# Run the Application

Open PowerShell in the project root:

```powershell
cd "C:\\Users\\oweis\\Desktop\\projet fin stage"
```

Start Streamlit:

```powershell
streamlit run app.py
```

Do not run:

```powershell
streamlit run src\\app.py
```

because `app.py` belongs in the project root.

# Troubleshooting

## `ModuleNotFoundError: No module named 'src'`

Make sure:

```text
projet fin stage/
├── app.py
└── src/
    ├── __init__.py
    ├── graph.py
    ├── loader.py
    ├── models.py
    └── llm.py
```

Then run:

```powershell
cd "C:\\Users\\oweis\\Desktop\\projet fin stage"
streamlit run app.py
```

## `ImportError: cannot import name 'load_questions'`

Make sure `src/loader.py` defines:

```python
def load_questions():
    ...
```

and `src/graph.py` imports:

```python
from .loader import load_questions
```

## Gemini `404 NOT_FOUND`

The Gemini model identifier may depend on availability associated with the API/account being used.

The current project is configured around:

```python
model="gemini-3.6-flash"
```

If the API reports that a model is unavailable, update the model identifier in `src/llm.py` to one currently available to the API account.

## Gemini API Key Error

Check that `.env` contains:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

and that the application calls:

```python
load_dotenv()
```

before reading the environment variable.

# Design Principles

## JSON is the source of truth

The question database provides the question, options, correct answers, explanation, and type.

The LLM does not replace these values.

## Deterministic grading

Python/LangGraph checks answers against:

```json
"correct_answers": [...]
```

This avoids letting an LLM decide whether a student's answer is correct.

## AI on demand

Gemini is used when it provides additional value, mainly for deep explanations.

This keeps the application simple and reduces unnecessary API usage.

# Future Improvements

Possible future additions:

- Adaptive learning.
- Track performance by type/topic.
- Identify weak areas.
- Generate future exams focused on weaknesses.
- Exam history.
- Persistent student scores.
- Difficulty levels.
- Topics in addition to `type`.
- Configurable exam distributions.
- Timed exams.
- Question review before submission.
- Unanswered-question detection.
- Progress dashboards.
- Study recommendations.
- Separate practice and mock-exam modes.
- Improved question import tools.

# Example User Flow

```text
1. Start application
        |
        v
2. Choose:
   "Tous les types"
   OR
   select specific types
        |
        v
3. Choose number of questions
        |
        v
4. Generate exam
        |
        v
5. Answer QCM
        |
        v
6. Submit
        |
        v
7. Score + correction
        |
        v
8. Open a question
        |
        v
9. See student's answer,
   correct answer,
   database explanation
        |
        v
10. Click "Explain in depth"
        |
        v
11. Gemini provides a deeper explanation
```

# Project Goal

The project provides a structured preparation environment for an Informatique Master's entrance exam using an existing QCM database.

The architecture separates:

```text
Question data       → JSON
Workflow            → LangGraph
Deterministic logic → Python
User interface      → Streamlit
AI explanations     → Gemini
```

This makes the system easier to test, maintain, and extend.
