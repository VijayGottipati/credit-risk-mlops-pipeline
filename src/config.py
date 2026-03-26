"""Project-wide constants and file paths."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = ROOT / "artifacts"
REPORTS_DIR = ROOT / "reports"

HISTORICAL_DATA_PATH = RAW_DATA_DIR / "historical_credit_data.csv"
LIVE_DATA_PATH = RAW_DATA_DIR / "live_credit_applications.csv"
PREDICTION_LOG_PATH = RAW_DATA_DIR / "prediction_logs.csv"
TRAIN_READY_PATH = PROCESSED_DATA_DIR / "train_ready.csv"
LIVE_READY_PATH = PROCESSED_DATA_DIR / "live_ready.csv"

MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
FEATURE_COLUMNS_PATH = ARTIFACTS_DIR / "feature_columns.json"
TRAINING_METADATA_PATH = ARTIFACTS_DIR / "training_metadata.json"
HOLDOUT_TEST_PATH = ARTIFACTS_DIR / "holdout_test.csv"
METRICS_PATH = REPORTS_DIR / "metrics.json"
MODEL_VERSION = "credit_xgb_v1"
