"""Dense classical baselines for the quantum linear solver challenge.

The script reads every YAML file in ``../instances`` and solves the
corresponding linear system using NumPy. It records condition numbers,
residual norms, and solution vectors. Results are written to
``../estimates/classical_baseline.json`` to keep the pipeline consistent
with the other quantum grand challenges.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
import yaml


@dataclass(frozen=True)
class LinearSystemInstance:
    instance_id: str
    system: str
    description: str
    matrix: np.ndarray
    rhs: np.ndarray
    target_precision: float

    @property
    def dimension(self) -> int:
        return int(self.matrix.shape[0])


def load_instances(instances_dir: Path) -> List[LinearSystemInstance]:
    instances: List[LinearSystemInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        matrix = np.array(raw["matrix"], dtype=float)
        rhs = np.array(raw["rhs"], dtype=float)
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError(f"Matrix in {path.name} must be square.")
        if rhs.shape[0] != matrix.shape[0]:
            raise ValueError(f"RHS length in {path.name} must equal matrix dimension.")

        instances.append(
            LinearSystemInstance(
                instance_id=path.stem,
                system=str(raw.get("system", path.stem)),
                description=str(raw.get("description", "")),
                matrix=matrix,
                rhs=rhs,
                target_precision=float(raw.get("target_precision", 1e-3)),
            )
        )
    return instances


def dense_solve(instance: LinearSystemInstance) -> dict:
    solution = np.linalg.solve(instance.matrix, instance.rhs)
    residual = instance.matrix @ solution - instance.rhs
    condition_number = float(np.linalg.cond(instance.matrix))

    return {
        "instance_id": instance.instance_id,
        "system": instance.system,
        "description": instance.description,
        "target_precision": instance.target_precision,
        "dimension": instance.dimension,
        "matrix": instance.matrix.tolist(),
        "rhs": instance.rhs.tolist(),
        "solution": solution.tolist(),
        "residual_norm": float(np.linalg.norm(residual)),
        "rhs_norm": float(np.linalg.norm(instance.rhs)),
        "condition_number_2": condition_number,
        "log2_condition_number": float(np.log2(condition_number)),
    }


def save_results(instances: List[LinearSystemInstance], output_path: Path) -> None:
    payload = {
        "problem_id": "04_linear_solvers",
        "model": "dense_direct_solve",
        "results": [dense_solve(instance) for instance in instances],
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
        raise RuntimeError("No linear solver instances found. Add YAML files to ../instances.")

    save_results(instances, root / "estimates" / "classical_baseline.json")


if __name__ == "__main__":
    main()
