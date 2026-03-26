"""FastAPI app for model serving and prediction logging."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import (
    FEATURE_COLUMNS_PATH,
    METRICS_PATH,
    MODEL_PATH,
    MODEL_VERSION,
    PREDICTION_LOG_PATH,
)

app = FastAPI(title="Credit Risk API", version="0.2.0")

_model = None
_feature_columns: list[str] | None = None


class PredictionRequest(BaseModel):
    age: int = Field(ge=18, le=100)
    annual_income: float = Field(gt=0, le=500000)
    credit_utilization: float = Field(ge=0, le=1)
    debt_to_income_ratio: float = Field(ge=0, le=1)
    number_of_open_accounts: int = Field(ge=0, le=100)
    late_payment_count: int = Field(ge=0, le=100)


class PredictionResponse(BaseModel):
    risk_score: float
    risk_label: str
    model_version: str


def _get_model_and_features() -> tuple[object, list[str]]:
    global _model, _feature_columns
    if _model is None:
        if not MODEL_PATH.exists():
            raise HTTPException(status_code=503, detail="Model not available. Run training first.")
        _model = joblib.load(MODEL_PATH)

    if _feature_columns is None:
        if not FEATURE_COLUMNS_PATH.exists():
            raise HTTPException(
                status_code=503, detail="Feature schema not available. Run training first."
            )
        _feature_columns = json.loads(FEATURE_COLUMNS_PATH.read_text(encoding="utf-8"))
    return _model, _feature_columns


def _score_to_label(score: float) -> str:
    if score < 0.33:
        return "low"
    if score < 0.66:
        return "medium"
    return "high"


def _append_prediction_log(payload: dict[str, int | float], score: float, label: str) -> None:
    PREDICTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "event_time_utc": datetime.now(UTC).isoformat(),
        **payload,
        "risk_score": round(float(score), 6),
        "risk_label": label,
        "model_version": MODEL_VERSION,
    }
    df = pd.DataFrame([row])
    exists = PREDICTION_LOG_PATH.exists()
    df.to_csv(PREDICTION_LOG_PATH, mode="a", index=False, header=not exists)


@app.get("/health")
def health() -> dict[str, str]:
    """Health endpoint for uptime checks."""
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    """Basic project endpoint."""
    return {"message": "Credit Risk MLOps API is running."}


@app.get("/model_info")
def model_info() -> dict[str, object]:
    """Return currently served model metadata and optional offline metrics."""
    if not MODEL_PATH.exists() or not FEATURE_COLUMNS_PATH.exists():
        raise HTTPException(status_code=503, detail="Model artifacts are not ready yet.")

    metrics: dict[str, float] | None = None
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    feature_columns = json.loads(FEATURE_COLUMNS_PATH.read_text(encoding="utf-8"))
    return {
        "model_version": MODEL_VERSION,
        "feature_count": len(feature_columns),
        "features": feature_columns,
        "offline_metrics": metrics,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    """Run credit risk prediction and persist feature logs for drift checks."""
    model, feature_columns = _get_model_and_features()
    feature_payload = payload.model_dump()
    frame = pd.DataFrame([feature_payload])[feature_columns]

    risk_score = float(model.predict_proba(frame)[0][1])
    risk_label = _score_to_label(risk_score)
    _append_prediction_log(feature_payload, risk_score, risk_label)

    return PredictionResponse(
        risk_score=round(risk_score, 6),
        risk_label=risk_label,
        model_version=MODEL_VERSION,
    )
