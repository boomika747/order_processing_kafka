# Event‑Driven Order Processing with Kafka

This project demonstrates an event‑driven microservices architecture using Apache Kafka for asynchronous communication between services. Orders are produced as events, processed by a consumer, and status events are published back to Kafka.

---

## Tech Stack
- Python 3.10
- Apache Kafka
- Zookeeper
- PostgreSQL
- Docker & Docker Compose

---

## Architecture Overview

Client / API
  ↓
Order Producer
  ↓
Kafka (order_created topic)
  ↓
Order Consumer
  ↓
PostgreSQL (optional persistence)
  ↓
Kafka (order_processed / order_failed topics)

---

## Kafka Topics
- order_created – New order event
- order_processed – Order processed successfully
- order_failed – Order processing failed

---

## Run the Application

docker-compose up --build

This starts:
- Zookeeper
- Kafka Broker
- PostgreSQL
- Order Consumer Service

---

## Create an Order (Kafka Event)

docker exec order-processing-kafka-kafka-1 \
bash -c 'echo "{\"order_id\":\"77777777-7777-7777-7777-777777777777\",\"customer_id\":\"88888888-8888-8888-8888-888888888888\",\"items\":[{\"product_id\":\"phone\",\"quantity\":1}],\"total_amount\":25000}" | kafka-console-producer --bootstrap-server kafka:9092 --topic order_created'

---

## Consumer Behavior
- Consumes messages from order_created
- Processes the order
- Publishes order_processed on success
- Publishes order_failed on failure

Example log output:
Consumed order: 77777777-7777-7777-7777-777777777777

---

## Environment Variables

KAFKA_BROKER_URL=kafka:9092
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=orders
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

---

## Notes
- Kafka enables asynchronous, decoupled communication
- Consumers can be scaled independently
- Docker Compose simplifies local development
- JSON is used as the event message format
