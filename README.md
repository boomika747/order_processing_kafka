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

## Create an Order (via API)

You can create an order by hitting the producer's REST API:

```bash
curl -X POST http://localhost:8080/api/orders \
-H "Content-Type: application/json" \
-d '{"customer_id": "88888888-8888-8888-8888-888888888888", "items": [{"product_id": "phone", "quantity": 1}], "total_amount": 25000}'
```

## Get Order Status (via API)

```bash
curl http://localhost:8080/api/orders/{order_id}
```

## Run Tests locally

To test the producer and consumer, navigate into their directories and run `pytest`:

```bash
# In producer-service
python -m pytest tests/

# In consumer-service
python -m pytest tests/
```

### End-to-End Integration Test

You can also run an E2E test from the root directory that validates Kafka event publishing and consumption over the API bounds. Ensure `docker-compose up -d` is running first:

```bash
pip install requests pytest
pytest tests/test_e2e.py
```

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
