"""Deterministic checks for the 02_catalysis classical baseline."""

from __future__ import annotations

import json
import math
from pathlib import Path


R_GAS_CONSTANT = 8.314


def _close(a: float, b: float, rel: float = 1e-9) -> bool:
    scale = max(1.0, abs(a), abs(b))
    return abs(a - b) <= rel * scale


def main() -> None:
    baseline_path = Path(__file__).resolve().parents[1] / "estimates" / "classical_baseline.json"
    payload = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert payload.get("problem_id") == "02_catalysis", "Unexpected problem_id"
    results = payload.get("results")
    assert isinstance(results, list) and len(results) >= 1, "Expected at least one catalysis result"

    for row in results:
        pre_exponential = float(row["pre_exponential"])
        activation_energy = float(row["activation_energy"])
        temperature = float(row["temperature"])
        observed_rate = float(row["rate"])

        expected_rate = pre_exponential * math.exp(-activation_energy / (R_GAS_CONSTANT * temperature))
        assert _close(observed_rate, expected_rate), f"Rate mismatch for instance {row.get('instance_id', 'unknown')}"

    print("PASS: 02_catalysis classical baseline checks")


if __name__ == "__main__":
    main()
