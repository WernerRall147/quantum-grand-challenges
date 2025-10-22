"""Lattice gauge theory baseline for coarse QCD plaquette observables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import log, prod, sqrt
from pathlib import Path
from typing import Dict, List

import numpy as np
import yaml

SU3_FACTOR = 8.0  # Rough scaling factor for SU(3) colour degrees of freedom.
MIN_PLAQUETTE = 0.05
MAX_PLAQUETTE = 0.99


@dataclass(frozen=True)
class LatticeInstance:
    instance_id: str
    name: str
    description: str
    lattice_shape: List[int]
    lattice_spacing: float
    beta: float
    anisotropy: float
    sea_quark_mass: float


def load_instances(instances_dir: Path) -> List[LatticeInstance]:
    instances: List[LatticeInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        shape = [int(value) for value in raw.get("lattice_shape", [4, 4, 4, 4])]
        instances.append(
            LatticeInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                lattice_shape=shape,
                lattice_spacing=float(raw.get("lattice_spacing_fm", 0.2)),
                beta=float(raw.get("beta", 5.5)),
                anisotropy=float(raw.get("anisotropy", 1.0)),
                sea_quark_mass=float(raw.get("sea_quark_mass_mev", 30.0)),
            )
        )
    return instances


def effective_plaquette(beta: float, spacing: float, anisotropy: float) -> float:
    base = 1.0 - 0.5 / max(beta, 1e-6)
    spacing_penalty = 0.12 * spacing
    anisotropy_term = 0.04 * log(1.0 + anisotropy)
    plaquette = base - spacing_penalty - anisotropy_term
    plaquette = max(MIN_PLAQUETTE, min(plaquette, MAX_PLAQUETTE))
    return plaquette


def string_tension(plaquette: float, spacing: float) -> float:
    gap = max(1e-6, 1.0 - plaquette)
    return gap / max(spacing ** 2, 1e-6)


def rough_glueball_mass(sigma: float) -> float:
    return sqrt(max(sigma, 1e-6)) * 4.5


def evaluate_instance(instance: LatticeInstance) -> Dict[str, object]:
    volume = prod(instance.lattice_shape)
    plaquette = effective_plaquette(instance.beta, instance.lattice_spacing, instance.anisotropy)
    sigma = string_tension(plaquette, instance.lattice_spacing)
    glueball = rough_glueball_mass(sigma)
    energy_density = (1.0 - plaquette) * SU3_FACTOR / max(instance.lattice_spacing, 1e-6)

    covariance = float(np.clip(0.02 / max(instance.beta, 1e-6), 0.0, 0.2))

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "lattice_shape": instance.lattice_shape,
        "lattice_spacing_fm": instance.lattice_spacing,
        "beta": instance.beta,
        "anisotropy": instance.anisotropy,
        "sea_quark_mass_mev": instance.sea_quark_mass,
        "volume": volume,
        "plaquette": plaquette,
        "string_tension": sigma,
        "scalar_glueball_mass_mev": glueball,
        "energy_density": energy_density,
        "plaquette_variance": covariance,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No QCD instances found. Add YAML files to ../instances.")

    results = [evaluate_instance(instance) for instance in instances]
    payload = {
        "problem_id": "19_quantum_chromodynamics",
        "model": "coarse_lattice_plaquette",
        "results": results,
    }

    output_path = estimates_dir / "classical_baseline.json"
    output_path.write_text(json.dumps(payload, indent=2))

    try:
        print(f"QCD baseline written to {output_path.relative_to(Path.cwd())}")
    except ValueError:
        print(f"QCD baseline written to {output_path}")


if __name__ == "__main__":
    main()
