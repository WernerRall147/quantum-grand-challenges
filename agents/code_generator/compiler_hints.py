"""Name the fix for the compiler errors generated Q# actually hits.

The compiler locates a type error and prints the two types, and that was not enough: of 24
generations of production requests on 2026-09-25, five never compiled after two repairs,
and every final error was a type mismatch. The dominant ones were `Exp` arguments passed
through `Controlled` without the tuple, `R1Frac` given an angle, and Int where Double was
required. Each has one correct form, so the repair is told it, rather than re-deriving it
from `expected (Pauli[], Double, Qubit[]), found Double`.

Every name cited here is checked against libs/qdk_stdlib/exports.json by the tests, so a
hint can never send a repair after a function that does not exist.
"""

from __future__ import annotations

import re

_HINTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"expected \(Pauli\[\], Double, Qubit\[\]\)"),
     "`Exp(paulis, theta, qubits)` takes a Pauli[], a Double and a Qubit[] of the same length: "
     "`Exp([PauliZ, PauliZ], theta, [q0, q1])`. Through `Controlled`, the controls come first and "
     "the original arguments form ONE tuple: `Controlled Exp([control], ([PauliZ], theta, [q]))`, "
     "never `Controlled Exp([control], [PauliZ], theta, [q])`."),
    (re.compile(r"expected \(Int, Int, Qubit\)"),
     "`R1Frac(numerator, power, qubit)` takes two Ints and applies the phase 2 pi numerator / 2^power. "
     "For an angle in radians use `R1(theta, qubit)`, controlled as `Controlled R1([control], (theta, target))`. "
     "Rather than writing a QFT or phase estimation by hand, call `ApplyQFT(qubits)` / "
     "`Adjoint ApplyQFT(qubits)` or `ApplyQPE(oracle, target, phase)`, whose oracle has type "
     "`(Int, Qubit[]) => Unit is Adj + Ctl` and receives the power to apply."),
    (re.compile(r"expected \(Double, Qubit\)"),
     "Single-qubit rotations take `(theta, qubit)`: `Rz(theta, q)`, `R1(theta, q)`. Controlled: "
     "`Controlled Rz([control], (theta, q))`."),
    (re.compile(r"expected Double, found Int"),
     "Int and Double never mix in Q#. Write Double literals with a decimal point (`2.0 * PI()`, not "
     "`2 * PI()`) and convert an Int with `IntAsDouble(n)`."),
    (re.compile(r"expected Int, found Double"),
     "An Int is required. Convert a Double with `Round(x)`, `Floor(x)`, `Ceiling(x)` or `Truncate(x)`, "
     "and write Int literals without a decimal point."),
    (re.compile(r"expected BigInt, found Int|expected Int, found BigInt"),
     "BigInt and Int never mix. BigInt literals end in L (`15L`); convert with `IntAsBigInt(n)` and "
     "`BigIntAsInt(b)`. A toy instance that fits in an Int does not need BigInt at all."),
    (re.compile(r"expected Qubit\[\], found Qubit(?!\[)"),
     "A single qubit passed where a Qubit[] is expected must be wrapped: `[q]`."),
    (re.compile(r"expected Qubit, found Qubit\[\]"),
     "A Qubit[] passed where one qubit is expected: index it (`qs[0]`) or apply to every qubit with "
     "`ApplyToEach(H, qs)` (`ApplyToEachCA` inside an adjointable operation)."),
    (re.compile(r"expected Pauli\[\], found Pauli(?!\[)"),
     "`Exp` and `Measure` take a Pauli[]: write `[PauliZ]`, not `PauliZ`."),
    (re.compile(r"LogicSeparation"),
     "An operation that is `is Adj`, `is Adj + Ctl`, or used through `Adjoint`/`Controlled` must not "
     "contain `set`, `while`, `repeat`, `return` or a measurement. Compute such values in a `function`, "
     "or before the adjointable operation, and pass them in."),
)


def hints_for(error: str) -> str:
    """Advice for each recognised error in `error`, or "" when none applies."""
    lines = [f"- {hint}" for pattern, hint in _HINTS if pattern.search(error or "")]
    if not lines:
        return ""
    return "How to fix errors of this kind:\n" + "\n".join(lines)


def cited_names() -> set[str]:
    """Callables the hints tell the model to use, for the test that they all exist."""
    names: set[str] = set()
    for _, hint in _HINTS:
        names.update(re.findall(r"`(?:Adjoint |Controlled )?([A-Z][A-Za-z0-9]*)\(", hint))
    return names
