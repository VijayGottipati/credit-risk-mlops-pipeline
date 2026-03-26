"""Model training for Phase 3."""

from __future__ import annotations

import json
import os

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from src.config import (
    ARTIFACTS_DIR,
    FEATURE_COLUMNS_PATH,
    HOLDOUT_TEST_PATH,
    MODEL_PATH,
    TRAIN_READY_PATH,
    TRAINING_METADATA_PATH,
)

TARGET_COLUMN = "default_risk"
RANDOM_STATE = 42


def _log_to_wandb(params: dict[str, int | float], metadata: dict[str, int | float]) -> None:
    """Log params and metadata to W&B if API key is configured."""
    if not os.getenv("WANDB_API_KEY"):
        return
    try:
        import wandb

        run = wandb.init(project="credit-risk-mlops", job_type="train", config=params)
        run.log(metadata)
        run.finish()
    except Exception as exc:
        print(f"W&B logging skipped due to error: {exc}")


def run_training() -> None:
    """Train an XGBoost classifier and persist model + training artifacts."""
    if not TRAIN_READY_PATH.exists():
        raise FileNotFoundError(
            f"Missing preprocessed training data at {TRAIN_READY_PATH}. Run src.preprocess first."
        )

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TRAIN_READY_PATH)
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Training dataset must contain target column '{TARGET_COLUMN}'.")

    feature_columns = [c for c in df.columns if c != TARGET_COLUMN]
    X = df[feature_columns]
    y = df[TARGET_COLUMN]
    class_counts = y.value_counts()
    if class_counts.shape[0] < 2:
        raise ValueError("Training data must contain at least two target classes.")
    if int(class_counts.min()) < 2:
        raise ValueError(
            "Each target class must have at least 2 rows for stratified train/test split."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    params: dict[str, int | float] = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.9,
        "colsample_bytree": 0.9,
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "random_state": RANDOM_STATE,
    }
    model = XGBClassifier(**params)
    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)
    FEATURE_COLUMNS_PATH.write_text(json.dumps(feature_columns, indent=2), encoding="utf-8")

    holdout_df = X_test.copy()
    holdout_df[TARGET_COLUMN] = y_test.values
    holdout_df.to_csv(HOLDOUT_TEST_PATH, index=False)

    metadata: dict[str, int | float] = {
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "feature_count": int(len(feature_columns)),
        "target_positive_rate": float(y.mean()),
    }
    TRAINING_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    _log_to_wandb(params=params, metadata=metadata)
    print(f"Model artifact saved to {MODEL_PATH}.")
    print(f"Holdout test split saved to {HOLDOUT_TEST_PATH}.")


if __name__ == "__main__":
    run_training()
