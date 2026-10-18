"""tooling/verify_reversible.py must catch a wrong reversible operation, and say how sure it is when it passes.

Problem 09's multiplier is checked on all 32 basis states, both control values and all 16
target values, for every base test_shor_kernel.py covers, so each result is exhaustive. The
negative cases are small Q# sources of their own, written into temporary projects, and each is
one way a reversible operation goes wrong: a wire moved, an ancilla left dirty (one the
harness passes in and one the operation allocates itself), a control disturbed, and an output
left in superposition. Problem 09's files are read, never changed.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
from qdk import qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tooling"))

from test_shor_kernel import COPRIME, PROJECT  # noqa: E402
from verify_reversible import Registers, default_seed, epsilon_bound, verify_reversible  # noqa: E402

# test_shor_kernel.py's convention: target[0] holds the most significant bit.
MULTIPLIER = Registers(inputs={"control": 1, "target": 4}, outputs={"target": 4}, big_endian=True)
COPY_REGISTERS = Registers(inputs={"x": 3}, outputs={"y": 3})

COPY = """
operation Copy(x : Qubit[], y : Qubit[]) : Unit {
    for i in 0..Length(x) - 1 {
        CNOT(x[i], y[i]);
    }
}
"""

# Problem 09's multiplication by 2 mod 15, with one wire moved: the last controlled SWAP
# should act on target[2] and target[3].
BROKEN_TIMES_2 = """
operation Times2(control : Qubit, target : Qubit[]) : Unit {
    Controlled SWAP([control], (target[0], target[1]));
    Controlled SWAP([control], (target[1], target[2]));
    Controlled SWAP([control], (target[1], target[3]));
}
"""

# Copies x into y, and marks x's lowest bit in a scratch qubit it never clears.
COPY_THROUGH_SCRATCH = """
operation Copy(x : Qubit[], y : Qubit[], scratch : Qubit[]) : Unit {
    CNOT(x[0], scratch[0]);
    for i in 0..Length(x) - 1 {
        CNOT(x[i], y[i]);
    }
}
"""

# The same, with a scratch qubit the operation allocates itself.
COPY_WITH_OWN_SCRATCH = """
operation Copy(x : Qubit[], y : Qubit[]) : Unit {
    use scratch = Qubit();
    CNOT(x[0], scratch);
    for i in 0..Length(x) - 1 {
        CNOT(x[i], y[i]);
    }
}
"""

# Multiplies by 4 mod 15 as problem 09 does, then flips its control when the result is odd.
TIMES_4_DISTURBS_CONTROL = """
operation Times4(control : Qubit, target : Qubit[]) : Unit {
    Controlled SWAP([control], (target[0], target[2]));
    Controlled SWAP([control], (target[1], target[3]));
    CNOT(target[3], control);
}
"""

# Copies x into y, then puts y's lowest bit into superposition when x is 3.
COPY_WITH_SUPERPOSITION = """
operation Copy(x : Qubit[], y : Qubit[]) : Unit {
    for i in 0..Length(x) - 1 {
        CNOT(x[i], y[i]);
    }
    Controlled H(x, y[0]);
}
"""


def times_a_mod_15(a: int, x: int) -> int:
    """What ControlledMultiplyMod15 is documented to do to a 4-bit value x.

    a * x mod 15 for x from 1 to 14. The register can also hold 0 and 15, which both stand for
    zero mod 15 and which Shor's algorithm never reaches from 1. The kernel multiplies by
    15 - b, for b = 1, 2, 4 or 8, by multiplying by b and then flipping every bit, which swaps
    0 and 15; multiplying by 1, 2, 4 or 8 rotates the bits and leaves both where they are.
    """
    if 1 <= x <= 14:
        return a * x % 15
    return x if a in (1, 2, 4, 8) else 15 - x


def multiplier_reference(a: int):
    return lambda v: {"target": times_a_mod_15(a, v["target"]) if v["control"] else v["target"]}


def project(tmp_path: Path, source: str) -> Path:
    (tmp_path / "src").mkdir()
    (tmp_path / "qsharp.json").write_text("{}", encoding="utf-8")
    (tmp_path / "src" / "Main.qs").write_bytes(source.encode("utf-8"))  # LF, on every platform
    return tmp_path


@pytest.mark.parametrize(
    "prepare, raises",
    [("X(q[0]);", True), ("H(q[0]);", True), ("H(q[0]); CNOT(q[0], q[1]);", True), ("X(q[0]); X(q[0]);", False)],
    ids=["one", "plus", "bell-pair", "zero-again"],
)
def test_the_simulator_raises_when_a_qubit_is_released_dirty(prepare, raises):
    """verify_reversible's every check rests on this, so it is pinned here rather than assumed.

    Twenty runs each, because a check that measured would let |+> through half the time.
    """
    qsharp.init()
    raised = 0
    for _ in range(20):
        try:
            qsharp.run(f"{{ use q = Qubit[2]; {prepare} }}", shots=1)
        except qsharp.QSharpError as error:
            assert "released while not in |0⟩ state" in str(error)
            raised += 1
    assert raised == (20 if raises else 0)


@pytest.mark.parametrize("a", COPRIME)
def test_the_problem_09_multiplier_is_right_on_every_basis_state(a):
    result = verify_reversible(
        PROJECT, f"Main.ControlledMultiplyMod15({a}, control[0], target)", MULTIPLIER,
        multiplier_reference(a), k=32, delta=1e-3,
    )
    assert (result.passed, result.exhaustive, result.k, result.epsilon_bound) == (True, True, 32, 0.0), result.report()


def test_a_multiplier_with_one_wire_moved_fails_and_names_the_input(tmp_path):
    result = verify_reversible(
        project(tmp_path, BROKEN_TIMES_2), "Main.Times2(control[0], target)", MULTIPLIER,
        multiplier_reference(2), k=32, delta=1e-3,
    )
    # With the control on, the result is right only when target qubits 0, 2 and 3 agree,
    # which leaves 12 of the 16 values wrong.
    assert (result.passed, result.exhaustive, result.failed, result.epsilon_bound) == (False, True, 12, None)
    first = result.failures[0]
    assert (first.inputs, first.expected, first.observed) == (
        {"control": 1, "target": 1}, {"control": 1, "target": 2}, {"control": 1, "target": 4})
    assert "input control=1 target=1: expected control=1 target=2, observed control=1 target=4" in result.report()


def test_an_ancilla_left_dirty_fails_and_names_the_input(tmp_path):
    registers = Registers(inputs={"x": 3}, outputs={"y": 3}, ancillas={"scratch": 1})
    result = verify_reversible(
        project(tmp_path, COPY_THROUGH_SCRATCH), "Main.Copy(x, y, scratch)", registers,
        lambda v: {"y": v["x"]}, k=8, delta=1e-3,
    )
    assert (result.passed, result.exhaustive, result.failed) == (False, True, 4)  # the odd values of x
    first = result.failures[0]
    assert (first.inputs, first.observed) == ({"x": 1}, {"x": 1, "y": 1, "scratch": 1})
    assert "input x=1: expected x=1 y=1 scratch=0, observed x=1 y=1 scratch=1" in result.report()


def test_an_ancilla_the_operation_allocates_and_leaves_dirty_fails(tmp_path):
    """The harness cannot see this qubit; only the simulator's release check can."""
    result = verify_reversible(
        project(tmp_path, COPY_WITH_OWN_SCRATCH), "Main.Copy(x, y)", COPY_REGISTERS,
        lambda v: {"y": v["x"]}, k=8, delta=1e-3,
    )
    assert (result.passed, result.exhaustive, result.failed) == (False, True, 4)
    first = result.failures[0]
    assert (first.inputs, first.observed) == ({"x": 1}, None)
    assert "released while not in |0⟩ state" in first.error and "Main.Copy" in first.error
    assert "input x=1: expected x=1 y=1, observed nothing, the operation raised" in result.report()


def test_a_multiplier_that_disturbs_its_control_fails(tmp_path):
    result = verify_reversible(
        project(tmp_path, TIMES_4_DISTURBS_CONTROL), "Main.Times4(control[0], target)", MULTIPLIER,
        multiplier_reference(4), k=32, delta=1e-3, max_failures=32,
    )
    # The target is right every time; the control flips whenever the result is odd.
    assert (result.failed, result.failures[0].inputs) == (16, {"control": 0, "target": 1})
    assert all(f.observed["target"] == f.expected["target"] and f.observed["control"] != f.inputs["control"]
               for f in result.failures)


def test_an_output_left_in_superposition_fails(tmp_path):
    """A measurement would read the right value half the time; the release check does not."""
    result = verify_reversible(
        project(tmp_path, COPY_WITH_SUPERPOSITION), "Main.Copy(x, y)", Registers(inputs={"x": 2}, outputs={"y": 2}),
        lambda v: {"y": v["x"]}, k=4, delta=1e-3,
    )
    assert (result.failed, result.failures[0].inputs) == (1, {"x": 3})


def test_the_default_seed_changes_when_the_qsharp_source_changes(tmp_path):
    root = project(tmp_path, COPY)
    main = root / "src" / "Main.qs"
    seed = default_seed(root, "Main.Copy(x, y)", COPY_REGISTERS)
    assert default_seed(root, "Main.Copy(x, y)", COPY_REGISTERS) == seed
    main.write_bytes(COPY.replace("\n", "\r\n").encode("utf-8"))  # a Windows checkout draws what CI draws
    assert default_seed(root, "Main.Copy(x, y)", COPY_REGISTERS) == seed
    main.write_bytes((COPY + "// one more line\n").encode("utf-8"))
    assert default_seed(root, "Main.Copy(x, y)", COPY_REGISTERS) != seed
    main.write_bytes(COPY.encode("utf-8"))
    assert default_seed(root, "Main.Copy(x, y)", COPY_REGISTERS) == seed
    assert default_seed(root, "Main.Copy(x, y)", Registers(inputs={"x": 4}, outputs={"y": 4})) != seed


def test_the_seed_is_printed_and_reproduces_the_run(tmp_path, capsys):
    registers = Registers(inputs={"x": 8}, outputs={"y": 8}, ancillas={"scratch": 1})
    root = project(tmp_path, COPY_THROUGH_SCRATCH)
    first = verify_reversible(root, "Main.Copy(x, y, scratch)", registers, lambda v: {"y": v["x"]}, k=20, delta=1e-3)
    assert f"seed {first.seed} (SHA-256 of the Q# sources)" in capsys.readouterr().out
    assert (first.exhaustive, first.k, first.domain_size) == (False, 20, 256) and first.failed > 0
    again = verify_reversible(
        root, "Main.Copy(x, y, scratch)", registers, lambda v: {"y": v["x"]}, k=20, delta=1e-3, seed=first.seed,
    )
    assert f"seed {first.seed} (given)" in capsys.readouterr().out
    assert (again.failed, again.failures) == (first.failed, first.failures)
    other = verify_reversible(
        root, "Main.Copy(x, y, scratch)", registers, lambda v: {"y": v["x"]}, k=20, delta=1e-3, seed=first.seed + 1,
    )
    assert [f.inputs for f in other.failures] != [f.inputs for f in first.failures]  # a new seed draws new tests


def test_it_is_exhaustive_when_there_are_at_most_k_inputs(tmp_path):
    root = project(tmp_path, COPY)
    registers = Registers(inputs={"x": 5}, outputs={"y": 5})
    every = verify_reversible(root, "Main.Copy(x, y)", registers, lambda v: {"y": v["x"]}, k=32, delta=1e-3)
    assert (every.passed, every.exhaustive, every.k, every.epsilon_bound) == (True, True, 32, 0.0)
    sampled = verify_reversible(root, "Main.Copy(x, y)", registers, lambda v: {"y": v["x"]}, k=31, delta=1e-3)
    assert (sampled.passed, sampled.exhaustive, sampled.k, sampled.domain_size) == (True, False, 31, 32)
    assert sampled.epsilon_bound == epsilon_bound(31, 1e-3)
    assert "arXiv:2610.22367v1" in sampled.outcome() and "Eq. 20" in sampled.outcome()


def test_the_bound_is_eq_20():
    for k, delta in [(1, 0.5), (32, 1e-3), (1000, 1e-3), (10**6, 1e-9)]:
        bound = epsilon_bound(k, delta)
        assert math.isclose(bound, 1 - delta ** (1 / k), rel_tol=1e-6)
        assert bound <= math.log(1 / delta) / k
    assert math.isclose(epsilon_bound(1, 0.5), 0.5)
    assert math.isclose(epsilon_bound(10**6, 1e-9), math.log(1e9) / 10**6, rel_tol=1e-4)


def test_specifications_it_cannot_check_are_refused(tmp_path):
    for bad in ({"inputs": {"x": 2}, "ancillas": {"x": 1}}, {"inputs": {"x": 2}, "outputs": {"x": 3}},
                {"inputs": {"2x": 2}}, {"inputs": {"x": 0}}, {"inputs": {"verifyQubits": 1}}, {"inputs": {}}):
        with pytest.raises(ValueError):
            Registers(**bad)
    root = project(tmp_path, COPY)
    with pytest.raises(ValueError, match="exactly the outputs"):
        verify_reversible(root, "Main.Copy(x, y)", COPY_REGISTERS, lambda v: {"z": 0}, k=8, delta=1e-3)
    with pytest.raises(ValueError, match="does not fit"):
        verify_reversible(root, "Main.Copy(x, y)", COPY_REGISTERS, lambda v: {"y": 8}, k=8, delta=1e-3)
    for k, delta in [(0, 1e-3), (8, 0.0), (8, 1.0)]:
        with pytest.raises(ValueError):
            verify_reversible(root, "Main.Copy(x, y)", COPY_REGISTERS, lambda v: {"y": v["x"]}, k=k, delta=delta)
