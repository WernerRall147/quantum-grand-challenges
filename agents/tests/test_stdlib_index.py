"""The name check must not cry wolf.

A false positive is worse than no check: it sends a repair chasing a name that is fine,
burning one of three attempts on nothing. So the headline test runs the checker over every
Q# file in this repo that is known to compile - the twenty problem implementations and the
ten samples vendored from microsoft/qdk - and requires zero unknown names.

That number is the whole justification for wiring this into repair().
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.code_generator.stdlib_index import (
    INDEX,
    diagnose,
    exported_names,
    suggest,
    unknown_names,
)

REPO = Path(__file__).resolve().parents[2]


def known_good_sources() -> list[Path]:
    """Q# that compiles today, grouped as the compiler sees it.

    A qsharp.json project is compiled as a unit, so a name declared in a sibling file is
    in scope. Checking files individually reported seven Runtime* helpers in 03_qae_risk
    as unknown when they are declared one file over. Generated code is always a single
    self-contained file, so this only affects the corpus, not the checker.
    """
    directories = {p.parent for p in (REPO / "problems").glob("**/qsharp/src/*.qs")}
    directories.add(REPO / "libs" / "qdk_samples")
    return sorted(directories)


def project_source(directory: Path) -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(directory.glob("*.qs")))


def test_the_index_exists_and_is_populated():
    assert INDEX.exists(), "run tooling/vendor_qdk_stdlib_index.py"
    assert len(exported_names()) > 250, f"only {len(exported_names())} names indexed"


def test_the_corpus_is_not_empty():
    """A glob matching nothing would make every no-false-positive test below vacuous."""
    assert len(known_good_sources()) >= 10, f"only {len(known_good_sources())} projects found"


@pytest.mark.parametrize("directory", known_good_sources(), ids=lambda p: p.parent.parent.name or p.name)
def test_no_false_positives_on_code_that_compiles(directory):
    found = unknown_names(project_source(directory))
    assert not found, f"{directory.name}: flagged names that are actually fine: {found}"


def test_names_that_burned_us_are_caught():
    """Both cost a production day. Neither is in the standard library."""
    assert "ConstantArray" in unknown_names("operation Main() : Unit { let x = ConstantArray(3, 0); }")


def test_a_real_name_is_not_flagged():
    assert unknown_names("operation Main() : Unit { let x = Repeated(true, 4); }") == []


def test_locally_defined_operations_are_not_flagged():
    code = """
    operation Helper(q : Qubit) : Unit { X(q); }
    operation Main() : Unit { use q = Qubit(); Helper(q); }
    """
    assert unknown_names(code) == []


def test_control_flow_is_not_mistaken_for_a_call():
    code = "operation Main() : Unit { for i in 0..3 { if (i > 1) { } } }"
    assert unknown_names(code) == []


def test_the_suggestion_names_a_real_replacement():
    """The point of the whole exercise: say what to write, not just what is wrong."""
    assert "Repeated" in suggest("Repeted")


def test_diagnose_is_silent_on_clean_code():
    assert diagnose("operation Main() : Unit { let x = Repeated(true, 4); }") == ""


def test_diagnose_names_the_alternative():
    message = diagnose("operation Main() : Unit { let x = Mappd(f, xs); }")
    assert "Mappd" in message
    assert "Mapped" in message


def test_a_missing_index_degrades_to_silence(monkeypatch, tmp_path):
    """No index must mean the old behaviour, not a prompt full of phantom errors."""
    from agents.code_generator import stdlib_index

    stdlib_index.exported_names.cache_clear()
    monkeypatch.setattr(stdlib_index, "INDEX", tmp_path / "absent.json")
    try:
        assert stdlib_index.unknown_names("operation Main() : Unit { Nonsense(); }") == []
    finally:
        stdlib_index.exported_names.cache_clear()


def test_the_index_pin_matches_the_vendored_samples():
    samples = json.loads((REPO / "libs" / "qdk_samples" / "provenance.json").read_text(encoding="utf-8"))
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    assert index["tag"] == samples["tag"], "stdlib index and samples are pinned to different tags"
