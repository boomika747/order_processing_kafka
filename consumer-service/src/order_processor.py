from db import get_db_connection
import json
import logging

logger = logging.getLogger(__name__)

def process_order(order):
    if any(i["quantity"] <= 0 for i in order["items"]):
        raise ValueError("Invalid quantity")

    with get_db_connection() as conn:
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
            
    # Simulate inventory update
    for item in order["items"]:
        logger.info(f"Inventory updated: deducted {item['quantity']} units of product '{item['product_id']}' for order {order['order_id']}")
        
    return "processed"
