"""Visualization routines for the pionless EFT classical baseline."""

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


def flatten_channels(results: List[Dict[str, object]]) -> List[Dict[str, object]]:
    flattened: List[Dict[str, object]] = []
    for entry in results:
        for channel in entry.get("channels", []):
            flattened.append(
                {
                    "label": f"{entry['instance_id']}:{channel['name']}",
                    "binding_energy_mev": float(channel.get("binding_energy_mev", 0.0)),
                    "scattering_length_fm": float(channel.get("scattering_length_fm", 0.0)),
                    "effective_range_fm": float(channel.get("effective_range_fm", 0.0)),
                    "cutoff_mev": float(entry.get("cutoff_mev", 0.0)),
                }
            )
    return flattened


def plot_binding_energies(flattened: List[Dict[str, object]], output_dir: Path) -> None:
    labels = [item["label"] for item in flattened]
    values = [item["binding_energy_mev"] for item in flattened]
    plt.figure(figsize=(10, 4.5))
    bars = plt.bar(labels, values, color="#1f77b4")
    plt.axhline(0.0, color="#444", linewidth=1.0)
    plt.ylabel("Ground-state energy (MeV)")
    plt.title("Pionless EFT binding energies by channel")
    plt.xticks(rotation=45, ha="right")
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2.0, value, f"{value:.2f}", ha="center", va="bottom")
    plt.tight_layout()
    output_path = output_dir / "binding_energies.png"
    plt.savefig(output_path)
    plt.close()


def plot_scattering_trends(flattened: List[Dict[str, object]], output_dir: Path) -> None:
    cutoffs = np.array([item["cutoff_mev"] for item in flattened], dtype=float)
    scattering = np.array([item["scattering_length_fm"] for item in flattened], dtype=float)
    plt.figure(figsize=(8, 4.5))
    plt.scatter(cutoffs, scattering, c=cutoffs, cmap="viridis", s=80, edgecolor="black")
    plt.xlabel("Cutoff (MeV)")
    plt.ylabel("Scattering length (fm)")
    plt.title("Scattering length sensitivity to cutoff")
    plt.colorbar(label="Cutoff (MeV)")
    plt.tight_layout()
    output_path = output_dir / "scattering_length_vs_cutoff.png"
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

    flattened = flatten_channels(results)
    if not flattened:
        raise RuntimeError("No channel data found in baseline results.")

    plot_binding_energies(flattened, plots_dir)
    plot_scattering_trends(flattened, plots_dir)

    try:
        print(f"📈 EFT plots saved to {plots_dir.relative_to(Path.cwd())}")
    except ValueError:
        print(f"📈 EFT plots saved to {plots_dir}")


if __name__ == "__main__":
    main()
