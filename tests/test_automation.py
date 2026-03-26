import json

from monitoring.drift_check import DRIFT_STATUS_PATH, run_drift_check


def test_drift_check_writes_status_report() -> None:
    run_drift_check()
    assert DRIFT_STATUS_PATH.exists()
    payload = json.loads(DRIFT_STATUS_PATH.read_text(encoding="utf-8"))
    assert "drift_detected" in payload
    assert "reason" in payload
