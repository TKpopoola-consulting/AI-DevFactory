import pytest
import requests

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module")
def setup():
    # Setup code for the test module
    yield
    # Teardown code

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

def test_main_endpoint():
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert "message" in response.json()

# Add more domain-specific tests below