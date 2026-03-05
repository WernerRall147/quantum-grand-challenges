"""Deterministic checks for the 14_materials_discovery classical baseline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_baseline_module(root: Path):
    module_path = root / "python" / "classical_baseline.py"
    spec = importlib.util.spec_from_file_location("materials_baseline", module_path)
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

    assert payload.get("problem_id") == "14_materials_discovery", "Unexpected problem_id"
    assert payload.get("model") == "surrogate_cluster_expansion", "Unexpected model"

    results = payload.get("results")
    assert isinstance(results, list) and len(results) == 3, "Expected exactly 3 instance results"

    small_row = next((row for row in results if row.get("instance_id") == "small"), None)
    assert small_row is not None, "Missing small instance result"

    module = _load_baseline_module(root)
    instances = module.load_instances(root / "instances")
    small_instance = next((inst for inst in instances if inst.instance_id == "small"), None)
    assert small_instance is not None, "Missing small instance definition"

    recomputed_results = module.surrogate_scores(small_instance)
    recomputed_front = module.pareto_front(recomputed_results)

    observed_results = small_row["results"]
    observed_front = small_row["pareto_front"]

    assert len(observed_results) == len(recomputed_results), "Result count mismatch"
    assert len(observed_front) == len(recomputed_front), "Pareto front size mismatch"

    # Compare first point deterministically to ensure stable surrogate evaluation.
    obs0 = observed_results[0]["metrics"]
    exp0 = recomputed_results[0]["metrics"]
    for key in ["voltage", "stability", "heterogeneity", "entropy_term"]:
        assert _close(float(obs0[key]), float(exp0[key])), f"Mismatch for first-result metrics.{key}"

    print("PASS: 14_materials_discovery classical baseline checks")


if __name__ == "__main__":
    main()
