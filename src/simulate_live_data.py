"""Live data simulation for synthetic incoming credit applications."""

from __future__ import annotations

import os
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from src.config import LIVE_DATA_PATH, RAW_DATA_DIR

RNG_SEED = 2026


def generate_live_batch(batch_size: int = 250) -> pd.DataFrame:
    """Generate a realistic batch of live application records."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RNG_SEED)

    age = rng.integers(21, 70, size=batch_size)
    annual_income = rng.normal(loc=60000, scale=20000, size=batch_size).clip(12000, 220000)
    credit_utilization = rng.uniform(0.05, 0.99, size=batch_size)
    debt_to_income_ratio = rng.uniform(0.05, 0.82, size=batch_size)
    number_of_open_accounts = rng.integers(1, 20, size=batch_size)
    late_payment_count = rng.poisson(lam=1.6, size=batch_size).clip(0, 14)

    df = pd.DataFrame(
        {
            "event_time_utc": [datetime.now(UTC).isoformat()] * batch_size,
            "age": age,
            "annual_income": annual_income.round(2),
            "credit_utilization": credit_utilization.round(4),
            "debt_to_income_ratio": debt_to_income_ratio.round(4),
            "number_of_open_accounts": number_of_open_accounts,
            "late_payment_count": late_payment_count,
        }
    )
    return df


def run_live_data_simulation(batch_size: int = 250) -> None:
    """Append a generated live batch to the live applications CSV."""
    batch_df = generate_live_batch(batch_size=batch_size)
    file_exists = LIVE_DATA_PATH.exists()
    batch_df.to_csv(LIVE_DATA_PATH, mode="a", index=False, header=not file_exists)
    print(f"Appended {len(batch_df)} rows to {LIVE_DATA_PATH}.")


if __name__ == "__main__":
    batch_size = int(os.getenv("SIMULATE_BATCH_SIZE", "250"))
    run_live_data_simulation(batch_size=batch_size)
