# ERPNext AI Chatbot

A simple chatbot that lets you ask questions about your ERPNext data in plain English. It uses Groq (a fast AI API) under the hood to understand your questions and give you answers.

## What it does

You type something like *"What is the status of SAL-ORD-2024-00012?"* and it will go fetch that order from your ERPNext system and tell you the answer. If you just ask a general question with no order/invoice/employee ID, it answers like a normal AI chatbot.

It currently supports:
- Sales Orders (e.g. SAL-ORD-2024-00012)
- Employees (e.g. HR-EMP-00042)
- Sales Invoices (e.g. ACC-SINV-2024-00008)

## Requirements

Make sure you have Python installed, then install the dependencies:

pip install flask requests groq python-dotenv

## Setup

**1. Clone or download this project**

**2. Create a `.env` file** in the same folder as `app.py` and add your API keys:

GROQ_API_KEY=your_groq_api_key_here
ERP_API_KEY=your_erpnext_api_key_here
ERP_API_SECRET=your_erpnext_api_secret_here
ERP_BASE_URL=http://localhost:8080

**3. Run the app**

python app.py

**4. Open your browser and go to:**

http://localhost:5000

## How to get your API keys

**Groq** — Sign up at [console.groq.com](https://console.groq.com), go to API Keys, and create one.

**ERPNext** — Log in to your ERPNext, go to your profile → My Settings → API Access, and generate a key and secret there.


## Project structure

project/
│
├── app.py         
├── .env           
├── .gitignore      
└── README.md       

That way your keys stay safe on your machine.

## Notes

- This was built and tested with ERPNext running locally. If your ERPNext is hosted somewhere else, just update `ERP_BASE_URL` in the `.env` file.
- Chat history resets every time you restart the server. It's stored in memory, not a database.
- The AI model being used is `llama-3.1-8b-instant` via Groq, which is free to use with generous limits.
