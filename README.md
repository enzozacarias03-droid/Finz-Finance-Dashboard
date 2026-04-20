# FinZ - AI Personal Finance Dashboard

A web app that tracks personal expenses and provides AI-powered financial advice using GPT-40-mini

## Features
- Add and categorize expenses
- Interactive spending charts (Plotly)
- Expense history table
- AI financial advisor chatbot

## Tech Stack
Python, Streamlit, Pandas, Plotly, OpenAI API, SQLite

## Setup
1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\Activate.ps1`
4. Install: `pip install -r requirements.txt`
5. Create `.env` with: `OPENAI_API_KEY=your_key_here`
6. Run: `python -m streamlit run app.py`