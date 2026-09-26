"""Problem 09 must find the period it claims to, and its estimate must include the arithmetic.

Checked on 2026-09-25, every part was wrong, and the demonstration that the paper said
"correctly factors 15 = 3 x 5" did not: in three runs it reported period 8 for every base
and found no factor in 8 of 9 attempts.

- ControlledMultiplyMod15 was right for a = 2 and 4 only. It multiplied by 13 for both 7
  and 8, by 4 for 11 and by 2 for 13.
- InverseQFT processed the qubits in the wrong order with angles twice too large, so the
  counting register was uniform over 0..15 whatever the period.
- The hardware kernel applied one multiplication, controlled by the qubit that should
  control U^8, and the resource estimate ran ShorPeriodFinding(3, 4): 3 shares a factor with
  15, no branch of the multiplier matched its powers, and the estimate had no modular
  arithmetic in it.
- The OpenQASM export repeated the kernel's errors in gates the QDK's OpenQASM 2 library
  does not define.
"""

from __future__ import annotations

import collections
import math
import re
import sys
from pathlib import Path

import pytest
from qdk import qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT = REPO_ROOT / "problems" / "09_factorization" / "qsharp"
sys.path.insert(0, str(REPO_ROOT / "tooling"))

COPRIME = (1, 2, 4, 7, 8, 11, 13, 14)
SHOTS = 160


def _order(a: int) -> int:
    return next(r for r in range(1, 16) if pow(a, r, 15) == 1)


def _read_big_endian(register: str) -> str:
    return (f"mutable v = 0; for i in 0..3 {{ if M({register}[i]) == One {{ set v += 1 <<< (3 - i); }} }} "
            f"ResetAll({register}); v")


@pytest.fixture()
def project():
    qsharp.init(project_root=str(PROJECT))


@pytest.mark.parametrize("a", COPRIME)
def test_the_multiplier_multiplies_by_a_mod_15(project, a):
    wrong = []
    for x in range(1, 15):
        flips = " ".join(f"X(t[{3 - i}]);" for i in range(4) if x >> i & 1)
        got = qsharp.eval(f"{{ use c = Qubit(); use t = Qubit[4]; X(c); {flips} "
                          f"Main.ControlledMultiplyMod15({a}, c, t); Reset(c); {_read_big_endian('t')} }}")
        if got != a * x % 15:
            wrong.append((x, got, a * x % 15))
    assert wrong == []


@pytest.mark.parametrize("a", COPRIME)
def test_the_multiplier_does_nothing_when_its_control_is_off(project, a):
    got = qsharp.eval(f"{{ use c = Qubit(); use t = Qubit[4]; X(t[3]); "
                      f"Main.ControlledMultiplyMod15({a}, c, t); {_read_big_endian('t')} }}")
    assert got == 1


@pytest.mark.parametrize("a", [2, 4, 7, 8, 11, 13, 14])
def test_period_finding_reads_s_times_16_over_r(project, a):
    r = _order(a)
    counts = collections.Counter(qsharp.eval(f"Main.ShorPeriodFinding({a}, 4)") for _ in range(SHOTS))
    assert set(counts) == {s * 16 // r for s in range(r)}, counts


def test_the_hardware_kernel_finds_the_order_of_7():
    qsharp.init()
    qsharp.eval((PROJECT / "HardwareKernel.qs").read_text(encoding="utf-8"))
    shots = qsharp.run("ShorKernel()", shots=SHOTS * 2)
    counts = collections.Counter(sum(1 << i for i, r in enumerate(s) if str(r) == "One") for s in shots)
    assert set(counts) == {0, 4, 8, 12}, counts
    # Four equally likely values: none should be far from a quarter of the shots.
    assert min(counts.values()) > len(shots) / 8


def test_the_openqasm_export_finds_the_order_of_7():
    """The export used OpenQASM 2 gates the QDK does not define, and the old kernel's bugs."""
    from qdk import openqasm

    source = (REPO_ROOT / "problems" / "09_factorization" / "estimates" / "shor_n15_a7.qasm").read_text(encoding="utf-8")
    shots = openqasm.run(source, shots=SHOTS * 2)
    counts = collections.Counter(sum(1 << i for i, r in enumerate(s) if str(r) == "One") for s in shots)
    assert set(counts) == {0, 4, 8, 12}, counts


def test_the_estimate_runs_modular_arithmetic_on_a_coprime_base():
    from estimator_config import ENTRY_POINTS, instruction_name
    from qdk.qre.interop import trace_from_entry_expr

    expr = ENTRY_POINTS["09_factorization"].expr()
    a = int(re.match(r"Main\.ShorPeriodFinding\((\d+),", expr).group(1))
    assert math.gcd(a, 15) == 1
    qsharp.init(project_root=str(PROJECT))
    trace = trace_from_entry_expr(expr)
    raw = trace.gate_counts() if callable(trace.gate_counts) else trace.gate_counts
    toffolis = sum(v for k, v in dict(raw).items() if instruction_name(k) == "CCX")
    # Each controlled SWAP of the multiplier is one Toffoli: three for U (x7) and two for
    # U^2 (x4); U^4 and U^8 are the identity. The a = 3 entry traced none.
    assert toffolis == 5
