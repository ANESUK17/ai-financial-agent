import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expenses.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                category TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()


def fetch_expenses() -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, amount, category, timestamp FROM expenses ORDER BY datetime(timestamp) DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def build_summary(expenses: list[dict]) -> dict:
    total_spending = sum(float(item["amount"]) for item in expenses)
    category_totals: dict[str, float] = {}

    for item in expenses:
        category = item["category"].strip() or "Uncategorized"
        category_totals[category] = category_totals.get(category, 0.0) + float(item["amount"])

    top_category = None
    if category_totals:
        top_category = max(category_totals.items(), key=lambda pair: pair[1])

    return {
        "count": len(expenses),
        "total_spending": round(total_spending, 2),
        "category_totals": {k: round(v, 2) for k, v in category_totals.items()},
        "top_category": {
            "name": top_category[0],
            "amount": round(top_category[1], 2),
        }
        if top_category
        else None,
    }


def generate_advice(summary: dict, message: str) -> str:
    message_lower = message.lower()
    total = summary["total_spending"]
    count = summary["count"]
    top_category = summary.get("top_category")

    if count == 0:
        return (
            "You have no expenses logged yet. Add a few expenses first, then I can provide tailored financial advice."
        )

    advice_parts = [
        f"You've logged {count} expense(s) with total spending of ${total:.2f}."
    ]

    if top_category:
        advice_parts.append(
            f"Your largest category is {top_category['name']} at ${top_category['amount']:.2f}."
        )

    if "save" in message_lower or "saving" in message_lower:
        advice_parts.append(
            "Try a 50/30/20 budget split and set a weekly savings transfer right after payday."
        )
    elif "budget" in message_lower:
        advice_parts.append(
            "Set category caps based on your current totals and review them every Sunday."
        )
    elif "debt" in message_lower:
        advice_parts.append(
            "If you have debt, prioritize high-interest balances first while keeping minimum payments on others."
        )
    else:
        advice_parts.append(
            "To optimize spending, focus on reducing your top category by 10% this month and track progress weekly."
        )

    return " ".join(advice_parts)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add-expense", methods=["POST"])
def add_expense():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    category = str(payload.get("category", "")).strip() or "Uncategorized"

    try:
        amount = float(payload.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a number."}), 400

    if not name:
        return jsonify({"error": "Expense name is required."}), 400

    if amount < 0:
        return jsonify({"error": "Amount must be zero or positive."}), 400

    timestamp = payload.get("timestamp")
    if timestamp:
        try:
            parsed = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            timestamp = parsed.isoformat()
        except ValueError:
            return jsonify({"error": "Timestamp must be ISO 8601 format."}), 400
    else:
        timestamp = datetime.utcnow().isoformat() + "Z"

    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO expenses (name, amount, category, timestamp) VALUES (?, ?, ?, ?)",
            (name, amount, category, timestamp),
        )
        conn.commit()
        new_id = cursor.lastrowid

    return jsonify(
        {
            "id": new_id,
            "name": name,
            "amount": round(amount, 2),
            "category": category,
            "timestamp": timestamp,
        }
    ), 201


@app.route("/get-expenses", methods=["GET"])
def get_expenses():
    return jsonify({"expenses": fetch_expenses()})


@app.route("/summary", methods=["GET"])
def summary():
    return jsonify(build_summary(fetch_expenses()))


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    summary_data = build_summary(fetch_expenses())
    response = generate_advice(summary_data, message)

    return jsonify({"response": response, "summary": summary_data})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
