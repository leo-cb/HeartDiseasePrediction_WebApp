import json
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))
from main import app
from db import generate_insert_api_key

os.environ['ENVIRONMENT'] = 'testing'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_predict_valid_request(client):
    api_key = generate_insert_api_key(url="mongodb://localhost:27017")

    data = {
        "features": [i for i in range(9)],
        "features_names": ['cp', 'ca', 'thal', 'oldpeak', 'thalach', 'exang', 'age', 'slope', 'sex']
    }
    headers = {
        "Authorization": api_key
    }

    response = client.post('/predict', json=data, headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "prediction" in json_data
    assert "confidence" in json_data
    assert "shap_values" in json_data

def test_predict_invalid_request(client):
    api_key = generate_insert_api_key(url="mongodb://localhost:27017")

    data = {
        "features": [1, 2, 3],
        "features_names": ["feat1", "feat2"]  # Mismatched feature names
    }
    headers = {
        "Authorization": api_key
    }

    response = client.post('/predict', json=data, headers=headers)
    assert response.status_code == 400
    json_data = response.get_json()
    assert "message" in json_data
    assert "Invalid request" in json_data["message"]

def test_unauthorized_request(client):
    data = {
        "features": [1, 2, 3],
        "features_names": ["feat1", "feat2", "feat3"]
    }
    headers = {
        "Authorization": "invalid_api_key"  # Unauthorized key
    }

    response = client.post('/predict', json=data, headers=headers)
    assert response.status_code == 401
    json_data = response.get_json()
    assert "error" in json_data
    assert "Unauthorized" in json_data["error"]