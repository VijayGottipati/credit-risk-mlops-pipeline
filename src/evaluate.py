"""Evaluation for Phase 3 model artifacts."""

from __future__ import annotations

import json
import os

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, roc_auc_score

from src.config import HOLDOUT_TEST_PATH, METRICS_PATH, MODEL_PATH, REPORTS_DIR

TARGET_COLUMN = "default_risk"


def _log_metrics_to_wandb(metrics: dict[str, float]) -> None:
    """Log evaluation metrics to W&B when configured."""
    if not os.getenv("WANDB_API_KEY"):
        return
    try:
        import wandb

        run = wandb.init(project="credit-risk-mlops", job_type="evaluate")
        run.log(metrics)
        run.finish()
    except Exception as exc:
        print(f"W&B metric logging skipped due to error: {exc}")


def run_evaluation() -> None:
    """Evaluate trained model on holdout data and write metrics report."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing model artifact at {MODEL_PATH}. Run src.train first.")
    if not HOLDOUT_TEST_PATH.exists():
        raise FileNotFoundError(
            f"Missing holdout test dataset at {HOLDOUT_TEST_PATH}. Run src.train first."
        )

    model = joblib.load(MODEL_PATH)
    holdout_df = pd.read_csv(HOLDOUT_TEST_PATH)
    if TARGET_COLUMN not in holdout_df.columns:
        raise ValueError(f"Holdout data must contain target column '{TARGET_COLUMN}'.")

    X_test = holdout_df.drop(columns=[TARGET_COLUMN])
    y_test = holdout_df[TARGET_COLUMN]
    unique_classes = y_test.nunique()
    if unique_classes < 2:
        raise ValueError(
            "Evaluation holdout contains a single target class; "
            "cannot compute ROC-AUC/PR-AUC reliably."
        )

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "pr_auc": float(average_precision_score(y_test, y_prob)),
        "accuracy_at_0_5": float(accuracy_score(y_test, y_pred)),
        "evaluation_rows": float(len(holdout_df)),
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    _log_metrics_to_wandb(metrics)

    print(f"Evaluation metrics saved to {METRICS_PATH}.")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    run_evaluation()
