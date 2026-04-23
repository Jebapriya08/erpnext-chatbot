# ERPNext Chatbot

A chatbot I made using Flask. It connects to ERPNext and gives you Sales Order details when you ask.


## What I used

- Python
- Flask
- ERPNext (runs on Docker)
- REST API

## How to run

**First — start ERPNext**

cd C:\Users\jebap\OneDrive\Desktop\OneDrive\Documents\frappe_docker\frappe_docker
docker compose -f pwd.yml up
Open `http://localhost:8080` and wait for ERPNext to load.

**Then — start the chatbot**

Open a new terminal window:
cd C:\Users\jebap\OneDrive\Desktop\OneDrive\Documents\frappe_docker\project
python app.py
Open `http://127.0.0.1:5000` in your browser.

> Note: Start ERPNext first. If ERPNext is not running, the chatbot will give a connection error.

## How to use it

Type something like this in the chatbot:

What is status of SAL-ORD-2026-00007
Show amount of SAL-ORD-2026-00007
Who is customer of SAL-ORD-2026-00007
What is delivery date of SAL-ORD-2026-00007
It will pull the data from ERPNext and show the answer.

## API

GET http://localhost:8080/api/resource/Sales Order/{order_id}
Login is done using API Key and API Secret from ERPNext.

## Problems I faced

- Got `401 Unauthorized` — fixed by adding API key properly in the request header
- Chatbot gave connection error — I was running the chatbot before ERPNext was ready
- Order ID was not getting detected — fixed by writing a proper regex pattern
- Docker path was wrong at first — had to navigate to the correct folder

## What it can do

- Get Sales Order status
- Get amount, customer name, delivery date
- Shows error message for wrong input

## What I want to add later

- Keep chat history so old messages don't disappear
- Add support for other ERPNext modules like Employee or Invoice
- Make the UI look better
