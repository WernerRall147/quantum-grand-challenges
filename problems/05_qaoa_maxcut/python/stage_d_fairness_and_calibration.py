#!/usr/bin/env python3
"""Generate Stage D fairness benchmark and backend calibration artifacts for 05_qaoa_maxcut."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import yaml


@dataclass(frozen=True)
class Instance:
    instance_id: str
    nodes: List[str]
    edges: List[Tuple[int, int, float]]


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON structure in {path}")
    return payload


def load_instances(instances_dir: Path) -> Dict[str, Instance]:
    instances: Dict[str, Instance] = {}
    for path in sorted(instances_dir.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid YAML structure in {path}")
        node_names = [str(v) for v in payload.get("nodes", [])]
        node_index = {name: i for i, name in enumerate(node_names)}
        edges: List[Tuple[int, int, float]] = []
        for entry in payload.get("edges", []):
            if not isinstance(entry, list) or len(entry) != 3:
                raise ValueError(f"Invalid edge entry in {path}: {entry}")
            u, v, w = str(entry[0]), str(entry[1]), float(entry[2])
            edges.append((node_index[u], node_index[v], w))
        instances[path.stem] = Instance(instance_id=path.stem, nodes=node_names, edges=edges)
    return instances


def cut_value(bits: Sequence[int], edges: Sequence[Tuple[int, int, float]]) -> float:
    total = 0.0
    for u, v, w in edges:
        if bits[u] != bits[v]:
            total += w
    return total


def greedy_local_search(instance: Instance, seed: int) -> float:
    rng = random.Random(seed)
    bits = [rng.randint(0, 1) for _ in instance.nodes]
    best = cut_value(bits, instance.edges)
    improved = True
    while improved:
        improved = False
        for i in range(len(bits)):
            bits[i] = 1 - bits[i]
            trial = cut_value(bits, instance.edges)
            if trial > best + 1e-12:
                best = trial
                improved = True
            else:
                bits[i] = 1 - bits[i]
    return best


def random_baseline(instance: Instance, samples: int, seed: int) -> float:
    rng = random.Random(seed)
    best = 0.0
    for _ in range(samples):
        bits = [rng.randint(0, 1) for _ in instance.nodes]
        best = max(best, cut_value(bits, instance.edges))
    return best


def choose_best_quantum_report(estimates_dir: Path, instance_id: str) -> Dict[str, Any]:
    candidates = sorted(estimates_dir.glob(f"quantum_baseline_{instance_id}_d*.json"))
    if not candidates:
        raise FileNotFoundError(f"No quantum baseline files for instance '{instance_id}'")
    best_payload: Dict[str, Any] | None = None
    best_key: Tuple[int, int] = (-1, -1)
    for path in candidates:
        payload = _load_json(path)
        depth = int(payload.get("depth", 1))
        trials = int(payload.get("trials", 0))
        if (depth, trials) > best_key:
            best_key = (depth, trials)
            best_payload = payload
            best_payload["_source_file"] = path.name
    assert best_payload is not None
    return best_payload


def write_fairness_artifacts(root: Path, instances: Dict[str, Instance]) -> None:
    estimates_dir = root / "estimates"
    classical = _load_json(estimates_dir / "classical_baseline.json")
    classical_rows = classical.get("results", [])
    classical_map = {str(row["instance_id"]): row for row in classical_rows if isinstance(row, dict)}

    rows: List[Dict[str, Any]] = []
    for instance_id in sorted(instances.keys()):
        quantum = choose_best_quantum_report(estimates_dir, instance_id)
        aggregate = quantum.get("aggregate", {}) if isinstance(quantum.get("aggregate"), dict) else {}
        refined = aggregate.get("refined_expectation", {}) if isinstance(aggregate.get("refined_expectation"), dict) else {}
        quantum_mean = float(refined.get("mean", 0.0))
        quantum_ci95 = float(refined.get("ci95", 0.0))

        classical_best = float(classical_map[instance_id]["best_cut"])
        greedy_best = greedy_local_search(instances[instance_id], seed=1000 + len(instance_id))
        random_best = random_baseline(instances[instance_id], samples=2048, seed=2000 + len(instance_id))

        rows.append(
            {
                "instance_id": instance_id,
                "quantum_source": str(quantum.get("_source_file", "unknown")),
                "quantum_depth": int(quantum.get("depth", 1)),
                "quantum_refined_mean": quantum_mean,
                "quantum_refined_ci95": quantum_ci95,
                "classical_optimum": classical_best,
                "greedy_local_search": greedy_best,
                "random_sampling_best": random_best,
                "gap_to_optimum": max(0.0, classical_best - quantum_mean),
                "gap_to_greedy": greedy_best - quantum_mean,
                "gap_to_random": random_best - quantum_mean,
            }
        )

    out_json = estimates_dir / "fairness_benchmark_stage_d.json"
    out_json.write_text(json.dumps({"problem_id": "05_qaoa_maxcut", "rows": rows}, indent=2) + "\n", encoding="utf-8")

    lines: List[str] = []
    lines.append("# Stage D Fairness Benchmark - 05_qaoa_maxcut")
    lines.append("")
    lines.append("Classical comparator families used: exhaustive optimum, greedy local search, and random sampling baseline.")
    lines.append("")
    lines.append("| Instance | Quantum Mean +/- CI95 | Classical Optimum | Greedy | Random Best | Gap To Optimum |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in rows:
        lines.append(
            f"| {row['instance_id']} | {row['quantum_refined_mean']:.4f} +/- {row['quantum_refined_ci95']:.4f} | "
            f"{row['classical_optimum']:.4f} | {row['greedy_local_search']:.4f} | {row['random_sampling_best']:.4f} | {row['gap_to_optimum']:.4f} |"
        )
    lines.append("")
    lines.append("Notes:")
    lines.append("- Quantum values are taken from highest-depth available baseline artifacts per instance.")
    lines.append("- Greedy/random comparators are deterministic through fixed seeds in this script.")
    lines.append("")

    out_md = estimates_dir / "fairness_benchmark_stage_d.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


def write_backend_calibration_artifact(root: Path) -> None:
    estimates_dir = root / "estimates"
    smoke = _load_json(estimates_dir / "azure_smoke_report_small_d3.json")
    noise = _load_json(estimates_dir / "noise_sweep_small_d3.json")

    records = noise.get("records", []) if isinstance(noise.get("records"), list) else []
    first = records[0] if records else {"noise": 0.0, "noisy_mean": 0.0, "noisy_ci95": 0.0}
    last = records[-1] if records else first
    degradation = float(first.get("noisy_mean", 0.0)) - float(last.get("noisy_mean", 0.0))

    payload = {
        "problem_id": "05_qaoa_maxcut",
        "artifact_type": "backend_calibration_stage_d",
        "backend": {
            "target_id": smoke.get("backend", {}).get("target_id"),
            "workspace_location": smoke.get("backend", {}).get("workspace", {}).get("location"),
            "smoke_report": "azure_smoke_report_small_d3.json",
        },
        "shot_plan": {
            "source": "azure_job_manifest_small_d3.json",
            "coarse_shots": 64,
            "refined_shots": 256,
            "trials": 16,
        },
        "readout_coherence_proxy": {
            "noise_model": noise.get("noise_model", {}),
            "records_analyzed": len(records),
            "start_noise": float(first.get("noise", 0.0)),
            "end_noise": float(last.get("noise", 0.0)),
            "degradation": degradation,
            "start_mean": float(first.get("noisy_mean", 0.0)),
            "end_mean": float(last.get("noisy_mean", 0.0)),
            "end_ci95": float(last.get("noisy_ci95", 0.0)),
        },
        "status": "provisional_backend_calibration",
        "notes": [
            "This artifact combines Azure smoke metadata and noise-sweep degradation proxy.",
            "Upgrade to hardware-calibrated evidence by replacing proxy section with backend readout/coherence measurements.",
        ],
    }

    out_path = estimates_dir / "backend_calibration_stage_d.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    for needed in ("small", "medium", "large"):
        if needed not in instances:
            raise RuntimeError(f"Missing required instance '{needed}'")
    write_fairness_artifacts(root, instances)
    write_backend_calibration_artifact(root)


if __name__ == "__main__":
    main()