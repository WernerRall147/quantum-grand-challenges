"""Diagnostic plots for the quantum linear solver classical baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    return payload.get("results", [])


def plot_condition_numbers(results: List[dict], plots_dir: Path) -> None:
    labels = [item["instance_id"] for item in results]
    condition_numbers = [item["condition_number_2"] for item in results]

    x_pos = np.arange(len(labels))
    plt.figure(figsize=(8, 4))
    bars = plt.bar(x_pos, condition_numbers, color="#4F81BD")
    plt.xticks(x_pos, labels)
    plt.ylabel("Condition number (2-norm)")
    plt.title("Condition numbers across linear system instances")
    plt.yscale("log")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    for bar, value in zip(bars, condition_numbers):
        plt.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "condition_numbers.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_residuals(results: List[dict], plots_dir: Path) -> None:
    labels = [item["instance_id"] for item in results]
    residuals = [item["residual_norm"] for item in results]
    target = [item["target_precision"] for item in results]

    plt.figure(figsize=(8, 4))
    plt.scatter(target, residuals, s=80, color="#9BBB59")
    plt.plot([min(target), max(target)], [min(target), max(target)], linestyle="--", color="gray", label="Residual = target precision")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Target precision")
    plt.ylabel("Residual norm")
    plt.title("Residual norms versus requested precision")
    for x, y, label in zip(target, residuals, labels):
        plt.annotate(label, (x, y), textcoords="offset points", xytext=(5, 5), fontsize=8)
    plt.legend(loc="best")

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "residual_vs_precision.png"
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
        raise ValueError("No results found in classical_baseline.json")

    # Sort results to keep figures consistent across runs
    results.sort(key=lambda item: item["dimension"])

    plots_dir = root / "plots"
    plot_condition_numbers(results, plots_dir)
    plot_residuals(results, plots_dir)


if __name__ == "__main__":
    main()
