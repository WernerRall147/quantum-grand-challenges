"""Deterministic checks for the 17_nuclear_physics classical baseline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_baseline_module(root: Path):
    module_path = root / "python" / "classical_baseline.py"
    spec = importlib.util.spec_from_file_location("nuclear_baseline", module_path)
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

    assert payload.get("problem_id") == "17_nuclear_physics", "Unexpected problem_id"
    assert payload.get("model") == "pionless_eft_contact", "Unexpected model"

    results = payload.get("results")
    assert isinstance(results, list) and len(results) == 3, "Expected exactly 3 instance results"

    small_row = next((row for row in results if row.get("instance_id") == "small"), None)
    assert small_row is not None, "Missing small instance result"

    module = _load_baseline_module(root)
    instances = module.load_instances(root / "instances")
    small_instance = next((inst for inst in instances if inst.instance_id == "small"), None)
    assert small_instance is not None, "Missing small instance definition"

    recomputed = module.solve_channels(small_instance)

    assert int(small_row["grid_size"]) == int(recomputed["grid_size"]), "Grid size mismatch"
    assert len(small_row["channels"]) == len(recomputed["channels"]), "Channel count mismatch"
    assert _close(float(small_row["lowest_channel_energy_mev"]), float(recomputed["lowest_channel_energy_mev"])), "Lowest energy mismatch"

    obs_first = small_row["channels"][0]
    exp_first = recomputed["channels"][0]
    for key in ["binding_energy_mev", "scattering_length_fm", "effective_range_fm"]:
        assert _close(float(obs_first[key]), float(exp_first[key])), f"Mismatch for first-channel {key}"

    print("PASS: 17_nuclear_physics classical baseline checks")


if __name__ == "__main__":
    main()
