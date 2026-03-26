"""Run a recruiter-friendly end-to-end project demo."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from monitoring.drift_check import MIN_LIVE_ROWS, run_drift_check
from src.data_ingest import run_data_ingestion
from src.evaluate import run_evaluation
from src.preprocess import run_preprocessing
from src.simulate_live_data import run_live_data_simulation
from src.train import run_training


def main() -> None:
    print("Step 1/7: Ingest historical data")
    run_data_ingestion()

    print("Step 2/7: Simulate live data")
    run_live_data_simulation(batch_size=300)

    print("Step 3/7: Preprocess datasets")
    run_preprocessing()

    print("Step 4/7: Train model")
    run_training()

    print("Step 5/7: Evaluate model")
    run_evaluation()

    print("Step 6/7: Call prediction API")
    client = TestClient(app)
    sample_payload = {
        "age": 29,
        "annual_income": 74000,
        "credit_utilization": 0.35,
        "debt_to_income_ratio": 0.27,
        "number_of_open_accounts": 5,
        "late_payment_count": 1,
    }
    last_response: dict[str, str | float] | None = None
    for i in range(MIN_LIVE_ROWS + 20):
        payload = sample_payload.copy()
        payload["age"] = 21 + (i % 45)
        payload["annual_income"] = 42000 + (i * 170)
        payload["credit_utilization"] = round(0.15 + ((i % 20) * 0.03), 4)
        payload["debt_to_income_ratio"] = round(0.12 + ((i % 15) * 0.02), 4)
        payload["number_of_open_accounts"] = 2 + (i % 9)
        payload["late_payment_count"] = i % 4
        response = client.post("/predict", json=payload)
        response.raise_for_status()
        last_response = response.json()
    print(f"Prediction response sample: {last_response}")

    print("Step 7/7: Run drift monitor")
    drift_status = run_drift_check()
    print(f"Drift status: detected={drift_status['drift_detected']}")

    metrics_path = Path("reports/metrics.json")
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        print(f"Offline metrics: {metrics}")

    print("Demo complete.")


if __name__ == "__main__":
    main()
