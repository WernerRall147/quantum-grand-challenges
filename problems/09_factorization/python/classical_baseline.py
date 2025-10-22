"""Pollard Rho classical baseline for integer factorization instances."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import List, Optional, Tuple

import yaml


@dataclass(frozen=True)
class FactorInstance:
    instance_id: str
    name: str
    description: str
    modulus: int
    expected_factors: Tuple[int, int]
    seed: int

    @property
    def bit_length(self) -> int:
        return self.modulus.bit_length()


def load_instances(instances_dir: Path) -> List[FactorInstance]:
    instances: List[FactorInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        factors = raw.get("expected_factors", [])
        if not factors or len(factors) != 2:
            raise ValueError(f"Instance {path} must provide two expected_factors.")
        modulus = int(raw["modulus"])
        instances.append(
            FactorInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                modulus=modulus,
                expected_factors=(int(factors[0]), int(factors[1])),
                seed=int(raw.get("seed", 1234)),
            )
        )
    return instances


def pollard_rho(modulus: int, seed: int, max_attempts: int = 25, max_iterations: int = 100000) -> Optional[Tuple[int, int, int, int]]:
    if modulus % 2 == 0:
        return 2, modulus // 2, 1, 0

    rng = Random(seed)

    for attempt in range(max_attempts):
        x = rng.randrange(2, modulus - 1)
        y = x
        c = rng.randrange(1, modulus - 1)
        d = 1
        iterations = 0

        while d == 1 and iterations < max_iterations:
            x = (x * x + c) % modulus
            y = (y * y + c) % modulus
            y = (y * y + c) % modulus
            diff = abs(x - y)
            d = math.gcd(diff, modulus)
            iterations += 1

        if 1 < d < modulus:
            other = modulus // d
            return d, other, iterations, attempt + 1

    return None


def trial_division(modulus: int, limit: int = 100000) -> Optional[Tuple[int, int, int]]:
    if modulus % 2 == 0:
        return 2, modulus // 2, 1
    factor = 3
    iterations = 0
    while factor * factor <= modulus and iterations < limit:
        if modulus % factor == 0:
            return factor, modulus // factor, iterations
        factor += 2
        iterations += 1
    return None


def analyze_instance(instance: FactorInstance) -> dict:
    start_time = time.perf_counter()
    rho_result = pollard_rho(instance.modulus, instance.seed)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    if rho_result is not None:
        factor_a, factor_b, iterations, attempts = rho_result
        algorithm = "pollard_rho"
    else:
        fallback = trial_division(instance.modulus)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        if fallback is None:
            raise RuntimeError(f"Failed to factor modulus {instance.modulus} with provided methods.")
        factor_a, factor_b, iterations = fallback
        attempts = 0
        algorithm = "trial_division_fallback"

    factors = tuple(sorted((factor_a, factor_b)))
    expected = tuple(sorted(instance.expected_factors))
    correct = factors == expected

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "modulus": instance.modulus,
        "bit_length": instance.bit_length,
        "algorithm": algorithm,
        "iterations": iterations,
        "attempts": attempts,
        "runtime_ms": elapsed_ms,
        "factors": list(factors),
        "expected_factors": list(expected),
        "matches_expected": correct,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    if not instances:
        raise RuntimeError("No factorization instances found. Add YAML files to ../instances.")

    results = [analyze_instance(instance) for instance in instances]
    payload = {
        "problem_id": "09_factorization",
        "model": "pollard_rho_baseline",
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
