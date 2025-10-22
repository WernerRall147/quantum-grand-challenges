"""Visualization helpers for the factorization classical baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    results = list(payload.get("results", []))
    results.sort(key=lambda entry: entry["bit_length"])
    return results


def plot_iterations(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    iterations = np.array([entry["iterations"] for entry in results], dtype=float)

    plt.figure(figsize=(7, 4))
    bars = plt.bar(labels, iterations, color="#4F81BD")
    plt.ylabel("Iterations")
    plt.title("Pollard Rho iterations per instance")
    plt.grid(axis="y", linestyle="--", alpha=0.35)

    for bar, value in zip(bars, iterations):
        plt.text(bar.get_x() + bar.get_width() / 2, value, f"{int(value)}", ha="center", va="bottom", fontsize=8)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "iterations.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_runtime(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    runtime = np.array([entry["runtime_ms"] for entry in results], dtype=float)

    plt.figure(figsize=(7, 4))
    plt.plot(labels, runtime, marker="o", color="#C0504D")
    plt.ylabel("Runtime (ms)")
    plt.title("Classical factoring runtime")
    plt.grid(linestyle="--", alpha=0.35)

    for x, y in zip(labels, runtime):
        plt.text(x, y, f"{y:.2f}", ha="center", va="bottom", fontsize=8)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "runtime.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_bitlength_vs_iterations(results: List[dict], plots_dir: Path) -> None:
    bits = np.array([entry["bit_length"] for entry in results], dtype=float)
    iterations = np.array([entry["iterations"] for entry in results], dtype=float)

    plt.figure(figsize=(7, 4))
    plt.scatter(bits, iterations, color="#9BBB59", s=60)
    for entry in results:
        plt.annotate(entry["instance_id"], (entry["bit_length"], entry["iterations"]), textcoords="offset points", xytext=(5, 5), fontsize=8)

    plt.xlabel("Bit length of modulus")
    plt.ylabel("Iterations")
    plt.title("Scaling trend: iterations vs. bit length")
    plt.grid(linestyle="--", alpha=0.35)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "bitlength_vs_iterations.png"
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
    plot_iterations(results, plots_dir)
    plot_runtime(results, plots_dir)
    plot_bitlength_vs_iterations(results, plots_dir)


if __name__ == "__main__":
    main()
