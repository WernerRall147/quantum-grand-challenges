#!/usr/bin/env python3
"""Generate Stage D fairness and multi-instance uncertainty artifacts for 03_qae_risk.

This script intentionally distinguishes between measured evidence and provisional
projection rows when quantum ensemble runs are not yet available for an instance.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist
from typing import Any, Dict, List

import yaml


@dataclass(frozen=True)
class InstanceSpec:
    instance_id: str
    threshold: float
    mean: float
    std_dev: float
    tail_probability: float | None


def _load_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML structure in {path}")
    return data


def load_instances(instances_dir: Path) -> Dict[str, InstanceSpec]:
    specs: Dict[str, InstanceSpec] = {}
    for path in sorted(instances_dir.glob("*.yaml")):
        payload = _load_yaml(path)
        dist = payload.get("distribution", {}) if isinstance(payload.get("distribution"), dict) else {}
        params = dist.get("parameters", {}) if isinstance(dist.get("parameters"), dict) else {}
        theo = payload.get("theoretical", {}) if isinstance(payload.get("theoretical"), dict) else {}
        specs[path.stem] = InstanceSpec(
            instance_id=path.stem,
            threshold=float(payload.get("risk_threshold", 0.0)),
            mean=float(params.get("mean", 0.0)),
            std_dev=float(params.get("std_dev", 1.0)),
            tail_probability=float(theo["tail_probability"]) if "tail_probability" in theo else None,
        )
    return specs


def _normal_survival(z: float) -> float:
    return 1.0 - NormalDist().cdf(z)


def approximate_tail_probability(spec: InstanceSpec) -> float:
    if spec.tail_probability is not None:
        return max(0.0, min(1.0, spec.tail_probability))
    if spec.threshold <= 0.0:
        return 1.0
    if spec.std_dev <= 0.0:
        return 0.0
    z = (math.log(spec.threshold) - spec.mean) / spec.std_dev
    return max(0.0, min(1.0, _normal_survival(z)))


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON structure in {path}")
    return payload


def build_projection_payload(instance_id: str, spec: InstanceSpec) -> Dict[str, Any]:
    probability = approximate_tail_probability(spec)
    effective_runs = 20
    effective_shots = 128
    std_error = math.sqrt(max(probability * (1.0 - probability), 0.0) / (effective_runs * effective_shots))
    return {
        "timestamp": None,
        "algorithm": "QPEAmplitudeEstimation",
        "mode": "ensemble",
        "evidence_mode": "provisional_projection",
        "instance_id": instance_id,
        "estimator_target": f"TailRisk > {spec.threshold}",
        "instance": {
            "parameters": {
                "threshold": spec.threshold,
                "mean": spec.mean,
                "std_dev": spec.std_dev,
            }
        },
        "metrics": {
            "ensemble_runs": effective_runs,
            "runs_requested": effective_runs,
            "quantum_estimate": probability,
            "ensemble_std_deviation": std_error * math.sqrt(effective_runs),
            "ensemble_std_error": std_error,
            "mean_reported_std_error": std_error,
            "mean_difference": 0.0,
        },
        "notes": [
            "This artifact is provisional and model-projected.",
            "Replace with measured ensemble output from analyze.py --ensemble-runs once available.",
        ],
    }


def write_markdown(
    estimates_dir: Path,
    classical_path: Path,
    rows: List[Dict[str, Any]],
) -> None:
    classical = _load_json(classical_path)
    lines: List[str] = []
    lines.append("# Stage D Fairness Review - 03_qae_risk")
    lines.append("")
    lines.append("This report compares available quantum ensemble estimates with classical Monte Carlo baselines.")
    lines.append("Rows marked `provisional_projection` are placeholders and must be replaced by measured ensemble runs.")
    lines.append("")
    lines.append("| Instance | Evidence Mode | Quantum Estimate | Ensemble Std Error | Classical Baseline (threshold 2.0) | Quantum-Classical Delta |")
    lines.append("|---|---|---:|---:|---:|---:|")

    threshold_2 = classical.get("2.0", {}) if isinstance(classical, dict) else {}
    classical_at_2 = float((threshold_2 or {}).get("estimates", [0.0])[0]) if isinstance((threshold_2 or {}).get("estimates"), list) and (threshold_2 or {}).get("estimates") else 0.0

    for row in rows:
        q = float(row["quantum_estimate"])
        se = float(row["ensemble_std_error"])
        delta = q - classical_at_2
        lines.append(
            f"| {row['instance_id']} | {row['evidence_mode']} | {q:.6f} | {se:.6f} | {classical_at_2:.6f} | {delta:.6f} |"
        )

    lines.append("")
    lines.append("## Fairness Notes")
    lines.append("")
    lines.append("- Baseline source: `python/classical_baseline.py` -> `estimates/classical_baseline.json`.")
    lines.append("- Current baseline is plain Monte Carlo and should be extended with variance-reduction comparators.")
    lines.append("- Promotion to demonstrated status requires measured ensemble artifacts for all listed instances.")
    lines.append("")

    out_path = estimates_dir / "fairness_review_stage_d.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates_dir = root / "estimates"
    instances_dir = root / "instances"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    specs = load_instances(instances_dir)
    required = ["small", "medium", "large"]
    missing = [name for name in required if name not in specs]
    if missing:
        raise RuntimeError(f"Missing required instance files for Stage D: {', '.join(missing)}")

    source_path = estimates_dir / "quantum_estimate_ensemble.json"
    source_payload = _load_json(source_path) if source_path.exists() else None

    summary_rows: List[Dict[str, Any]] = []
    for instance_id in required:
        out_path = estimates_dir / f"quantum_estimate_ensemble_{instance_id}.json"
        if instance_id == "small" and source_payload is not None:
            payload = dict(source_payload)
            payload["instance_id"] = "small"
            payload["evidence_mode"] = "measured"
        else:
            payload = build_projection_payload(instance_id, specs[instance_id])

        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        metrics = payload.get("metrics", {}) if isinstance(payload.get("metrics"), dict) else {}
        summary_rows.append(
            {
                "instance_id": instance_id,
                "evidence_mode": str(payload.get("evidence_mode", "unknown")),
                "quantum_estimate": float(metrics.get("quantum_estimate", 0.0)),
                "ensemble_std_error": float(metrics.get("ensemble_std_error", 0.0)),
            }
        )
        print(f"Wrote {out_path}")

    classical_path = estimates_dir / "classical_baseline.json"
    if not classical_path.exists():
        raise FileNotFoundError(f"Missing classical baseline artifact: {classical_path}")
    write_markdown(estimates_dir, classical_path, summary_rows)


if __name__ == "__main__":
    main()