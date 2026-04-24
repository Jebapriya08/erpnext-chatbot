from flask import Flask, request, render_template_string
import requests
import re

app = Flask(__name__)
API_KEY = "2d0cdea1e39320d"
API_SECRET = "2ad8b76228da471"

headers = {
    "Authorization": f"token {API_KEY}:{API_SECRET}"
}

html = """
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
        }

        .chat-container {
            width: 400px;
            height: 600px;
            background: #fff;
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
            background: #fff;
            align-self: flex-start;
        }

        .input-box {
            display: flex;
            padding: 10px;
            background: #f0f0f0;
        }

        input {
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

messages = []

@app.route("/", methods=["GET", "POST"])
def home():
    global messages

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        messages.append({"type": "user", "text": query})

        if not query:
            messages.append({"type": "bot", "text": "Please enter a query"})
            return render_template_string(html, messages=messages)

        try:
            q = query.lower()

            so = re.search(r"SAL-ORD-\d{4}-\d{5}", query)
            inv = re.search(r"ACC-SINV-\d{4}-\d{5}", query)
            emp = re.search(r"HR-EMP-\d+", query)

            if so:
                doc_type = "Sales Order"
                doc_id = so.group()
            elif inv:
                doc_type = "Sales Invoice"
                doc_id = inv.group()
            elif emp:
                doc_type = "Employee"
                doc_id = emp.group()
            else:
                messages.append({"type": "bot", "text": "Invalid ID format"})
                return render_template_string(html, messages=messages)

            url = f"http://localhost:8080/api/resource/{doc_type}/{doc_id}"

            r = requests.get(url, headers=headers)

            if r.status_code != 200:
                messages.append({"type": "bot", "text": f"API Error: {r.status_code}"})
                return render_template_string(html, messages=messages)

            data = r.json().get("data", {})


            if doc_type == "Sales Order":
                if "status" in q:
                    response = f"Status: {data.get('status')}"
                elif "amount" in q or "total" in q:
                    response = f"Amount: {data.get('grand_total')}"
                elif "customer" in q:
                    response = f"Customer: {data.get('customer_name')}"
                elif "delivery" in q:
                    response = f"Delivery Date: {data.get('delivery_date')}"
                else:
                    response = "Ask about status, amount, customer or delivery"

            elif doc_type == "Sales Invoice":
                if "status" in q:
                    response = f"Status: {data.get('status')}"
                elif "amount" in q or "total" in q:
                    response = f"Amount: {data.get('grand_total')}"
                else:
                    response = "Ask about status or amount"

            elif doc_type == "Employee":
                if "name" in q:
                    response = f"Employee Name: {data.get('employee_name')}"
                elif "status" in q or "active" in q:
                    response = f"Status: {data.get('status')}"
                elif "joining" in q:
                    response = f"Joining Date: {data.get('date_of_joining')}"
                else:
                    response = "Ask about name, status or joining date"

            messages.append({"type": "bot", "text": response})

        except Exception as e:
            messages.append({"type": "bot", "text": f"Error: {str(e)}"})

    return render_template_string(html, messages=messages)


if __name__ == "__main__":
    app.run(port=5000)
