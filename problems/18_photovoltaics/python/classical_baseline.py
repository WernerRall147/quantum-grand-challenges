"""Photovoltaic efficiency baseline using simplified Shockley-Queisser style heuristics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import exp, log
from pathlib import Path
from typing import Dict, List

import numpy as np
import yaml

K_BOLTZMANN_EV = 8.617333262e-5  # Boltzmann constant in eV/K.
SOLAR_INPUT_MW_CM2 = 100.0       # Approximate AM1.5 irradiance per cm^2.
MAX_FILL_FACTOR = 0.88           # Empirical maximum for high-quality devices.


@dataclass(frozen=True)
class PvInstance:
    instance_id: str
    name: str
    description: str
    bandgaps: List[float]
    temperature: float
    concentration: float
    radiative_coeff: float
    nonradiative_ratio: float
    series_resistance: float
    shunt_resistance: float


def ensure_bandgap_list(raw_bandgap: object) -> List[float]:
    if isinstance(raw_bandgap, (list, tuple)):
        return [float(value) for value in raw_bandgap]
    return [float(raw_bandgap)]


def load_instances(instances_dir: Path) -> List[PvInstance]:
    instances: List[PvInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        bandgaps = ensure_bandgap_list(raw.get("bandgap_ev", 1.4))
        instances.append(
            PvInstance(
                instance_id=path.stem,
                name=str(raw.get("name", path.stem)),
                description=str(raw.get("description", "")),
                bandgaps=bandgaps,
                temperature=float(raw.get("temperature_k", 300.0)),
                concentration=float(raw.get("spectral_concentration", 1.0)),
                radiative_coeff=float(raw.get("radiative_coeff", 1.0e-10)),
                nonradiative_ratio=float(raw.get("nonradiative_ratio", 0.05)),
                series_resistance=float(raw.get("series_resistance_ohm_cm2", 0.5)),
                shunt_resistance=float(raw.get("shunt_resistance_ohm_cm2", 3000.0)),
            )
        )
    return instances


def short_circuit_current(bandgap: float, concentration: float) -> float:
    penalty = max(0.05, exp(-max(bandgap - 1.2, 0.0)))
    return 46.0 * concentration * penalty


def open_circuit_voltage(
    bandgap: float,
    temperature: float,
    concentration: float,
    nonradiative_ratio: float,
    radiative_coeff: float,
) -> float:
    thermal_voltage = K_BOLTZMANN_EV * temperature
    radiative_loss = 0.28 + 0.02 * log(1.0 + concentration)
    nonradiative_loss = thermal_voltage * log(1.0 + nonradiative_ratio * 200.0)
    coefficient_loss = thermal_voltage * log(1.0 + radiative_coeff * 1.0e11)
    voltage = bandgap - (radiative_loss + nonradiative_loss + coefficient_loss)
    return max(voltage, 0.0)


def approximate_fill_factor(voc_total: float, temperature: float, jsc_ma_cm2: float, instance: PvInstance) -> float:
    thermal_voltage = K_BOLTZMANN_EV * temperature
    normalized = voc_total / max(thermal_voltage * 25.0, 1e-6)
    if normalized <= 0.0:
        return 0.0
    ideal_ff = (normalized - log(normalized + 0.72)) / (normalized + 1.0)
    ideal_ff = max(0.0, min(ideal_ff, MAX_FILL_FACTOR))

    current_a = jsc_ma_cm2 / 1000.0
    series_factor = max(0.5, 1.0 - instance.series_resistance * current_a * 0.5)
    shunt_factor = max(0.5, 1.0 - 10.0 / max(instance.shunt_resistance, 1.0))
    fill_factor = ideal_ff * series_factor * shunt_factor
    return max(0.0, min(fill_factor, MAX_FILL_FACTOR))


def evaluate_instance(instance: PvInstance) -> Dict[str, object]:
    subcell_data: List[Dict[str, float]] = []
    currents = []
    voltages = []

    for bandgap in instance.bandgaps:
        jsc = short_circuit_current(bandgap, instance.concentration)
        voc = open_circuit_voltage(
            bandgap=bandgap,
            temperature=instance.temperature,
            concentration=instance.concentration,
            nonradiative_ratio=instance.nonradiative_ratio,
            radiative_coeff=instance.radiative_coeff,
        )
        currents.append(jsc)
        voltages.append(voc)
        subcell_data.append(
            {
                "bandgap_ev": bandgap,
                "jsc_ma_cm2": jsc,
                "voc_v": voc,
            }
        )

    limited_current = min(currents) if currents else 0.0
    total_voltage = float(np.sum(voltages)) if voltages else 0.0
    fill_factor = approximate_fill_factor(total_voltage, instance.temperature, limited_current, instance)
    power_output = total_voltage * limited_current * fill_factor
    power_input = SOLAR_INPUT_MW_CM2 * instance.concentration
    efficiency = power_output / power_input if power_input > 0 else 0.0

    return {
        "instance_id": instance.instance_id,
        "name": instance.name,
        "description": instance.description,
        "junction_count": len(instance.bandgaps),
        "temperature_k": instance.temperature,
        "concentration": instance.concentration,
        "series_resistance_ohm_cm2": instance.series_resistance,
        "shunt_resistance_ohm_cm2": instance.shunt_resistance,
        "subcells": subcell_data,
        "current_limit_ma_cm2": limited_current,
        "total_voltage_v": total_voltage,
        "fill_factor": fill_factor,
        "max_power_density_mw_cm2": power_output,
        "efficiency": efficiency,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances_dir = root / "instances"
    estimates_dir = root / "estimates"
    estimates_dir.mkdir(parents=True, exist_ok=True)

    instances = load_instances(instances_dir)
    if not instances:
        raise RuntimeError("No photovoltaic instances found. Add YAML files to ../instances.")

    results = [evaluate_instance(instance) for instance in instances]
    payload = {
        "problem_id": "18_photovoltaics",
        "model": "shockley_queisser_heuristic",
        "results": results,
    }

    output_path = estimates_dir / "classical_baseline.json"
    output_path.write_text(json.dumps(payload, indent=2))

    try:
        print(f"Photovoltaic baseline written to {output_path.relative_to(Path.cwd())}")
    except ValueError:
        print(f"Photovoltaic baseline written to {output_path}")


if __name__ == "__main__":
    main()
