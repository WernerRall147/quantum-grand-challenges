"""Deterministic checks for the 04_linear_solvers classical baseline."""

from __future__ import annotations

import json
import math
from pathlib import Path


def _close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    baseline_path = Path(__file__).resolve().parents[1] / "estimates" / "classical_baseline.json"
    payload = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert payload.get("problem_id") == "04_linear_solvers", "Unexpected problem_id"
    results = payload.get("results")
    assert isinstance(results, list) and len(results) >= 1, "Expected at least 1 result"

    # Validate the small instance (2x2 symmetric system)
    small = None
    for r in results:
        if r.get("instance_id") == "small":
            small = r
            break
    assert small is not None, "Missing 'small' instance"

    # Check solution solves Ax = b within residual tolerance
    residual = float(small["residual_norm"])
    assert residual < 1e-10, f"Residual too large: {residual}"

    # Condition number should be finite and positive
    cond = float(small["condition_number_2"])
    assert cond >= 1.0, f"Condition number must be >= 1, got {cond}"
    assert math.isfinite(cond), "Condition number must be finite"

    # Solution vector dimension must match matrix dimension
    dim = int(small["dimension"])
    sol = small["solution"]
    assert len(sol) == dim, f"Solution dimension {len(sol)} != matrix dimension {dim}"

    print("PASS: 04_linear_solvers classical baseline checks")


if __name__ == "__main__":
    main()
