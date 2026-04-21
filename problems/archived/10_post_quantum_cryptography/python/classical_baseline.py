"""Classical security estimation baseline for post-quantum cryptography instances."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


@dataclass(frozen=True)
class PQCInstance:
    instance_id: str
    name: str
    description: str
    scheme: str
    variant: str
    lattice_dimension: int
    modulus: int
    target_security_bits: float
    classical_block_size: int
    quantum_block_size: int
    seed: int


def load_instances(instances_dir: Path) -> List[PQCInstance]:
    instances: List[PQCInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        instances.append(
            PQCInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                scheme=str(raw.get("scheme", "Unknown")),
                variant=str(raw.get("variant", "")),
                lattice_dimension=int(raw.get("lattice_dimension", 0)),
                modulus=int(raw.get("modulus", 0)),
                target_security_bits=float(raw.get("target_security_bits", 0.0)),
                classical_block_size=int(raw.get("classical_block_size", 300)),
                quantum_block_size=int(raw.get("quantum_block_size", 260)),
                seed=int(raw.get("seed", 0)),
            )
        )
    return instances


def bkz_cost(block_size: int, quantum: bool) -> float:
    coefficient = 0.0029 if not quantum else 0.0024
    linear = 0.6 if not quantum else 0.5
    return coefficient * (block_size ** 2) - linear * block_size + 8.0


def grover_speedup_bits(cost_bits: float, dimension: int) -> float:
    # Toy model: assume amplitude amplification drops cost proportional to sqrt of sieving space.
    speedup = 0.5 * math.log2(max(dimension, 2))
    return max(cost_bits - speedup, 0.0)


def gaussian_heuristic_norm(dimension: int, modulus: int) -> float:
    if dimension <= 0 or modulus <= 0:
        return 0.0
    return float(modulus) * math.sqrt(dimension / (2.0 * math.pi * math.e))


def analyze_instance(instance: PQCInstance) -> dict:
    classical_bits = bkz_cost(instance.classical_block_size, quantum=False)
    quantum_bits = bkz_cost(instance.quantum_block_size, quantum=True)
    grover_bits = grover_speedup_bits(quantum_bits, instance.lattice_dimension)

    classical_margin = instance.target_security_bits - classical_bits
    quantum_margin = instance.target_security_bits - grover_bits

    gh_norm = gaussian_heuristic_norm(instance.lattice_dimension, instance.modulus)
    sieving_attempts = max(1, instance.lattice_dimension // 25)
    log10_runtime = grover_bits * math.log10(2.0) - 12.0
    estimated_runtime_hours = float("inf") if log10_runtime > 250 else 10 ** log10_runtime

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "scheme": instance.scheme,
        "variant": instance.variant,
        "lattice_dimension": instance.lattice_dimension,
        "modulus": instance.modulus,
        "target_security_bits": instance.target_security_bits,
        "classical_cost_bits": classical_bits,
        "quantum_cost_bits": grover_bits,
        "classical_margin_bits": classical_margin,
        "quantum_margin_bits": quantum_margin,
        "gaussian_heuristic_norm": gh_norm,
        "sieving_attempts": sieving_attempts,
        "estimated_runtime_hours": estimated_runtime_hours,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    if not instances:
        raise RuntimeError("No PQC instances found. Add YAML files to ../instances.")

    results = [analyze_instance(instance) for instance in instances]
    payload = {
        "problem_id": "10_post_quantum_cryptography",
        "model": "bkz_cost_estimator",
        "results": results,
    }

    estimates_path = root / "estimates" / "classical_baseline.json"
    estimates_path.write_text(json.dumps(payload, indent=2))

    try:
        rel_path = estimates_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_path = estimates_path

    print(f"✅ Classical baseline written to {rel_path}")


if __name__ == "__main__":
    main()
