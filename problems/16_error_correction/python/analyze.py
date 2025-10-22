"""Visualization for repetition-code logical error analysis."""

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


def plot_logical_curves(results: List[dict], output_dir: Path) -> None:
    plt.figure(figsize=(8, 4.5))
    for entry in results:
        physical = [point["physical_error"] for point in entry["points"]]
        logical = [point["logical_error"] for point in entry["points"]]
        plt.plot(physical, logical, marker="o", label=f"{entry['name']} (d={entry['code_distance']})")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Physical error rate")
    plt.ylabel("Logical error rate")
    plt.title("Repetition Code Logical Error Curves")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "logical_vs_physical.png"
    plt.savefig(output_path)
    plt.close()


def plot_suppression(results: List[dict], output_dir: Path) -> None:
    plt.figure(figsize=(8, 4.5))
    for entry in results:
        physical = [point["physical_error"] for point in entry["points"]]
        suppression = [point["suppression"] for point in entry["points"]]
        plt.plot(physical, suppression, marker="s", label=entry["name"])
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Physical error rate")
    plt.ylabel("Suppression factor (physical/logical)")
    plt.title("Logical Error Suppression")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "suppression_factor.png"
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

    plot_logical_curves(results, plots_dir)
    plot_suppression(results, plots_dir)

    try:
        rel_plots = plots_dir.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_plots = plots_dir

    print(f"📈 QEC plots saved to {rel_plots}")


if __name__ == "__main__":
    main()
