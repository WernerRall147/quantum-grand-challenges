"""Visualization helpers for the quantum ML classical baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    results = list(payload.get("results", []))
    results.sort(key=lambda entry: entry["features"])
    return results


def plot_accuracy(results: List[dict], plots_dir: Path) -> None:
    labels = [entry["instance_id"] for entry in results]
    train_acc = np.array([entry["train_accuracy"] for entry in results])
    test_acc = np.array([entry["test_accuracy"] for entry in results])

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(8, 4))
    plt.bar(x - width / 2, train_acc, width, label="Train", color="#4F81BD")
    plt.bar(x + width / 2, test_acc, width, label="Test", color="#C0504D")
    plt.ylim(0.0, 1.05)
    plt.xticks(x, labels)
    plt.ylabel("Accuracy")
    plt.title("Kernel ridge accuracy per dataset")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.legend()

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "accuracy_comparison.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_alignment(results: List[dict], plots_dir: Path) -> None:
    features = np.array([entry["features"] for entry in results], dtype=float)
    alignment = np.array([entry["kernel_alignment"] for entry in results], dtype=float)
    overlaps = np.array([entry["expected_overlap"] for entry in results], dtype=float)

    plt.figure(figsize=(7, 4))
    scatter = plt.scatter(features, alignment, c=overlaps, cmap="viridis", s=80)
    plt.colorbar(scatter, label="Mean overlap")
    for entry in results:
        plt.annotate(entry["instance_id"], (entry["features"], entry["kernel_alignment"]), textcoords="offset points", xytext=(6, 4), fontsize=8)

    plt.xlabel("Feature dimension")
    plt.ylabel("Kernel alignment")
    plt.title("Alignment vs. feature dimension")
    plt.grid(linestyle="--", alpha=0.35)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "alignment_vs_features.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_bandwidth(results: List[dict], plots_dir: Path) -> None:
    bandwidths = np.array([entry["kernel_bandwidth"] for entry in results])
    accuracy = np.array([entry["test_accuracy"] for entry in results])

    plt.figure(figsize=(7, 4))
    plt.plot(bandwidths, accuracy, marker="o", color="#9BBB59")
    for entry in results:
        plt.annotate(entry["instance_id"], (entry["kernel_bandwidth"], entry["test_accuracy"]), textcoords="offset points", xytext=(5, 5), fontsize=8)

    plt.xlabel("Kernel bandwidth")
    plt.ylabel("Test accuracy")
    plt.title("Bandwidth sensitivity")
    plt.grid(linestyle="--", alpha=0.35)

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "bandwidth_vs_accuracy.png"
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
    plot_accuracy(results, plots_dir)
    plot_alignment(results, plots_dir)
    plot_bandwidth(results, plots_dir)


if __name__ == "__main__":
    main()
