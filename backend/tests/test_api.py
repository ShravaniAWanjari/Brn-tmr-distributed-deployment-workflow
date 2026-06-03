import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "brain_tumor_classification"}

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "request_count" in response.text
    
def test_predict_invalid_file_type():
    # Attempt to upload a non-image file
    files = {'file': ('test.txt', b'fake data', 'text/plain')}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    assert "not an image" in response.json()["detail"]
