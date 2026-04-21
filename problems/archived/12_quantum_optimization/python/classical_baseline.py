"""Greedy weighted tardiness baseline for parallel machine scheduling instances."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


@dataclass(frozen=True)
class Job:
    job_id: str
    processing_time: int
    due_date: int
    weight: float


@dataclass(frozen=True)
class SchedulingInstance:
    instance_id: str
    name: str
    description: str
    machines: int
    jobs: List[Job]


def load_instances(instances_dir: Path) -> List[SchedulingInstance]:
    instances: List[SchedulingInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        jobs = [
            Job(
                job_id=str(entry["id"]),
                processing_time=int(entry["processing_time"]),
                due_date=int(entry["due_date"]),
                weight=float(entry["weight"]),
            )
            for entry in raw.get("jobs", [])
        ]
        if not jobs:
            raise ValueError(f"Instance {path} does not define any jobs.")
        machines = int(raw.get("machines", 1))
        if machines <= 0:
            raise ValueError(f"Instance {path} must define a positive machine count.")
        instances.append(
            SchedulingInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                machines=machines,
                jobs=jobs,
            )
        )
    return instances


def greedy_weighted_tardiness(instance: SchedulingInstance) -> dict:
    jobs = sorted(
        instance.jobs,
        key=lambda job: (-job.weight / max(job.processing_time, 1), job.due_date),
    )

    machine_available = [0 for _ in range(instance.machines)]
    machine_busy_time = [0 for _ in range(instance.machines)]
    assignments = []

    total_tardiness = 0.0
    total_weighted_tardiness = 0.0
    max_tardiness = 0.0

    for job in jobs:
        machine_index = min(range(instance.machines), key=lambda idx: machine_available[idx])
        start_time = machine_available[machine_index]
        completion_time = start_time + job.processing_time
        tardiness = max(0, completion_time - job.due_date)

        total_tardiness += tardiness
        total_weighted_tardiness += tardiness * job.weight
        max_tardiness = max(max_tardiness, tardiness)

        machine_available[machine_index] = completion_time
        machine_busy_time[machine_index] += job.processing_time

        assignments.append(
            {
                "job_id": job.job_id,
                "machine": machine_index,
                "start_time": start_time,
                "completion_time": completion_time,
                "due_date": job.due_date,
                "tardiness": tardiness,
                "weight": job.weight,
                "weighted_tardiness": tardiness * job.weight,
            }
        )

    makespan = max(machine_available)
    average_tardiness = total_tardiness / len(jobs)
    utilization = [
        busy / makespan if makespan > 0 else 0.0 for busy in machine_busy_time
    ]

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "machines": instance.machines,
        "schedule": assignments,
        "metrics": {
            "job_count": len(jobs),
            "makespan": makespan,
            "total_tardiness": total_tardiness,
            "average_tardiness": average_tardiness,
            "max_tardiness": max_tardiness,
            "total_weighted_tardiness": total_weighted_tardiness,
            "machine_utilization": utilization,
        },
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No scheduling instances found. Add YAML files to ../instances.")

    results = [greedy_weighted_tardiness(instance) for instance in instances]

    payload = {
        "problem_id": "12_quantum_optimization",
        "model": "greedy_weighted_tardiness",
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
