"""Preprocessing for historical and live credit datasets."""

from __future__ import annotations

import pandas as pd

from src.config import (
    HISTORICAL_DATA_PATH,
    LIVE_DATA_PATH,
    LIVE_READY_PATH,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    TRAIN_READY_PATH,
)

NUMERIC_FEATURES = [
    "age",
    "annual_income",
    "credit_utilization",
    "debt_to_income_ratio",
    "number_of_open_accounts",
    "late_payment_count",
]


def _coerce_numeric(df: pd.DataFrame, expected_columns: list[str]) -> pd.DataFrame:
    """Convert expected columns to numeric and drop invalid rows."""
    clean = df.copy()
    for col in expected_columns:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    clean = clean.dropna(subset=expected_columns)
    return clean


def _prep_historical() -> pd.DataFrame:
    if not HISTORICAL_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing historical dataset at {HISTORICAL_DATA_PATH}. Run src.data_ingest first."
        )
    historical_df = pd.read_csv(HISTORICAL_DATA_PATH)
    required = NUMERIC_FEATURES + ["default_risk"]
    missing = [c for c in required if c not in historical_df.columns]
    if missing:
        raise ValueError(f"Historical data is missing columns: {missing}")

    historical_df = _coerce_numeric(historical_df, required)
    historical_df["default_risk"] = historical_df["default_risk"].astype(int).clip(0, 1)
    return historical_df[required]


def _prep_live() -> pd.DataFrame:
    if not LIVE_DATA_PATH.exists():
        return pd.DataFrame(columns=["event_time_utc"] + NUMERIC_FEATURES)
    live_df = pd.read_csv(LIVE_DATA_PATH)
    required = NUMERIC_FEATURES
    missing = [c for c in required if c not in live_df.columns]
    if missing:
        raise ValueError(f"Live data is missing columns: {missing}")

    live_df = _coerce_numeric(live_df, required)
    if "event_time_utc" not in live_df.columns:
        live_df["event_time_utc"] = pd.NaT
    return live_df[["event_time_utc"] + required]


def run_preprocessing() -> None:
    """Preprocess both historical training data and simulated live data."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    historical = _prep_historical()
    live = _prep_live()

    historical.to_csv(TRAIN_READY_PATH, index=False)
    live.to_csv(LIVE_READY_PATH, index=False)
    print(f"Train-ready data written to {TRAIN_READY_PATH} (rows={len(historical)}).")
    print(f"Live-ready data written to {LIVE_READY_PATH} (rows={len(live)}).")


if __name__ == "__main__":
    run_preprocessing()
