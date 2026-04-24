
from flask import Flask, request, render_template_string
import requests
import re

app = Flask(__name__)

API_KEY = "2d0cdea1e39320d"
API_SECRET = "2ad8b76228da471"

AUTH_HEADERS = {
    "Authorization": f"token {API_KEY}:{API_SECRET}"
}


PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>ERPNext Chatbot</title>
    <style>
        body {
            font-family: Arial;
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
            background: white;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }

        .header {
            background: #075E54;
            color: white;
            padding: 15px;
            font-size: 18px;
        }

        .chat-box {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            background: #ece5dd;
            display: flex;
            flex-direction: column;
        }

        .message {
            margin: 5px 0;
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
            word-wrap: break-word;
        }

        .user {
            background: #dcf8c6;
            align-self: flex-end;
        }

        .bot {
            background: white;
            align-self: flex-start;
        }

        .input-box {
            display: flex;
            padding: 10px;
            background: #f0f0f0;
        }

        input[type=text] {
            flex: 1;
            padding: 10px;
            border-radius: 20px;
            border: 1px solid #ccc;
            outline: none;
        }

        button {
            margin-left: 10px;
            padding: 10px 15px;
            border: none;
            border-radius: 20px;
            background: #128C7E;
            color: white;
            cursor: pointer;
        }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="header">ERPNext Chatbot</div>
    <div class="chat-box">
        {% for msg in messages %}
            <div class="message {{ msg.type }}">{{ msg.text }}</div>
        {% endfor %}
    </div>
    <form method="POST" class="input-box">
        <input type="text" name="query" placeholder="Type a message..." required>
        <button type="submit">Send</button>
    </form>
</div>
</body>
</html>
"""

def get_doc_info(query):
    # figure out what doc type and id user is asking about
    so_match  = re.search(r"SAL-ORD-\d{4}-\d{5}", query)
    inv_match = re.search(r"ACC-SINV-\d{4}-\d{5}", query)
    emp_match = re.search(r"HR-EMP-\d+", query)

    if so_match:
        return "Sales Order", so_match.group()
    elif inv_match:
        return "Sales Invoice", inv_match.group()
    elif emp_match:
        return "Employee", emp_match.group()
    
    return None, None


def build_response(doc_type, data, q):
    if doc_type == "Sales Order":
        if "status" in q:
            return f"Status: {data.get('status')}"
        elif "amount" in q or "total" in q:
            return f"Amount: {data.get('grand_total')}"
        elif "customer" in q:
            return f"Customer: {data.get('customer_name')}"
        elif "delivery" in q:
            return f"Delivery Date: {data.get('delivery_date')}"
        else:
            return "Ask about status, amount, customer or delivery"

    elif doc_type == "Sales Invoice":
        if "status" in q:
            return f"Status: {data.get('status')}"
        elif "amount" in q or "total" in q:
            return f"Amount: {data.get('grand_total')}"
        else:
            return "Ask about status or amount"

    elif doc_type == "Employee":
        if "name" in q:
            return f"Employee Name: {data.get('employee_name')}"
        elif "status" in q or "active" in q:
            return f"Status: {data.get('status')}"
        elif "joining" in q:
            return f"Joining Date: {data.get('date_of_joining')}"
        else:
            return "Ask about name, status or joining date"


@app.route("/", methods=["GET", "POST"])
def home():
    global messages

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        messages.append({"type": "user", "text": query})

        if not query:
            messages.append({"type": "bot", "text": "Please enter a query"})
            return render_template_string(PAGE, messages=messages)

        try:
            q = query.lower()
            doc_type, doc_id = get_doc_info(query)

            if not doc_type:
                messages.append({"type": "bot", "text": "Invalid ID format"})
                return render_template_string(PAGE, messages=messages)

            url = f"http://localhost:8080/api/resource/{doc_type}/{doc_id}"
            resp = requests.get(url, headers=AUTH_HEADERS)

            if resp.status_code != 200:
                messages.append({"type": "bot", "text": f"API Error: {resp.status_code}"})
                return render_template_string(PAGE, messages=messages)

            data = resp.json().get("data", {})
            reply = build_response(doc_type, data, q)
            messages.append({"type": "bot", "text": reply})

        except Exception as e:
            messages.append({"type": "bot", "text": f"Error: {str(e)}"})

    return render_template_string(PAGE, messages=messages)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
