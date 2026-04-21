"""Run and aggregate QAOA readout-noise sensitivity evidence for one instance/depth.

This script perturbs each trial's best assignment from a quantum baseline report by
independent bit flips with probability p (a simple readout-noise proxy), then
measures how expected cut value degrades across configured noise levels.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

import matplotlib.pyplot as plt
import yaml


@dataclass(frozen=True)
class MaxCutInstance:
    instance_id: str
    nodes: List[str]
    edges: List[Tuple[int, int, float]]


def parse_noise_levels(raw: str) -> List[float]:
    levels: List[float] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        value = float(part)
        if value < 0.0 or value > 1.0:
            raise ValueError("Noise levels must be in [0, 1].")
        levels.append(value)
    if not levels:
        raise ValueError("No noise levels provided.")

    seen = set()
    ordered: List[float] = []
    for level in levels:
        key = round(level, 8)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(level)
    return ordered


def load_instance(instances_dir: Path, instance_id: str) -> MaxCutInstance:
    path = instances_dir / f"{instance_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Instance file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    nodes = [str(node) for node in raw.get("nodes", [])]
    if not nodes:
        raise ValueError(f"Instance '{instance_id}' has no nodes.")

    node_index = {node: idx for idx, node in enumerate(nodes)}
    edges: List[Tuple[int, int, float]] = []
    for item in raw.get("edges", []):
        if not isinstance(item, list) or len(item) != 3:
            raise ValueError(f"Invalid edge entry in {path}: {item}")
        u, v, w = str(item[0]), str(item[1]), float(item[2])
        if u not in node_index or v not in node_index:
            raise ValueError(f"Edge references unknown nodes in {path}: {u}, {v}")
        edges.append((node_index[u], node_index[v], w))

    return MaxCutInstance(instance_id=instance_id, nodes=nodes, edges=edges)


def cut_value(bits: Sequence[int], edges: Sequence[Tuple[int, int, float]]) -> float:
    total = 0.0
    for u, v, w in edges:
        if bits[u] != bits[v]:
            total += w
    return total


def bitflip_assignment(bits: Sequence[int], noise: float, rng: random.Random) -> List[int]:
    if noise <= 0.0:
        return [int(bit) for bit in bits]
    out: List[int] = []
    for bit in bits:
        bit_int = int(bit)
        if rng.random() < noise:
            out.append(1 - bit_int)
        else:
            out.append(bit_int)
    return out


def compute_stats(values: Sequence[float]) -> Tuple[float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0
    n = len(values)
    mean = sum(values) / n
    if n == 1:
        return mean, 0.0, 0.0
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    std = math.sqrt(max(0.0, variance))
    ci95 = 1.96 * std / math.sqrt(n)
    return mean, std, ci95


def run_driver(
    problem_root: Path,
    instance: str,
    depth: int,
    coarse_shots: int,
    refined_shots: int,
    trials: int,
) -> None:
    cmd = [
        "dotnet",
        "run",
        "--project",
        "host/QaoaMaxCut.Driver.csproj",
        "--",
        "--instance",
        instance,
        "--depth",
        str(depth),
        "--coarse-shots",
        str(coarse_shots),
        "--refined-shots",
        str(refined_shots),
        "--trials",
        str(trials),
    ]
    print(f"[run] {' '.join(cmd)}")
    subprocess.run(cmd, cwd=problem_root, check=True)


def write_markdown(
    instance: str,
    depth: int,
    records: List[dict],
    classical_optimum: float,
    report_source: str,
    out_path: Path,
) -> None:
    lines = [
        f"# QAOA Noise Sweep ({instance}, depth={depth})",
        "",
        "Readout-noise proxy: each bit in each trial's best assignment is flipped independently with probability `p`.",
        f"Source quantum report: `{report_source}`",
        "",
        "| Noise p | Noisy Mean +/- 95% CI | Mean Gap To Optimum | Retention vs Optimum |",
        "|---:|---:|---:|---:|",
    ]

    for row in records:
        retention = 100.0 * row["noisy_mean"] / classical_optimum if classical_optimum > 0 else 0.0
        lines.append(
            f"| {row['noise']:.3f} | {row['noisy_mean']:.4f} +/- {row['noisy_ci95']:.4f} "
            f"| {row['mean_optimality_gap']:.4f} | {retention:.1f}% |"
        )

    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def plot_noise_curve(instance: str, depth: int, records: List[dict], plots_dir: Path) -> Path:
    x = [row["noise"] for row in records]
    means = [row["noisy_mean"] for row in records]
    ci95 = [row["noisy_ci95"] for row in records]

    plt.figure(figsize=(8, 4.5))
    plt.errorbar(x, means, yerr=ci95, fmt="o-", capsize=5, color="#d62728", ecolor="#444")
    plt.title(f"QAOA noise sensitivity ({instance}, depth={depth})")
    plt.xlabel("Independent bit-flip probability p")
    plt.ylabel("Noisy cut value (mean +/- 95% CI)")
    plt.grid(True, linestyle="--", alpha=0.35)

    plots_dir.mkdir(parents=True, exist_ok=True)
    out_path = plots_dir / f"qaoa_noise_sweep_{instance}_d{depth}.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run/aggregate QAOA noise sensitivity evidence.")
    parser.add_argument("--instance", default="small", help="Problem instance id (small/medium/large).")
    parser.add_argument("--depth", type=int, default=1, help="QAOA depth associated with the source report.")
    parser.add_argument("--noise-levels", default="0.00,0.01,0.02,0.05,0.10")
    parser.add_argument("--samples-per-trial", type=int, default=256)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--coarse-shots", type=int, default=24)
    parser.add_argument("--refined-shots", type=int, default=96)
    parser.add_argument("--trials", type=int, default=6)
    parser.add_argument(
        "--run",
        action="store_true",
        default=False,
        help="Run the QAOA host driver before noise aggregation (default: disabled).",
    )
    args = parser.parse_args()

    if args.depth < 1:
        raise ValueError("Depth must be >= 1.")
    if args.samples_per_trial < 1:
        raise ValueError("samples-per-trial must be >= 1.")

    root = Path(__file__).resolve().parents[1]
    estimates_dir = root / "estimates"
    plots_dir = root / "plots"
    instances_dir = root / "instances"

    if args.run:
        run_driver(
            root,
            args.instance,
            args.depth,
            args.coarse_shots,
            args.refined_shots,
            args.trials,
        )

    report_path = estimates_dir / f"quantum_baseline_{args.instance}_d{args.depth}.json"
    if not report_path.exists():
        raise FileNotFoundError(
            f"Missing source quantum report: {report_path}. Run the QAOA driver or pass --run."
        )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    trial_results = payload.get("trial_results", [])
    if not isinstance(trial_results, list) or not trial_results:
        raise ValueError(f"No trial_results found in {report_path}")

    instance = load_instance(instances_dir, args.instance)
    classical_optimum = float(payload.get("classical_optimum", {}).get("value", 0.0))

    levels = parse_noise_levels(args.noise_levels)
    rng = random.Random(args.seed)
    records: List[dict] = []

    for noise in levels:
        trial_means: List[float] = []
        for trial in trial_results:
            assignment = trial.get("RefinedAssignment", [])
            if not isinstance(assignment, list) or len(assignment) != len(instance.nodes):
                continue

            noisy_values: List[float] = []
            for _ in range(args.samples_per_trial):
                noisy_bits = bitflip_assignment(assignment, noise, rng)
                noisy_values.append(cut_value(noisy_bits, instance.edges))
            trial_means.append(sum(noisy_values) / len(noisy_values))

        mean, std, ci95 = compute_stats(trial_means)
        records.append(
            {
                "noise": noise,
                "samples_per_trial": args.samples_per_trial,
                "trial_count": len(trial_means),
                "noisy_mean": mean,
                "noisy_std": std,
                "noisy_ci95": ci95,
                "mean_optimality_gap": max(0.0, classical_optimum - mean),
            }
        )

    output = {
        "problem_id": "05_qaoa_maxcut",
        "instance_id": args.instance,
        "depth": args.depth,
        "source_quantum_report": report_path.name,
        "noise_model": {
            "type": "independent_bit_flip",
            "description": "Each bit in each trial best assignment is flipped independently with probability p.",
        },
        "classical_optimum": classical_optimum,
        "seed": args.seed,
        "samples_per_trial": args.samples_per_trial,
        "records": records,
    }

    json_path = estimates_dir / f"noise_sweep_{args.instance}_d{args.depth}.json"
    md_path = estimates_dir / f"noise_sweep_{args.instance}_d{args.depth}.md"
    json_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    write_markdown(args.instance, args.depth, records, classical_optimum, report_path.name, md_path)
    plot_path = plot_noise_curve(args.instance, args.depth, records, plots_dir)

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Saved {plot_path}")


if __name__ == "__main__":
    main()
