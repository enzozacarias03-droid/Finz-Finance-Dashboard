# FinZ - AI Personal Finance Dashboard

A web app that tracks personal expenses and provides 
AI-powered financial advice using Claude AI (Haiku).

## Live Demo
https://finz-finance-dashboard-pbn2sug6ykaaununuoqbk2.streamlit.app/

## Features
- Add and categorise expenses with date tracking
- Interactive spending charts (donut + bar chart)
- Full expense history table
- AI financial advisor chatbot powered by Claude

## Tech Stack
Python, Streamlit, Pandas, Plotly, Anthropic Claude API, SQLite

## Setup
1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with: `ANTHROPIC_API_KEY=your_key_here`
6. Run: `python -m streamlit run app.py`

## Project Structure
- `app.py` — main Streamlit application
- `database.py` — SQLite database layer
- `requirements.txt` — project dependencies
- `.env` — API keys (not included, see Setup)

## Architecture Note
Currently uses SQLite for simplicity. 
Production version would use PostgreSQL for 
persistent multi-user data storage.