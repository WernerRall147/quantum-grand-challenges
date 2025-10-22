"""Visualization helpers for the drug discovery classical baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    results = payload.get("results", [])
    results.sort(key=lambda item: item["instance_id"])  # stable ordering
    return results


def plot_energy_breakdown(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    lj = np.array([entry["lj_energy"] for entry in results])
    coulomb = np.array([entry["coulomb_energy"] for entry in results])

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(9, 4))
    plt.bar(x - width / 2, lj, width, label="Lennard-Jones", color="#4BACC6")
    plt.bar(x + width / 2, coulomb, width, label="Coulomb", color="#8064A2")
    plt.xticks(x, labels)
    plt.ylabel("Energy (kcal/mol)")
    plt.title("Interaction energy components by instance")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend()

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "energy_breakdown.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_total_energy(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    totals = [entry["total_energy"] for entry in results]

    plt.figure(figsize=(7, 4))
    bars = plt.bar(labels, totals, color="#9BBB59")
    plt.ylabel("Total energy (kcal/mol)")
    plt.title("Total interaction energy ranking")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    for bar, value in zip(bars, totals):
        plt.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "total_energy_ranking.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_contacts_vs_energy(results: List[dict], plots_dir: Path) -> None:
    contacts = np.array([entry["contact_pairs"] for entry in results], dtype=float)
    totals = np.array([entry["total_energy"] for entry in results], dtype=float)

    plt.figure(figsize=(7, 4))
    plt.scatter(contacts, totals, color="#C0504D", s=60)
    for entry in results:
        plt.annotate(entry["instance_id"], (entry["contact_pairs"], entry["total_energy"]), textcoords="offset points", xytext=(5, 5), fontsize=8)

    plt.xlabel("Contact pairs (< cutoff)")
    plt.ylabel("Total energy (kcal/mol)")
    plt.title("Contact count vs. interaction energy")
    plt.grid(linestyle="--", alpha=0.4)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "contacts_vs_energy.png"
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
    plot_energy_breakdown(results, plots_dir)
    plot_total_energy(results, plots_dir)
    plot_contacts_vs_energy(results, plots_dir)


if __name__ == "__main__":
    main()
