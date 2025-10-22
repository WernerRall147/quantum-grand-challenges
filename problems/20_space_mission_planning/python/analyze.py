"""Visualization for mission planning baseline outputs."""

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


def plot_delta_v(results: List[Dict[str, object]], output_dir: Path) -> None:
    labels = [entry.get("name", "instance") for entry in results]
    base = [entry.get("base_delta_v_kms", 0.0) for entry in results]
    adjusted = [entry.get("adjusted_delta_v_kms", 0.0) for entry in results]
    x = range(len(labels))
    plt.figure(figsize=(9, 4.5))
    plt.bar(x, base, width=0.4, label="Base", color="#5a9")
    plt.bar([i + 0.4 for i in x], adjusted, width=0.4, label="Adjusted", color="#1f77b4")
    plt.xticks([i + 0.2 for i in x], labels, rotation=25, ha="right")
    plt.ylabel("Delta-v (km/s)")
    plt.title("Mission delta-v budgets")
    plt.legend()
    plt.tight_layout()
    output_path = output_dir / "delta_v_budgets.png"
    plt.savefig(output_path)
    plt.close()


def plot_schedule_slack(results: List[Dict[str, object]], output_dir: Path) -> None:
    slack = [entry.get("duration_slack_days", 0.0) for entry in results]
    scores = [entry.get("mission_score", 0.0) for entry in results]
    plt.figure(figsize=(8, 4.5))
    plt.scatter(slack, scores, c=scores, cmap="cividis", s=80, edgecolors="black")
    plt.xlabel("Duration slack (days)")
    plt.ylabel("Mission score")
    plt.title("Mission score versus slack")
    plt.tight_layout()
    output_path = output_dir / "mission_score_scatter.png"
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

    plot_delta_v(results, plots_dir)
    plot_schedule_slack(results, plots_dir)

    try:
        print(f"Mission planning plots saved to {plots_dir.relative_to(Path.cwd())}")
    except ValueError:
        print(f"Mission planning plots saved to {plots_dir}")


if __name__ == "__main__":
    main()
