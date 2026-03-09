import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Mock env vars before imports
os.environ["KAFKA_BROKER_URL"] = "localhost:9092"
os.environ["DATABASE_URL"] = "postgres://user:pass@db:5432/order_db"

# Mock Kafka components so they don't try to connect on import
patch('kafka.KafkaProducer').start()
patch('kafka.KafkaConsumer').start()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from order_processor import process_order

@patch("order_processor.get_db_connection")
def test_process_order_success(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_get_db.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    # Not a duplicate
    mock_cursor.fetchone.return_value = None
    
    order_data = {
        "order_id": "77777777-7777-7777-7777-777777777777",
        "customer_id": "88888888-8888-8888-8888-888888888888",
        "items": [{"product_id": "phone", "quantity": 1}],
        "total_amount": 25000
    }
    
    result = process_order(order_data)
    assert result == "processed"
    
    # Check that insert was called
    assert mock_cursor.execute.call_count == 2
    
@patch("order_processor.get_db_connection")
def test_process_order_duplicate(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_get_db.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    # Is a duplicate
    mock_cursor.fetchone.return_value = ("processed",)
    
    order_data = {
        "order_id": "77777777-7777-7777-7777-777777777777",
        "customer_id": "88888888-8888-8888-8888-888888888888",
        "items": [{"product_id": "phone", "quantity": 1}],
        "total_amount": 25000
    }
    
    result = process_order(order_data)
    assert result == "duplicate"
    
    # Check that insert was NOT called
    assert mock_cursor.execute.call_count == 1

def test_process_order_invalid_quantity():
    order_data = {
        "order_id": "77777777-7777-7777-7777-777777777777",
        "customer_id": "88888888-8888-8888-8888-888888888888",
        "items": [{"product_id": "phone", "quantity": 0}],
        "total_amount": 25000
    }
    
    with pytest.raises(ValueError, match="Invalid quantity"):
        process_order(order_data)

def test_process_order_empty_items():
    order_data = {
        "order_id": "77777777-7777-7777-7777-777777777777",
        "customer_id": "88888888-8888-8888-8888-888888888888",
        "items": [],
        "total_amount": 25000
    }
    
    with pytest.raises(ValueError, match="Order must contain at least one item"):
        process_order(order_data)
