"""Visualization utilities for the coarse QCD lattice baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt


def load_results(estimates_path: Path) -> List[Dict[str, object]]:
    if not estimates_path.exists():
        raise FileNotFoundError(
            f"Missing baseline results at {estimates_path}. Run classical_baseline.py first."
        )
    payload = json.loads(estimates_path.read_text())
    return payload.get("results", [])


def plot_plaquette_vs_spacing(results: List[Dict[str, object]], output_dir: Path) -> None:
    spacings = [entry.get("lattice_spacing_fm", 0.0) for entry in results]
    plaquettes = [entry.get("plaquette", 0.0) for entry in results]
    labels = [entry.get("name", "instance") for entry in results]
    plt.figure(figsize=(8, 4.5))
    plt.plot(spacings, plaquettes, marker="o")
    for x, y, label in zip(spacings, plaquettes, labels):
        plt.text(x, y, label, fontsize=8, ha="center", va="bottom")
    plt.xlabel("Lattice spacing (fm)")
    plt.ylabel("Average plaquette")
    plt.title("Plaquette expectation versus lattice spacing")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.tight_layout()
    output_path = output_dir / "plaquette_vs_spacing.png"
    plt.savefig(output_path)
    plt.close()


def plot_string_tension(results: List[Dict[str, object]], output_dir: Path) -> None:
    betas = [entry.get("beta", 0.0) for entry in results]
    tensions = [entry.get("string_tension", 0.0) for entry in results]
    plt.figure(figsize=(8, 4.5))
    plt.scatter(betas, tensions, c=betas, cmap="viridis", s=90, edgecolor="black")
    plt.xlabel("Gauge coupling beta")
    plt.ylabel("String tension (fm^-2)")
    plt.title("String tension as a function of beta")
    plt.tight_layout()
    output_path = output_dir / "string_tension_vs_beta.png"
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

    plot_plaquette_vs_spacing(results, plots_dir)
    plot_string_tension(results, plots_dir)

    try:
        print(f"QCD plots saved to {plots_dir.relative_to(Path.cwd())}")
    except ValueError:
        print(f"QCD plots saved to {plots_dir}")


if __name__ == "__main__":
    main()
