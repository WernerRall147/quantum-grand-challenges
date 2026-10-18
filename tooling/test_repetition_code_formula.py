"""Problem 16's repetition-code formula against the definitions proved in Lean.

formal/QGC/RepetitionCode.lean proves that, for odd d, summing C(d, k) q^k (1 - q)^(d - k)
over k from d // 2 + 1 to d gives exactly the probability that majority decoding of a d-bit
repetition code returns the wrong bit. A proof is about its own definitions, though, not
about the Python that publishes the numbers. This test closes that gap: it computes the
failure probability from the same definitions, by enumerating every flip pattern, and
checks repetition_logical_error against it at rounds = 1, where the code's flip
probability is p itself.

For rounds > 1 the code uses 1 - (1 - p) ** rounds as the flip probability, which the proof
does not cover (issue #297).
"""

from __future__ import annotations

import functools
import importlib.util
import itertools
import math
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBLEM = REPO_ROOT / "problems" / "16_error_correction"


@functools.cache
def _baseline():
    name = "qec_classical_baseline"
    spec = importlib.util.spec_from_file_location(name, PROBLEM / "python" / "classical_baseline.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # @dataclass resolves its class's module through sys.modules
    spec.loader.exec_module(module)
    return module


def _instance_distances() -> list[int]:
    return [
        int(yaml.safe_load(path.read_text(encoding="utf-8"))["code_distance"])
        for path in sorted((PROBLEM / "instances").glob("*.yaml"))
    ]


def _decode(received: tuple[int, ...]) -> int:
    """`decode` in RepetitionCode.lean: 1 exactly when more than half the bits are 1."""
    return 1 if 2 * sum(received) > len(received) else 0


def enumerated_failure_probability(d: int, q: float, sent: int) -> float:
    """`failureProb` in RepetitionCode.lean, by enumerating all 2^d flip patterns."""
    total = 0.0
    for flips in itertools.product((0, 1), repeat=d):
        if _decode(tuple(sent ^ flip for flip in flips)) != sent:
            k = sum(flips)
            total += q**k * (1 - q) ** (d - k)
    return total


DISTANCES = _instance_distances()
RATES = (0.0005, 0.002, 0.01, 0.1, 0.3)


def test_the_instances_use_odd_distances():
    # The theorem is for odd d. With even d a tie can only be broken in favour of one bit,
    # so the closed form is exact for one transmitted bit and wrong for the other.
    assert DISTANCES and all(d % 2 == 1 for d in DISTANCES), DISTANCES


@pytest.mark.parametrize("sent", (0, 1))
@pytest.mark.parametrize("p", RATES)
@pytest.mark.parametrize("d", DISTANCES)
def test_the_baseline_matches_exhaustive_enumeration_at_one_round(d, p, sent):
    published = _baseline().repetition_logical_error(d, p, rounds=1, bias=1.0)
    assert math.isclose(published, enumerated_failure_probability(d, p, sent), rel_tol=1e-9)


def test_an_off_by_one_threshold_disagrees_with_the_enumeration():
    """The comparison above has teeth: summing from d // 2 instead of d // 2 + 1 fails it."""
    d, q = 5, 0.1
    wrong = sum(math.comb(d, k) * q**k * (1 - q) ** (d - k) for k in range(d // 2, d + 1))
    assert not math.isclose(wrong, enumerated_failure_probability(d, q, 0), rel_tol=1e-9)
