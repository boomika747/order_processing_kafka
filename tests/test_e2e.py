import pytest
import requests
import time
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8080")

def test_end_to_end_order_processing():
    """
    Integration test that acts as an E2E check.
    It hits the Producer API to queue an order, and then checks the 
    Status API to verify the Consumer pulled the message and saved it 
    as 'processed' in the database.
    
    Ensure docker-compose up -d is running before executing this.
    """
    # 1. Produce an order
    order_data = {
        "customer_id": "88888888-8888-8888-8888-888888888888",
        "items": [{"product_id": "laptop", "quantity": 2}],
        "total_amount": 50000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip("Producer API not reachable. Is docker-compose running?")
        return

    assert response.status_code == 202
    data = response.json()
    order_id = data.get("order_id")
    assert order_id is not None
    
    # 2. Poll the API to check if consumer processed it
    max_retries = 10
    processed = False
    
    for _ in range(max_retries):
        time.sleep(2)
        status_response = requests.get(f"{BASE_URL}/api/orders/{order_id}", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "processed":
                processed = True
                break
                
    assert processed, f"Order {order_id} was not processed in time."
