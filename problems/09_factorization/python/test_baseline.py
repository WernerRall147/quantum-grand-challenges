"""Deterministic checks for the 09_factorization classical baseline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_baseline_module(root: Path):
    module_path = root / "python" / "classical_baseline.py"
    spec = importlib.util.spec_from_file_location("factor_baseline", module_path)
    assert spec is not None and spec.loader is not None, "Unable to load baseline module"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    baseline_path = root / "estimates" / "classical_baseline.json"
    payload = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert payload.get("problem_id") == "09_factorization", "Unexpected problem_id"
    assert payload.get("model") == "pollard_rho_baseline", "Unexpected model"

    results = payload.get("results")
    assert isinstance(results, list) and len(results) == 3, "Expected exactly 3 instance results"

    for row in results:
        factors = list(row.get("factors", []))
        expected = list(row.get("expected_factors", []))
        assert sorted(factors) == sorted(expected), f"Incorrect factors for {row.get('instance_id', 'unknown')}"
        assert bool(row.get("matches_expected")), f"Expected match flag for {row.get('instance_id', 'unknown')}"

    small_row = next((row for row in results if row.get("instance_id") == "small"), None)
    assert small_row is not None, "Missing small instance result"

    module = _load_baseline_module(root)
    instances = module.load_instances(root / "instances")
    small_instance = next((inst for inst in instances if inst.instance_id == "small"), None)
    assert small_instance is not None, "Missing small instance definition"

    recomputed = module.analyze_instance(small_instance)
    for key in ["algorithm", "iterations", "attempts", "bit_length", "modulus", "matches_expected"]:
        assert small_row[key] == recomputed[key], f"Mismatch for {key}"

    print("PASS: 09_factorization classical baseline checks")


if __name__ == "__main__":
    main()
