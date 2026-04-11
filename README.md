# ai-financial-agent

A Flask-based fintech assistant with:

- Expense tracking and SQLite storage
- REST APIs (`/add-expense`, `/get-expenses`, `/summary`, `/chat`)
- AI-style financial advice using your current expense profile
- Dark modern dashboard with totals, recent expenses, and a Chart.js pie chart

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000`.

## Deploy

Gunicorn entrypoint:

```bash
gunicorn app:app
```
