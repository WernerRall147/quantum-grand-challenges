#!/usr/bin/env python3
"""Generate Stage D variance-reduction fairness and overhead artifacts for 03_qae_risk."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist
from typing import Any, Dict, List

import numpy as np


@dataclass(frozen=True)
class InstanceInput:
    instance_id: str
    threshold: float
    mean: float
    std_dev: float
    phase_bits: int
    repetitions: int
    t_count: int
    quantum_std_error: float
    quantum_estimate: float


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON structure in {path}")
    return payload


def _normal_survival(z: float) -> float:
    return 1.0 - NormalDist().cdf(z)


def _analytic_tail_probability(mean: float, std_dev: float, threshold: float) -> float:
    if threshold <= 0.0:
        return 1.0
    z = (math.log(threshold) - mean) / std_dev
    return max(0.0, min(1.0, _normal_survival(z)))


def _read_instance_input(path: Path, instance_id: str) -> InstanceInput:
    payload = _load_json(path)
    params = payload.get("instance", {}).get("parameters", {})
    metrics = payload.get("metrics", {})

    threshold = float(params.get("threshold", 0.0))
    mean = float(params.get("mean", 0.0))
    std_dev = float(params.get("std_dev", 1.0))
    phase_bits = int(params.get("phase_bits", metrics.get("phase_bits", 0)))
    repetitions = int(params.get("repetitions", metrics.get("repetitions", 0)))

    return InstanceInput(
        instance_id=instance_id,
        threshold=threshold,
        mean=mean,
        std_dev=std_dev,
        phase_bits=phase_bits,
        repetitions=repetitions,
        t_count=int(metrics.get("t_count", 0)),
        quantum_std_error=float(metrics.get("ensemble_std_error", 0.0)),
        quantum_estimate=float(metrics.get("quantum_estimate", 0.0)),
    )


def _mc_estimators(inst: InstanceInput, samples: int, seed: int) -> Dict[str, float]:
    rng = np.random.default_rng(seed)

    z = rng.normal(loc=inst.mean, scale=inst.std_dev, size=samples)
    losses = np.exp(z)
    indicator = (losses > inst.threshold).astype(np.float64)

    naive_est = float(indicator.mean())
    naive_se = float(indicator.std(ddof=1) / math.sqrt(samples))

    # Antithetic variates: pair z and -z around the mean.
    half = samples // 2
    z_half = rng.normal(loc=0.0, scale=inst.std_dev, size=half)
    z1 = inst.mean + z_half
    z2 = inst.mean - z_half
    i1 = (np.exp(z1) > inst.threshold).astype(np.float64)
    i2 = (np.exp(z2) > inst.threshold).astype(np.float64)
    antithetic_pair = 0.5 * (i1 + i2)
    antithetic_est = float(antithetic_pair.mean())
    antithetic_se = float(antithetic_pair.std(ddof=1) / math.sqrt(half))

    # Control variate with X = lognormal sample and known E[X].
    ex = math.exp(inst.mean + 0.5 * inst.std_dev * inst.std_dev)
    centered_x = losses - ex
    cov = float(np.cov(indicator, centered_x, ddof=1)[0, 1])
    var_x = float(np.var(centered_x, ddof=1))
    beta = cov / var_x if var_x > 0 else 0.0
    cv_values = indicator - beta * centered_x
    cv_est = float(cv_values.mean())
    cv_se = float(cv_values.std(ddof=1) / math.sqrt(samples))

    return {
        "samples": float(samples),
        "naive_estimate": naive_est,
        "naive_std_error": naive_se,
        "antithetic_estimate": antithetic_est,
        "antithetic_std_error": antithetic_se,
        "control_variate_estimate": cv_est,
        "control_variate_std_error": cv_se,
    }


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_markdown(
    path: Path,
    rows: List[Dict[str, Any]],
    overhead_rows: List[Dict[str, Any]],
    seed: int,
    samples: int,
) -> None:
    lines: List[str] = []
    lines.append("# Stage D Variance Reduction And Overhead Review - 03_qae_risk")
    lines.append("")
    lines.append(f"Monte Carlo seed: {seed}")
    lines.append(f"Monte Carlo samples per instance: {samples}")
    lines.append("")
    lines.append("## Variance-Reduction Fairness")
    lines.append("")
    lines.append("| Instance | Threshold | Quantum Std Error | Naive MC Std Error | Antithetic Std Error | Control-Variate Std Error |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in rows:
        lines.append(
            "| {instance_id} | {threshold:.3f} | {quantum_std_error:.6f} | {naive_std_error:.6f} | {antithetic_std_error:.6f} | {control_variate_std_error:.6f} |".format(**row)
        )

    lines.append("")
    lines.append("## Oracle/State-Preparation Overhead Accounting")
    lines.append("")
    lines.append("Effective query-equivalent is modeled as QAE query rounds multiplied by an overhead factor.")
    lines.append("")
    lines.append("| Instance | QAE Query Rounds | Classical Samples @1e-3 | Overhead Factor | Effective Quantum Query-Equivalent | Effective Speedup |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in overhead_rows:
        lines.append(
            "| {instance_id} | {qae_query_rounds:.0f} | {classical_samples:.0f} | {overhead_factor:.0f} | {effective_quantum_queries:.0f} | {effective_speedup:.2f}x |".format(**row)
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Variance-reduction comparators now include antithetic and control-variate Monte Carlo estimators.")
    lines.append("- Overhead accounting is model-based and should be replaced with backend measured timing when available.")
    lines.append("- This artifact supports Stage D fairness and overhead checklist closure for projected-claim hardening.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates = root / "estimates"

    inputs = [
        _read_instance_input(estimates / "quantum_estimate_ensemble_small.json", "small"),
        _read_instance_input(estimates / "quantum_estimate_ensemble_medium.json", "medium"),
        _read_instance_input(estimates / "quantum_estimate_ensemble_large.json", "large"),
    ]

    sample_count = 200000
    seed = 314159

    variance_rows: List[Dict[str, Any]] = []
    for idx, inst in enumerate(inputs):
        stats = _mc_estimators(inst, sample_count, seed + idx)
        variance_rows.append(
            {
                "instance_id": inst.instance_id,
                "threshold": inst.threshold,
                "quantum_std_error": inst.quantum_std_error,
                "quantum_estimate": inst.quantum_estimate,
                **stats,
            }
        )

    classical = _load_json(estimates / "classical_baseline.json")
    baseline_samples = 47500.0
    if isinstance(classical.get("2.0"), dict):
        values = classical["2.0"].get("samples_needed", [])
        if isinstance(values, list) and values:
            baseline_samples = float(values[-1])

    overhead_rows: List[Dict[str, Any]] = []
    for inst in inputs:
        qae_query_rounds = float((2 ** max(inst.phase_bits, 0)) * max(inst.repetitions, 1))
        for factor in (1.0, 10.0, 100.0):
            effective_quantum_queries = qae_query_rounds * factor
            effective_speedup = baseline_samples / max(effective_quantum_queries, 1.0)
            overhead_rows.append(
                {
                    "instance_id": inst.instance_id,
                    "qae_query_rounds": qae_query_rounds,
                    "classical_samples": baseline_samples,
                    "overhead_factor": factor,
                    "effective_quantum_queries": effective_quantum_queries,
                    "effective_speedup": effective_speedup,
                }
            )

    out_json = estimates / "variance_and_overhead_stage_d.json"
    out_md = estimates / "variance_and_overhead_stage_d.md"

    payload = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "problem_id": "03_qae_risk",
        "seed": seed,
        "samples_per_instance": sample_count,
        "variance_reduction_rows": variance_rows,
        "overhead_rows": overhead_rows,
    }
    _write_json(out_json, payload)
    _write_markdown(out_md, variance_rows, overhead_rows, seed, sample_count)

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
