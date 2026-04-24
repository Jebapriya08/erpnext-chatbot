# ERPNext ChatBot
 
A simple chatbot I built using Flask that talks to ERPNext through its REST API. Instead of opening ERPNext and clicking through menus, you just type a question and get the answer directly in the chat.
 
## What I used
 
- Python + Flask for the backend
- ERPNext running locally through Docker
- ERPNext REST API to fetch order data
- Simple HTML and CSS for the chat interface
 
## How it works
 
You type something like "what is the status of SAL-ORD-2026-00007" and the chatbot picks out the Order ID from your message using regex, calls the ERPNext API, and returns the answer. That's basically it.
 
User types → Flask finds Order ID → Calls ERPNext API → Shows the answer
 
API used:

GET http://localhost:8080/api/resource/Sales Order/{order_id}
 
Authentication is handled using an API Key and API Secret from ERPNext settings.
 
## What you can ask
 
What is status of SAL-ORD-2026-00007
Show amount of SAL-ORD-2026-00007
Who is customer of SAL-ORD-2026-00007
What is delivery date of SAL-ORD-2026-00007

## How to run it
 
**Step 1 — Start ERPNext**
 
```bash
cd frappe_docker
docker compose -f pwd.yml up -d
```
 
Wait around 5 to 10 minutes for everything to load, then open `http://localhost:8080` to confirm it's running.
 
**Step 2 — Run the chatbot**
 
```bash
cd project
python app.py
```
 
Open `http://127.0.0.1:5000` in your browser.
 
> Start ERPNext first. If you run the chatbot before ERPNext is ready it will throw a connection error.
 
## Problems I ran into
 
- Got a **401 Unauthorized** error at first — I wasn't passing the API key correctly in the request headers
- Kept getting **connection refused** because I was starting the chatbot before ERPNext finished loading
- Had a **Docker path issue** — had to make sure I was in the right folder before running the compose command
- The **regex wasn't matching** at first because the order ID format wasn't what I expected — fixed it by testing patterns manually
 
## What it can do right now
 
- Check Sales Order status
- Get order amount
- Find customer name
- Get delivery date
- Shows a proper error message for invalid input
 
## What I want to add later
 
- Chat history so old messages don't disappear when you send a new one
- Support for other modules like Employee and Purchase Invoice
- Better UI overall
