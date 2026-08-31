"""The generator kept emitting Q# that was removed from the language.

Three of four beat-3 runs on 2026-08-31 failed on `new Result[n]` or `ConstantArray`,
and the repair loop could not fix them across three attempts: the compiler says
`expected `{`, found `[`', which locates the error without naming the replacement.
The parenthesised-for-loop rule shows the shape that works - state the modern form.

These tests assert the rule is present and that the examples we hand the model do not
themselves contain the syntax we are telling it to avoid.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agents.code_generator.generate import (
    DEFAULT_REFERENCE,
    REFERENCE_IMPLEMENTATIONS,
    SYSTEM_PROMPT,
    QSharpCodeGenerator,
)

ROOT = Path(__file__).resolve().parents[2]

# `new Result[0]`, `new Int[n]`, `new Qubit[Length(xs)]` - removed in QDK 1.0.
LEGACY_NEW_ARRAY = re.compile(r"\bnew\s+[A-Za-z_][A-Za-z0-9_]*\s*\[")


def test_prompt_bans_legacy_array_construction():
    assert "new Result[n]" in SYSTEM_PROMPT or "new T[n]" in SYSTEM_PROMPT, \
        "the prompt never mentions `new T[n]`, the most common observed failure"


def test_prompt_supplies_the_modern_array_replacement():
    """Naming the banned form is not enough - the compiler already does that."""
    assert "size =" in SYSTEM_PROMPT, "prompt bans `new T[n]` without giving `[value, size = n]`"
    assert "Repeated" in SYSTEM_PROMPT, "prompt does not name Repeated as the ConstantArray replacement"


def test_prompt_bans_constantarray():
    assert "ConstantArray" in SYSTEM_PROMPT, \
        "`ConstantArray` is not in the modern stdlib and the model reaches for it"


@pytest.mark.parametrize("algorithm", sorted(REFERENCE_IMPLEMENTATIONS))
def test_reference_implementations_exist(algorithm):
    path = ROOT / REFERENCE_IMPLEMENTATIONS[algorithm]
    assert path.exists(), f"{algorithm} points at {path}, which is not there"


def test_default_reference_exists():
    assert (ROOT / DEFAULT_REFERENCE).exists()


@pytest.mark.parametrize(
    "rel", sorted(set(REFERENCE_IMPLEMENTATIONS.values()) | {DEFAULT_REFERENCE})
)
def test_references_do_not_teach_legacy_syntax(rel):
    """A reference containing the banned form would be teaching the error."""
    source = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    assert not LEGACY_NEW_ARRAY.search(source), f"{rel} contains legacy `new T[...]`"
    assert "ConstantArray" not in source, f"{rel} contains ConstantArray"


def test_unmapped_algorithm_still_gets_an_example():
    """VQE, QAOA, Grover and HHL all missed the map and got no example at all."""
    reference = QSharpCodeGenerator._load_reference(
        QSharpCodeGenerator.__new__(QSharpCodeGenerator), "VQE"
    )
    assert reference.strip(), "an unmapped algorithm gets no reference implementation"
    assert "operation" in reference


def test_mapped_algorithm_still_gets_its_own_example():
    """The fallback must not shadow the specific references."""
    gen = QSharpCodeGenerator.__new__(QSharpCodeGenerator)
    shor = gen._load_reference("Shor")
    default = gen._load_reference("does-not-exist")
    assert shor.strip()
    assert shor != default, "Shor is resolving to the fallback instead of its own reference"
