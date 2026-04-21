"""Deterministic checks for the 13_climate_modeling classical baseline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_baseline_module(root: Path):
    module_path = root / "python" / "classical_baseline.py"
    spec = importlib.util.spec_from_file_location("climate_baseline", module_path)
    assert spec is not None and spec.loader is not None, "Unable to load baseline module"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _close(a: float, b: float, rel: float = 1e-9) -> bool:
    scale = max(1.0, abs(a), abs(b))
    return abs(a - b) <= rel * scale


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    baseline_path = root / "estimates" / "classical_baseline.json"
    payload = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert payload.get("problem_id") == "13_climate_modeling", "Unexpected problem_id"
    assert payload.get("model") == "finite_difference_energy_balance", "Unexpected model"

    results = payload.get("results")
    assert isinstance(results, list) and len(results) == 3, "Expected exactly 3 instance results"

    small_row = next((row for row in results if row.get("instance_id") == "small"), None)
    assert small_row is not None, "Missing small instance result"

    module = _load_baseline_module(root)
    instances = module.load_instances(root / "instances")
    small_instance = next((inst for inst in instances if inst.instance_id == "small"), None)
    assert small_instance is not None, "Missing small instance definition"

    recomputed = module.run_diffusion(small_instance)

    for key in ["grid_points", "time_steps", "time_step_hours", "stability_alpha"]:
        observed = float(small_row[key])
        expected = float(recomputed[key])
        assert _close(observed, expected), f"Mismatch for {key}: observed={observed}, expected={expected}"

    for key in ["final_mean", "final_std", "max_anomaly", "min_anomaly", "mean_convergence"]:
        observed = float(small_row["metrics"][key])
        expected = float(recomputed["metrics"][key])
        assert _close(observed, expected), f"Mismatch for metrics.{key}: observed={observed}, expected={expected}"

    assert len(small_row["snapshots"]) == len(recomputed["snapshots"]), "Snapshot count mismatch"
    assert len(small_row["time_series"]["mean_anomaly"]) == int(small_row["time_steps"]), "Mean series length mismatch"

    print("PASS: 13_climate_modeling classical baseline checks")


if __name__ == "__main__":
    main()
