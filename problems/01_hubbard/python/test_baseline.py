"""Deterministic checks for the 01_hubbard classical baseline."""

from __future__ import annotations

import json
import math
from pathlib import Path


def _close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    baseline_path = Path(__file__).resolve().parents[1] / "estimates" / "classical_baseline.json"
    payload = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert payload.get("problem_id") == "01_hubbard", "Unexpected problem_id"
    grid = payload.get("grid")
    assert isinstance(grid, list) and len(grid) == 8, "Expected 8 grid points"

    # Validate a known analytical point: t=1.0, U=4.0.
    target = None
    for row in grid:
        if _close(float(row.get("hopping", -1.0)), 1.0) and _close(float(row.get("interaction", -1.0)), 4.0):
            target = row
            break
    assert target is not None, "Missing expected grid point (t=1.0, U=4.0)"

    discriminant = math.sqrt(4.0 * 4.0 + 16.0 * 1.0 * 1.0)
    expected_gs = 0.5 * (4.0 - discriminant)
    expected_us = 0.5 * (4.0 + discriminant)
    expected_triplet = 0.0

    assert _close(float(target["ground_state_energy"]), expected_gs), "Ground-state energy mismatch"
    assert _close(float(target["upper_singlet_energy"]), expected_us), "Upper singlet energy mismatch"
    assert _close(float(target["triplet_energy"]), expected_triplet), "Triplet energy mismatch"

    print("PASS: 01_hubbard classical baseline checks")


if __name__ == "__main__":
    main()
