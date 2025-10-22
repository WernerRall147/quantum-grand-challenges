"""Classical exhaustive search baseline for Grover-style database instances."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


@dataclass(frozen=True)
class SearchInstance:
    instance_id: str
    name: str
    description: str
    dataset_size: int
    marked_fraction: float
    confidence: float

    @property
    def marked_count(self) -> float:
        return self.marked_fraction * self.dataset_size


def load_instances(instances_dir: Path) -> List[SearchInstance]:
    instances: List[SearchInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        dataset_size = int(raw.get("dataset_size", 0))
        marked_fraction = float(raw.get("marked_fraction", 0.0))
        confidence = float(raw.get("confidence", 0.95))
        if dataset_size <= 0:
            raise ValueError(f"Instance {path} must define a positive dataset_size.")
        if not 0.0 < marked_fraction <= 1.0:
            raise ValueError(f"Instance {path} must define marked_fraction in (0, 1].")
        instances.append(
            SearchInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                dataset_size=dataset_size,
                marked_fraction=marked_fraction,
                confidence=confidence,
            )
        )
    return instances


def classical_queries(marked_fraction: float, confidence: float) -> float:
    return math.log(1.0 - confidence) / math.log(1.0 - marked_fraction)


def quantum_iterations(marked_fraction: float, confidence: float) -> int:
    amplitude = math.sqrt(marked_fraction)
    theta = math.asin(min(1.0, max(0.0, amplitude)))
    if theta <= 0.0:
        return 0
    optimal_rounds = math.floor((math.pi / (2.0 * theta) - 1.0) / 2.0)
    optimal_rounds = max(optimal_rounds, 0)

    def success_prob(rounds: int) -> float:
        return math.sin((2 * rounds + 1) * theta) ** 2

    rounds = optimal_rounds
    while success_prob(rounds) < confidence:
        rounds += 1
    return rounds


def analyze_instance(instance: SearchInstance) -> dict:
    classical_expected = classical_queries(instance.marked_fraction, instance.confidence)
    quantum_rounds = quantum_iterations(instance.marked_fraction, instance.confidence)

    quantum_query_count = max(quantum_rounds, 1)
    classical_query_count = max(classical_expected, 1.0)

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "dataset_size": instance.dataset_size,
        "marked_fraction": instance.marked_fraction,
        "confidence": instance.confidence,
        "metrics": {
            "classical_queries": classical_query_count,
            "quantum_rounds": quantum_query_count,
            "speedup_factor": classical_query_count / quantum_query_count,
        },
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No database search instances found. Add YAML files to ../instances.")

    results = [analyze_instance(instance) for instance in instances]

    payload = {
        "problem_id": "15_database_search",
        "model": "classical_exhaustive_search",
        "results": results,
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
