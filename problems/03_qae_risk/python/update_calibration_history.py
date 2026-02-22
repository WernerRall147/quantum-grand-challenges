#!/usr/bin/env python3
"""Append latest QAE calibration metrics to a persistent history file."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _as_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        return datetime.min
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min


def _load_ensemble_record(ensemble_path: Path) -> dict[str, Any]:
    payload = json.loads(ensemble_path.read_text(encoding="utf-8"))
    metrics = payload.get("metrics", {})
    instance = payload.get("instance", {}).get("parameters", {})
    runs = int(metrics.get("ensemble_runs") or metrics.get("runs_requested") or 0)

    theoretical = _as_float(metrics.get("analytic_probability"))
    if theoretical is None:
        runs_data = payload.get("ensemble", {}).get("runs", [])
        if runs_data:
            theoretical = _as_float(runs_data[0].get("metrics", {}).get("analytic_probability"))

    return {
        "source": "ensemble",
        "timestamp": payload.get("timestamp"),
        "phase_bits": instance.get("phase_bits") or metrics.get("phase_bits"),
        "repetitions": instance.get("repetitions") or metrics.get("repetitions"),
        "runs": runs,
        "quantum_estimate": _as_float(metrics.get("quantum_estimate")),
        "std_error": _as_float(metrics.get("ensemble_std_error") or metrics.get("mean_reported_std_error")),
        "theoretical": theoretical,
        "mean_difference": _as_float(metrics.get("mean_difference")),
    }


def _load_single_record(single_path: Path) -> dict[str, Any]:
    payload = json.loads(single_path.read_text(encoding="utf-8"))
    metrics = payload.get("metrics", {})
    instance = payload.get("instance", {}).get("parameters", {})
    theoretical = _as_float(metrics.get("analytic_probability"))
    estimate = _as_float(metrics.get("quantum_estimate"))
    diff = None
    if theoretical is not None and estimate is not None:
        diff = estimate - theoretical
    return {
        "source": "single",
        "timestamp": payload.get("timestamp"),
        "phase_bits": instance.get("phase_bits") or metrics.get("phase_bits"),
        "repetitions": instance.get("repetitions") or metrics.get("repetitions"),
        "runs": 1,
        "quantum_estimate": estimate,
        "std_error": _as_float(metrics.get("quantum_std_error")),
        "theoretical": theoretical,
        "mean_difference": diff,
    }


def load_latest(estimates_dir: Path) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    ensemble = estimates_dir / "quantum_estimate_ensemble.json"
    single = estimates_dir / "quantum_estimate.json"

    if ensemble.exists():
        candidates.append(_load_ensemble_record(ensemble))
    if single.exists():
        candidates.append(_load_single_record(single))

    if not candidates:
        raise FileNotFoundError("No quantum estimate JSON available (expected quantum_estimate*.json in estimates/)")

    return max(candidates, key=lambda record: _parse_timestamp(record.get("timestamp")))


def append_history(history_path: Path, record: dict[str, Any]) -> int:
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    else:
        history = {"records": []}

    history.setdefault("records", [])
    history["records"].append(record)
    history["last_updated_utc"] = datetime.utcnow().isoformat() + "Z"

    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return len(history["records"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append latest QAE calibration to history")
    parser.add_argument(
        "--history-file",
        default="../estimates/quantum_calibration_history.json",
        help="Path to the calibration history JSON file",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    problem_dir = script_dir.parent
    estimates_dir = problem_dir / "estimates"

    latest = load_latest(estimates_dir)
    estimate = latest.get("quantum_estimate")
    theoretical = latest.get("theoretical")
    rel_error_pct = None
    if isinstance(estimate, float) and isinstance(theoretical, float) and theoretical != 0.0:
        rel_error_pct = abs(estimate - theoretical) / abs(theoretical) * 100.0

    record = {
        "recorded_utc": datetime.utcnow().isoformat() + "Z",
        **latest,
        "relative_error_percent": rel_error_pct,
    }

    history_path = (script_dir / args.history_file).resolve()
    total = append_history(history_path, record)
    print(f"Appended calibration record to {history_path} (total records: {total})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
