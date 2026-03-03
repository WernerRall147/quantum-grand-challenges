"""Run/aggregate QAOA depth sweep evidence for a selected instance."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt


def parse_depths(raw: str) -> List[int]:
    depths = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        value = int(part)
        if value < 1:
            raise ValueError("Depth values must be >= 1")
        depths.append(value)
    if not depths:
        raise ValueError("No depths provided")
    # Keep order stable and unique.
    seen = set()
    ordered = []
    for depth in depths:
        if depth not in seen:
            seen.add(depth)
            ordered.append(depth)
    return ordered


def run_depth(instance: str, depth: int, coarse_shots: int, refined_shots: int, trials: int, problem_root: Path) -> None:
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
    print(f"[depth={depth}] {' '.join(cmd)}")
    subprocess.run(cmd, cwd=problem_root, check=True)


def load_report(estimates_dir: Path, instance: str, depth: int) -> dict:
    path = estimates_dir / f"quantum_baseline_{instance}_d{depth}.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing report for depth={depth}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    aggregate = payload.get("aggregate", {})
    refined = aggregate.get("refined_expectation", {})
    coarse = aggregate.get("coarse_expectation", {})
    return {
        "depth": depth,
        "refined_mean": float(refined.get("mean", 0.0)),
        "refined_ci95": float(refined.get("ci95", 0.0)),
        "coarse_mean": float(coarse.get("mean", 0.0)),
        "mean_optimality_gap": float(aggregate.get("mean_optimality_gap", 0.0)),
        "trials": int(payload.get("trials", 0)),
        "source": path.name,
    }


def write_markdown(instance: str, records: List[dict], out_path: Path) -> None:
    lines = [
        f"# QAOA Depth Sweep ({instance})",
        "",
        "| Depth | Refined Mean +/- 95% CI | Coarse Mean | Mean Optimality Gap | Trials | Source |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in records:
        lines.append(
            f"| {row['depth']} | {row['refined_mean']:.4f} +/- {row['refined_ci95']:.4f} "
            f"| {row['coarse_mean']:.4f} | {row['mean_optimality_gap']:.4f} | {row['trials']} | `{row['source']}` |"
        )
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def plot_depth_curve(instance: str, records: List[dict], plots_dir: Path) -> Path:
    depths = [row["depth"] for row in records]
    means = [row["refined_mean"] for row in records]
    ci95 = [row["refined_ci95"] for row in records]

    plt.figure(figsize=(8, 4.5))
    plt.errorbar(depths, means, yerr=ci95, fmt="o-", capsize=5, color="#1f77b4", ecolor="#444")
    plt.title(f"QAOA depth sweep ({instance})")
    plt.xlabel("Depth")
    plt.ylabel("Refined expectation (mean +/- 95% CI)")
    plt.grid(True, linestyle="--", alpha=0.35)

    plots_dir.mkdir(parents=True, exist_ok=True)
    out_path = plots_dir / f"qaoa_depth_sweep_{instance}.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run/aggregate QAOA depth sweep evidence.")
    parser.add_argument("--instance", default="small", help="Problem instance id (small/medium/large).")
    parser.add_argument("--depths", default="1,2,3", help="Comma-separated depth values.")
    parser.add_argument("--coarse-shots", type=int, default=24)
    parser.add_argument("--refined-shots", type=int, default=96)
    parser.add_argument("--trials", type=int, default=6)
    parser.add_argument(
        "--run",
        action="store_true",
        default=True,
        help="Execute dotnet runs before aggregating reports (default: enabled).",
    )
    parser.add_argument(
        "--no-run",
        dest="run",
        action="store_false",
        help="Skip execution and aggregate from existing quantum_baseline files.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    estimates_dir = root / "estimates"
    plots_dir = root / "plots"

    depths = parse_depths(args.depths)

    if args.run:
        for depth in depths:
            run_depth(args.instance, depth, args.coarse_shots, args.refined_shots, args.trials, root)

    records = [load_report(estimates_dir, args.instance, depth) for depth in depths]

    payload = {
        "problem_id": "05_qaoa_maxcut",
        "instance_id": args.instance,
        "depths": depths,
        "coarse_shots": args.coarse_shots,
        "refined_shots": args.refined_shots,
        "trials": args.trials,
        "records": records,
    }

    json_path = estimates_dir / f"depth_sweep_{args.instance}.json"
    md_path = estimates_dir / f"depth_sweep_{args.instance}.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(args.instance, records, md_path)
    plot_path = plot_depth_curve(args.instance, records, plots_dir)

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Saved {plot_path}")


if __name__ == "__main__":
    main()
