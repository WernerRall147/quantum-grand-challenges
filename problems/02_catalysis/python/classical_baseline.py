"""Classical analytical baseline for the quantum catalysis challenge.

The script loads every YAML instance in ``../instances`` and evaluates an
Arrhenius reaction rate for the supplied thermodynamic parameters. Results are
written to ``../estimates/classical_baseline.json`` for downstream analysis.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import yaml


R_GAS_CONSTANT = 8.314  # J · mol⁻¹ · K⁻¹


@dataclass(frozen=True)
class CatalysisInstance:
    instance_id: str
    reaction: str
    temperature: float
    pressure: float
    catalyst: str
    active_sites: int
    pre_exponential: float
    activation_energy: float

    @property
    def rate(self) -> float:
        return arrhenius_rate(self.pre_exponential, self.activation_energy, self.temperature)


def arrhenius_rate(pre_exponential: float, activation_energy: float, temperature: float) -> float:
    return pre_exponential * math.exp(-activation_energy / (R_GAS_CONSTANT * temperature))


def load_instances(instances_dir: Path) -> List[CatalysisInstance]:
    instances: List[CatalysisInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        instances.append(
            CatalysisInstance(
                instance_id=path.stem,
                reaction=raw["reaction"],
                temperature=float(raw["temperature"]),
                pressure=float(raw["pressure"]),
                catalyst=str(raw["catalyst"]),
                active_sites=int(raw["active_sites"]),
                pre_exponential=float(raw["pre_exponential"]),
                activation_energy=float(raw["activation_energy"]),
            )
        )
    return instances


def save_results(instances: List[CatalysisInstance], output_path: Path) -> None:
    payload = {
        "problem_id": "02_catalysis",
        "model": "arrhenius_activation_energy",
        "results": [
            {
                **asdict(instance),
                "rate": instance.rate,
            }
            for instance in instances
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2))

    try:
        rel_path = output_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_path = output_path

    print(f"✅ Classical baseline written to {rel_path}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    if not instances:
        raise RuntimeError("No catalysis instances found. Add YAML files to ../instances.")

    save_results(instances, root / "estimates" / "classical_baseline.json")


if __name__ == "__main__":
    main()
