import os
import re
import requests
from flask import Flask, request, render_template_string
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GROQ_KEY = os.environ.get("GROQ_API_KEY")
ERP_KEY = os.environ.get("ERP_API_KEY")
ERP_SECRET = os.environ.get("ERP_API_SECRET")
ERP_URL = os.environ.get("ERP_BASE_URL", "http://localhost:8080")

client = Groq(api_key=GROQ_KEY)

auth = {
    "Authorization": f"token {ERP_KEY}:{ERP_SECRET}"
}

history = []

patterns = {
    "Sales Order": r"SAL-ORD-\d{4}-\d{5}",
    "Employee": r"HR-EMP-\d{5}",
    "Sales Invoice": r"ACC-SINV-\d{4}-\d{5}",
}

html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI ERPNext Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #e5ddd5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .chat-container {
            width: 400px;
            height: 600px;
            background: #fff;
            display: flex;
            flex-direction: column;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }

        .header {
            background: #075E54;
            color: white;
            padding: 12px 16px;
            font-size: 18px;
            font-weight: bold;
        }

        .chat-box {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .message {
            padding: 10px 14px;
            border-radius: 10px;
            max-width: 75%;
            word-wrap: break-word;
            font-size: 14px;
            line-height: 1.4;
        }

        .user {
            background: #dcf8c6;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }

        .bot {
            background: #f1f0f0;
            align-self: flex-start;
            border-bottom-left-radius: 2px;
        }

        .input-box {
            display: flex;
            padding: 10px;
            border-top: 1px solid #ccc;
            gap: 8px;
        }

        input {
            flex: 1;
            padding: 10px 14px;
            border-radius: 20px;
            border: 1px solid #ccc;
            outline: none;
            font-size: 14px;
        }

        button {
            padding: 10px 16px;
            border: none;
            border-radius: 20px;
            background: #128C7E;
            color: white;
            cursor: pointer;
            font-size: 14px;
        }

        button:hover {
            background: #0e7a6e;
        }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="header">AI ERPNext Chatbot</div>

    <div class="chat-box" id="chatBox">
        {% for msg in messages %}
        <div class="message {{ msg.type }}">{{ msg.text }}</div>
        {% endfor %}
    </div>

    <form method="POST" class="input-box">
        <input name="query" placeholder="Type your message..." autocomplete="off" required>
        <button type="submit">Send</button>
    </form>
</div>

<script>
    const chatBox = document.getElementById("chatBox");
    chatBox.scrollTop = chatBox.scrollHeight;
</script>

</body>
</html>
"""
def find_doc(query):
    for doc_type, pattern in patterns.items():
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return doc_type, match.group()
    return None, None

def get_erp_data(doc_type, doc_id):
    url = f"{ERP_URL}/api/resource/{doc_type}/{doc_id}"
    res = requests.get(url, headers=auth)
    if res.status_code != 200:
        return None
    return res.json().get("data", {})
    
def ask_ai(prompt):
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content
    
def get_reply(query):
    doc_type, doc_id = find_doc(query)

    if not doc_id:
        return ask_ai(query)

    data = get_erp_data(doc_type, doc_id)
    if data is None:
        return "Could not fetch data from ERPNext. Please check the document ID."

    prompt = f"""User question: {query}

Here is the ERP data for {doc_type} ({doc_id}):
{data}

Answer the user's question clearly based on the data above."""

    return ask_ai(prompt)


@app.route("/", methods=["GET", "POST"])
def home():
    global history

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        history.append({"type": "user", "text": query})

        try:
            reply = get_reply(query)
        except Exception as e:
            reply = f"Something went wrong: {str(e)}"

        history.append({"type": "bot", "text": reply})

    return render_template_string(html, messages=history)
    
if __name__ == "__main__":
    app.run(port=5000, debug=True)
