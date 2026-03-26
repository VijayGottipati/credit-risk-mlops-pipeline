import pandas as pd

from monitoring.drift_check import MIN_LIVE_ROWS, run_drift_check
from src.config import PREDICTION_LOG_PATH, TRAIN_READY_PATH
from src.data_ingest import run_data_ingestion
from src.preprocess import run_preprocessing


def _prepare_reference_data() -> pd.DataFrame:
    run_data_ingestion()
    run_preprocessing()
    return pd.read_csv(TRAIN_READY_PATH)


def test_drift_check_skips_when_logs_are_too_small() -> None:
    reference = _prepare_reference_data()
    small_live = reference.head(20).drop(columns=["default_risk"])
    small_live.to_csv(PREDICTION_LOG_PATH, index=False)

    status = run_drift_check()
    assert status["drift_detected"] is False
    assert "Need at least" in status["reason"]


def test_drift_check_detects_distribution_shift() -> None:
    reference = _prepare_reference_data()
    shifted_live = reference.sample(n=max(MIN_LIVE_ROWS + 30, 150), random_state=7).copy()
    shifted_live = shifted_live.drop(columns=["default_risk"])
    shifted_live["annual_income"] = shifted_live["annual_income"] * 0.15
    shifted_live["credit_utilization"] = 0.95
    shifted_live["debt_to_income_ratio"] = 0.88
    shifted_live.to_csv(PREDICTION_LOG_PATH, index=False)

    status = run_drift_check()
    assert status["drift_detected"] is True
    assert len(status["drifted_features"]) >= 1


def test_drift_check_handles_missing_columns_safely() -> None:
    _prepare_reference_data()
    bad_live = pd.DataFrame({"age": [30, 35, 40]})
    bad_live.to_csv(PREDICTION_LOG_PATH, index=False)

    status = run_drift_check()
    assert status["drift_detected"] is False
    assert "missing required columns" in status["reason"]
