"""Visualization helpers for QAOA Max-Cut classical and quantum baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    return payload.get("results", [])


def load_quantum_reports(estimates_dir: Path) -> List[dict]:
    reports: List[dict] = []
    for path in sorted(estimates_dir.glob("quantum_baseline_*_d*.json")):
        payload = json.loads(path.read_text())
        aggregate = payload.get("aggregate", {})
        refined = aggregate.get("refined_expectation", {})
        reports.append(
            {
                "instance_id": payload.get("instance_id"),
                "depth": int(payload.get("depth", 1)),
                "refined_mean": float(refined.get("mean", 0.0)),
                "refined_ci95": float(refined.get("ci95", 0.0)),
                "coarse_mean": float(aggregate.get("coarse_expectation", {}).get("mean", 0.0)),
                "trials": int(payload.get("trials", 0)),
            }
        )
    return reports


def plot_best_values(results: List[dict], plots_dir: Path) -> None:
    labels = [item["instance_id"] for item in results]
    values = [item["best_cut"] for item in results]

    plt.figure(figsize=(8, 4))
    bars = plt.bar(labels, values, color="#8064A2")
    plt.ylabel("Best cut value")
    plt.title("Max-Cut optimum across instances")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "best_cut_values.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_value_distribution(instance: dict, plots_dir: Path) -> None:
    histogram = instance.get("value_histogram", {})
    if not histogram:
        return

    values = sorted(histogram.items(), key=lambda item: float(item[0]))
    labels = [item[0] for item in values]
    counts = [item[1] for item in values]

    plt.figure(figsize=(8, 4))
    plt.bar(labels, counts, color="#4BACC6")
    plt.xlabel("Cut value")
    plt.ylabel("Number of assignments")
    plt.title(f"Cut value distribution for {instance['instance_id']}")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "value_distribution_small.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def pick_best_depth_reports(quantum_reports: List[dict]) -> List[dict]:
    # Keep one report per instance (highest depth, then highest trials) for stable comparisons.
    by_instance: Dict[str, dict] = {}
    for report in quantum_reports:
        instance_id = str(report.get("instance_id", ""))
        if not instance_id:
            continue
        current = by_instance.get(instance_id)
        if current is None:
            by_instance[instance_id] = report
            continue
        candidate_key = (int(report.get("depth", 1)), int(report.get("trials", 0)))
        current_key = (int(current.get("depth", 1)), int(current.get("trials", 0)))
        if candidate_key > current_key:
            by_instance[instance_id] = report
    return [by_instance[key] for key in sorted(by_instance.keys())]


def plot_quantum_vs_classical(results: List[dict], quantum_reports: List[dict], plots_dir: Path) -> Optional[Path]:
    if not quantum_reports:
        print("ℹ️ No quantum baseline reports found; skipping uncertainty comparison plot.")
        return None

    classical_map = {item["instance_id"]: float(item["best_cut"]) for item in results}
    selected_reports = pick_best_depth_reports(quantum_reports)

    labels: List[str] = []
    classical_values: List[float] = []
    quantum_means: List[float] = []
    quantum_ci95: List[float] = []

    for report in selected_reports:
        instance_id = str(report["instance_id"])
        if instance_id not in classical_map:
            continue
        labels.append(instance_id)
        classical_values.append(classical_map[instance_id])
        quantum_means.append(float(report["refined_mean"]))
        quantum_ci95.append(float(report["refined_ci95"]))

    if not labels:
        print("ℹ️ Quantum reports did not match classical instances; skipping uncertainty comparison plot.")
        return None

    x = np.arange(len(labels))
    width = 0.36

    plt.figure(figsize=(9, 4.8))
    plt.bar(x - width / 2, classical_values, width, label="Classical optimum", color="#1f77b4")
    plt.bar(
        x + width / 2,
        quantum_means,
        width,
        yerr=quantum_ci95,
        capsize=5,
        label="QAOA refined expectation (mean ± 95% CI)",
        color="#ff7f0e",
        error_kw={"elinewidth": 1.0, "ecolor": "#444"},
    )

    plt.xticks(x, labels)
    plt.ylabel("Cut value")
    plt.title("QAOA vs classical Max-Cut values with uncertainty bounds")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.legend()

    output_path = plots_dir / "quantum_vs_classical_uncertainty.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")
    return output_path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates_path = root / "estimates" / "classical_baseline.json"
    if not estimates_path.exists():
        raise FileNotFoundError("Run `make classical` before generating plots.")

    results = load_results(estimates_path)
    if not results:
        raise ValueError("No results available in classical_baseline.json")

    # Keep output order stable.
    results.sort(key=lambda item: item["instance_id"])
    plots_dir = root / "plots"
    plot_best_values(results, plots_dir)
    plot_value_distribution(results[0], plots_dir)
    quantum_reports = load_quantum_reports(root / "estimates")
    plot_quantum_vs_classical(results, quantum_reports, plots_dir)


if __name__ == "__main__":
    main()
