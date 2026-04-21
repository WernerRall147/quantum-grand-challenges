"""Visualize temperature profiles and convergence diagnostics for climate diffusion baseline."""

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


def plot_final_profiles(results: List[dict], output_dir: Path) -> None:
    plt.figure(figsize=(8, 4.5))
    for entry in results:
        grid_points = entry["grid_points"]
        grid = np.linspace(0.0, 1.0, grid_points)
        profile = entry["snapshots"][-1]["profile"]
        plt.plot(grid, profile, label=entry["name"])
    plt.title("Final Temperature Anomaly Profiles")
    plt.xlabel("Normalized latitude")
    plt.ylabel("Temperature anomaly (K)")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "final_profiles.png"
    plt.savefig(output_path)
    plt.close()


def plot_mean_convergence(results: List[dict], output_dir: Path) -> None:
    plt.figure(figsize=(8, 4.5))
    for entry in results:
        convergence = entry["time_series"]["convergence"]
        if not convergence:
            continue
        dt_years = entry["time_step_hours"] / (24.0 * 365.0)
        time_axis = np.arange(1, len(convergence) + 1) * dt_years
        plt.plot(time_axis, convergence, label=entry["name"])
    plt.yscale("log")
    plt.title("Mean Anomaly Convergence")
    plt.xlabel("Simulation time (years)")
    plt.ylabel("|Δ mean anomaly|")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "mean_convergence.png"
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

    plot_final_profiles(results, plots_dir)
    plot_mean_convergence(results, plots_dir)

    try:
        rel_plots = plots_dir.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_plots = plots_dir

    print(f"📈 Climate modeling plots saved to {rel_plots}")


if __name__ == "__main__":
    main()
