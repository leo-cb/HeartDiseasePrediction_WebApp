import json
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_predict_valid_request(client):
    data = {
        "features": [i for i in range(9)],
        "features_names": ['cp', 'ca', 'thal', 'oldpeak', 'thalach', 'exang', 'age', 'slope', 'sex']
    }
    headers = {
        "Authorization": "VjKq9czKVqvH1NsMHO-qrd-fiEyYMzyDoWTkXlp85Is"
    }

    response = client.post('/predict', json=data, headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "prediction" in json_data
    assert "confidence" in json_data
    assert "shap_values" in json_data

def test_predict_invalid_request(client):
    data = {
        "features": [1, 2, 3],
        "features_names": ["feat1", "feat2"]  # Mismatched feature names
    }
    headers = {
        "Authorization": "VjKq9czKVqvH1NsMHO-qrd-fiEyYMzyDoWTkXlp85Is"
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
        "Authorization": "VjKq9czKVqvH1NsMHO-qrd-fiEyYMzyDoWTkXlp85Ia"  # Unauthorized key
    }

    response = client.post('/predict', json=data, headers=headers)
    assert response.status_code == 401
    json_data = response.get_json()
    assert "error" in json_data
    assert "Unauthorized" in json_data["error"]