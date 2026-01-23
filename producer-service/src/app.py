from fastapi import FastAPI
from uuid import uuid4
from kafka_producer import publish_order

app = FastAPI()

@app.post("/api/orders", status_code=202)
def create_order(order: dict):
    order_id = str(uuid4())
    event = {**order, "order_id": order_id}
    publish_order(event)
    return {"message": "Order received", "order_id": order_id}

@app.get("/health")
def health():
    return {"status": "ok"}
