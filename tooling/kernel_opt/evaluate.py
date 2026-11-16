"""Decide whether a candidate reversible Q# kernel is right, and what it costs.

This is the evaluator of the optimisation loop planned in #298. A model proposes rewrites of a
reversible kernel and sees only what `evaluate` returns; `certify` is the held-out check a
candidate passes before it is recorded.

A candidate is a Q# project: `qsharp.json` and the `.qs` files under `src/`. A `Spec` gives the
statement that applies it to its registers (`verify_reversible.Registers`) and the Python
reference it must match. These checks run in order, and the first to fail rejects the candidate
with a reason:

1. Sources. No `.qs` file may mention
   - `Std.ResourceEstimation`, whose calls tell the trace what to count instead of letting it
     count what runs: `AccountForEstimates` adds the counts it is given;
   - `CheckZero` or `CheckAllZero`, which read the simulator's state. The circuit and the trace
     of steps 2 and 3 are built without simulating, and there both answer true, so a candidate
     could branch on them to apply one set of gates when it is tested and show another when it
     is counted. One that computes AND by reading its inputs this way passes
     `verify_reversible` on every input, with no gate in its circuit or its trace;
   - `Std.Random`, whose draws can take one branch in the run that is counted and another in
     the runs that are tested.
   The text is read as written, comments included.
2. Gates. Every gate in the compiled circuit (`qsharp.circuit`) must be X or SWAP, with any
   number of controls. Such a circuit permutes basis states, so its action on them, which step
   4 tests, is all there is to it, and each test is exact. Any other gate is rejected and
   named: with H, Z or a rotation an operation can change phases that basis-state tests do not
   see, as problem 10's oracle does, and a measurement or a reset is not reversible.
3. Cost. T is the number of Toffoli gates (CCX) and Q the most qubits allocated at once, both
   read from the qdk trace as `tooling/estimator_config.py` reads them. The score is T x Q, the
   measure of Gu, Kemeny, Yelin and Lukin (arXiv:2610.22367v1, Eq. 22). The trace leaves out
   Clifford gates, so after step 2 it can count only CCX; anything else means the circuit and
   the trace disagree, and the candidate is rejected.
4. Correctness. `tooling/verify_reversible.py` checks the operation against the reference on
   basis-state inputs.

`evaluate` is the loop's check. Its tests come from `verify_reversible`'s default seed, a hash
of the candidate's sources, so any edit draws new tests. Anyone can compute that draw, though,
and a candidate revised with its draw known can pass tests it would otherwise fail, so a pass
there ranks candidates and is never recorded.

`certify` is the held-out check. Before any test runs, it appends the candidate's hash to an
attempts log with a seed drawn by `secrets.randbits(64)` and the SHA-256 of the reference, read
once: that text is the reference that runs. It then tests every input when there
are at most `exhaustive_limit` or `held_out_k` of them, and otherwise `held_out_k` inputs drawn
from that seed.
A candidate gets one attempt: `certify` refuses a second for a hash already in the log, whatever
the first returned, so a failed attempt bars the candidate for good, and so does one stopped
before it finished. Run one certifier at a time on a log.

Each check runs in a Python process of its own, because `verify_reversible` re-initialises the
global Q# interpreter, and so that a candidate that never halts can be stopped after `timeout`
seconds.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import types
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tooling.verify_reversible import Registers, harness_source, project_sources  # noqa: E402

WHITELIST = frozenset({"X", "SWAP"})
TOFFOLI = "CCX"
HELD_OUT_SEED_SOURCE = "secrets.randbits(64), drawn after the candidate was hashed and logged"

_NAMESPACE = "KernelOptEvaluate"
_ENTRY = f"{_NAMESPACE}.Apply()"
_BANNED = (
    (re.compile(r"ResourceEstimation"),
     "Std.ResourceEstimation tells the trace what to count instead of letting it count what runs"),
    (re.compile(r"\bCheck(?:All)?Zero\b"),
     "it reads the simulator's state and answers true when the circuit and the trace are built, so a "
     "candidate could apply one set of gates when it is tested and show another when it is counted"),
    (re.compile(r"\bRandom\b|\bDrawRandom\w*"),
     "a random draw can take one branch in the run that is counted and another in the runs that are tested"),
)


@dataclass(frozen=True)
class Spec:
    """What a candidate must do, and how hard it is tested.

    task: names the task. A candidate gets one held-out attempt per task.
    operation: a Q# statement that applies the candidate to the registers by name, as
        `verify_reversible` takes it, for example "Controlled Main.IncrementSite([coin[0]], position)".
    registers: the registers that statement uses.
    reference: a Python file, and reference_function a function in it, that maps the input
        register values to the output register values, as `verify_reversible` takes it.
    loop_k: the tests `evaluate` runs, or every input when there are at most loop_k.
    held_out_k, exhaustive_limit: `certify` tests every input when there are at most
        exhaustive_limit or held_out_k of them, and otherwise held_out_k inputs drawn from a
        fresh seed.
    delta: one minus the confidence of `verify_reversible`'s bound on a sampled check.
    """

    task: str
    operation: str
    registers: Registers
    reference: str | Path
    reference_function: str = "reference"
    loop_k: int = 1000
    held_out_k: int = 7000
    delta: float = 1e-3
    exhaustive_limit: int = 1 << 17

    def __post_init__(self) -> None:
        if not self.task.strip() or not self.operation.strip():
            raise ValueError("a spec needs a task name and an operation")
        reference = Path(self.reference).resolve()
        if reference.suffix != ".py" or not reference.is_file():
            raise ValueError(f"the reference must be a Python file, not {self.reference}")
        object.__setattr__(self, "reference", reference)
        if not self.reference_function.isidentifier():
            raise ValueError(f"{self.reference_function!r} is not a Python function name")
        for name in ("loop_k", "held_out_k", "exhaustive_limit"):
            value = getattr(self, name)
            if not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer, not {value!r}")
        if not 0 < self.delta < 1:
            raise ValueError(f"delta must lie strictly between 0 and 1, not {self.delta!r}")

    @property
    def domain_size(self) -> int:
        """How many values the input registers can hold together."""
        return 1 << sum(self.registers.inputs.values())


@dataclass(frozen=True)
class Evaluation:
    """What the evaluator decided about one candidate.

    mode: "loop" from `evaluate`, "held-out" from `certify`.
    candidate: `candidate_hash` of what was checked.
    reason: why the candidate was rejected, or what the correctness check found when it was not.
    gates: every gate in the compiled circuit, "X/ctl2" for an X with two controls; empty if the
        candidate was rejected before the circuit was built.
    toffoli, qubits: T and Q from the trace, or None if the candidate was rejected first.
    verification: what `verify_reversible` found, or None if it did not run.
    qdk: the qdk version that built the circuit and the trace, which fixes how many Toffolis a
        gate with many controls costs.
    """

    mode: str
    task: str
    candidate: str
    accepted: bool
    reason: str
    gates: dict[str, int] = field(default_factory=dict)
    toffoli: int | None = None
    qubits: int | None = None
    verification: dict[str, Any] | None = None
    qdk: str | None = None

    @property
    def tq(self) -> int | None:
        """T x Q, the score to lower."""
        return None if self.toffoli is None or self.qubits is None else self.toffoli * self.qubits


class AttemptRefused(RuntimeError):
    """`certify` was asked for a second held-out attempt on a candidate that already had one."""


def candidate_hash(project_root: str | Path, spec: Spec) -> str:
    """The SHA-256 of what `verify_reversible` hashes for its default seed: the project's
    `qsharp.json`, every `.qs` file under `src/`, and the harness that applies the operation."""
    digest = hashlib.sha256()
    for name, text in [*project_sources(project_root), ("<harness>", harness_source(spec.operation, spec.registers))]:
        for part in (name, text):
            data = part.encode("utf-8")
            digest.update(len(data).to_bytes(8, "big") + data)
    return digest.hexdigest()


def evaluate(project_root: str | Path, spec: Spec, *, timeout: float = 600.0) -> Evaluation:
    """The loop's check: sources, gates, cost, then `spec.loop_k` tests from the default seed.

    The candidate is copied first, and the copy is what is hashed and checked, so the project
    can change while this runs.
    """
    with tempfile.TemporaryDirectory(prefix="kernel-opt-", ignore_cleanup_errors=True) as scratch:
        scratch = Path(scratch)
        snapshot = _snapshot(project_root, scratch / "candidate")
        candidate = candidate_hash(snapshot, spec)
        banned = _banned(snapshot)
        if banned:
            return Evaluation("loop", spec.task, candidate, False, banned)
        reference = spec.reference.read_text(encoding="utf-8")
        return _run(scratch, snapshot, spec, reference, "loop", candidate, spec.loop_k, None, timeout)


def certify(project_root: str | Path, spec: Spec, log: str | Path, *, timeout: float = 3600.0) -> Evaluation:
    """The held-out check, once per candidate and task, recorded in the attempts log `log`.

    Raises AttemptRefused, and appends nothing, if the log already holds an attempt on this
    candidate for this task. Otherwise appends the attempt, with its seed and the SHA-256 of the
    reference, before any test runs, and the result when the check ends, whether the candidate
    passed, failed or was stopped. The reference is read once, and that text is what runs.
    """
    log = Path(log)
    with tempfile.TemporaryDirectory(prefix="kernel-opt-", ignore_cleanup_errors=True) as scratch:
        scratch = Path(scratch)
        snapshot = _snapshot(project_root, scratch / "candidate")
        candidate = candidate_hash(snapshot, spec)
        for record in _records(log):
            if record.get("event") == "attempt" and (record.get("task"), record.get("candidate")) == (spec.task, candidate):
                raise AttemptRefused(
                    f"candidate {candidate} already had its held-out attempt on task {spec.task!r}, at "
                    f"{record.get('at')}. A second would void the guarantee of the first, so it is refused.")
        # verify_reversible tests every input whenever there are at most k of them.
        exhaustive = spec.domain_size <= max(spec.exhaustive_limit, spec.held_out_k)
        k = spec.domain_size if exhaustive else spec.held_out_k
        seed = None if exhaustive else secrets.randbits(64)
        reference = spec.reference.read_text(encoding="utf-8")
        _append(log, {
            "event": "attempt", "task": spec.task, "candidate": candidate, "operation": spec.operation,
            "registers": _registers(spec.registers), "reference": _shown(spec.reference),
            "reference_function": spec.reference_function,
            "reference_sha256": hashlib.sha256(reference.encode("utf-8")).hexdigest(),
            "method": "exhaustive" if exhaustive else "sampled", "k": k, "domain_size": spec.domain_size,
            "delta": spec.delta, "seed": seed, "seed_source": None if exhaustive else HELD_OUT_SEED_SOURCE,
            "at": _now(),
        })
        banned = _banned(snapshot)
        result = (Evaluation("held-out", spec.task, candidate, False, banned) if banned
                  else _run(scratch, snapshot, spec, reference, "held-out", candidate, k, seed, timeout))
        _append(log, {
            "event": "result", "task": spec.task, "candidate": candidate, "accepted": result.accepted,
            "reason": result.reason, "gates": result.gates, "toffoli": result.toffoli, "qubits": result.qubits,
            "tq": result.tq, "verification": result.verification, "qdk": result.qdk, "at": _now(),
        })
        return result


def _snapshot(project_root: str | Path, destination: Path) -> Path:
    root = Path(project_root)
    if not (root / "qsharp.json").is_file() or not (root / "src").is_dir():
        raise ValueError(f"{root} is not a Q# project: it needs qsharp.json and a src folder")
    for name, _ in project_sources(root):
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    return destination


def _banned(project: Path) -> str | None:
    for name, text in project_sources(project):
        if not name.endswith(".qs"):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for pattern, why in _BANNED:
                match = pattern.search(line)
                if match:
                    return f"{name} line {number} uses {match.group(0)}, which is not allowed: {why}"
    return None


def _run(scratch: Path, snapshot: Path, spec: Spec, reference: str, mode: str, candidate: str, k: int,
         seed: int | None, timeout: float) -> Evaluation:
    request = {
        "project": str(snapshot), "operation": spec.operation, "registers": _registers(spec.registers),
        "reference": str(spec.reference), "reference_source": reference,
        "reference_function": spec.reference_function, "k": k, "delta": spec.delta, "seed": seed,
    }
    request_path, result_path = scratch / "request.json", scratch / "result.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    # PYTHONPATH as well as cwd, so the worker imports this repository's tooling even with
    # PYTHONSAFEPATH set; utf-8 because the simulator's messages contain non-ASCII characters.
    env = {**os.environ, "PYTHONIOENCODING": "utf-8",
           "PYTHONPATH": os.pathsep.join(filter(None, [str(REPO_ROOT), os.environ.get("PYTHONPATH")]))}
    try:
        done = subprocess.run(
            [sys.executable, "-m", "tooling.kernel_opt.evaluate", str(request_path), str(result_path)],
            cwd=REPO_ROOT, env=env, capture_output=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return Evaluation(mode, spec.task, candidate, False, f"its check did not finish within {timeout:g} s and was stopped")
    if done.returncode != 0 or not result_path.is_file():
        output = (done.stderr or done.stdout).decode("utf-8", "replace").strip().splitlines()
        tail = " | ".join(line.strip() for line in output[-3:]) or "no output"
        return Evaluation(mode, spec.task, candidate, False, f"its check stopped with exit code {done.returncode}: {tail}")
    return Evaluation(mode, spec.task, candidate, **json.loads(result_path.read_text(encoding="utf-8")))


def _records(log: Path) -> list[dict[str, Any]]:
    if not log.exists():
        return []
    records = []
    for number, line in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{log} line {number} is not JSON; repair the log before certifying anything") from error
    return records


def _append(log: Path, record: Mapping[str, Any]) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _registers(registers: Registers) -> dict[str, Any]:
    return {"inputs": dict(registers.inputs), "outputs": dict(registers.outputs),
            "ancillas": dict(registers.ancillas), "big_endian": registers.big_endian}


def _shown(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- The worker: everything below runs in the separate process. ---


def _check(request: Mapping[str, Any]) -> dict[str, Any]:
    from qdk import qsharp
    from qdk.qre import instruction_name
    from qdk.qre.interop import trace_from_entry_expr

    from tooling.verify_reversible import verify_reversible

    registers = Registers(**request["registers"])
    found: dict[str, Any] = {"accepted": False, "gates": {}, "toffoli": None, "qubits": None,
                             "verification": None, "qdk": importlib.metadata.version("qdk")}
    try:
        qsharp.init(project_root=request["project"])
        qsharp.eval(_wrapper(request["operation"], registers))
    except qsharp.QSharpError as error:
        return {**found, "reason": f"it does not compile: {_describe(error)}"}
    try:
        circuit = json.loads(qsharp.circuit(_ENTRY, group_by_scope=False).json())
    except qsharp.QSharpError as error:
        return {**found, "reason": f"its circuit could not be built: {_describe(error)}"}
    found["gates"], others = _gates(circuit)
    if others:
        return {**found, "reason": f"its circuit contains {_listing(others)}; only X and SWAP, with any number "
                                   f"of controls, are allowed"}
    try:
        trace = trace_from_entry_expr(_ENTRY)
    except qsharp.QSharpError as error:
        return {**found, "reason": f"it could not be traced: {_describe(error)}"}
    raw = trace.gate_counts() if callable(trace.gate_counts) else trace.gate_counts
    counted: Counter[str] = Counter()
    for instruction, count in dict(raw).items():
        counted[str(instruction_name(instruction))] += count
    unexpected = {name: count for name, count in counted.items() if name != TOFFOLI}
    if unexpected:
        return {**found, "reason": f"its trace counts {_listing(unexpected)}, which X and SWAP gates do not "
                                   f"make, so the circuit and the trace disagree"}
    found["toffoli"], found["qubits"] = counted[TOFFOLI], trace.total_qubits
    reference = _load_reference(request["reference"], request["reference_source"], request["reference_function"])
    try:
        verification = verify_reversible(request["project"], request["operation"], registers, reference,
                                         k=request["k"], delta=request["delta"], seed=request["seed"])
    except qsharp.QSharpError as error:
        return {**found, "reason": f"its correctness check could not run: {_describe(error)}"}
    sampled = not verification.exhaustive
    found["verification"] = {
        "passed": verification.passed, "method": "sampled" if sampled else "exhaustive",
        "k": verification.k, "domain_size": verification.domain_size, "delta": verification.delta,
        "epsilon_bound": verification.epsilon_bound, "seed": verification.seed if sampled else None,
        "seed_source": verification.seed_source if sampled else None, "failed": verification.failed,
        "failures": [failure.describe() for failure in verification.failures],
        "outcome": verification.outcome().strip(),
    }
    return {**found, "accepted": verification.passed, "reason": verification.outcome().strip()}


def _wrapper(operation: str, registers: Registers) -> str:
    """An entry point that allocates the registers in |0> and applies the operation once."""
    allocate = "".join(f"        use {name} = Qubit[{width}];\n" for name, width in registers.layout)
    call = operation.strip().rstrip(";").strip()
    return (f"namespace {_NAMESPACE} {{\n"
            f"    operation Apply() : Unit {{\n"
            f"{allocate}"
            f"        {call};\n"
            f"    }}\n"
            f"}}\n")


def _gates(circuit: Mapping[str, Any]) -> tuple[dict[str, int], dict[str, int]]:
    """Every gate in a `qsharp.circuit` diagram, and those outside the whitelist.

    Groups are opened, so only gates are counted. A gate is named as the diagram names it, with
    "/ctl2" for two controls; measurements and resets are named as such.
    """
    gates: Counter[str] = Counter()
    others: Counter[str] = Counter()
    columns = list(circuit.get("componentGrid", []))
    while columns:
        for component in columns.pop().get("components", []):
            if component.get("children"):
                columns.extend(component["children"])
                continue
            kind, gate = component.get("kind"), component.get("gate")
            controls = len(component.get("controls") or [])
            if kind == "unitary":
                name = f"{gate}/ctl{controls}" if controls else str(gate)
            else:
                name = {"measurement": "measurement", "ket": "reset"}.get(kind, f"{kind} {gate}")
            gates[name] += 1
            if kind != "unitary" or gate not in WHITELIST:
                others[name] += 1
    return dict(sorted(gates.items())), dict(sorted(others.items()))


def _listing(counts: Mapping[str, int]) -> str:
    return ", ".join(f"{name} ({count})" for name, count in sorted(counts.items()))


def _describe(error: Exception) -> str:
    """The error's first line, and what its diagnostic points at."""
    lines = [line.strip() for line in str(error).splitlines() if line.strip()]
    if not lines:
        return repr(error)
    head = lines[0].removeprefix("Error:").strip()
    details = [line.removeprefix("`->").strip() for line in lines if line.startswith("`->")]
    details = [detail for detail in details if detail not in head]
    return f"{head} ({'; '.join(details)})" if details else head


def _load_reference(path: str, source: str, function: str) -> Callable[[Mapping[str, int]], Mapping[str, int]]:
    """The reference function, compiled from the text the parent read: not from the file, which
    may have changed since, and not from a cached .pyc, whose check is only a timestamp and size."""
    module = types.ModuleType("kernel_opt_reference")
    module.__file__ = path
    sys.modules[module.__name__] = module
    exec(compile(source, path, "exec"), module.__dict__)
    return getattr(module, function)


def _worker(request_path: str, result_path: str) -> None:
    request = json.loads(Path(request_path).read_text(encoding="utf-8"))
    Path(result_path).write_text(json.dumps(_check(request)), encoding="utf-8")


if __name__ == "__main__":
    _worker(*sys.argv[1:])
