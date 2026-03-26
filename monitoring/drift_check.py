"""Data drift detection against production prediction logs."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pandas as pd
from scipy.stats import ks_2samp

from src.config import PREDICTION_LOG_PATH, REPORTS_DIR, TRAIN_READY_PATH

DRIFT_STATUS_PATH = REPORTS_DIR / "drift_status.json"
DRIFT_PVALUE_THRESHOLD = 0.01
DRIFT_FEATURE_RATIO_THRESHOLD = 0.4
MIN_LIVE_ROWS = 100
NUMERIC_FEATURES = [
    "age",
    "annual_income",
    "credit_utilization",
    "debt_to_income_ratio",
    "number_of_open_accounts",
    "late_payment_count",
]


def _sanitize_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    clean = df.copy()
    for col in cols:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    return clean.dropna(subset=cols)


def _missing_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    return [col for col in required if col not in df.columns]


def _run_ks(reference: pd.Series, current: pd.Series) -> dict[str, float | bool]:
    stat, p_value = ks_2samp(reference, current)
    return {
        "ks_statistic": float(stat),
        "p_value": float(p_value),
        "drifted": bool(p_value < DRIFT_PVALUE_THRESHOLD),
    }


def _build_no_data_status(reason: str) -> dict[str, Any]:
    return {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "drift_detected": False,
        "reason": reason,
        "thresholds": {
            "ks_pvalue_threshold": DRIFT_PVALUE_THRESHOLD,
            "drift_feature_ratio_threshold": DRIFT_FEATURE_RATIO_THRESHOLD,
            "min_live_rows": MIN_LIVE_ROWS,
        },
        "row_counts": {"reference_rows": 0, "live_rows": 0},
        "feature_results": {},
        "drifted_features": [],
    }


def run_drift_check() -> dict[str, Any]:
    """Compare training vs production logs and write drift status report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if not TRAIN_READY_PATH.exists():
        status = _build_no_data_status(
            f"Missing reference dataset: {TRAIN_READY_PATH}. Run preprocess first."
        )
        DRIFT_STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")
        print(f"Drift check skipped. {status['reason']}")
        return status

    if not PREDICTION_LOG_PATH.exists():
        status = _build_no_data_status(
            f"No prediction logs found at {PREDICTION_LOG_PATH}. Skipping drift check."
        )
        DRIFT_STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")
        print(f"Drift check skipped. {status['reason']}")
        return status

    reference_raw = pd.read_csv(TRAIN_READY_PATH)
    live_raw = pd.read_csv(PREDICTION_LOG_PATH)

    missing_reference = _missing_columns(reference_raw, NUMERIC_FEATURES)
    if missing_reference:
        status = _build_no_data_status(
            f"Reference data is missing required columns: {missing_reference}."
        )
        DRIFT_STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")
        print(f"Drift check skipped. {status['reason']}")
        return status

    missing_live = _missing_columns(live_raw, NUMERIC_FEATURES)
    if missing_live:
        status = _build_no_data_status(
            f"Prediction logs are missing required columns: {missing_live}."
        )
        DRIFT_STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")
        print(f"Drift check skipped. {status['reason']}")
        return status

    reference_df = _sanitize_numeric(reference_raw, NUMERIC_FEATURES)
    live_df = _sanitize_numeric(live_raw, NUMERIC_FEATURES).tail(1000)

    if len(reference_df) == 0:
        status = _build_no_data_status(
            "Reference data has zero valid numeric rows after sanitization."
        )
        DRIFT_STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")
        print(f"Drift check skipped. {status['reason']}")
        return status

    if len(live_df) < MIN_LIVE_ROWS:
        status = _build_no_data_status(
            f"Need at least {MIN_LIVE_ROWS} prediction rows for stable drift detection; "
            f"found {len(live_df)}."
        )
        status["row_counts"] = {
            "reference_rows": int(len(reference_df)),
            "live_rows": int(len(live_df)),
        }
        DRIFT_STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")
        print(f"Drift check skipped. {status['reason']}")
        return status

    feature_results: dict[str, dict[str, float | bool]] = {}
    drifted_features: list[str] = []
    for feature in NUMERIC_FEATURES:
        result = _run_ks(reference_df[feature], live_df[feature])
        feature_results[feature] = result
        if result["drifted"]:
            drifted_features.append(feature)

    drift_ratio = len(drifted_features) / len(NUMERIC_FEATURES)
    drift_detected = drift_ratio >= DRIFT_FEATURE_RATIO_THRESHOLD
    reason = (
        f"Drift detected: {len(drifted_features)}/{len(NUMERIC_FEATURES)} features drifted."
        if drift_detected
        else (
            f"No significant drift: {len(drifted_features)}/"
            f"{len(NUMERIC_FEATURES)} features drifted."
        )
    )

    status = {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "drift_detected": drift_detected,
        "reason": reason,
        "thresholds": {
            "ks_pvalue_threshold": DRIFT_PVALUE_THRESHOLD,
            "drift_feature_ratio_threshold": DRIFT_FEATURE_RATIO_THRESHOLD,
            "min_live_rows": MIN_LIVE_ROWS,
        },
        "row_counts": {
            "reference_rows": int(len(reference_df)),
            "live_rows": int(len(live_df)),
        },
        "feature_results": feature_results,
        "drifted_features": drifted_features,
    }
    DRIFT_STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(f"Drift check complete. Wrote {DRIFT_STATUS_PATH}.")
    print(reason)
    return status


if __name__ == "__main__":
    run_drift_check()
