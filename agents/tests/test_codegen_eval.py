"""The Q# generation benchmark must classify outcomes the way its numbers claim.

run_codegen_eval.py calls a live model, so CI never runs it; these check the parts that turn
its runs into the figures quoted from it - the error classes and the summary - offline.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from agents.evaluations.run_codegen_eval import error_class, summarise  # noqa: E402

# Final errors recorded against the deployed generator on 2026-09-25.
CONTROLLED_EXP = ("compile failed: Qdk.Qsc.TypeCk.TyMismatch\n\n  x type error\n"
                  "  `-> expected (Pauli[], Double, Qubit[]), found Double\n    ,-[/tmp/src/Main.qs:31:9]")
R1FRAC = ("compile failed: Qdk.Qsc.TypeCk.TyMismatch\n\n  x type error\n"
          "  `-> expected (Int, Int, Qubit), found (Int, Double, Qubit, Qubit)\n")


def test_a_type_error_is_classed_by_its_expected_and_found_types():
    assert error_class(CONTROLLED_EXP) == "TypeCk.TyMismatch (expected (Pauli[], Double, Qubit[]), found Double)"
    assert error_class(R1FRAC).startswith("TypeCk.TyMismatch (expected (Int, Int, Qubit)")


def test_an_error_without_a_compiler_code_keeps_its_first_line():
    assert error_class("The program compiled but uses 0 qubit(s)\nmore") == "The program compiled but uses 0 qubit(s)"
    assert error_class("") == ""


def test_usable_excludes_failures_placeholders_and_missing_estimates():
    records = [
        {"compiled": True, "attempts": 1, "physical_qubits": 59505, "seconds": 7.0},
        {"compiled": True, "attempts": 2, "physical_qubits": 463390, "seconds": 16.9,
         "attempt_errors": [error_class(R1FRAC)]},
        {"compiled": True, "attempts": 1, "physical_qubits": 17, "trivial": True, "seconds": 6.2},
        {"compiled": True, "attempts": 1, "physical_qubits": None, "seconds": 9.0},
        {"compiled": False, "attempts": 3, "seconds": 23.4,
         "attempt_errors": [error_class(CONTROLLED_EXP)] * 3},
    ]
    s = summarise(records)
    assert (s["runs"], s["compiled"], s["never_compiled"]) == (5, 4, 1)
    assert (s["compiled_first_try"], s["compiled_after_repair"]) == (3, 1)
    assert (s["trivial_programs"], s["estimate_failed"], s["usable"]) == (1, 1, 2)
    assert s["final_error_classes"] == [(error_class(CONTROLLED_EXP), 1)]
    assert s["median_seconds"] == 9.0
