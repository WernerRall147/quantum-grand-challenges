#!/usr/bin/env python3
"""Generate Stage D uncertainty and overhead/sensitivity artifacts for 15_database_search."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass(frozen=True)
class SearchInstance:
    instance_id: str
    dataset_size: int
    marked_fraction: float
    confidence: float


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON structure in {path}")
    return payload


def _load_instances(instances_dir: Path) -> Dict[str, SearchInstance]:
    out: Dict[str, SearchInstance] = {}
    for path in sorted(instances_dir.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid YAML structure in {path}")
        out[path.stem] = SearchInstance(
            instance_id=path.stem,
            dataset_size=int(payload.get("dataset_size", 0)),
            marked_fraction=float(payload.get("marked_fraction", 0.0)),
            confidence=float(payload.get("confidence", 0.95)),
        )
    return out


def _wilson_interval(successes: int, shots: int, z: float = 1.96) -> tuple[float, float]:
    if shots <= 0:
        return (0.0, 0.0)
    p_hat = successes / shots
    denom = 1.0 + (z * z) / shots
    center = (p_hat + (z * z) / (2.0 * shots)) / denom
    radius = (z / denom) * math.sqrt((p_hat * (1.0 - p_hat) / shots) + (z * z) / (4.0 * shots * shots))
    lo = max(0.0, center - radius)
    hi = min(1.0, center + radius)
    return (lo, hi)


def _quantum_iterations(marked_fraction: float, confidence: float) -> int:
    amplitude = math.sqrt(marked_fraction)
    theta = math.asin(min(1.0, max(0.0, amplitude)))
    if theta <= 0.0:
        return 0
    rounds = max(math.floor((math.pi / (2.0 * theta) - 1.0) / 2.0), 0)
    while math.sin((2 * rounds + 1) * theta) ** 2 < confidence:
        rounds += 1
    return rounds


def write_uncertainty_artifacts(root: Path, instances: Dict[str, SearchInstance]) -> None:
    estimates_dir = root / "estimates"
    smoke = _load_json(estimates_dir / "azure_smoke_report_small_d1.json")

    backend_target = str(smoke.get("backend", {}).get("target_id", "unknown"))
    workspace_location = str(smoke.get("backend", {}).get("workspace", {}).get("location", "unknown"))

    for instance_id in ("small", "medium", "large"):
        spec = instances[instance_id]
        rounds = max(1, _quantum_iterations(spec.marked_fraction, spec.confidence))
        shots = max(256, rounds * 32)
        observed_success_rate = min(0.999, max(0.001, spec.confidence))
        successes = int(round(observed_success_rate * shots))
        ci_lo, ci_hi = _wilson_interval(successes, shots)

        payload = {
            "problem_id": "15_database_search",
            "instance_id": instance_id,
            "artifact_type": "backend_uncertainty",
            "evidence_mode": "projected_from_model",
            "backend": {
                "target_id": backend_target,
                "workspace_location": workspace_location,
                "source_smoke_report": "azure_smoke_report_small_d1.json",
            },
            "shot_plan": {
                "shots": shots,
                "estimated_quantum_rounds": rounds,
            },
            "observed": {
                "successes": successes,
                "shots": shots,
                "success_rate": successes / shots,
            },
            "confidence_interval": {
                "method": "wilson_95",
                "lower": ci_lo,
                "upper": ci_hi,
            },
            "notes": [
                "This uncertainty artifact is model-projected from instance confidence targets.",
                "Replace with backend measured success counts once repeated execution data is available.",
            ],
        }

        out_path = estimates_dir / f"backend_uncertainty_{instance_id}.json"
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {out_path}")


def write_overhead_report(root: Path, baseline: Dict[str, Any]) -> None:
    estimates_dir = root / "estimates"
    rows = baseline.get("results", []) if isinstance(baseline.get("results"), list) else []
    oracle_cost_factors = [1, 10, 100, 1000]

    lines: List[str] = []
    lines.append("# Oracle And Transpilation Overhead Accounting - Stage D")
    lines.append("")
    lines.append("This report models how per-round oracle/transpilation overhead changes practical speedup interpretation.")
    lines.append("")
    for row in rows:
        if not isinstance(row, dict):
            continue
        instance_id = str(row.get("instance_id", "unknown"))
        metrics = row.get("metrics", {}) if isinstance(row.get("metrics"), dict) else {}
        classical_queries = float(metrics.get("classical_queries", 0.0))
        quantum_rounds = float(metrics.get("quantum_rounds", 1.0))

        lines.append(f"## Instance: {instance_id}")
        lines.append("")
        lines.append("| Oracle/Transpile Cost Factor | Effective Quantum Query-Equivalent | Effective Speedup |")
        lines.append("|---:|---:|---:|")
        for factor in oracle_cost_factors:
            effective_quantum = quantum_rounds * factor
            effective_speedup = classical_queries / max(effective_quantum, 1e-9)
            lines.append(f"| {factor} | {effective_quantum:.2f} | {effective_speedup:.2f}x |")
        lines.append("")

    out_path = estimates_dir / "oracle_overhead_accounting_stage_d.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def write_marked_fraction_sensitivity(root: Path, instances: Dict[str, SearchInstance]) -> None:
    estimates_dir = root / "estimates"
    multipliers = [0.5, 1.0, 2.0, 4.0]

    lines: List[str] = []
    lines.append("# Marked-Fraction Sensitivity - Stage D")
    lines.append("")
    lines.append("Sensitivity analysis over marked-fraction scaling multipliers, clamped to (0, 0.5].")
    lines.append("")

    for instance_id in ("small", "medium", "large"):
        spec = instances[instance_id]
        lines.append(f"## Instance: {instance_id}")
        lines.append("")
        lines.append("| Multiplier | Marked Fraction | Classical Queries | Quantum Rounds | Speedup |")
        lines.append("|---:|---:|---:|---:|---:|")

        for multiplier in multipliers:
            p = min(0.5, max(1e-12, spec.marked_fraction * multiplier))
            classical = math.log(1.0 - spec.confidence) / math.log(1.0 - p)
            rounds = max(1, _quantum_iterations(p, spec.confidence))
            speedup = classical / rounds
            lines.append(f"| {multiplier:.1f} | {p:.12f} | {classical:.2f} | {rounds} | {speedup:.2f}x |")
        lines.append("")

    out_path = estimates_dir / "marked_fraction_sensitivity_stage_d.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates_dir = root / "estimates"
    baseline_path = estimates_dir / "classical_baseline.json"
    if not baseline_path.exists():
        raise FileNotFoundError(f"Missing baseline artifact: {baseline_path}")
    baseline = _load_json(baseline_path)

    instances = _load_instances(root / "instances")
    for needed in ("small", "medium", "large"):
        if needed not in instances:
            raise RuntimeError(f"Missing required instance '{needed}'")

    write_uncertainty_artifacts(root, instances)
    write_overhead_report(root, baseline)
    write_marked_fraction_sensitivity(root, instances)


if __name__ == "__main__":
    main()