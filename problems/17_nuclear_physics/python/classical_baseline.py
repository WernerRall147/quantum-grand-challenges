"""Pionless EFT contact-interaction baseline for few-nucleon toy systems."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import yaml

MASS_NUCLEON_MEV = 938.92  # Simplified nucleon mass in MeV.
CENTRIFUGAL_SCALE_FM = 2.0  # Characteristic radius for centrifugal estimate.
MOMENTUM_FLOOR = 20.0       # Prevents zero-momentum singularities.
GRID_SIZE = 12              # Momentum grid resolution for diagonalization.


@dataclass(frozen=True)
class ChannelSpec:
    name: str
    l: int
    spins: int


@dataclass(frozen=True)
class EftInstance:
    instance_id: str
    name: str
    description: str
    cutoff: float
    couplings: Dict[str, float]
    channels: List[ChannelSpec]


def load_instances(instances_dir: Path) -> List[EftInstance]:
    instances: List[EftInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        couplings: Dict[str, float] = {key: float(value) for key, value in raw.get("coupling_constants", {}).items()}
        if "c0" not in couplings:
            raise ValueError(f"Instance {path.name} must define at least a c0 coupling.")
        channels_data = raw.get("channels", [])
        if not channels_data:
            raise ValueError(f"Instance {path.name} must define at least one channel entry.")
        channels = [
            ChannelSpec(
                name=str(entry.get("name", f"channel-{idx}")),
                l=int(entry.get("l", 0)),
                spins=int(entry.get("spins", 0)),
            )
            for idx, entry in enumerate(channels_data)
        ]
        instances.append(
            EftInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                cutoff=float(raw.get("cutoff", 250.0)),
                couplings=couplings,
                channels=channels,
            )
        )
    return instances


def build_momentum_grid(cutoff: float, size: int = GRID_SIZE) -> np.ndarray:
    lower = min(cutoff * 0.25, MOMENTUM_FLOOR)
    start = max(lower, MOMENTUM_FLOOR)
    stop = max(cutoff, start + 1.0)
    return np.linspace(start, stop, num=size, dtype=float)


def centrifugal_energy(l: int) -> float:
    if l <= 0:
        return 0.0
    term = l * (l + 1)
    radius = CENTRIFUGAL_SCALE_FM
    return term / (2.0 * MASS_NUCLEON_MEV * radius ** 2)


def contact_kernel(pi: float, pj: float, cutoff: float, couplings: Dict[str, float]) -> float:
    c0 = couplings.get("c0", 0.0)
    c2 = couplings.get("c2", 0.0)
    c4 = couplings.get("c4", 0.0)
    exp_damper = np.exp(-((pi ** 2 + pj ** 2) / max(cutoff ** 2, 1.0)))
    polynomial = c0
    polynomial += 0.5 * c2 * (pi ** 2 + pj ** 2) / max(cutoff ** 2, 1.0)
    polynomial += 0.5 * c4 * (pi ** 4 + pj ** 4) / max(cutoff ** 4, 1.0)
    return polynomial * exp_damper


def channel_scale(channel: ChannelSpec) -> float:
    spin_factor = 1.0 + 0.2 * channel.spins
    angular_factor = 1.0 + 0.15 * float(channel.l)
    return spin_factor * angular_factor


def estimate_scattering_length(cutoff: float, couplings: Dict[str, float], scale: float) -> float:
    c0 = couplings.get("c0", 0.0)
    c2 = couplings.get("c2", 0.0)
    c4 = couplings.get("c4", 0.0)
    effective = c0 + (cutoff ** 2) * c2 / 6.0 + (cutoff ** 4) * c4 / 120.0
    effective *= scale
    if abs(effective) < 1e-6:
        effective = -1e-6
    return float(-1.0 / effective)


def estimate_effective_range(cutoff: float) -> float:
    return float(2.0 / max(cutoff, 1.0))


def solve_channels(instance: EftInstance) -> Dict[str, object]:
    grid = build_momentum_grid(instance.cutoff)
    grid_size = int(grid.size)
    channel_payloads: List[Dict[str, object]] = []
    lowest_energy = None

    for channel in instance.channels:
        scale = channel_scale(channel)
        kinetic = np.diag((grid ** 2) / (2.0 * MASS_NUCLEON_MEV) + centrifugal_energy(channel.l))
        potential = np.zeros((grid_size, grid_size), dtype=float)
        for i in range(grid_size):
            for j in range(grid_size):
                potential[i, j] = scale * contact_kernel(grid[i], grid[j], instance.cutoff, instance.couplings)

        hamiltonian = kinetic + potential
        eigenvalues, _ = np.linalg.eigh(hamiltonian)
        binding_energy = float(eigenvalues[0])
        if lowest_energy is None or binding_energy < lowest_energy:
            lowest_energy = binding_energy
        channel_payloads.append(
            {
                "name": channel.name,
                "l": channel.l,
                "spins": channel.spins,
                "binding_energy_mev": binding_energy,
                "scattering_length_fm": estimate_scattering_length(instance.cutoff, instance.couplings, scale),
                "effective_range_fm": estimate_effective_range(instance.cutoff),
            }
        )

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "cutoff_mev": instance.cutoff,
        "grid_size": grid_size,
        "channels": channel_payloads,
        "lowest_channel_energy_mev": lowest_energy,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No EFT instances found. Add YAML files under ../instances.")

    results = [solve_channels(instance) for instance in instances]
    payload = {
        "problem_id": "17_nuclear_physics",
        "model": "pionless_eft_contact",
        "grid_size": GRID_SIZE,
        "results": results,
    }

    output_path = estimates_dir / "classical_baseline.json"
    output_path.write_text(json.dumps(payload, indent=2))

    try:
        print(f"✅ Classical EFT baseline written to {output_path.relative_to(Path.cwd())}")
    except ValueError:
        print(f"✅ Classical EFT baseline written to {output_path}")


if __name__ == "__main__":
    main()
