import os

from flask import Flask, jsonify, render_template, request
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# In-memory expense storage
expenses = []


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/add-expense", methods=["POST"])
def add_expense():
    payload = request.get_json(silent=True) or {}

    name = str(payload.get("name", "")).strip()
    category = str(payload.get("category", "")).strip()

    try:
        amount = float(payload.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a valid number."}), 400

    if not name:
        return jsonify({"error": "Name is required."}), 400
    if not category:
        return jsonify({"error": "Category is required."}), 400
    if amount < 0:
        return jsonify({"error": "Amount must be non-negative."}), 400

    expense = {"name": name, "amount": amount, "category": category}
    expenses.append(expense)

    return jsonify({"message": "Expense added.", "expense": expense}), 201


@app.route("/get-expenses", methods=["GET"])
def get_expenses():
    return jsonify({"expenses": expenses})


@app.route("/summary", methods=["GET"])
def summary():
    total_spending = sum(expense["amount"] for expense in expenses)
    return jsonify({"total_spending": total_spending, "count": len(expenses)})


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({"error": "OPENAI_API_KEY is not set."}), 500

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful, concise AI assistant.",
                },
                {"role": "user", "content": message},
            ],
        )
        reply = completion.choices[0].message.content or ""
        return jsonify({"response": reply})
    except Exception as exc:
        return jsonify({"error": f"OpenAI API error: {str(exc)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
