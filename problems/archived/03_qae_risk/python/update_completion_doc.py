#!/usr/bin/env python3
"""Synchronize key calibration numbers into docs/QAE_PROJECT_COMPLETION.md."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any


def _as_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _load_single_metrics(estimates_dir: Path) -> dict[str, float | int]:
    single_path = estimates_dir / "quantum_estimate.json"
    if not single_path.exists():
        raise FileNotFoundError("quantum_estimate.json not found in estimates/")

    payload = json.loads(single_path.read_text(encoding="utf-8"))
    metrics = payload.get("metrics", {})
    instance = payload.get("instance", {}).get("parameters", {})
    theoretical = _as_float(metrics.get("analytic_probability")) or 0.0
    qae_estimate = _as_float(metrics.get("quantum_estimate")) or 0.0
    rel_error_pct = abs(qae_estimate - theoretical) / theoretical * 100.0 if theoretical else 0.0

    return {
        "phase_bits": int(instance.get("phase_bits") or metrics.get("phase_bits") or 0),
        "runs": int(instance.get("repetitions") or metrics.get("repetitions") or 0),
        "qae_estimate": qae_estimate,
        "qae_std": _as_float(metrics.get("quantum_std_error")) or 0.0,
        "theoretical": theoretical,
        "rel_error_pct": rel_error_pct,
    }


def _load_ensemble_metrics(estimates_dir: Path) -> dict[str, float | int] | None:
    ensemble_path = estimates_dir / "quantum_estimate_ensemble.json"
    if not ensemble_path.exists():
        return None

    payload = json.loads(ensemble_path.read_text(encoding="utf-8"))
    metrics = payload.get("metrics", {})
    runs = int(metrics.get("ensemble_runs", metrics.get("runs_requested", 0)) or 0)
    if runs <= 0:
        return None

    theoretical = None
    runs_data = payload.get("ensemble", {}).get("runs", [])
    if runs_data:
        first_metrics = runs_data[0].get("metrics", {})
        theoretical = _as_float(first_metrics.get("analytic_probability"))

    theoretical_val = theoretical or _as_float(metrics.get("analytic_probability")) or 0.0
    mean_difference = _as_float(metrics.get("mean_difference")) or 0.0
    rel_error_pct = abs(mean_difference) / theoretical_val * 100.0 if theoretical_val else 0.0

    return {
        "runs": runs,
        "qae_estimate": _as_float(metrics.get("quantum_estimate")) or 0.0,
        "qae_std": _as_float(metrics.get("ensemble_std_error") or metrics.get("mean_reported_std_error")) or 0.0,
        "theoretical": theoretical_val,
        "rel_error_pct": rel_error_pct,
    }


def _fmt_pct(prob: float) -> str:
    return f"{prob * 100.0:.2f}%"


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    problem_dir = script_dir.parent
    repo_root = problem_dir.parent.parent
    doc_path = repo_root / "docs" / "QAE_PROJECT_COMPLETION.md"

    single_metrics = _load_single_metrics(problem_dir / "estimates")
    ensemble_metrics = _load_ensemble_metrics(problem_dir / "estimates")
    headline_metrics = ensemble_metrics or single_metrics
    text = doc_path.read_text(encoding="utf-8")

    text = re.sub(r"\*\*Date\*\*: .*", f"**Date**: {date.today():%B %d, %Y}  ", text, count=1)

    config_line = (
        f"- **Configuration**: 4 loss qubits, {single_metrics['phase_bits']} precision qubits, "
        "log-normal(0,1), threshold=2.5"
    )
    text = re.sub(r"- \*\*Configuration\*\*: .*", config_line, text, count=1)

    qae_line = (
        f"- **QAE Current**: {_fmt_pct(headline_metrics['qae_estimate'])} ± {_fmt_pct(headline_metrics['qae_std'])} "
        f"({headline_metrics['runs']} repetitions; calibrated baseline run)"
    )
    text = re.sub(r"- \*\*QAE Current\*\*: .*", qae_line, text, count=1)

    baseline_line = (
        f"   - Current baseline: QAE {_fmt_pct(headline_metrics['qae_estimate'])} vs theoretical {_fmt_pct(headline_metrics['theoretical'])} "
        f"(about {headline_metrics['rel_error_pct']:.1f}% relative error)"
    )
    text = re.sub(r"\s*- Current baseline: QAE .*", baseline_line, text, count=1)

    doc_path.write_text(text, encoding="utf-8")
    print(f"Updated {doc_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
