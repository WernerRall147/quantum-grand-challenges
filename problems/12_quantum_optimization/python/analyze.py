"""Generate visualization for the weighted tardiness scheduling baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    if not estimates_path.exists():
        raise FileNotFoundError(
            f"Missing baseline results at {estimates_path}. Run classical_baseline.py first."
        )
    payload = json.loads(estimates_path.read_text())
    return payload.get("results", [])


def plot_weighted_tardiness(results: List[dict], output_dir: Path) -> None:
    labels = [entry["name"] for entry in results]
    tardiness = [entry["metrics"]["total_weighted_tardiness"] for entry in results]

    plt.figure(figsize=(8, 4.5))
    bars = plt.bar(labels, tardiness, color="#4f46e5")
    plt.title("Total Weighted Tardiness by Instance")
    plt.ylabel("Weighted Tardiness")
    plt.xticks(rotation=20, ha="right")
    for bar, value in zip(bars, tardiness):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    output_path = output_dir / "weighted_tardiness.png"
    plt.savefig(output_path)
    plt.close()


def plot_machine_utilization(results: List[dict], output_dir: Path) -> None:
    labels = [entry["name"] for entry in results]
    utilizations = [entry["metrics"]["machine_utilization"] for entry in results]
    max_machines = max(len(row) for row in utilizations)

    data = np.zeros((len(results), max_machines))
    for idx, row in enumerate(utilizations):
        data[idx, : len(row)] = row

    plt.figure(figsize=(8, 4.5))
    bottom = np.zeros(len(results))
    machine_colors = plt.cm.Blues(np.linspace(0.4, 0.9, max_machines))
    for machine_idx in range(max_machines):
        plt.bar(
            labels,
            data[:, machine_idx],
            bottom=bottom,
            color=machine_colors[machine_idx],
            label=f"Machine {machine_idx}",
        )
        bottom += data[:, machine_idx]

    plt.title("Machine Utilization Breakdown")
    plt.ylabel("Utilization")
    plt.xticks(rotation=20, ha="right")
    plt.ylim(0, min(1.05, data.sum(axis=1).max() + 0.1))
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "machine_utilization.png"
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates_path = root / "estimates" / "classical_baseline.json"
    plots_dir = root / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    results = load_results(estimates_path)
    if not results:
        raise RuntimeError("Baseline results are empty. Ensure classical_baseline.py completed successfully.")

    plot_weighted_tardiness(results, plots_dir)
    plot_machine_utilization(results, plots_dir)

    try:
        rel_plots = plots_dir.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_plots = plots_dir

    print(f"📈 Scheduling plots saved to {rel_plots}")


if __name__ == "__main__":
    main()
