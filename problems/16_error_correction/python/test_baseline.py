"""Deterministic checks for the 16_error_correction classical baseline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_baseline_module(root: Path):
    module_path = root / "python" / "classical_baseline.py"
    spec = importlib.util.spec_from_file_location("qec_baseline", module_path)
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

    assert payload.get("problem_id") == "16_error_correction", "Unexpected problem_id"
    assert payload.get("model") == "repetition_code_analytical", "Unexpected model"

    results = payload.get("results")
    assert isinstance(results, list) and len(results) == 3, "Expected exactly 3 instance results"

    small_row = next((row for row in results if row.get("instance_id") == "small"), None)
    assert small_row is not None, "Missing small instance result"

    module = _load_baseline_module(root)
    instances = module.load_instances(root / "instances")
    small_instance = next((inst for inst in instances if inst.instance_id == "small"), None)
    assert small_instance is not None, "Missing small instance definition"

    logical_rates = [
        module.repetition_logical_error(
            distance=small_instance.code_distance,
            physical_error=rate,
            rounds=small_instance.measurement_rounds,
            bias=small_instance.bias,
        )
        for rate in small_instance.physical_error_rates
    ]
    expected_threshold = module.pseudo_threshold(small_instance.physical_error_rates, logical_rates)

    points = small_row["points"]
    assert len(points) == len(small_instance.physical_error_rates), "Point count mismatch"

    for point, physical, logical in zip(points, small_instance.physical_error_rates, logical_rates):
        assert _close(float(point["physical_error"]), float(physical)), "Physical error mismatch"
        assert _close(float(point["logical_error"]), float(logical)), "Logical error mismatch"

    observed_threshold = small_row["pseudo_threshold"]
    if expected_threshold is None:
        assert observed_threshold is None, "Expected no pseudo-threshold"
    else:
        assert _close(float(observed_threshold), float(expected_threshold)), "Pseudo-threshold mismatch"

    print("PASS: 16_error_correction classical baseline checks")


if __name__ == "__main__":
    main()
