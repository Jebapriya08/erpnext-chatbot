from flask import Flask, request, render_template_string
import requests
import re

app = Flask(__name__)

API_KEY = "2d0cdea1e39320d"
API_SECRET = "3c42c12801b0b59"

html = """
<!DOCTYPE html>
<html>
<head>
    <title>ERPNext Chatbot</title>
    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #ece5dd;
        }

        .container {
            width: 400px;
            margin: 30px auto;
            background: white;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            height: 600px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        }

        .header {
            background: #075e54;
            color: white;
            padding: 15px 20px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px 10px 0 0;
        }

        .chat-area {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .msg {
            max-width: 75%;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.4;
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

        .input-area {
            display: flex;
            padding: 10px;
            border-top: 1px solid #ddd;
            gap: 8px;
        }

        input[type="text"] {
            flex: 1;
            padding: 10px;
            border-radius: 20px;
            border: 1px solid #ccc;
            outline: none;
            font-size: 14px;
        }

        input[type="text"]:focus {
            border-color: #128c7e;
        }

        button {
            padding: 10px 18px;
            border: none;
            background: #128c7e;
            color: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
        }

        button:hover {
            background: #0a7a6e;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">ERPNext Chatbot</div>

    <div class="chat-area">
        {% if query %}
            <div class="msg user">{{ query }}</div>
        {% endif %}
        {% if response %}
            <div class="msg bot">{{ response }}</div>
        {% endif %}
    </div>

    <form method="POST" class="input-area">
        <input type="text" name="query" placeholder="Type a message..." autocomplete="off" required>
        <button type="submit">Send</button>
    </form>
</div>

</body>
</html>
"""


def fetch_order(order_id):
    url = f"http://localhost:8080/api/resource/Sales Order/{order_id}"
    headers = {"Authorization": f"token {API_KEY}:{API_SECRET}"}
    r = requests.get(url, headers=headers, timeout=5)
    return r


def build_response(query, order):
    q = query.lower()

    if "status" in q:
        return "Status: " + order.get("status", "Not available")
    elif "amount" in q:
        return "Amount: ₹" + str(order.get("grand_total", "Not available"))
    elif "customer" in q:
        return "Customer: " + order.get("customer_name", "Not available")
    elif "delivery" in q:
        return "Delivery Date: " + str(order.get("delivery_date", "Not available"))
    else:
        return "You can ask about the status, amount, customer, or delivery date."


@app.route("/", methods=["GET", "POST"])
def home():
    query = ""
    response = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if not query:
            return render_template_string(html, query=query, response="Please type something.")

        match = re.search(r"SAL-ORD-\d{4}-\d{5}", query)
        if not match:
            return render_template_string(html, query=query, response="Couldn't find a valid Order ID. Format should be like SAL-ORD-2024-00001.")

        order_id = match.group()

        try:
            r = fetch_order(order_id)

            if r.status_code != 200:
                return render_template_string(html, query=query, response=f"Couldn't fetch the order (HTTP {r.status_code}).")

            data = r.json()

            if "data" not in data:
                return render_template_string(html, query=query, response="Order not found.")

            response = build_response(query, data["data"])

        except requests.exceptions.ConnectionError:
            response = "Couldn't connect to ERPNext. Is the server running?"
        except requests.exceptions.Timeout:
            response = "Request timed out. Try again in a moment."
        except Exception as e:
            response = f"Something went wrong: {e}"

    return render_template_string(html, query=query, response=response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
