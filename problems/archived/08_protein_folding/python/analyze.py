"""Visualization utilities for the protein folding classical baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    results = list(payload.get("results", []))
    results.sort(key=lambda entry: entry["instance_id"])
    return results


def plot_energy_components(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    hydrophobic = np.array([entry["hydrophobic_energy"] for entry in results])
    electrostatic = np.array([entry["electrostatic_energy"] for entry in results])
    hbond = np.array([entry["hydrogen_bond_bonus"] for entry in results])

    x = np.arange(len(labels))
    width = 0.6

    plt.figure(figsize=(9, 4))
    plt.bar(x, hydrophobic, width, label="Hydrophobic", color="#4F81BD")
    plt.bar(x, electrostatic, width, bottom=hydrophobic, label="Electrostatic", color="#C0504D")
    plt.bar(x, -hbond, width, bottom=hydrophobic + electrostatic, label="Hydrogen bonus", color="#9BBB59")
    plt.xticks(x, labels)
    plt.ylabel("Energy contribution (a.u.)")
    plt.title("Energy components per instance (stacked)")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend()

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "energy_components.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_total_energy(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    totals = np.array([entry["total_energy"] for entry in results])

    plt.figure(figsize=(7, 4))
    bars = plt.bar(labels, totals, color="#8064A2")
    plt.ylabel("Total energy (a.u.)")
    plt.title("Total folding energy (lower is better)")
    plt.axhline(0.0, color="#333", linewidth=0.8)
    plt.grid(axis="y", linestyle="--", alpha=0.35)

    for bar, value in zip(bars, totals):
        plt.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "total_energy.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_stability_phase_space(results: List[dict], plots_dir: Path) -> None:
    contact_order = np.array([entry["contact_order"] for entry in results])
    stability = np.array([entry["stability_index"] for entry in results])
    compactness = np.array([entry["compactness"] for entry in results])

    plt.figure(figsize=(7, 4))
    scatter = plt.scatter(contact_order, stability, c=compactness, cmap="viridis", s=70)
    plt.colorbar(scatter, label="Compactness")
    for entry in results:
        plt.annotate(entry["instance_id"], (entry["contact_order"], entry["stability_index"]), textcoords="offset points", xytext=(6, 4), fontsize=8)

    plt.xlabel("Contact order")
    plt.ylabel("Stability index (higher is better)")
    plt.title("Stability vs. contact order phase space")
    plt.grid(linestyle="--", alpha=0.4)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "stability_phase_space.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates_path = root / "estimates" / "classical_baseline.json"
    if not estimates_path.exists():
        raise FileNotFoundError("Run `python python/classical_baseline.py` before generating plots.")

    results = load_results(estimates_path)
    if not results:
        raise ValueError("No results recorded in classical_baseline.json")

    plots_dir = root / "plots"
    plot_energy_components(results, plots_dir)
    plot_total_energy(results, plots_dir)
    plot_stability_phase_space(results, plots_dir)


if __name__ == "__main__":
    main()
