import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Mock env vars before imports
os.environ["KAFKA_BROKER_URL"] = "localhost:9092"
os.environ["DATABASE_URL"] = "postgres://user:pass@db:5432/order_db"

# Mock KafkaProducer so it doesn't try to connect on import
patch('kafka.KafkaProducer').start()

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from app import app
import psycopg2

client = TestClient(app)

@patch("app.publish_order")
def test_create_order(mock_publish_order):
    order_data = {
        "customer_id": "88888888-8888-8888-8888-888888888888",
        "items": [{"product_id": "phone", "quantity": 1}],
        "total_amount": 25000
    }
    response = client.post("/api/orders", json=order_data)
    assert response.status_code == 202
    data = response.json()
    assert "order_id" in data
    assert data["message"] == "Order received"
    mock_publish_order.assert_called_once()
    called_event = mock_publish_order.call_args[0][0]
    assert called_event["order_id"] == data["order_id"]
    assert called_event["customer_id"] == order_data["customer_id"]

@patch("app.get_db_connection")
def test_get_order_status_found(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_get_db.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    mock_cursor.fetchone.return_value = (
        "77777777-7777-7777-7777-777777777777",
        "88888888-8888-8888-8888-888888888888",
        [{"product_id": "phone", "quantity": 1}],
        25000,
        "processed"
    )
    
    response = client.get("/api/orders/77777777-7777-7777-7777-777777777777")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "77777777-7777-7777-7777-777777777777"
    assert data["status"] == "processed"
    mock_cursor.execute.assert_called_once()

@patch("app.get_db_connection")
def test_get_order_status_not_found(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_get_db.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    mock_cursor.fetchone.return_value = None
    
    response = client.get("/api/orders/77777777-7777-7777-7777-777777777777")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
