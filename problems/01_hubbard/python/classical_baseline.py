"""Classical baseline for the two-site Hubbard model at half filling.

The script computes analytical singlet, excited singlet, and triplet energies
for a grid of hopping (t) and on-site interaction (U) strengths and stores the
results in ``../estimates/classical_baseline.json`` for downstream analysis.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class HubbardPoint:
    hopping: float
    interaction: float
    ground_state_energy: float
    upper_singlet_energy: float
    triplet_energy: float

    @property
    def charge_gap(self) -> float:
        return self.upper_singlet_energy - self.ground_state_energy

    @property
    def spin_gap(self) -> float:
        return self.triplet_energy - self.ground_state_energy


def singlet_energy(t: float, u: float) -> float:
    discriminant = math.sqrt(u * u + 16.0 * t * t)
    return 0.5 * (u - discriminant)


def upper_singlet_energy(t: float, u: float) -> float:
    discriminant = math.sqrt(u * u + 16.0 * t * t)
    return 0.5 * (u + discriminant)


def triplet_energy(_: float, __: float) -> float:
    return 0.0


def generate_grid(hoppings: Iterable[float], interactions: Iterable[float]) -> List[HubbardPoint]:
    grid: List[HubbardPoint] = []
    for t in hoppings:
        for u in interactions:
            gs = singlet_energy(t, u)
            us = upper_singlet_energy(t, u)
            tr = triplet_energy(t, u)
            grid.append(
                HubbardPoint(
                    hopping=t,
                    interaction=u,
                    ground_state_energy=gs,
                    upper_singlet_energy=us,
                    triplet_energy=tr,
                )
            )
    return grid


def save_results(points: Iterable[HubbardPoint], output_path: Path) -> None:
    payload = {
        "problem_id": "01_hubbard",
        "model": "two_site_half_filled",
        "grid": [
            {
                **asdict(point),
                "charge_gap": point.charge_gap,
                "spin_gap": point.spin_gap,
            }
            for point in points
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2))

    try:
        rel_path = output_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_path = output_path

    print(f"✅ Classical baseline written to {rel_path}")


if __name__ == "__main__":
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description="Classical baseline for two-site Hubbard model")
    parser.add_argument(
        "--instance-file",
        type=str,
        default=None,
        help="Path to a YAML instance file (e.g. instances/small.yaml)",
    )
    args = parser.parse_args()

    instance_dir = Path(__file__).resolve().parents[1] / "instances"

    if args.instance_file:
        instance_path = Path(args.instance_file)
        if not instance_path.is_absolute() and not instance_path.exists():
            instance_path = instance_dir / instance_path.name
        with open(instance_path) as f:
            inst = yaml.safe_load(f)
        hoppings = inst["hopping"]
        interactions = inst["interaction"]
    else:
        # Default: union of all instance files for backwards compatibility
        hoppings_set: set[float] = set()
        interactions_set: set[float] = set()
        for yaml_file in sorted(instance_dir.glob("*.yaml")):
            with open(yaml_file) as f:
                inst = yaml.safe_load(f)
            hoppings_set.update(inst.get("hopping", []))
            interactions_set.update(inst.get("interaction", []))
        hoppings = sorted(hoppings_set) if hoppings_set else [0.5, 1.0]
        interactions = sorted(interactions_set) if interactions_set else [0.0, 2.0, 4.0, 8.0]

    data = generate_grid(hoppings, interactions)
    save_results(data, Path(__file__).resolve().parents[1] / "estimates" / "classical_baseline.json")