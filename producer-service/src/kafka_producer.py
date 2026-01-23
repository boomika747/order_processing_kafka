from kafka import KafkaProducer
import json, os

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BROKER_URL"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def publish_order(event):
    producer.send("order_created", event)
    producer.flush()
