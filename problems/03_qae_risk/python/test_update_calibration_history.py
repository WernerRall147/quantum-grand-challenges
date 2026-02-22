import json
from pathlib import Path

from update_calibration_history import append_history, load_latest


def test_load_latest_prefers_newer_single_record(tmp_path: Path):
    estimates_dir = tmp_path / "estimates"
    estimates_dir.mkdir(parents=True)

    ensemble_payload = {
        "timestamp": "2026-02-22T10:00:00Z",
        "metrics": {
            "ensemble_runs": 3,
            "quantum_estimate": 0.2,
            "ensemble_std_error": 0.03,
            "mean_difference": 0.01,
        },
        "instance": {"parameters": {"phase_bits": 6, "repetitions": 120}},
        "ensemble": {
            "runs": [
                {"metrics": {"analytic_probability": 0.19}},
            ]
        },
    }
    single_payload = {
        "timestamp": "2026-02-22T10:05:00Z",
        "metrics": {
            "phase_bits": 6,
            "repetitions": 120,
            "quantum_estimate": 0.21,
            "quantum_std_error": 0.031,
            "analytic_probability": 0.19,
        },
        "instance": {"parameters": {"phase_bits": 6, "repetitions": 120}},
    }

    (estimates_dir / "quantum_estimate_ensemble.json").write_text(json.dumps(ensemble_payload), encoding="utf-8")
    (estimates_dir / "quantum_estimate.json").write_text(json.dumps(single_payload), encoding="utf-8")

    latest = load_latest(estimates_dir)

    assert latest["source"] == "single"
    assert latest["timestamp"] == "2026-02-22T10:05:00Z"
    assert latest["quantum_estimate"] == 0.21
    assert abs(latest["mean_difference"] - 0.02) < 1e-12


def test_append_history_creates_and_appends(tmp_path: Path):
    history_file = tmp_path / "quantum_calibration_history.json"

    first = {"recorded_utc": "2026-02-22T10:00:00Z", "quantum_estimate": 0.2}
    second = {"recorded_utc": "2026-02-22T10:01:00Z", "quantum_estimate": 0.21}

    count1 = append_history(history_file, first)
    count2 = append_history(history_file, second)

    assert count1 == 1
    assert count2 == 2

    payload = json.loads(history_file.read_text(encoding="utf-8"))
    assert len(payload["records"]) == 2
    assert payload["records"][0]["quantum_estimate"] == 0.2
    assert payload["records"][1]["quantum_estimate"] == 0.21
    assert "last_updated_utc" in payload
