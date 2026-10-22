"""Deterministic checks for the 16_error_correction classical baseline."""

from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path

# The published logical errors may exceed the exact value of the model by at most this
# fraction; README.md quotes it.
MAX_OVERESTIMATE = 0.02


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


def _relatively_close(a: float, b: float, rel: float) -> bool:
    return abs(a - b) <= rel * max(abs(a), abs(b))


def _net_flip(p: float, rounds: int) -> float:
    """Probability that a bit ends up flipped after independent flips in each round.

    Two flips cancel, so this is (1 - (1 - 2p)^rounds) / 2. The recurrence gives exactly p
    for one round, where the closed form would round.
    """
    q = 0.0
    for _ in range(rounds):
        q = q + p - 2.0 * p * q
    return q


def _majority_failure(distance: int, q: float) -> float:
    return sum(
        math.comb(distance, k) * q**k * (1.0 - q) ** (distance - k)
        for k in range(distance // 2 + 1, distance + 1)
    )


def _enumerated_failure(distance: int, p: float, rounds: int) -> float:
    """The model itself: every flip pattern over distance x rounds, then one majority vote."""
    total = 0.0
    for flips in itertools.product((0, 1), repeat=distance * rounds):
        flipped_bits = sum(sum(flips[i * rounds:(i + 1) * rounds]) % 2 for i in range(distance))
        if flipped_bits > distance // 2:
            total += math.prod(p if flip else 1.0 - p for flip in flips)
    return total


def check_bound(root: Path, payload: dict) -> None:
    """The published logical errors bound the model's exact value, and say so where published.

    repetition_logical_error folds the rounds into effective_p = 1 - (1 - p)^rounds, the
    probability of at least one flip. That is the net flip probability for one round and
    larger for more, so its logical errors are exact for one round and upper bounds
    otherwise (#297).
    """
    for distance, rounds, p in ((3, 2, 0.011), (3, 3, 0.002), (5, 2, 0.011)):
        enumerated = _enumerated_failure(distance, p, rounds)
        closed_form = _majority_failure(distance, _net_flip(p, rounds))
        assert _relatively_close(enumerated, closed_form, 1e-12), (
            f"d={distance}, rounds={rounds}, p={p}: enumeration {enumerated} != closed form {closed_form}"
        )

    worst = 0.0
    for row in payload["results"]:
        if float(row["bias"]) != 1.0:
            continue  # the bias weighting is a heuristic, not a noise model
        distance, rounds = int(row["code_distance"]), int(row["measurement_rounds"])
        for point in row["points"]:
            physical = float(point["physical_error"])
            published = float(point["logical_error"])
            exact = _majority_failure(distance, _net_flip(physical, rounds))
            label = f"{row['instance_id']} at p={physical}"
            if rounds == 1:
                assert _relatively_close(published, exact, 1e-9), f"{label}: one round should be exact"
            assert published >= exact * (1.0 - 1e-12), f"{label}: {published} is below the exact {exact}"
            worst = max(worst, published / exact - 1.0)
    assert worst <= MAX_OVERESTIMATE, (
        f"the published logical errors exceed the exact model by up to {worst:.2%}, more than "
        f"the {MAX_OVERESTIMATE:.0%} README.md states"
    )

    if worst > 1e-9:
        note = payload.get("model_notes", {}).get("logical_error", "")
        assert "upper bound" in note, (
            "estimates/classical_baseline.json must say that logical_error is an upper bound "
            "when measurement_rounds > 1"
        )
        readme = (root / "README.md").read_text(encoding="utf-8")
        assert "upper bound" in readme and f"{MAX_OVERESTIMATE:.0%}" in readme, (
            f"README.md must say that the logical errors are upper bounds within {MAX_OVERESTIMATE:.0%}"
        )


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

    check_bound(root, payload)

    print("PASS: 16_error_correction classical baseline checks")


if __name__ == "__main__":
    main()
