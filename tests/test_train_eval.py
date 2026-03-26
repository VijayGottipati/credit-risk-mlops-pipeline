import json

import pandas as pd
import pytest

from src.config import METRICS_PATH, MODEL_PATH, TRAINING_METADATA_PATH
from src.data_ingest import run_data_ingestion
from src.evaluate import run_evaluation
from src.preprocess import run_preprocessing
from src.simulate_live_data import run_live_data_simulation
from src.train import run_training


def test_phase3_training_and_evaluation_outputs_exist() -> None:
    run_data_ingestion()
    run_live_data_simulation(batch_size=40)
    run_preprocessing()
    run_training()
    run_evaluation()

    assert MODEL_PATH.exists()
    assert TRAINING_METADATA_PATH.exists()
    assert METRICS_PATH.exists()

    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    assert 0.0 <= metrics["roc_auc"] <= 1.0
    assert 0.0 <= metrics["pr_auc"] <= 1.0
    assert metrics["evaluation_rows"] > 0


def test_training_fails_with_single_class_target() -> None:
    run_data_ingestion()
    run_live_data_simulation(batch_size=20)
    run_preprocessing()

    train_df = pd.read_csv("data/processed/train_ready.csv")
    train_df["default_risk"] = 1
    train_df.to_csv("data/processed/train_ready.csv", index=False)

    with pytest.raises(ValueError, match="at least two target classes"):
        run_training()
