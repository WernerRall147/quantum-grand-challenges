"""Energy balance diffusion baseline for 1D climate column instances."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import yaml


@dataclass(frozen=True)
class InitialPeak:
    location: float
    amplitude: float
    width: float


@dataclass(frozen=True)
class ClimateInstance:
    instance_id: str
    name: str
    description: str
    grid_points: int
    time_steps: int
    time_step_hours: float
    diffusion_coefficient: float
    heat_capacity: float
    forcing_amplitude: float
    forcing_frequency_per_year: float
    initial_peak: InitialPeak


def load_instances(instances_dir: Path) -> List[ClimateInstance]:
    instances: List[ClimateInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        peak_raw: Dict[str, float] = raw.get("initial_peak", {})
        peak = InitialPeak(
            location=float(peak_raw.get("location", 0.5)),
            amplitude=float(peak_raw.get("amplitude", 1.0)),
            width=float(peak_raw.get("width", 0.1)),
        )
        instances.append(
            ClimateInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                grid_points=int(raw.get("grid_points", 25)),
                time_steps=int(raw.get("time_steps", 200)),
                time_step_hours=float(raw.get("time_step_hours", 24.0)),
                diffusion_coefficient=float(raw.get("diffusion_coefficient", 0.2)),
                heat_capacity=float(raw.get("heat_capacity", 4.0)),
                forcing_amplitude=float(raw.get("forcing_amplitude", 1.0)),
                forcing_frequency_per_year=float(raw.get("forcing_frequency_per_year", 1.0)),
                initial_peak=peak,
            )
        )
    return instances


def gaussian_profile(grid: np.ndarray, peak: InitialPeak) -> np.ndarray:
    return peak.amplitude * np.exp(-((grid - peak.location) ** 2) / (2.0 * peak.width ** 2))


def run_diffusion(instance: ClimateInstance) -> dict:
    grid = np.linspace(0.0, 1.0, instance.grid_points)
    state = gaussian_profile(grid, instance.initial_peak)

    dt_years = instance.time_step_hours / (24.0 * 365.0)
    dx = 1.0 / (instance.grid_points - 1)
    alpha = instance.diffusion_coefficient * dt_years / (dx * dx)

    if alpha >= 0.5:
        raise ValueError(
            f"Instance {instance.instance_id} violates explicit diffusion stability (alpha={alpha:.2f})."
        )

    rhs_scaling = instance.forcing_amplitude / instance.heat_capacity
    steps_per_year = max(1, round(1.0 / dt_years))

    snapshots: List[dict] = []
    target_steps = sorted({0, instance.time_steps // 4, instance.time_steps // 2, instance.time_steps - 1})

    running_mean = []
    running_std = []

    for step in range(instance.time_steps):
        forcing = rhs_scaling * (
            math.sin(2.0 * math.pi * instance.forcing_frequency_per_year * step / steps_per_year)
            + 0.02 * step / steps_per_year
        )

        next_state = np.copy(state)
        next_state[1:-1] = (
            state[1:-1]
            + alpha * (state[:-2] - 2.0 * state[1:-1] + state[2:])
            + forcing
        )

        state = next_state
        running_mean.append(float(np.mean(state)))
        running_std.append(float(np.std(state)))

        if step in target_steps:
            snapshots.append(
                {
                    "step": step,
                    "years": step * dt_years,
                    "profile": state.tolist(),
                }
            )

    convergence = [abs(running_mean[i] - running_mean[i - 1]) for i in range(1, len(running_mean))]

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "grid_points": instance.grid_points,
        "time_steps": instance.time_steps,
    "time_step_hours": instance.time_step_hours,
        "stability_alpha": alpha,
        "snapshots": snapshots,
        "time_series": {
            "mean_anomaly": running_mean,
            "std_anomaly": running_std,
            "convergence": convergence,
        },
        "metrics": {
            "final_mean": running_mean[-1],
            "final_std": running_std[-1],
            "max_anomaly": float(np.max(state)),
            "min_anomaly": float(np.min(state)),
            "mean_convergence": float(np.mean(convergence)) if convergence else 0.0,
        },
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No climate modeling instances found. Add YAML files to ../instances.")

    results = [run_diffusion(instance) for instance in instances]

    payload = {
        "problem_id": "13_climate_modeling",
        "model": "finite_difference_energy_balance",
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
