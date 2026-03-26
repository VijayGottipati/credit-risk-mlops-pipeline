from pathlib import Path

import pandas as pd

from src.config import HISTORICAL_DATA_PATH, LIVE_DATA_PATH, LIVE_READY_PATH, TRAIN_READY_PATH
from src.data_ingest import run_data_ingestion
from src.preprocess import run_preprocessing
from src.simulate_live_data import run_live_data_simulation


def test_phase2_generates_raw_and_processed_data() -> None:
    run_data_ingestion()
    run_live_data_simulation(batch_size=25)
    run_preprocessing()

    assert HISTORICAL_DATA_PATH.exists()
    assert LIVE_DATA_PATH.exists()
    assert TRAIN_READY_PATH.exists()
    assert LIVE_READY_PATH.exists()

    train_df = pd.read_csv(TRAIN_READY_PATH)
    live_df = pd.read_csv(LIVE_READY_PATH)

    assert len(train_df) > 0
    assert len(live_df) > 0
    assert "default_risk" in train_df.columns
    assert "event_time_utc" in live_df.columns


def test_phase2_files_are_inside_workspace_data_dir() -> None:
    for path in [HISTORICAL_DATA_PATH, LIVE_DATA_PATH, TRAIN_READY_PATH, LIVE_READY_PATH]:
        assert isinstance(path, Path)
        assert "data" in str(path)
