from flask import Flask, request, render_template_string
import requests
import re

app = Flask(__name__)

API_KEY = "2d0cdea1e39320d"
API_SECRET = "3c42c12801b0b59"
BASE_URL = "http://localhost:8080/api/resource"
AUTH = f"token {API_KEY}:{API_SECRET}"

html = """
<!DOCTYPE html>
<html>
<head>
    <title>ERPNext Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #ece5dd;
            margin: 0;
            padding: 0;
        }

        .chat-container {
            width: 420px;
            margin: 40px auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            height: 580px;
        }

        .header {
            background: #075e54;
            color: white;
            padding: 14px 18px;
            font-size: 17px;
            font-weight: bold;
        }

        .chat-area {
            flex: 1;
            padding: 14px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .message {
            max-width: 78%;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
        }

        .user {
            background: #dcf8c6;
            align-self: flex-end;
        }

        .bot {
            background: #f1f0f0;
            align-self: flex-start;
        }

        .input-box {
            display: flex;
            border-top: 1px solid #ddd;
            padding: 10px;
            gap: 8px;
        }

        input[type="text"] {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid #ccc;
            border-radius: 20px;
            font-size: 14px;
            outline: none;
        }

        input[type="text"]:focus {
            border-color: #128c7e;
        }

        button {
            padding: 10px 18px;
            background: #128c7e;
            color: white;
            border: none;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
        }

        button:hover {
            background: #0a6e63;
        }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="header">ERPNext Chatbot</div>

    <div class="chat-area">
        {% if query %}
            <div class="message user">{{ query }}</div>
        {% endif %}
        {% if response %}
            <div class="message bot">{{ response }}</div>
        {% endif %}
    </div>

    <form method="POST" class="input-box">
        <input type="text" name="query" placeholder="Type a message..." autocomplete="off" required>
        <button type="submit">Send</button>
    </form>
</div>

</body>
</html>
"""

def get_url_for_id(doc_id):
    if doc_id.startswith("SAL-ORD"):
        return f"{BASE_URL}/Sales Order/{doc_id}"
    elif doc_id.startswith("ACC-SINV"):
        return f"{BASE_URL}/Sales Invoice/{doc_id}"
    elif doc_id.startswith("HR-EMP"):
        return f"{BASE_URL}/Employee/{doc_id}"
    return None

def get_answer(doc_id, doc, query):
    q = query.lower()

    if doc_id.startswith("SAL-ORD"):
        if "status" in q:
            return "Status: " + str(doc.get("status", "Not found"))
        elif "amount" in q:
            return "Amount: ₹" + str(doc.get("grand_total", "Not found"))
        elif "customer" in q:
            return "Customer: " + str(doc.get("customer_name", "Not found"))
        elif "delivery" in q:
            return "Delivery Date: " + str(doc.get("delivery_date", "Not found"))
        else:
            # default — just show the status if user doesn't ask anything specific
            return "Status: " + str(doc.get("status", "Not found"))

    elif doc_id.startswith("ACC-SINV"):
        if "amount" in q:
            return "Invoice Amount: ₹" + str(doc.get("grand_total", "Not found"))
        else:
            return "Invoice Status: " + str(doc.get("status", "Not found"))

    elif doc_id.startswith("HR-EMP"):
        if "status" in q or "active" in q:
            return "Employee Status: " + str(doc.get("status", "Not found"))
        else:
            return "Employee Name: " + str(doc.get("employee_name", "Not found"))

    return "Couldn't understand what you're looking for."


@app.route("/", methods=["GET", "POST"])
def home():
    query = ""
    response = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if not query:
            return render_template_string(html, query=query, response="Please type something.")

        # extract the document ID from the user's message
        match = re.search(r"(SAL-ORD-\d{4}-\d{5}|ACC-SINV-\d{4}-\d{5}|HR-EMP-\d+)", query)

        if not match:
            return render_template_string(
                html, query=query,
                response="Couldn't find a valid ID. Try something like SAL-ORD-2026-00007"
            )

        doc_id = match.group()
        url = get_url_for_id(doc_id)

        if not url:
            return render_template_string(html, query=query, response="This ID type is not supported yet.")

        try:
            r = requests.get(url, headers={"Authorization": AUTH}, timeout=5)

            if r.status_code == 401:
                return render_template_string(html, query=query, response="Authentication failed. Check your API key.")
            elif r.status_code == 404:
                return render_template_string(html, query=query, response=f"No record found for {doc_id}.")
            elif r.status_code != 200:
                return render_template_string(html, query=query, response=f"API returned an error: {r.status_code}")

            data = r.json()

            if "data" not in data:
                return render_template_string(html, query=query, response="Got a response but no data inside it.")

            response = get_answer(doc_id, data["data"], query)

        except requests.exceptions.ConnectionError:
            response = "Can't connect to ERPNext. Make sure Docker is running."
        except requests.exceptions.Timeout:
            response = "ERPNext took too long to respond. Try again."
        except Exception as e:
            response = "Something went wrong: " + str(e)

    return render_template_string(html, query=query, response=response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
