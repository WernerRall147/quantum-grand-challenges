"""Generate diagnostics for the quantum catalysis classical baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates_path = root / "estimates" / "classical_baseline.json"
    if not estimates_path.exists():
        raise FileNotFoundError("Run `make classical` before attempting analysis.")

    payload = json.loads(estimates_path.read_text())
    results: List[dict] = payload["results"]

    # Sort by temperature to make the trend line readable
    results.sort(key=lambda item: item["temperature"])

    temperatures = [item["temperature"] for item in results]
    rates = [item["rate"] for item in results]
    labels = [item["catalyst"] for item in results]

    plt.figure(figsize=(8, 5))
    plt.plot(temperatures, rates, marker="o")
    for temperature, rate, label in zip(temperatures, rates, labels):
        plt.annotate(label, (temperature, rate), textcoords="offset points", xytext=(0, 8), ha="center")
    plt.xlabel("Temperature (K)")
    plt.ylabel("Reaction rate (s$^{-1}$)")
    plt.title("Arrhenius rates across catalysis instances")
    plt.grid(True, linestyle="--", alpha=0.4)

    plots_dir = root / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / "rate_vs_temperature.png"
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"📈 Plot saved to {output_path.relative_to(root)}")


if __name__ == "__main__":
    main()
