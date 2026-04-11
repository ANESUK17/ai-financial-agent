import os

from flask import Flask, jsonify, request
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@app.route("/", methods=["GET"])
def index():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Flask AI Chatbot</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 30px auto; padding: 0 12px; }
    #chat { border: 1px solid #ddd; border-radius: 8px; padding: 12px; height: 360px; overflow-y: auto; background: #fafafa; }
    .msg { margin: 8px 0; }
    .user { color: #0b57d0; }
    .bot { color: #1b5e20; }
    form { display: flex; gap: 8px; margin-top: 10px; }
    input { flex: 1; padding: 10px; }
    button { padding: 10px 14px; cursor: pointer; }
  </style>
</head>
<body>
  <h2>Flask AI Chatbot</h2>
  <div id="chat"></div>
  <form id="chatForm">
    <input id="message" type="text" placeholder="Type a message..." required />
    <button type="submit">Send</button>
  </form>

  <script>
    const chat = document.getElementById('chat');
    const form = document.getElementById('chatForm');
    const input = document.getElementById('message');

    function addMessage(role, text) {
      const div = document.createElement('div');
      div.className = `msg ${role}`;
      div.textContent = `${role === 'user' ? 'You' : 'Bot'}: ${text}`;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const message = input.value.trim();
      if (!message) return;

      addMessage('user', message);
      input.value = '';

      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
        });

        const data = await res.json();
        if (!res.ok) {
          addMessage('bot', data.error || 'Request failed.');
          return;
        }

        addMessage('bot', data.response || 'No response.');
      } catch (err) {
        addMessage('bot', 'Network error.');
      }
    });
  </script>
</body>
</html>
"""


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
