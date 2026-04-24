ERPNext Chatbot
I built this as a small project to learn how APIs work. It's a chatbot that connects to ERPNext and lets you ask questions about Sales Orders, Invoices, and Employees just by typing.

What it does:
You type something like "what is the status of SAL-ORD-2026-00007" and it fetches that data from ERPNext and shows the answer. 

Supports:
*Sales Orders
*Sales Invoices
*Employees

Tech I used
*Python
*Flask
*ERPNext (running locally with Docker)
*REST API


How to run it
You need two terminals for this.

*Terminal 1 — start ERPNext
cd C:\Users\jebap\OneDrive\Desktop\OneDrive\Documents\frappe_docker\frappe_docker
docker compose -f pwd.yml up
Then go to http://localhost:8080

*Terminal 2 — run the chatbot
cd C:\Users\jebap\OneDrive\Desktop\OneDrive\Documents\frappe_docker\project
python app.py
Then open http://127.0.0.1:5000

Important: always start ERPNext first. If we run the chatbot before ERPNext is ready, we'll get a connection error.


Example queries you can try:

What is status of SAL-ORD-2026-00007
Show amount of SAL-ORD-2026-00007
Who is customer of SAL-ORD-2026-00007
What is delivery date of SAL-ORD-2026-00007

What is status of ACC-SINV-2026-00001
Show amount of ACC-SINV-2026-00001

Who is HR-EMP-00001
Is HR-EMP-00001 active

How it works:

You type a query
The app finds the ID in your message using regex
It figures out which ERPNext module to call (Sales Order, Invoice, Employee)
Sends a GET request to the ERPNext API
Shows the result in the chat


Problems I faced while building this:

*Got 401 error at first — I wasn't sending the API key correctly in the headers
*Connection refused error — was running chatbot before Docker finished loading ERPNext
*Regex wasn't matching the ID — had to fix the pattern after testing a few times
*Docker path issue — wrong folder, took me a while to figure out


what works now:

Fetch status, amount, customer, delivery date for Sales Orders
Fetch status and amount for Invoices
Fetch employee name and status
Error messages for wrong input or connection issues


Future enhancements:

Chat history
Support for more ERPNext modules
Better looking UI
Maybe AI integration to make it smarter.
