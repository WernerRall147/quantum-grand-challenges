"""Deterministic checks for the 15_database_search classical baseline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_baseline_module(root: Path):
    module_path = root / "python" / "classical_baseline.py"
    spec = importlib.util.spec_from_file_location("search_baseline", module_path)
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

    assert payload.get("problem_id") == "15_database_search", "Unexpected problem_id"
    assert payload.get("model") == "classical_exhaustive_search", "Unexpected model"

    results = payload.get("results")
    assert isinstance(results, list) and len(results) == 3, "Expected exactly 3 instance results"

    module = _load_baseline_module(root)

    for row in results:
        marked_fraction = float(row["marked_fraction"])
        confidence = float(row["confidence"])
        metrics = row["metrics"]

        expected_classical = max(module.classical_queries(marked_fraction, confidence), 1.0)
        expected_rounds = max(module.quantum_iterations(marked_fraction, confidence), 1)
        expected_speedup = expected_classical / expected_rounds

        assert _close(float(metrics["classical_queries"]), float(expected_classical)), "Classical query mismatch"
        assert int(metrics["quantum_rounds"]) == int(expected_rounds), "Quantum rounds mismatch"
        assert _close(float(metrics["speedup_factor"]), float(expected_speedup)), "Speedup mismatch"

    print("PASS: 15_database_search classical baseline checks")


if __name__ == "__main__":
    main()
