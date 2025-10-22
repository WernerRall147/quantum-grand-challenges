"""Classical exhaustive baseline for QAOA Max-Cut instances."""

from __future__ import annotations

import json
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


@dataclass(frozen=True)
class MaxCutInstance:
    instance_id: str
    description: str
    nodes: List[str]
    edges: List[Tuple[str, str, float]]
    target_precision: float


def load_instances(instances_dir: Path) -> List[MaxCutInstance]:
    instances: List[MaxCutInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        nodes = list(map(str, raw["nodes"]))
        edges_raw = raw.get("edges", [])
        edges: List[Tuple[str, str, float]] = []
        for item in edges_raw:
            if len(item) != 3:
                raise ValueError(f"Edge entry {item} in {path.name} must have three fields [u, v, weight].")
            u, v, weight = item
            edges.append((str(u), str(v), float(weight)))
        instances.append(
            MaxCutInstance(
                instance_id=path.stem,
                description=str(raw.get("description", "")),
                nodes=nodes,
                edges=edges,
                target_precision=float(raw.get("target_precision", 1e-2)),
            )
        )
    return instances


def enumerate_cut_values(instance: MaxCutInstance) -> Dict[str, float]:
    node_index = {node: idx for idx, node in enumerate(instance.nodes)}
    best_value = float("-inf")
    best_assignments: List[str] = []
    value_histogram: Dict[str, int] = {}

    for assignment_bits in itertools.product([0, 1], repeat=len(instance.nodes)):
        value = 0.0
        for u, v, weight in instance.edges:
            if assignment_bits[node_index[u]] != assignment_bits[node_index[v]]:
                value += weight
        value_histogram.setdefault(f"{value:.3f}", 0)
        value_histogram[f"{value:.3f}"] += 1
        if value > best_value + 1e-12:
            best_value = value
            best_assignments = ["".join(str(bit) for bit in assignment_bits)]
        elif abs(value - best_value) <= 1e-12:
            best_assignments.append("".join(str(bit) for bit in assignment_bits))

    return {
        "instance_id": instance.instance_id,
        "description": instance.description,
        "num_nodes": len(instance.nodes),
        "num_edges": len(instance.edges),
        "best_cut": best_value,
        "best_assignments": best_assignments,
        "value_histogram": value_histogram,
        "target_precision": instance.target_precision,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    if not instances:
        raise RuntimeError("No Max-Cut instances found. Add YAML files to ../instances.")

    results = [enumerate_cut_values(instance) for instance in instances]
    payload = {
        "problem_id": "05_qaoa_maxcut",
        "model": "exhaustive_maxcut",
        "results": results,
    }

    estimates_path = root / "estimates" / "classical_baseline.json"
    estimates_path.parent.mkdir(parents=True, exist_ok=True)
    estimates_path.write_text(json.dumps(payload, indent=2))

    try:
        rel_path = estimates_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_path = estimates_path

    print(f"✅ Classical baseline written to {rel_path}")


if __name__ == "__main__":
    main()
