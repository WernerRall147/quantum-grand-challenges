"""Mission planning baseline using patched-conic style heuristics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml

SAFETY_WINDOW_BUFFER_DAYS = 1.5
GRAVITY_ASSIST_BONUS = 0.85
MAX_FIGURE_OF_MERIT = 100.0


@dataclass(frozen=True)
class MissionLeg:
    origin: str
    destination: str
    departure_window_days: float
    arrival_window_days: float
    required_delta_v_kms: float
    time_of_flight_days: float


@dataclass(frozen=True)
class MissionInstance:
    instance_id: str
    name: str
    description: str
    legs: List[MissionLeg]
    launch_energy_c3: float
    max_mission_duration_days: float
    propellant_margin_percent: float


def load_instances(instances_dir: Path) -> List[MissionInstance]:
    instances: List[MissionInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        legs_raw = raw.get("legs", [])
        legs: List[MissionLeg] = []
        for entry in legs_raw:
            legs.append(
                MissionLeg(
                    origin=str(entry.get("origin", "")),
                    destination=str(entry.get("destination", "")),
                    departure_window_days=float(entry.get("departure_window_days", 0.0)),
                    arrival_window_days=float(entry.get("arrival_window_days", 0.0)),
                    required_delta_v_kms=float(entry.get("required_delta_v_kms", 0.0)),
                    time_of_flight_days=float(entry.get("time_of_flight_days", 0.0)),
                )
            )
        instances.append(
            MissionInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                legs=legs,
                launch_energy_c3=float(raw.get("launch_energy_c3", 0.0)),
                max_mission_duration_days=float(raw.get("max_mission_duration_days", 0.0)),
                propellant_margin_percent=float(raw.get("propellant_margin_percent", 0.0)),
            )
        )
    return instances


def aggregate_delta_v(legs: List[MissionLeg], margin_percent: float) -> Dict[str, float]:
    base_sum = sum(leg.required_delta_v_kms for leg in legs)
    gravity_adjustment = 0.0
    for leg in legs:
        if "Flyby" in leg.destination or "Assist" in leg.destination:
            gravity_adjustment += leg.required_delta_v_kms * (1.0 - GRAVITY_ASSIST_BONUS)
    margin_factor = 1.0 + margin_percent / 100.0
    adjusted = (base_sum - gravity_adjustment) * margin_factor
    return {
        "base_delta_v_kms": base_sum,
        "adjusted_delta_v_kms": max(adjusted, 0.0),
        "gravity_bonus_kms": gravity_adjustment,
    }


def mission_duration(legs: List[MissionLeg]) -> float:
    return sum(leg.time_of_flight_days for leg in legs)


def window_feasibility(legs: List[MissionLeg]) -> float:
    if not legs:
        return 0.0
    score = 0.0
    for leg in legs:
        departure_slack = max(leg.departure_window_days - SAFETY_WINDOW_BUFFER_DAYS, 0.0)
        arrival_slack = max(leg.arrival_window_days - SAFETY_WINDOW_BUFFER_DAYS, 0.0)
        score += departure_slack + arrival_slack
    return min(score, MAX_FIGURE_OF_MERIT)


def evaluate_instance(instance: MissionInstance) -> Dict[str, object]:
    delta_v = aggregate_delta_v(instance.legs, instance.propellant_margin_percent)
    total_duration = mission_duration(instance.legs)
    slack = instance.max_mission_duration_days - total_duration
    feasibility = window_feasibility(instance.legs)
    mission_score = max(0.0, slack) * 0.05 + feasibility * 0.4
    mission_score += max(0.0, MAX_FIGURE_OF_MERIT - delta_v["adjusted_delta_v_kms"]) * 0.2
    mission_score = min(mission_score, MAX_FIGURE_OF_MERIT)

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "launch_energy_c3": instance.launch_energy_c3,
        "max_mission_duration_days": instance.max_mission_duration_days,
        "legs": [
            {
                "origin": leg.origin,
                "destination": leg.destination,
                "departure_window_days": leg.departure_window_days,
                "arrival_window_days": leg.arrival_window_days,
                "required_delta_v_kms": leg.required_delta_v_kms,
                "time_of_flight_days": leg.time_of_flight_days,
            }
            for leg in instance.legs
        ],
        "base_delta_v_kms": delta_v["base_delta_v_kms"],
        "adjusted_delta_v_kms": delta_v["adjusted_delta_v_kms"],
        "gravity_bonus_kms": delta_v["gravity_bonus_kms"],
        "total_time_of_flight_days": total_duration,
        "duration_slack_days": slack,
        "window_feasibility_score": feasibility,
        "mission_score": mission_score,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No mission instances found. Add YAML files to ../instances.")

    results = [evaluate_instance(instance) for instance in instances]
    payload = {
        "problem_id": "20_space_mission_planning",
        "model": "patched_conic_budget",
        "results": results,
    }

    output_path = estimates_dir / "classical_baseline.json"
    output_path.write_text(json.dumps(payload, indent=2))

    try:
        print(f"Mission planning baseline written to {output_path.relative_to(Path.cwd())}")
    except ValueError:
        print(f"Mission planning baseline written to {output_path}")


if __name__ == "__main__":
    main()
