from kafka import KafkaProducer
import json, os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BROKER_URL"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def on_send_success(record_metadata):
    logger.info(f"Successfully produced message to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")

def on_send_error(excp):
    logger.error(f"Failed to produce message: {excp}")

def publish_order(event):
    try:
        future = producer.send("order_created", event)
        future.add_callback(on_send_success).add_errback(on_send_error)
        logger.info(f"Order created event sent to topic async for order_id: {event.get('order_id')}")
    except Exception as e:
        logger.error(f"Failed to publish order: {e}")
