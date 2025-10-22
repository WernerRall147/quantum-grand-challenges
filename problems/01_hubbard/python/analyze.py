"""Generate simple diagnostics for the two-site Hubbard benchmark."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt


def load_baseline(path: Path) -> List[Dict[str, float]]:
    payload = json.loads(path.read_text())
    return payload.get("grid", [])


def plot_gaps(points: List[Dict[str, float]], output_path: Path) -> None:
    if not points:
        print("⚠️ No data points available for analysis")
        return

    grouped: Dict[float, List[Dict[str, float]]] = {}
    for point in points:
        grouped.setdefault(point["interaction"], []).append(point)

    interactions = sorted(grouped.keys())
    charge = []
    spin = []
    for u in interactions:
        pts = grouped[u]
        charge.append(sum(p["charge_gap"] for p in pts) / len(pts))
        spin.append(sum(p["spin_gap"] for p in pts) / len(pts))

    plt.figure(figsize=(6, 4))
    plt.plot(interactions, charge, marker="o", label="Charge gap Δc")
    plt.plot(interactions, spin, marker="s", label="Spin gap Δs")
    plt.xlabel("Interaction strength U (t units)")
    plt.ylabel("Gap energy (t units)")
    plt.title("Two-site Hubbard gaps")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    try:
        rel_path = output_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_path = output_path

    print(f"📊 Saved gap plot to {rel_path}")


if __name__ == "__main__":
    problem_root = Path(__file__).resolve().parents[1]
    baseline_path = problem_root / "estimates" / "classical_baseline.json"

    if not baseline_path.exists():
        raise FileNotFoundError(
            "Run classical_baseline.py first to generate estimates/classical_baseline.json"
        )

    data = load_baseline(baseline_path)
    plot_gaps(data, problem_root / "plots" / "gaps.png")
