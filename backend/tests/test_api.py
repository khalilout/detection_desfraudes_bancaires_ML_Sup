"""
Tests d'intégration : appellent l'API comme le ferait le frontend Streamlit,
via TestClient (pas besoin de lancer un vrai serveur).
"""
import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root_returns_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_model_info_returns_expected_fields():
    response = client.get("/model-info")
    assert response.status_code == 200
    body = response.json()
    assert body["model_type"]
    assert 0.0 <= body["decision_threshold"] <= 1.0
    assert body["n_features"] == 30


def test_predict_single_valid_transaction(sample_transaction_dict):
    response = client.post("/predict", json=sample_transaction_dict)
    assert response.status_code == 200
    body = response.json()
    assert "is_fraud" in body
    assert "fraud_probability" in body
    assert 0.0 <= body["fraud_probability"] <= 1.0


def test_predict_single_missing_field_returns_422(sample_transaction_dict):
    incomplete = sample_transaction_dict.copy()
    del incomplete["V1"]
    response = client.post("/predict", json=incomplete)
    assert response.status_code == 422


def test_predict_single_negative_amount_returns_422(sample_transaction_dict):
    invalid = sample_transaction_dict.copy()
    invalid["Amount"] = -50.0
    response = client.post("/predict", json=invalid)
    assert response.status_code == 422


def test_predict_batch_valid_csv(sample_batch_df):
    csv_bytes = sample_batch_df.to_csv(index=False).encode("utf-8")
    response = client.post("/predict-batch", files={"file": ("transactions.csv", csv_bytes, "text/csv")})
    assert response.status_code == 200
    body = response.json()
    assert body["n_transactions"] == len(sample_batch_df)
    assert len(body["predictions"]) == len(sample_batch_df)
    assert body["n_predicted_fraud"] == sum(p["is_fraud"] for p in body["predictions"])


def test_predict_batch_missing_columns_returns_400(sample_batch_df):
    incomplete_df = sample_batch_df.drop(columns=["V1", "V2"])
    csv_bytes = incomplete_df.to_csv(index=False).encode("utf-8")
    response = client.post("/predict-batch", files={"file": ("transactions.csv", csv_bytes, "text/csv")})
    assert response.status_code == 400
    assert "V1" in response.json()["detail"]


def test_predict_batch_rejects_non_csv_file():
    response = client.post("/predict-batch", files={"file": ("transactions.txt", b"pas un csv", "text/plain")})
    assert response.status_code == 400


def test_predict_batch_rejects_malformed_csv():
    response = client.post(
        "/predict-batch",
        files={"file": ("transactions.csv", b"ceci,n,est,pas\nun,csv,valide", "text/csv")},
    )
    assert response.status_code == 400