from fastapi import FastAPI, HTTPException
from uuid import uuid4
from src.kafka_producer import publish_order
from src.db import get_db_connection
import psycopg2


app = FastAPI()

@app.post("/api/orders", status_code=202)
def create_order(order: dict):
    order_id = str(uuid4())
    event = {**order, "order_id": order_id}
    publish_order(event)
    return {"message": "Order received", "order_id": order_id}

@app.get("/api/orders/{order_id}")
def get_order_status(order_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT order_id, customer_id, items, total_amount, status FROM orders WHERE order_id = %s", (order_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Order not found")
                
                return {
                    "order_id": row[0],
                    "customer_id": row[1],
                    "items": row[2],
                    "total_amount": row[3],
                    "status": row[4]
                }
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
