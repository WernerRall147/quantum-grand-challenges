"""Visualization helpers for the high-frequency trading classical baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def load_results(estimates_path: Path) -> List[dict]:
    payload = json.loads(estimates_path.read_text())
    results = payload.get("results", [])
    results.sort(key=lambda item: item["instance_id"])
    return results


def plot_performance_bars(results: List[dict], plots_dir: Path) -> None:
    labels = [item["instance_id"] for item in results]
    sharpe = [item["sharpe_ratio"] for item in results]
    total_return = [item["total_return"] for item in results]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(9, 4))
    plt.bar(x - width / 2, sharpe, width, label="Sharpe", color="#4BACC6")
    plt.bar(x + width / 2, total_return, width, label="Total return", color="#8064A2")
    plt.xticks(x, labels)
    plt.ylabel("Value")
    plt.title("Classical baseline performance metrics")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend()

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "metrics_overview.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📈 Saved {output_path.relative_to(plots_dir.parent)}")


def plot_price_and_equity(instance: dict, plots_dir: Path) -> None:
    prices = instance.get("sampled_price_path", [])
    equity = instance.get("sampled_equity_curve", [])
    if not prices or not equity:
        return

    steps = instance.get("steps", max(len(prices), len(equity)))
    price_x = np.linspace(0, steps, num=len(prices))
    equity_x = np.linspace(0, steps, num=len(equity))

    fig, ax1 = plt.subplots(figsize=(9, 4))
    ax1.plot(price_x, prices, color="#4BACC6", label="Price path")
    ax1.set_xlabel("Step")
    ax1.set_ylabel("Simulated price", color="#4BACC6")
    ax1.tick_params(axis="y", labelcolor="#4BACC6")
    ax1.grid(linestyle="--", alpha=0.4)

    ax2 = ax1.twinx()
    ax2.plot(equity_x, equity, color="#8064A2", label="Equity curve")
    ax2.set_ylabel("Equity curve", color="#8064A2")
    ax2.tick_params(axis="y", labelcolor="#8064A2")

    fig.suptitle(f"Price & equity trajectory ({instance['instance_id']})")

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / f"trajectory_{instance['instance_id']}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
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
    plot_performance_bars(results, plots_dir)
    for instance in results:
        plot_price_and_equity(instance, plots_dir)


if __name__ == "__main__":
    main()
