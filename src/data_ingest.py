"""Historical dataset ingestion for Phase 2."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import HISTORICAL_DATA_PATH, RAW_DATA_DIR

RNG_SEED = 42
UCI_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "00350/default%20of%20credit%20card%20clients.xls"
)


def _generate_fallback_dataset(rows: int = 5000) -> pd.DataFrame:
    """Generate synthetic credit-risk data if remote download is unavailable."""
    rng = np.random.default_rng(RNG_SEED)

    age = rng.integers(21, 70, size=rows)
    annual_income = rng.normal(loc=55000, scale=18000, size=rows).clip(12000, 200000)
    credit_utilization = rng.uniform(0.05, 0.98, size=rows)
    debt_to_income_ratio = rng.uniform(0.05, 0.75, size=rows)
    number_of_open_accounts = rng.integers(1, 18, size=rows)
    late_payment_count = rng.poisson(lam=1.4, size=rows).clip(0, 12)

    risk_signal = (
        1.2 * credit_utilization
        + 1.1 * debt_to_income_ratio
        + 0.08 * late_payment_count
        - 0.000004 * annual_income
        - 0.002 * age
    )
    threshold = np.quantile(risk_signal, 0.62)
    target = (risk_signal > threshold).astype(int)

    return pd.DataFrame(
        {
            "age": age,
            "annual_income": annual_income.round(2),
            "credit_utilization": credit_utilization.round(4),
            "debt_to_income_ratio": debt_to_income_ratio.round(4),
            "number_of_open_accounts": number_of_open_accounts,
            "late_payment_count": late_payment_count,
            "default_risk": target,
        }
    )


def _try_download_uci_dataset() -> pd.DataFrame | None:
    """
    Attempt to ingest UCI credit default data and map it to project schema.
    Returns None if download fails in offline/network-restricted environments.
    """
    try:
        df_raw = pd.read_excel(UCI_URL, header=1)
    except Exception:
        return None

    rename_map = {
        "AGE": "age",
        "LIMIT_BAL": "annual_income",
        "PAY_AMT1": "credit_utilization",
        "BILL_AMT1": "debt_to_income_ratio",
        "PAY_0": "late_payment_count",
        "default payment next month": "default_risk",
    }
    missing_cols = [c for c in rename_map if c not in df_raw.columns]
    if missing_cols:
        return None

    df = df_raw.rename(columns=rename_map)
    df = df[list(rename_map.values())].copy()

    # Use available signals to derive a stable v1 feature set.
    if "ID" in df_raw.columns:
        df["number_of_open_accounts"] = (df_raw["ID"] % 15) + 1
    else:
        df["number_of_open_accounts"] = 5

    # Convert to approximate ranges used in this project schema.
    df["annual_income"] = (df["annual_income"] * 0.35).clip(12000, 250000)
    df["credit_utilization"] = (df["credit_utilization"].abs() / 200000).clip(0, 1)
    df["debt_to_income_ratio"] = (df["debt_to_income_ratio"].abs() / 300000).clip(0, 1)
    df["late_payment_count"] = df["late_payment_count"].clip(-3, 10).abs()

    return df


def run_data_ingestion(output_path: Path = HISTORICAL_DATA_PATH) -> Path:
    """Create historical dataset file from UCI source or fallback synthetic data."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    historical_df = _try_download_uci_dataset()
    source = "UCI download"
    if historical_df is None:
        historical_df = _generate_fallback_dataset(rows=5000)
        source = "synthetic fallback"

    historical_df.to_csv(output_path, index=False)
    print(f"Historical data ready at {output_path} ({source}, rows={len(historical_df)}).")
    return output_path


if __name__ == "__main__":
    run_data_ingestion()
