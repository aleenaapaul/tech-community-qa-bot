# 💬 Tech Community QA Bot

A Streamlit-based QA assistant that helps users find relevant answers to programming questions by querying a custom dataset built from Stack Overflow.

---

## 🚀 Features

- Ask natural language coding questions
- Returns the most relevant Stack Overflow match
- Summarizes long answers using NLP
- Supports filtering by tech stack (Python, JavaScript, Flask, etc.)
- Displays agent reasoning trace and alternate matches

---

## 🧠 Tech Stack

- `Streamlit` – Web app interface
- `Sentence Transformers` – Semantic similarity
- `Transformers (HuggingFace)` – Summarization pipeline
- `BeautifulSoup` – Web scraping for Stack Overflow answers
- `Pandas` – CSV handling
- `Torch` – Model backend

---

## 🛠️ Setup Instructions

1. **Clone this repo**
   ```bash
   git clone https://github.com/aleenaapaul/tech-community-qa-bot.git
   cd tech-community-qa-bot
Create virtual environment
  python -m venv venv
  venv\Scripts\activate   # For Windows

Install dependencies
  pip install -r requirements.txt
Run the app
  streamlit run qa_bot_app.py


 Project Structure:


 tech-community-qa-bot/
│
├── data/
│   ├── clean_questions.csv
│   └── clean_questions_with_answers.csv
│
├── scripts/
│   └── fetch_answers.py
│
├── qa_bot_app.py
├── requirements.txt
└── README.md


👩‍💻 Built by
Aleena Paul

