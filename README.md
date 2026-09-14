# M2I FS Tétouan — QCM Preparation System

A Python + LangGraph application for preparing the **Master M2I (Informatique) entrance exam at FS Tétouan** through randomized QCM exams generated from a curated JSON database of questions and verified correct answers.

The application is designed so that the **question database remains the source of truth**. The LLM is optional and is used mainly for explanations and personalized feedback, not for deciding which answer is correct.

---

## 1. Project Goals

The application should allow a student to:

- Practice individual subjects.
- Generate complete mock exams.
- Generate randomized QCMs from an existing question bank.
- Answer questions through a Streamlit interface.
- Automatically calculate the score.
- Review wrong answers.
- Get AI explanations for mistakes.
- Track weak subjects/topics.
- Generate future practice exams focused on weaknesses.

The main principle is:

> **Questions and correct answers come from the JSON database. Python performs deterministic selection and correction. LangGraph orchestrates the workflow. Gemini is used only where an LLM adds value.**

---

## 2. High-Level Architecture

```text
                        questions.json
                              |
                              v
                    +-------------------+
                    | Load Questions    |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Select Questions  |
                    | Random / Subject  |
                    | / Difficulty      |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Validate Exam     |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    |    Student        |
                    |    takes QCM      |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Collect Answers   |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Correct Exam      |
                    | Using JSON        |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Calculate Score   |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Analyze Results   |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Gemini (optional) |
                    | Explain Mistakes |
                    +---------+---------+
                              |
                              v
                           Results
```

---

## 3. Technologies

- **Python 3.11+**
- **LangGraph** — workflow orchestration
- **LangChain** — LLM integration
- **Google Gemini** — optional AI explanations and feedback
- **Streamlit** — web interface
- **JSON** — question database
- **Pydantic / TypedDict** — structured state and validation
- **python-dotenv** — environment variables

No vector database or RAG system is required for the first version.

---

## 4. Recommended Project Structure

```text
m2i_preparation/
│
├── data/
│   └── questions.json
│
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── loader.py
│   ├── exam.py
│   ├── graph.py
│   └── llm.py
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 5. Question Database

The main database is `data/questions.json`.

Each question should contain:

- `id`
- `subject`
- `topic`
- `difficulty`
- `question`
- `choices`
- `correct_answer`
- `explanation`

Example:

```json
[
  {
    "id": 1,
    "subject": "Algorithmique",
    "topic": "Complexité algorithmique",
    "difficulty": "medium",
    "question": "Quelle est la complexité de la recherche binaire ?",
    "choices": {
      "A": "O(n)",
      "B": "O(log n)",
      "C": "O(n²)",
      "D": "O(1)"
    },
    "correct_answer": "B",
    "explanation": "La recherche binaire divise l'espace de recherche par deux à chaque étape."
  },
  {
    "id": 2,
    "subject": "Bases de données",
    "topic": "SQL",
    "difficulty": "easy",
    "question": "Que signifie SQL ?",
    "choices": {
      "A": "Structured Query Language",
      "B": "Simple Query Language",
      "C": "System Query Language",
      "D": "Sequential Query Language"
    },
    "correct_answer": "A",
    "explanation": "SQL signifie Structured Query Language."
  }
]
```

### Important

`correct_answer` must be stored explicitly.

For example:

```json
"correct_answer": "B"
```

The application should compare the student's answer directly with this value.

The LLM must **not** be responsible for grading the QCM.

---

## 6. Suggested Subjects

The question bank can be organized around the computer-science domains relevant to the M2I preparation, for example:

```text
Architecture des ordinateurs
Algorithmique
Structures de données
Langage C
Python
C++
Java
Programmation orientée objet
Bases de données
SQL
Systèmes d'information
UML
Systèmes d'exploitation
Réseaux
Développement Web
IoT
Compilation
Programmation linéaire
Programmation en nombres entiers
```

The exact question distribution should be based on the material and past exams available to you.

---

## 7. LangGraph State

The workflow can use a state similar to:

```python
from typing import TypedDict


class ExamState(TypedDict):

    # Configuration
    exam_name: str
    number_of_questions: int
    subjects: list[str]

    # Question bank
    all_questions: list[dict]

    # Generated exam
    exam: list[dict]

    # Student progress
    current_question: int
    user_answers: dict[int, str]

    # Results
    score: int
    results: list[dict]

    # Learning
    weak_topics: list[str]

    # Optional AI feedback
    ai_feedback: str
```

---

## 8. LangGraph Workflow

### Exam generation

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
  +---- invalid ----> select_questions
  |
  v
END
```

### Exam correction

```text
START
  |
  v
correct_exam
  |
  v
calculate_score
  |
  v
analyze_results
  |
  v
optional_ai_feedback
  |
  v
END
```

### Complete conceptual workflow

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
                       /       \
                 invalid       valid
                   |             |
                   +----<--------+
                                 |
                                 v
                           take exam
                                 |
                                 v
                         collect answers
                                 |
                                 v
                           correct_exam
                                 |
                                 v
                         calculate_score
                                 |
                                 v
                        analyze_results
                                 |
                                 v
                       Gemini (optional)
                                 |
                                 v
                                END
```

---

## 9. Deterministic vs LLM Tasks

The project should separate tasks that require an LLM from tasks that should remain deterministic.

### Deterministic Python tasks

These should not use an API:

```text
Load JSON
Select questions
Randomize questions
Randomize answer order (if implemented)
Check answers
Calculate score
Identify correct/wrong answers
Calculate percentages
Track question history
Track weak subjects
```

### Gemini / LLM tasks

These are optional:

```text
Explain a wrong answer
Explain a difficult concept
Summarize weak topics
Generate personalized study advice
Answer follow-up questions about a topic
```

This design keeps the system reliable and reduces API usage.

---

## 10. API Usage

The core QCM application can run with:

```text
0 API calls
```

for:

- loading questions
- generating a randomized exam
- displaying questions
- collecting answers
- correcting answers
- calculating the score

If Gemini is enabled, the recommended design is to make **one batched API call after the exam** for explanations.

Example:

```text
30-question exam
      |
      v
Student answers
      |
      v
Python identifies 6 mistakes
      |
      v
1 Gemini request containing the 6 mistakes
      |
      v
Explanations
```

So a complete exam can typically use:

```text
Core QCM:        0 API calls
AI explanations: 1 API call
```

A separate follow-up chat question would use another API call.

---

## 11. Why the LLM Should Not Generate the Correct Answers

The database contains verified answers.

For example:

```json
{
  "question": "What is the time complexity of binary search?",
  "correct_answer": "B"
}
```

The application should do:

```python
student_answer == question["correct_answer"]
```

rather than:

```text
Student answer
      |
      v
LLM
      |
      v
"Probably B"
```

This prevents the model from introducing grading errors or hallucinating answers.

---

## 12. Random Exam Generation

Suppose the database contains:

```text
1000 questions
```

The user requests:

```text
30 questions
```

The program selects 30 questions randomly.

Example:

```text
Exam 1
Q12
Q47
Q81
Q102
Q205
...

Exam 2
Q5
Q31
Q88
Q154
Q202
...
```

Each attempt can therefore produce a different exam.

---

## 13. Subject-Based Exams

The application should support:

```text
Subject:
    Algorithmique

Number of questions:
    20
```

and then retrieve only:

```python
question["subject"] == "Algorithmique"
```

Example interface:

```text
+--------------------------------------+
| M2I FS Tétouan Preparation           |
+--------------------------------------+
| Subject: [ Algorithmique          ]  |
|                                      |
| Questions: [ 20 ]                    |
|                                      |
| Difficulty: [ Mixed              ]  |
|                                      |
|           [ START EXAM ]             |
+--------------------------------------+
```

---

## 14. Full Mock Exam

A future version can generate a mixed exam.

Example:

```text
M2I Mock Exam
30 questions

Algorithmique          5
Python                 3
C                      3
Bases de données       4
Réseaux                3
Systèmes d'exploitation 3
Java / C++              3
Web                     2
Architecture            2
UML                     1
Compilation              1
```

The exact distribution can later be configurable.

---

## 15. Adaptive Preparation

A later version can store the student's results.

Example:

```text
Student performance

Algorithmique       85%
Python              80%
SQL                 72%
Réseaux             45%
OS                  50%
```

The application can identify:

```text
Weak topics:
- Réseaux
- Systèmes d'exploitation
```

Then the next exam can focus more on those topics.

Example:

```text
Next Exam
------------------------------
Algorithmique       2 questions
Python              3 questions
SQL                 5 questions
Réseaux            10 questions
OS                  10 questions
```

This turns the project into an adaptive learning system.

---

## 16. Streamlit Interface

The final application can have several modes:

```text
M2I FS Tétouan Preparation
--------------------------------

[ Full Mock Exam ]
[ Subject Practice ]
[ Random QCM ]
[ Weak Topics ]
[ Review Mistakes ]
```

### QCM screen

```text
Question 7 / 30

What is a primary key?

A. A duplicated value
B. A unique identifier
C. A foreign table
D. An SQL command

( ) A
( ) B
( ) C
( ) D

[ Previous ]     [ Next ]
```

### Results screen

```text
RESULTS

Score: 24 / 30
Percentage: 80%

Correct: 24
Wrong:   6
```

Then:

```text
Question 7

Your answer:
C

Correct answer:
B

Explanation:
...
```

---

## 17. Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
langgraph
langchain
langchain-google-genai
streamlit
python-dotenv
pydantic
```

---

## 18. Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

Load it in Python:

```python
from dotenv import load_dotenv

load_dotenv()
```

Do not commit `.env` to Git.

Add this to `.gitignore`:

```text
.env
.venv/
__pycache__/
*.pyc
```

---

## 19. Running the Application

Run:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

---

## 20. Development Roadmap

### Phase 1 — Question Database

- Create `questions.json`
- Validate the JSON structure
- Load questions with Python
- Filter by subject
- Randomly select questions

### Phase 2 — QCM

- Create exam
- Display questions
- Collect answers
- Correct automatically
- Calculate score

### Phase 3 — LangGraph

- Create `ExamState`
- Implement nodes
- Add conditional edges
- Compile the graph

### Phase 4 — Streamlit

- Build exam configuration
- Build QCM interface
- Add results page
- Add mistake review

### Phase 5 — Gemini

- Explain wrong answers
- Generate personalized feedback
- Identify weak topics

### Phase 6 — Adaptive Learning

- Store exam history
- Track performance by subject/topic
- Prioritize weak topics
- Generate personalized exams

---

## 21. Core Design Principle

The final architecture should remain:

```text
                JSON DATABASE
                     |
                     v
              Python / LangGraph
                     |
          +----------+----------+
          |                     |
          v                     v
      QCM generation         Correction
          |                     |
          +----------+----------+
                     |
                     v
                 Results
                     |
                     v
              Gemini (optional)
                     |
                     v
               Explanations
```

The **JSON question bank is the source of truth**.

LangGraph orchestrates the process.

Python handles deterministic logic.

Gemini adds intelligence where it is useful.

Streamlit provides the student interface.
