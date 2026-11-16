"""tooling/kernel_opt/evaluate.py must reject what it cannot certify, score what it accepts, and give
each candidate one held-out attempt.

The evaluator is Issue B of the plan in #298. Problem 10's oracle changes only phases, so it passes
basis-state tests against the identity; the gate whitelist rejects it for its H gates, and problem
19's Trotter step for its rotations. Candidates that use Std.ResourceEstimation, read the
simulator's state or draw random numbers are rejected for their sources, and one test shows why
reading the state must be: an AND that reads its inputs with CheckZero passes verify_reversible on
every input with no gate in its circuit or trace. The scores are those of problem 09's multiplier by
7 and problem 18's controlled increment on 8 qubits, as traced for the plan. A candidate written
against its own loop draw passes the loop and fails the held-out check; a second held-out attempt
is refused whatever the first returned, including one stopped for running too long, whose attempt
is logged before its check starts; and a check leaves the caller's Q# interpreter alone. Problem
files are read, never changed: the evaluator checks a copy.

The reference functions below are loaded by name, from this file, in the evaluator's own process.
"""

from __future__ import annotations

import hashlib
import json
import os
import py_compile
import sys
import threading
import time
from pathlib import Path

import pytest
from qdk import qsharp
from qdk.qre.interop import trace_from_entry_expr

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tooling"))
sys.path.insert(0, str(REPO_ROOT))

from test_verify_reversible import times_a_mod_15  # noqa: E402
from tooling.kernel_opt.evaluate import AttemptRefused, Spec, certify, evaluate  # noqa: E402
from tooling.verify_reversible import Registers, _sampled_inputs, default_seed, verify_reversible  # noqa: E402

PROBLEMS = REPO_ROOT / "problems"
AND = Registers(inputs={"x": 2}, outputs={"y": 1})
COPY_3 = Registers(inputs={"x": 3}, outputs={"y": 3})
COPY_8 = Registers(inputs={"x": 8}, outputs={"y": 8})

COPY = """
operation Copy(x : Qubit[], y : Qubit[]) : Unit {
    for i in 0..Length(x) - 1 {
        CNOT(x[i], y[i]);
    }
}
"""

NEVER_ENDS = """
operation Copy(x : Qubit[], y : Qubit[]) : Unit {
    mutable i = 0;
    repeat {
        set i += 1;
    } until false;
}
"""

# An AND that reads its inputs instead of computing on them: no gate touches x.
AND_READING_STATE = """
operation And(x : Qubit[], y : Qubit[]) : Unit {
    if not Std.Diagnostics.CheckZero(x[0]) and not Std.Diagnostics.CheckZero(x[1]) {
        X(y[0]);
    }
}
"""

# Each is a right AND built from X gates, with or without controls; only the source check rejects
# it, and with that check removed each is accepted.
SOURCES_THE_CHECK_REJECTS = {
    "resource-estimation": ("ResourceEstimation", """
import Std.ResourceEstimation.*;
operation And(x : Qubit[], y : Qubit[]) : Unit {
    if BeginEstimateCaching("And", SingleVariant()) {
        CCNOT(x[0], x[1], y[0]);
        EndEstimateCaching();
    }
}
"""),
    "check-zero": ("CheckZero", AND_READING_STATE),
    "check-all-zero": ("CheckAllZero", """
operation And(x : Qubit[], y : Qubit[]) : Unit {
    if not Std.Diagnostics.CheckAllZero([x[0]]) and not Std.Diagnostics.CheckAllZero([x[1]]) {
        X(y[0]);
    }
}
"""),
    "random": ("Random", """
operation And(x : Qubit[], y : Qubit[]) : Unit {
    // One Toffoli or three: right either way, but which is counted is a coin toss.
    for _ in 0..2 * Std.Random.DrawRandomInt(0, 1) {
        CCNOT(x[0], x[1], y[0]);
    }
}
"""),
}

# The values of x on which the copy written against its own draw is wrong: 32 of the 256.
WRONG = frozenset(range(3, 256, 8))


def copy(values):
    return {"y": values["x"]}


def logical_and(values):
    return {"y": int(values["x"] == 3)}


def unchanged(values):
    return {"qubits": values["qubits"]}


def times_7_mod_15(values):
    return {"target": times_a_mod_15(7, values["target"]) if values["control"] else values["target"]}


def step_right_if_coin(values):
    return {"position": (values["position"] + values["coin"]) % 2**8}


def spec(task, operation, registers, reference, **policy) -> Spec:
    return Spec(task=task, operation=operation, registers=registers, reference=Path(__file__),
                reference_function=reference.__name__, **policy)


def project(root: Path, source: str) -> Path:
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "qsharp.json").write_text("{}", encoding="utf-8")
    (root / "src" / "Main.qs").write_bytes(source.encode("utf-8"))  # LF, on every platform
    return root


def written_against_its_own_draw(root: Path, k: int) -> Path:
    """An 8-bit copy that is wrong on WRONG, with a last comment tried until the k tests drawn from
    its own default seed miss every value it gets wrong."""
    flips = "".join(f"    ApplyControlledOnInt({x}, X, x, y[0]);\n" for x in sorted(WRONG))
    for salt in range(1000):
        project(root, "operation Copy(x : Qubit[], y : Qubit[]) : Unit {\n"
                      "    for i in 0..Length(x) - 1 {\n        CNOT(x[i], y[i]);\n    }\n"
                      f"{flips}}}\n// {salt}\n")
        drawn = {inputs["x"] for inputs in _sampled_inputs(COPY_8, k, default_seed(root, "Main.Copy(x, y)", COPY_8))}
        if not drawn & WRONG:
            return root
    raise AssertionError("no comment made the draw miss every wrong value")


@pytest.mark.parametrize(
    "root, operation, gates",
    [(PROBLEMS / "archived" / "10_post_quantum_cryptography" / "qsharp", "Main.MarkTargetKey(5, qubits)", ["H"]),
     (PROBLEMS / "19_quantum_chromodynamics" / "qsharp", "Main.TrotterGaugeStep(0.3, 0.7, qubits)", ["Rx", "Rz"])],
    ids=["problem-10-phase-oracle", "problem-19-trotter-step"],
)
def test_the_whitelist_rejects_every_gate_but_x_and_swap_and_names_it(root, operation, gates):
    registers = Registers(inputs={"qubits": 3}, outputs={"qubits": 3})
    result = evaluate(root, spec("whitelist", operation, registers, unchanged))
    assert not result.accepted and result.verification is None, result.reason
    for gate in gates:
        assert f"{gate} (" in result.reason and gate in result.gates, result.reason


@pytest.mark.parametrize("token, source", SOURCES_THE_CHECK_REJECTS.values(), ids=SOURCES_THE_CHECK_REJECTS.keys())
def test_sources_that_could_change_what_is_counted_are_rejected(tmp_path, token, source):
    result = evaluate(project(tmp_path, source), spec("and", "Main.And(x, y)", AND, logical_and))
    assert not result.accepted and f"uses {token}," in result.reason, result.reason
    assert (result.toffoli, result.verification) == (None, None)


def test_reading_the_state_passes_every_basis_test_with_no_gate_counted(tmp_path):
    """Why the source check bans CheckZero. The circuit and the trace are built without simulating,
    and there CheckZero answers true, so this AND shows no gate at all where an AND needs a Toffoli;
    the simulator, where CheckZero reads the state, gets every input right."""
    root = project(tmp_path, AND_READING_STATE)
    checked = verify_reversible(root, "Main.And(x, y)", AND, logical_and, k=4, delta=1e-3)
    assert (checked.passed, checked.exhaustive) == (True, True), checked.report()
    entry = "{ use x = Qubit[2]; use y = Qubit[1]; Main.And(x, y); }"
    qsharp.init(project_root=str(root))
    assert json.loads(qsharp.circuit(entry, group_by_scope=False).json())["componentGrid"] == []
    trace = trace_from_entry_expr(entry)
    assert dict(trace.gate_counts() if callable(trace.gate_counts) else trace.gate_counts) == {}


@pytest.mark.parametrize(
    "root, operation, registers, reference, counts",
    [(PROBLEMS / "09_factorization" / "qsharp", "Main.ControlledMultiplyMod15(7, control[0], target)",
      Registers(inputs={"control": 1, "target": 4}, outputs={"target": 4}, big_endian=True), times_7_mod_15, (3, 5)),
     (PROBLEMS / "18_photovoltaics" / "qsharp", "Controlled Main.IncrementSite([coin[0]], position)",
      Registers(inputs={"coin": 1, "position": 8}, outputs={"position": 8}, big_endian=True), step_right_if_coin,
      (49, 15))],
    ids=["problem-09-multiplier-by-7", "problem-18-controlled-increment-8"],
)
def test_the_counts_of_two_repository_kernels(root, operation, registers, reference, counts):
    result = evaluate(root, spec("counts", operation, registers, reference))
    assert result.accepted, result.reason
    assert (result.toffoli, result.qubits, result.tq) == (*counts, counts[0] * counts[1])
    assert result.verification["method"] == "exhaustive"


@pytest.mark.parametrize("exhaustive_limit, method", [(1 << 17, "exhaustive"), (128, "sampled")],
                         ids=["exhaustive", "sampled"])
def test_a_candidate_written_against_its_own_draw_passes_the_loop_and_fails_the_held_out_check(
        tmp_path, exhaustive_limit, method):
    """The loop draws its tests from a hash of the candidate's sources, which anyone can compute.
    This candidate was revised, one comment at a time, until its own draw of 8 tests missed the 32
    values it gets wrong. The held-out check tests all 256 values, or 200 drawn from a fresh seed,
    which miss all 32 with probability (7/8)^200, about 2.5e-12; then the candidate is barred."""
    root = written_against_its_own_draw(tmp_path / "candidate", k=8)
    task = spec("copy-8", "Main.Copy(x, y)", COPY_8, copy, loop_k=8, held_out_k=200, exhaustive_limit=exhaustive_limit)
    loop = evaluate(root, task)
    assert loop.accepted and loop.verification["method"] == "sampled", loop.reason
    log = tmp_path / "attempts.jsonl"
    held_out = certify(root, task, log)
    assert not held_out.accepted and held_out.verification["method"] == method, held_out.reason
    if method == "exhaustive":
        assert held_out.verification["failed"] == len(WRONG)
    # The tests were drawn from the seed logged before they ran; an exhaustive check needs none.
    assert json.loads(log.read_text(encoding="utf-8").splitlines()[0])["seed"] == held_out.verification["seed"]
    with pytest.raises(AttemptRefused):
        certify(root, task, log)


def test_a_candidate_gets_one_held_out_attempt_whatever_it_returned(tmp_path):
    """A second draw on the same candidate would let a wrong one be drawn for until it passes. The
    log keys on the candidate's hash, so an edited candidate is a new one with an attempt of its own."""
    root = project(tmp_path / "candidate", COPY)
    task = spec("copy-3", "Main.Copy(x, y)", COPY_3, copy)
    log = tmp_path / "attempts.jsonl"
    first = certify(root, task, log)
    assert first.accepted, first.reason
    with pytest.raises(AttemptRefused, match="already had its held-out attempt"):
        certify(root, task, log)
    project(root, COPY + "// edited\n")
    second = certify(root, task, log)
    assert second.accepted and second.candidate != first.candidate, second.reason
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert [(record["event"], record["candidate"]) for record in records] == [
        ("attempt", first.candidate), ("result", first.candidate),
        ("attempt", second.candidate), ("result", second.candidate)]


def test_a_check_that_never_ends_is_stopped_and_its_attempt_was_logged_before_it_ran(tmp_path):
    """Logged first, so stopping a check, by a timeout or by killing the certifier, cannot buy a
    second draw."""
    root = project(tmp_path / "candidate", NEVER_ENDS)
    task = spec("copy-3", "Main.Copy(x, y)", COPY_3, copy)
    log = tmp_path / "attempts.jsonl"
    seen: list[str] = []

    def watch() -> None:
        deadline = time.monotonic() + 4  # inside the 5 s the check is given
        while not log.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        seen.append(log.read_text(encoding="utf-8") if log.exists() else "")

    watcher = threading.Thread(target=watch)
    watcher.start()
    stopped = certify(root, task, log, timeout=5)
    watcher.join()
    assert [json.loads(line)["event"] for line in seen[0].splitlines()] == ["attempt"]
    assert not stopped.accepted and "did not finish within 5 s" in stopped.reason, stopped.reason
    with pytest.raises(AttemptRefused):
        certify(root, task, log, timeout=5)


def test_a_check_leaves_the_callers_qsharp_interpreter_alone(tmp_path):
    """verify_reversible re-initialises the global interpreter, which in the caller's process would
    discard whatever the caller had defined."""
    qsharp.init()
    qsharp.eval("function Marker() : Int { 42 }")
    result = evaluate(project(tmp_path, COPY), spec("copy-3", "Main.Copy(x, y)", COPY_3, copy))
    assert result.accepted, result.reason
    assert qsharp.eval("Marker()") == 42


def test_the_reference_that_runs_is_the_text_read_and_logged(tmp_path):
    """A check reads its reference once; that text is what runs and what the attempt log hashes.
    Loaded from the file in the worker instead, a stale .pyc could run, because an edit of the same
    length within the same second passes the cache's timestamp check, and so could an edit made
    after the attempt was logged."""
    right = "def reference(values):\n    return {'y': values['x'] ^ 0}\n"
    wrong = right.replace("^ 0", "^ 1")
    path = tmp_path / "reference.py"
    path.write_text(wrong, encoding="utf-8")
    stamp = path.stat()
    py_compile.compile(str(path), invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    path.write_text(right, encoding="utf-8")
    os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    task = Spec(task="copy-3", operation="Main.Copy(x, y)", registers=COPY_3, reference=path)
    root = project(tmp_path / "candidate", COPY)
    looped = evaluate(root, task)
    assert looped.accepted, looped.reason

    log = tmp_path / "attempts.jsonl"

    def edit_once_logged() -> None:
        deadline = time.monotonic() + 30
        while not log.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        path.write_text(wrong, encoding="utf-8")

    editor = threading.Thread(target=edit_once_logged)
    editor.start()
    held_out = certify(root, task, log)
    editor.join()
    assert held_out.accepted, held_out.reason
    attempt = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
    assert attempt["reference_sha256"] == hashlib.sha256(right.encode("utf-8")).hexdigest()
