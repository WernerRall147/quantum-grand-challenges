"""Surrogate scoring baseline for cathode material compositions."""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import yaml


@dataclass(frozen=True)
class CompositionGrid:
    a_elements: Tuple[str, ...]
    b_elements: Tuple[str, ...]
    c_elements: Tuple[str, ...]
    discretization: int


@dataclass(frozen=True)
class GridFeatures:
    redox_energy_base: float
    mixing_parameter: float
    strain_penalty: float
    entropy_bonus: float


@dataclass(frozen=True)
class MaterialsInstance:
    instance_id: str
    name: str
    description: str
    grid: CompositionGrid
    features: GridFeatures


def load_instances(instances_dir: Path) -> List[MaterialsInstance]:
    instances: List[MaterialsInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        grid_raw: Dict[str, Iterable[str]] = raw.get("composition_grid", {})
        features_raw: Dict[str, float] = raw.get("features", {})
        grid = CompositionGrid(
            a_elements=tuple(grid_raw.get("a_elements", [])),
            b_elements=tuple(grid_raw.get("b_elements", [])),
            c_elements=tuple(grid_raw.get("c_elements", [])),
            discretization=int(grid_raw.get("discretization", 5)),
        )
        features = GridFeatures(
            redox_energy_base=float(features_raw.get("redox_energy_base", -3.5)),
            mixing_parameter=float(features_raw.get("mixing_parameter", 0.15)),
            strain_penalty=float(features_raw.get("strain_penalty", 0.08)),
            entropy_bonus=float(features_raw.get("entropy_bonus", 0.02)),
        )
        instances.append(
            MaterialsInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                grid=grid,
                features=features,
            )
        )
    return instances


def composition_simplex(discretization: int) -> List[Tuple[float, float, float]]:
    points: List[Tuple[float, float, float]] = []
    for i in range(discretization + 1):
        for j in range(discretization + 1 - i):
            k = discretization - i - j
            points.append(
                (
                    i / discretization,
                    j / discretization,
                    k / discretization,
                )
            )
    return points


def entropy_score(fractions: np.ndarray) -> float:
    mask = fractions > 1e-8
    filtered = fractions[mask]
    if filtered.size == 0:
        return 0.0
    return -float(np.sum(filtered * np.log(filtered)))


def surrogate_scores(instance: MaterialsInstance) -> List[dict]:
    grid = instance.grid
    features = instance.features

    simplex_points = composition_simplex(grid.discretization)
    results: List[dict] = []

    for (a_fraction, b_fraction, c_fraction) in simplex_points:
        for b_combo in itertools.product(grid.b_elements, repeat=min(3, len(grid.b_elements))):
            site_counts = {element: b_combo.count(element) for element in set(b_combo)}
            heterogeneity = len(site_counts)
            mixing_term = features.mixing_parameter * heterogeneity

            strain_term = features.strain_penalty * abs(b_fraction - 0.5)

            fractions = np.array([a_fraction, b_fraction, c_fraction], dtype=float)
            entropy_term = features.entropy_bonus * entropy_score(fractions)

            voltage = features.redox_energy_base + mixing_term - strain_term + entropy_term
            stability = 1.0 - abs(voltage + 3.5) * 0.2

            results.append(
                {
                    "composition": {
                        "a": dict(zip(grid.a_elements, [a_fraction] * len(grid.a_elements))),
                        "b": dict(zip(grid.b_elements, [b_fraction / len(grid.b_elements)] * len(grid.b_elements))),
                        "c": dict(zip(grid.c_elements, [c_fraction] * len(grid.c_elements))),
                    },
                    "b_site_tuple": b_combo,
                    "metrics": {
                        "voltage": voltage,
                        "stability": stability,
                        "heterogeneity": heterogeneity,
                        "entropy_term": entropy_term,
                    },
                }
            )

    return results


def pareto_front(results: List[dict]) -> List[dict]:
    sorted_results = sorted(results, key=lambda entry: (-entry["metrics"]["stability"], -entry["metrics"]["voltage"]))
    front: List[dict] = []
    best_voltage = float("-inf")
    for entry in sorted_results:
        voltage = entry["metrics"]["voltage"]
        if voltage > best_voltage:
            front.append(entry)
            best_voltage = voltage
    return front


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No materials discovery instances found. Add YAML files to ../instances.")

    payload_results = []
    for instance in instances:
        results = surrogate_scores(instance)
        payload_results.append(
            {
                "instance_id": instance.instance_id,
                "name": instance.name,
                "description": instance.description,
                "grid": {
                    "a_elements": list(instance.grid.a_elements),
                    "b_elements": list(instance.grid.b_elements),
                    "c_elements": list(instance.grid.c_elements),
                    "discretization": instance.grid.discretization,
                },
                "features": {
                    "redox_energy_base": instance.features.redox_energy_base,
                    "mixing_parameter": instance.features.mixing_parameter,
                    "strain_penalty": instance.features.strain_penalty,
                    "entropy_bonus": instance.features.entropy_bonus,
                },
                "results": results,
                "pareto_front": pareto_front(results),
            }
        )

    payload = {
        "problem_id": "14_materials_discovery",
        "model": "surrogate_cluster_expansion",
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
