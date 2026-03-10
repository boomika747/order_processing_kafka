from kafka import KafkaConsumer, KafkaProducer
import json, os
from src.order_processor import process_order

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

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_consumer():
    logger.info("Starting order consumer...")
    for msg in consumer:
        if msg.value is None:
            continue   # ignore malformed messages

        order = msg.value
        logger.info(f"Consumed order: {order.get('order_id')}")

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
                logger.info(f"Published order_processed for order: {order.get('order_id')}")
            else:
                logger.warning(f"Duplicate order ignored: {order.get('order_id')}")

        except Exception as e:
            logger.error(f"Error processing order {order.get('order_id')}: {e}")
            producer.send(
                "order_failed",
                {
                    "order_id": order.get("order_id"),
                    "customer_id": order.get("customer_id"),
                    "error_message": "Validation or processing failed",
                    "status": "failed",
                },
            )

