from kafka import KafkaConsumer, KafkaProducer
import json, os
from order_processor import process_order

def safe_json_deserializer(m):
    try:
        return json.loads(m.decode("utf-8"))
    except Exception:
        return None   # skip bad messages safely

consumer = KafkaConsumer(
    "order_created",
    bootstrap_servers=os.getenv("KAFKA_BROKER_URL"),
    group_id="order-consumer-group-v2",   # NEW group (important)
    value_deserializer=safe_json_deserializer,
    auto_offset_reset="latest"
)

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BROKER_URL"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

for msg in consumer:
    if msg.value is None:
        continue   # ignore malformed messages

    order = msg.value
    print("Consumed order:", order["order_id"], flush=True)

    try:
        result = process_order(order)

        if result != "duplicate":
            producer.send(
                "order_processed",
                {
                    "order_id": order["order_id"],
                    "customer_id": order["customer_id"],
                    "status": "processed",
                },
            )

    except Exception as e:
        producer.send(
            "order_failed",
            {
                "order_id": order.get("order_id"),
                "customer_id": order.get("customer_id"),
                "error_message": str(e),
                "status": "failed",
            },
        )
