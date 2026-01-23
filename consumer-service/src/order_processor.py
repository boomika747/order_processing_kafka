from db import conn
import json

def process_order(order):
    if any(i["quantity"] <= 0 for i in order["items"]):
        raise ValueError("Invalid quantity")

    with conn.cursor() as cur:
        cur.execute("SELECT status FROM orders WHERE order_id=%s", (order["order_id"],))
        if cur.fetchone():
            return "duplicate"

        cur.execute("""
            INSERT INTO orders(order_id, customer_id, items, total_amount, status)
            VALUES (%s,%s,%s,%s,'processed')
        """, (
            order["order_id"],
            order["customer_id"],
            json.dumps(order["items"]),
            order["total_amount"]
        ))
