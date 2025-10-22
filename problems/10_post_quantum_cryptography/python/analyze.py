"""Visualization utilities for the PQC security baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    results = list(payload.get("results", []))
    results.sort(key=lambda entry: entry["lattice_dimension"])
    return results


def plot_costs(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    classical = np.array([entry["classical_cost_bits"] for entry in results])
    quantum = np.array([entry["quantum_cost_bits"] for entry in results])

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(9, 4))
    plt.bar(x - width / 2, classical, width, label="Classical cost", color="#4F81BD")
    plt.bar(x + width / 2, quantum, width, label="Quantum cost", color="#C0504D")
    plt.xticks(x, labels)
    plt.ylabel("Cost (log2 operations)")
    plt.title("Attack cost estimates per PQC instance")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.legend()

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "attack_costs.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_margins(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    classical_margin = np.array([entry["classical_margin_bits"] for entry in results])
    quantum_margin = np.array([entry["quantum_margin_bits"] for entry in results])

    plt.figure(figsize=(9, 4))
    x = np.arange(len(labels))
    width = 0.35
    plt.bar(x - width / 2, classical_margin, width, label="Classical margin", color="#9BBB59")
    plt.bar(x + width / 2, quantum_margin, width, label="Quantum margin", color="#8064A2")
    plt.axhline(0.0, color="#333", linewidth=0.8)
    plt.xticks(x, labels)
    plt.ylabel("Margin (bits)")
    plt.title("Security margin vs. target level")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.legend()

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "security_margins.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_runtime(results: List[dict], plots_dir: Path) -> None:
    dimensions = np.array([entry["lattice_dimension"] for entry in results])
    runtime = np.array([entry["estimated_runtime_hours"] for entry in results])

    plt.figure(figsize=(7, 4))
    plt.plot(dimensions, runtime, marker="o", color="#F79646")
    for entry in results:
        plt.annotate(entry["instance_id"], (entry["lattice_dimension"], entry["estimated_runtime_hours"]), textcoords="offset points", xytext=(5, 5), fontsize=8)

    plt.xlabel("Lattice dimension")
    plt.ylabel("Estimated runtime (hours)")
    plt.title("Quantum sieving runtime estimate (1 THz oracle)")
    plt.yscale("log")
    plt.grid(linestyle="--", alpha=0.35)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "runtime_estimate.png"
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
    plot_costs(results, plots_dir)
    plot_margins(results, plots_dir)
    plot_runtime(results, plots_dir)


if __name__ == "__main__":
    main()
