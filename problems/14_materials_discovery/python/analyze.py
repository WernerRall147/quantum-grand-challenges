"""Visualize voltage-stability tradeoffs for materials discovery baseline."""

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


def scatter_voltage_stability(results: List[dict], output_dir: Path) -> None:
    plt.figure(figsize=(8, 4.5))
    for entry in results:
        voltages = [res["metrics"]["voltage"] for res in entry["results"]]
        stability = [res["metrics"]["stability"] for res in entry["results"]]
        plt.scatter(voltages, stability, alpha=0.6, label=entry["name"])
    plt.title("Voltage vs. Stability Tradeoff")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Stability score")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "voltage_vs_stability.png"
    plt.savefig(output_path)
    plt.close()


def plot_pareto_fronts(results: List[dict], output_dir: Path) -> None:
    plt.figure(figsize=(8, 4.5))
    for entry in results:
        front = entry.get("pareto_front", [])
        if not front:
            continue
        voltages = [res["metrics"]["voltage"] for res in front]
        stability = [res["metrics"]["stability"] for res in front]
        order = np.argsort(voltages)
        plt.plot(np.array(voltages)[order], np.array(stability)[order], marker="o", label=entry["name"])
    plt.title("Pareto Front: Stability vs. Voltage")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Stability score")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "pareto_front.png"
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

    scatter_voltage_stability(results, plots_dir)
    plot_pareto_fronts(results, plots_dir)

    try:
        rel_plots = plots_dir.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_plots = plots_dir

    print(f"📈 Materials discovery plots saved to {rel_plots}")


if __name__ == "__main__":
    main()
