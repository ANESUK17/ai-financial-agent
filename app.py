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


@app.route("/advice", methods=["GET"])
def advice():
    if not expenses:
        return jsonify({"advice": "Add a few expenses first to get personalized AI advice."})

    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({"error": "OPENAI_API_KEY is not set."}), 500

    total_spending = sum(expense["amount"] for expense in expenses)
    by_category = {}
    for expense in expenses:
        category = expense.get("category", "Other")
        by_category[category] = by_category.get(category, 0) + float(expense.get("amount", 0))

    top_categories = sorted(by_category.items(), key=lambda item: item[1], reverse=True)[:3]
    category_summary = ", ".join(
        [f"{name}: ${amount:.2f}" for name, amount in top_categories]
    )

    prompt = (
        "You are a practical financial coach. Based on the expense data, "
        "give 3 short, actionable tips to reduce spending and improve savings.\n"
        f"Total spending: ${total_spending:.2f}\n"
        f"Top categories: {category_summary}\n"
        f"Expense count: {len(expenses)}"
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You provide concise, friendly financial advice.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        advice_text = completion.choices[0].message.content or "No advice generated."
        return jsonify({"advice": advice_text})
    except Exception as exc:
        return jsonify({"error": f"OpenAI API error: {str(exc)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
