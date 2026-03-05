"""Deterministic checks for the 12_quantum_optimization classical baseline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_baseline_module(root: Path):
    module_path = root / "python" / "classical_baseline.py"
    spec = importlib.util.spec_from_file_location("opt_baseline", module_path)
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

    assert payload.get("problem_id") == "12_quantum_optimization", "Unexpected problem_id"
    assert payload.get("model") == "greedy_weighted_tardiness", "Unexpected model"

    results = payload.get("results")
    assert isinstance(results, list) and len(results) == 3, "Expected exactly 3 instance results"

    small_row = next((row for row in results if row.get("instance_id") == "small"), None)
    assert small_row is not None, "Missing small instance result"

    module = _load_baseline_module(root)
    instances = module.load_instances(root / "instances")
    small_instance = next((inst for inst in instances if inst.instance_id == "small"), None)
    assert small_instance is not None, "Missing small instance definition"

    recomputed = module.greedy_weighted_tardiness(small_instance)
    small_metrics = small_row["metrics"]
    recomputed_metrics = recomputed["metrics"]

    for key in [
        "job_count",
        "makespan",
        "total_tardiness",
        "average_tardiness",
        "max_tardiness",
        "total_weighted_tardiness",
    ]:
        observed = float(small_metrics[key])
        expected = float(recomputed_metrics[key])
        assert _close(observed, expected), f"Mismatch for {key}: observed={observed}, expected={expected}"

    obs_util = small_metrics["machine_utilization"]
    exp_util = recomputed_metrics["machine_utilization"]
    assert len(obs_util) == len(exp_util), "Machine utilization length mismatch"
    for idx, (observed, expected) in enumerate(zip(obs_util, exp_util)):
        assert _close(float(observed), float(expected)), f"Utilization mismatch at machine {idx}"

    print("PASS: 12_quantum_optimization classical baseline checks")


if __name__ == "__main__":
    main()
