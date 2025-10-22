"""Visualization for photovoltaic efficiency baseline results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[Dict[str, object]]:
    if not estimates_path.exists():
        raise FileNotFoundError(
            f"Missing baseline results at {estimates_path}. Run classical_baseline.py first."
        )
    payload = json.loads(estimates_path.read_text())
    return payload.get("results", [])


def bar_efficiency(results: List[Dict[str, object]], output_dir: Path) -> None:
    labels = [entry["name"] for entry in results]
    efficiency = [entry.get("efficiency", 0.0) * 100.0 for entry in results]
    plt.figure(figsize=(9, 4.5))
    bars = plt.bar(labels, efficiency, color="#ffb703")
    plt.ylabel("Efficiency (%)")
    plt.title("Estimated photovoltaic efficiency by instance")
    plt.xticks(rotation=30, ha="right")
    for bar, value in zip(bars, efficiency):
        plt.text(bar.get_x() + bar.get_width() / 2.0, value, f"{value:.1f}", ha="center", va="bottom")
    plt.tight_layout()
    output_path = output_dir / "efficiency_bar.png"
    plt.savefig(output_path)
    plt.close()


def scatter_voltage_current(results: List[Dict[str, object]], output_dir: Path) -> None:
    voltages = []
    currents = []
    bands = []
    for entry in results:
        for subcell in entry.get("subcells", []):
            voltages.append(subcell.get("voc_v", 0.0))
            currents.append(subcell.get("jsc_ma_cm2", 0.0))
            bands.append(subcell.get("bandgap_ev", 0.0))
    if not voltages:
        return
    plt.figure(figsize=(8, 4.5))
    scatter = plt.scatter(voltages, currents, c=bands, cmap="plasma", s=80, edgecolors="black")
    plt.xlabel("Open-circuit voltage (V)")
    plt.ylabel("Short-circuit current (mA/cm^2)")
    plt.title("Subcell current-voltage landscape")
    cbar = plt.colorbar(scatter)
    cbar.set_label("Bandgap (eV)")
    plt.tight_layout()
    output_path = output_dir / "voc_vs_jsc.png"
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

    bar_efficiency(results, plots_dir)
    scatter_voltage_current(results, plots_dir)

    try:
        print(f"Photovoltaic plots saved to {plots_dir.relative_to(Path.cwd())}")
    except ValueError:
        print(f"Photovoltaic plots saved to {plots_dir}")


if __name__ == "__main__":
    main()
