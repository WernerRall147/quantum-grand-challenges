"""Analytical repetition-code logical error baseline for QEC instances."""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import comb
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass(frozen=True)
class QecInstance:
    instance_id: str
    name: str
    description: str
    code_distance: int
    measurement_rounds: int
    physical_error_rates: List[float]
    bias: float


def load_instances(instances_dir: Path) -> List[QecInstance]:
    instances: List[QecInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        rates = [float(value) for value in raw.get("physical_error_rates", [])]
        if not rates:
            raise ValueError(f"Instance {path} must define physical_error_rates.")
        instances.append(
            QecInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                code_distance=int(raw.get("code_distance", 3)),
                measurement_rounds=int(raw.get("measurement_rounds", 1)),
                physical_error_rates=rates,
                bias=float(raw.get("bias", 1.0)),
            )
        )
    return instances


def repetition_logical_error(distance: int, physical_error: float, rounds: int, bias: float) -> float:
    effective_p = 1.0 - (1.0 - physical_error) ** rounds
    threshold = distance // 2 + 1
    failure_prob = 0.0
    for k in range(threshold, distance + 1):
        weight = comb(distance, k) * (effective_p ** k) * ((1.0 - effective_p) ** (distance - k))
        if bias != 1.0:
            # Apply simple bias weighting for Z-biased noise scenarios.
            weight *= bias if k % 2 == 1 else 1.0
        failure_prob += weight
    return min(max(failure_prob, 0.0), 1.0)


def pseudo_threshold(physical: List[float], logical: List[float]) -> Optional[float]:
    for p, l in zip(physical, logical):
        if l <= p:
            return p
    return None


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No QEC instances found. Add YAML files to ../instances.")

    payload_results: List[Dict[str, object]] = []
    for instance in instances:
        physical_rates = instance.physical_error_rates
        logical_rates = [
            repetition_logical_error(
                distance=instance.code_distance,
                physical_error=rate,
                rounds=instance.measurement_rounds,
                bias=instance.bias,
            )
            for rate in physical_rates
        ]
        suppression = [p / l if l > 0 else float("inf") for p, l in zip(physical_rates, logical_rates)]
        threshold = pseudo_threshold(physical_rates, logical_rates)

        payload_results.append(
            {
                "instance_id": instance.instance_id,
                "name": instance.name,
                "description": instance.description,
                "code_distance": instance.code_distance,
                "measurement_rounds": instance.measurement_rounds,
                "bias": instance.bias,
                "points": [
                    {
                        "physical_error": p,
                        "logical_error": l,
                        "suppression": s,
                    }
                    for p, l, s in zip(physical_rates, logical_rates, suppression)
                ],
                "pseudo_threshold": threshold,
            }
        )

    payload = {
        "problem_id": "16_error_correction",
        "model": "repetition_code_analytical",
        "results": payload_results,
    }

    output_path = estimates_dir / "classical_baseline.json"
    output_path.write_text(json.dumps(payload, indent=2))

    try:
        relative_output = output_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        relative_output = output_path

    print(f"✅ Classical baseline written to {relative_output}")


if __name__ == "__main__":
    main()
