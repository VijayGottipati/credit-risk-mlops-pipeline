from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from api.main import app
from src.config import PREDICTION_LOG_PATH
from src.data_ingest import run_data_ingestion
from src.preprocess import run_preprocessing
from src.simulate_live_data import run_live_data_simulation
from src.train import run_training


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint_returns_score_and_logs() -> None:
    run_data_ingestion()
    run_live_data_simulation(batch_size=20)
    run_preprocessing()
    run_training()

    if PREDICTION_LOG_PATH.exists():
        Path(PREDICTION_LOG_PATH).unlink()

    client = TestClient(app)
    payload = {
        "age": 35,
        "annual_income": 82000,
        "credit_utilization": 0.41,
        "debt_to_income_ratio": 0.29,
        "number_of_open_accounts": 6,
        "late_payment_count": 1,
    }
    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["risk_score"] <= 1
    assert body["risk_label"] in {"low", "medium", "high"}
    assert body["model_version"] == "credit_xgb_v1"

    assert PREDICTION_LOG_PATH.exists()
    log_df = pd.read_csv(PREDICTION_LOG_PATH)
    assert len(log_df) == 1
    assert "risk_score" in log_df.columns


def test_model_info_endpoint_returns_metadata() -> None:
    run_data_ingestion()
    run_live_data_simulation(batch_size=20)
    run_preprocessing()
    run_training()

    client = TestClient(app)
    response = client.get("/model_info")
    assert response.status_code == 200
    body = response.json()
    assert body["model_version"] == "credit_xgb_v1"
    assert body["feature_count"] >= 1
    assert isinstance(body["features"], list)
