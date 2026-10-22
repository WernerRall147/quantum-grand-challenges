"""Check a Q# operation that maps computational-basis states to computational-basis states.

`verify_reversible` runs the operation on k basis-state inputs and checks each against a
Python reference: every output register holds the reference value, every input register that
is not also an output is unchanged, and every ancilla is back in |0>. It then states the
guarantee Gu, Kemeny, Yelin and Lukin give for sampled tests (arXiv:2610.22367v1, Methods,
"Validation and statistical guarantees", Eq. 20): for a candidate fixed before the test draw,
if all k independent tests pass, then with confidence 1 - delta the failure probability
epsilon under the test distribution satisfies epsilon <= 1 - delta^(1/k), approximately
ln(1/delta)/k. Here the test distribution is uniform over every value of the input
registers, drawn with replacement, and the bound needs the draw to be independent of the
candidate (see "When the bound holds", below). When there are at most k such values, every
one is checked and the result is exhaustive rather than statistical.

How one input is checked. The harness allocates the registers, sets the input value, applies
the operation, then applies X wherever the expected final state has a 1. A correct operation
now leaves every qubit in |0>. The qdk 1.31.0 simulator raises `ReleasedQubitNotZero` when a
qubit is released away from |0>, and it does not sample: a qubit left in |+> raises every
time. It has a numerical tolerance, though: a qubit with a probability of 2.5e-9 of reading 1
(after Ry(1e-4)) raises every time, and one with 1e-10 (after Ry(2e-5)) never does
(tooling/test_verify_reversible.py holds these facts in place). So a wrong output, a changed
input, a dirty ancilla, a superposition, and an ancilla the operation allocates itself and
leaves dirty, all fail, unless the error is that small. For an operation that only permutes
basis states, as X, CNOT, SWAP and Toffoli gates and their controlled forms do, each check is
exact. An operation with rotations can be wrong by less than the tolerance and pass, even on
every input. Each input runs in its own simulator, through `qsharp.run`. Any runtime error
counts as a failure on that input; the input is then run once more with every register
measured, to report what came out.

What it does not check: phases. The paper's evaluator also compares the phase with the
target, and its bound on the distance between the candidate's and the target's states (Eq. 19)
needs that; this check does not give it.

The default seed is the SHA-256 of the Q# sources involved: the project's `qsharp.json`,
every `.qs` file under its `src/`, and the generated harness, which contains the call and the
register layout. Changing any of them draws new tests, as Gu et al.'s evaluator draws its test
inputs from a hash of the emitted circuit (github.com/andigu/uncompute, README). Line endings
are normalised so that a Windows checkout and CI draw the same tests. The seed is printed so a
failure can be reproduced by passing it back.

When the bound holds. Eq. 20 is for one draw of k tests that is independent of the candidate.
The default seed is a function of the candidate's own sources that anyone can compute, so it
gives that independence only if the candidate was not revised, or chosen among variants, with
its draw known: a candidate made to pass its own draw can be wrong on every input outside it.
Drawing again with new seeds until one passes voids the bound in the same way. A given seed
reproduces a run; it is fresh evidence only if it was drawn at random after the candidate was
fixed, for example with `secrets.randbits(64)`. The report says which case applies.
"""

from __future__ import annotations

import hashlib
import itertools
import math
import operator
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator, Mapping, Sequence

from qdk import qsharp

CITATION = 'Gu, Kemeny, Yelin, Lukin, arXiv:2610.22367v1, Methods, "Validation and statistical guarantees", Eq. 20'
SEED_FROM_SOURCES = "SHA-256 of the Q# sources"

_NAMESPACE = "VerifyReversible"
_IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
# Names the generated harness uses for its own variables.
_RESERVED = frozenset({"verifyBefore", "verifyAfter", "verifyQubits", "verifyIndex", "verifyBits", "verifyQubit"})


@dataclass(frozen=True)
class Registers:
    """The qubit registers an operation acts on, each a `Qubit[]` of the given width.

    inputs: set to the test value before the call, and must be unchanged afterwards unless
        the register is also an output.
    outputs: must hold the reference value afterwards. An output that is not an input starts
        in |0>; one that is also an input is updated in place, like a multiplier's target.
    ancillas: start in |0> and must end in |0>.
    big_endian: qubit 0 of each register holds its most significant bit. The default is the
        Q# standard library's convention, qubit 0 the least significant.
    """

    inputs: Mapping[str, int]
    outputs: Mapping[str, int] = field(default_factory=dict)
    ancillas: Mapping[str, int] = field(default_factory=dict)
    big_endian: bool = False

    def __post_init__(self) -> None:
        for role in ("inputs", "outputs", "ancillas"):
            registers = dict(getattr(self, role))
            for name, width in registers.items():
                if not _IDENTIFIER.fullmatch(name) or name in _RESERVED:
                    raise ValueError(f"{role}: {name!r} is not a usable Q# register name")
                if not isinstance(width, int) or width < 1:
                    raise ValueError(f"{role}: {name} needs a positive integer width, not {width!r}")
            object.__setattr__(self, role, registers)
        for name, width in self.outputs.items():
            if name in self.inputs and self.inputs[name] != width:
                raise ValueError(f"{name} is an input of width {self.inputs[name]} and an output of width {width}")
        shared = set(self.ancillas) & (set(self.inputs) | set(self.outputs))
        if shared:
            raise ValueError(f"ancillas cannot also be inputs or outputs: {sorted(shared)}")
        if not self.layout:
            raise ValueError("no registers")

    @property
    def layout(self) -> tuple[tuple[str, int], ...]:
        """Each register once, in allocation order: inputs, then outputs, then ancillas."""
        widths = {**self.inputs, **self.outputs, **self.ancillas}
        return tuple(widths.items())

    def bits(self, values: Mapping[str, int]) -> list[bool]:
        """One bit per qubit, in allocation order, for the given register values."""
        out: list[bool] = []
        for name, width in self.layout:
            bits = [bool(values[name] >> i & 1) for i in range(width)]
            out += bits[::-1] if self.big_endian else bits
        return out

    def values(self, bits: Sequence[bool]) -> dict[str, int]:
        """The inverse of `bits`."""
        out, start = {}, 0
        for name, width in self.layout:
            chunk = list(bits[start:start + width])
            start += width
            ordered = chunk[::-1] if self.big_endian else chunk
            out[name] = sum(1 << i for i, bit in enumerate(ordered) if bit)
        return out


@dataclass(frozen=True)
class Failure:
    """One input on which the operation did not do what the reference says.

    `observed` holds every register as measured once after the call, or None when the
    operation itself raised. `error` is the simulator's message and where it was raised.
    """

    inputs: dict[str, int]
    expected: dict[str, int]
    observed: dict[str, int] | None
    error: str

    def describe(self) -> str:
        line = f"input {_show(self.inputs)}: expected {_show(self.expected)}, "
        if self.observed is None:
            line += "observed nothing, the operation raised"
        elif self.observed == self.expected:
            line += f"measured {_show(self.observed)}, but the state was not that basis state"
        else:
            line += f"observed {_show(self.observed)}"
        return f"{line}. {self.error}"


@dataclass(frozen=True)
class Verification:
    """What `verify_reversible` found.

    k: inputs checked. When exhaustive, every value of the input registers, so the domain size.
    epsilon_bound: 1 - delta^(1/k) if every sampled test passed, 0.0 if every input passed an
        exhaustive check, None if any test failed, when no bound holds. The sampled bound holds
        only if the inputs were independent of the candidate, and 0.0 means that no input failed
        a check, which is exact only for an operation that permutes basis states (see the module
        docstring). `outcome()` states both conditions.
    failures: the first few failures, each with its input and what came out.
    """

    operation: str
    k: int
    delta: float
    epsilon_bound: float | None
    exhaustive: bool
    seed: int
    seed_source: str
    domain_size: int
    failed: int
    failures: tuple[Failure, ...]

    @property
    def passed(self) -> bool:
        return self.failed == 0

    def header(self) -> str:
        return (f"verify_reversible: {self.operation}\n"
                f"  seed {self.seed} ({self.seed_source}); pass seed={self.seed} to reproduce")

    def outcome(self) -> str:
        scope = (f"exhaustive, all {self.k} inputs" if self.exhaustive else
                 f"sampled, {self.k} inputs drawn uniformly with replacement from {self.domain_size}")
        if not self.passed:
            lines = [f"  FAILED on {self.failed} of {self.k} inputs ({scope}). No guarantee holds."]
            lines += [f"    {failure.describe()}" for failure in self.failures]
            if self.failed > len(self.failures):
                lines.append(f"    ... and {self.failed - len(self.failures)} more")
            return "\n".join(lines)
        exactness = ("Each check is exact for an operation that only permutes basis states, as X, CNOT, "
                     "SWAP and Toffoli gates do; otherwise a final state within the simulator's numerical "
                     "tolerance of the expected one also passes. Phases are not checked.")
        if self.exhaustive:
            return f"  passed ({scope}). Not statistical: every input was checked. {exactness}"
        return (f"  passed ({scope}). If these inputs are independent of the candidate, then with "
                f"confidence 1 - delta = {1 - self.delta:g}, its failure probability under this test "
                f"distribution is at most 1 - delta^(1/k) = {self.epsilon_bound:.4g} (ln(1/delta)/k = "
                f"{math.log(1 / self.delta) / self.k:.4g}); {CITATION}. {self.independence()} {exactness}")

    def independence(self) -> str:
        """Whether the sampled inputs can be independent of the candidate, as the bound needs."""
        if self.seed_source == SEED_FROM_SOURCES:
            return ("The inputs come from a seed hashed from the candidate's own sources, which anyone "
                    "can compute, so they are independent of it only if it was not revised or chosen "
                    "with its draw known.")
        return ("The seed was given, so the inputs are independent of the candidate only if the seed "
                "was drawn at random after the candidate was fixed; a replay of an earlier run's seed "
                "reproduces that run and adds no evidence.")

    def report(self) -> str:
        return f"{self.header()}\n{self.outcome()}"


def epsilon_bound(k: int, delta: float) -> float:
    """1 - delta^(1/k), the bound of Eq. 20, computed so it stays accurate for large k."""
    return -math.expm1(math.log(delta) / k)


def harness_source(operation: str, registers: Registers) -> str:
    """The Q# that checks one input (`Check`) and reports what came out (`Observe`)."""
    allocate = "".join(f"        use {name} = Qubit[{width}];\n" for name, width in registers.layout)
    gather = " + ".join(name for name, _ in registers.layout)
    call = operation.strip().rstrip(";").strip()
    prepare = (f"{allocate}"
               f"        let verifyQubits = {gather};\n"
               f"        for verifyIndex in 0..Length(verifyQubits) - 1 {{\n"
               f"            if verifyBefore[verifyIndex] {{ X(verifyQubits[verifyIndex]); }}\n"
               f"        }}\n"
               f"        {call};\n")
    return (f"namespace {_NAMESPACE} {{\n"
            f"    operation Check(verifyBefore : Bool[], verifyAfter : Bool[]) : Unit {{\n"
            f"{prepare}"
            f"        // Undo the expected final state, leaving every qubit in |0> if the operation\n"
            f"        // is right. Releasing a qubit in any other state raises.\n"
            f"        for verifyIndex in 0..Length(verifyQubits) - 1 {{\n"
            f"            if verifyAfter[verifyIndex] {{ X(verifyQubits[verifyIndex]); }}\n"
            f"        }}\n"
            f"    }}\n"
            f"\n"
            f"    operation Observe(verifyBefore : Bool[]) : Bool[] {{\n"
            f"{prepare}"
            f"        mutable verifyBits = [];\n"
            f"        for verifyQubit in verifyQubits {{\n"
            f"            set verifyBits += [MResetZ(verifyQubit) == One];\n"
            f"        }}\n"
            f"        verifyBits\n"
            f"    }}\n"
            f"}}\n")


def project_sources(project_root: str | Path) -> list[tuple[str, str]]:
    """(relative path, text) of the manifest and every `.qs` file under `src/`, in path order."""
    root = Path(project_root)
    paths = [root / "qsharp.json", *(root / "src").rglob("*.qs")]
    # Sorted as strings: Path order ignores case on Windows and not on Linux. read_text turns
    # \r\n into \n, so a Windows checkout hashes as CI's does.
    named = sorted((path.relative_to(root).as_posix(), path) for path in paths if path.is_file())
    return [(name, path.read_text(encoding="utf-8")) for name, path in named]


def default_seed(project_root: str | Path, operation: str, registers: Registers) -> int:
    """The first 8 bytes of the SHA-256 of the project's Q# sources and the generated harness."""
    digest = hashlib.sha256()
    for name, text in [*project_sources(project_root), ("<harness>", harness_source(operation, registers))]:
        for part in (name, text):
            data = part.encode("utf-8")
            digest.update(len(data).to_bytes(8, "big") + data)
    return int.from_bytes(digest.digest()[:8], "big")


def verify_reversible(
    project_root: str | Path,
    operation: str,
    registers: Registers,
    reference: Callable[[Mapping[str, int]], Mapping[str, int]],
    *,
    k: int,
    delta: float,
    seed: int | None = None,
    max_failures: int = 5,
) -> Verification:
    """Check `operation` against `reference` on k inputs, or on every input if there are at most k.

    project_root: a Q# project, a folder with `qsharp.json` and `src/`. This re-initialises the
        global Q# interpreter with it.
    operation: a Q# statement that applies the operation to the registers by name, each a
        `Qubit[]`, for example "Main.ControlledMultiplyMod15(7, control[0], target)".
    reference: maps the input register values to the output register values, one entry per
        output register.
    k, delta: the number of tests, and one minus the confidence of the bound.
    seed: draws the inputs; by default `default_seed`. Printed either way. A given seed
        reproduces a run, and is fresh evidence only if drawn at random after the candidate was
        fixed.
    """
    if not isinstance(k, int) or k < 1:
        raise ValueError(f"k must be a positive integer, not {k!r}")
    if not 0 < delta < 1:
        raise ValueError(f"delta must lie strictly between 0 and 1, not {delta!r}")
    seed_source = "given"
    if seed is None:
        seed, seed_source = default_seed(project_root, operation, registers), SEED_FROM_SOURCES
    print(f"verify_reversible: {operation}: seed {seed} ({seed_source})", flush=True)

    qsharp.init(project_root=str(project_root))
    qsharp.eval(harness_source(operation, registers))

    domain_size = 1 << sum(registers.inputs.values())
    exhaustive = domain_size <= k
    tests = list(_every_input(registers) if exhaustive else _sampled_inputs(registers, k, seed))
    failed, failures = 0, []
    for inputs in tests:
        expected = _expected(registers, inputs, reference)
        before = registers.bits({**{name: 0 for name, _ in registers.layout}, **inputs})
        try:
            _run(f"{_NAMESPACE}.Check({_qs_bools(before)}, {_qs_bools(registers.bits(expected))})")
        except qsharp.QSharpError as error:
            failed += 1
            if len(failures) < max_failures:
                failures.append(Failure(dict(inputs), expected, _observe(registers, before), _summary(error)))

    result = Verification(
        operation=operation,
        k=len(tests),
        delta=delta,
        epsilon_bound=None if failed else 0.0 if exhaustive else epsilon_bound(len(tests), delta),
        exhaustive=exhaustive,
        seed=seed,
        seed_source=seed_source,
        domain_size=domain_size,
        failed=failed,
        failures=tuple(failures),
    )
    print(result.outcome(), flush=True)
    return result


def _every_input(registers: Registers) -> Iterator[dict[str, int]]:
    names = list(registers.inputs)
    for values in itertools.product(*(range(1 << registers.inputs[name]) for name in names)):
        yield dict(zip(names, values))


def _sampled_inputs(registers: Registers, k: int, seed: int) -> Iterator[dict[str, int]]:
    rng = random.Random(seed)
    for _ in range(k):
        yield {name: rng.getrandbits(width) for name, width in registers.inputs.items()}


def _expected(registers: Registers, inputs: Mapping[str, int], reference) -> dict[str, int]:
    produced = dict(reference(dict(inputs)))
    if set(produced) != set(registers.outputs):
        raise ValueError(f"the reference returned {sorted(produced)} for {dict(inputs)}; "
                         f"it must return exactly the outputs {sorted(registers.outputs)}")
    expected = {}
    for name, width in registers.layout:
        if name in registers.outputs:
            value = operator.index(produced[name])
            if not 0 <= value < 1 << width:
                raise ValueError(f"the reference gave {name} = {value} for {dict(inputs)}, "
                                 f"which does not fit in {width} qubits")
            expected[name] = value
        else:
            expected[name] = inputs.get(name, 0)
    return expected


def _observe(registers: Registers, before: list[bool]) -> dict[str, int] | None:
    try:
        bits = _run(f"{_NAMESPACE}.Observe({_qs_bools(before)})")
    except qsharp.QSharpError:
        return None
    return registers.values(bits)


def _run(expression: str):
    # One shot, its own simulator. save_events keeps the operation's messages off stdout.
    return qsharp.run(expression, shots=1, save_events=True)[0]["result"]


def _qs_bools(bits: Sequence[bool]) -> str:
    return "[" + ", ".join("true" if bit else "false" for bit in bits) + "]"


def _summary(error: Exception) -> str:
    """The simulator's message and the innermost frame outside the runtime library."""
    lines = str(error).splitlines()
    message = lines[0].removeprefix("Error: ").strip() if lines else repr(error)
    frames = [line.strip() for line in lines if line.strip().startswith("at ") and "QIR.Runtime" not in line]
    return f"{message} ({frames[0]})" if frames else message


def _show(values: Mapping[str, int]) -> str:
    return " ".join(f"{name}={value}" for name, value in values.items())
