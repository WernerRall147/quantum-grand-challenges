"""Analytical repetition-code logical error baseline for QEC instances."""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import comb
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# Published with the results so the qualifiers travel with the numbers (#297).
MODEL_NOTES = {
    "noise": (
        "Each of the code_distance data bits flips independently with probability physical_error "
        "in each of measurement_rounds rounds. There is no correction between rounds, one majority "
        "vote at the end, and no measurement error."
    ),
    "logical_error": (
        "Exact when measurement_rounds is 1 and an upper bound when it is larger. The rounds are "
        "folded into effective_p = 1 - (1 - p)^rounds, the probability of at least one flip, but two "
        "flips on one bit cancel, so the probability that a bit ends up flipped is "
        "(1 - (1 - 2p)^rounds) / 2."
    ),
    "suppression": "physical_error / logical_error, so a lower bound wherever logical_error is an upper bound.",
    "pseudo_threshold": (
        "The smallest swept physical_error at which logical_error is at or below it, not the "
        "crossing point the name usually means."
    ),
    "bias": "A value other than 1.0 applies a heuristic weighting, not a noise model.",
}


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
    """Probability that one majority vote over ``distance`` bits decodes wrongly.

    Each bit flips independently with probability ``physical_error`` in each round, with no
    correction until the vote. ``effective_p`` is the probability of at least one flip. Two
    flips on one bit cancel, so the probability that a bit ends up flipped is
    (1 - (1 - 2p)^rounds) / 2: equal for one round, smaller for more. The result is therefore
    exact for one round and an upper bound otherwise (#297). ``bias`` other than 1.0 applies a
    heuristic weighting, not a noise model.
    """
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
        "model_notes": MODEL_NOTES,
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
