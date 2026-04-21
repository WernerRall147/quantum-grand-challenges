"""Visual reports for classical vs. quantum query complexity in database search."""

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


def plot_query_complexity(results: List[dict], output_dir: Path) -> None:
    dataset_sizes = [entry["dataset_size"] for entry in results]
    classical = [entry["metrics"]["classical_queries"] for entry in results]
    quantum = [entry["metrics"]["quantum_rounds"] for entry in results]

    indices = np.arange(len(results))
    width = 0.35

    plt.figure(figsize=(8, 4.5))
    plt.bar(indices - width / 2, classical, width, label="Classical", color="#2563eb")
    plt.bar(indices + width / 2, quantum, width, label="Quantum", color="#10b981")
    plt.yscale("log")
    plt.xticks(indices, [entry["name"] for entry in results], rotation=20, ha="right")
    plt.ylabel("Queries (log scale)")
    plt.title("Query Complexity Comparison")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "query_complexity.png"
    plt.savefig(output_path)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.plot(dataset_sizes, classical, marker="o", label="Classical")
    plt.plot(dataset_sizes, quantum, marker="s", label="Quantum")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Dataset size (N)")
    plt.ylabel("Queries")
    plt.title("Scaling of Query Complexity")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "query_scaling.png"
    plt.savefig(output_path)
    plt.close()


def plot_speedup(results: List[dict], output_dir: Path) -> None:
    plt.figure(figsize=(8, 4.5))
    plt.bar(
        [entry["name"] for entry in results],
        [entry["metrics"]["speedup_factor"] for entry in results],
        color="#f97316",
    )
    plt.ylabel("Classical / Quantum query ratio")
    plt.title("Estimated Speedup Factor")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    output_path = output_dir / "speedup_factor.png"
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

    plot_query_complexity(results, plots_dir)
    plot_speedup(results, plots_dir)

    try:
        rel_plots = plots_dir.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_plots = plots_dir

    print(f"📈 Database search plots saved to {rel_plots}")


if __name__ == "__main__":
    main()
