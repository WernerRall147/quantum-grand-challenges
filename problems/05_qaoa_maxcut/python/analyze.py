"""Visualization helpers for the QAOA Max-Cut classical baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    return payload.get("results", [])


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


if __name__ == "__main__":
    main()
