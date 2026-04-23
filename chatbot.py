import frappe

while True:
    order_id = input("Enter Sales Order ID (or 'exit'): ")

    if order_id.lower() == "exit":
        break

    try:
        doc = frappe.get_doc("Sales Order", order_id)
        print("Status:", doc.status)
    except:
        print("Invalid ID")