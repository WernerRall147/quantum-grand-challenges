"""The live code-generation check must fail on everything a user should not be shown.

Its value is only as good as its classifier: a check that passes a placeholder is how two
of three production Shor requests shipped trial division without anything going red.
Responses below follow the API's shape; the placeholder is the one production returned.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "check_codegen_live.py"
spec = importlib.util.spec_from_file_location("check_codegen_live", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

PARETO_OK = [{"config": "qubit_gate_ns_e3+surface_code", "physical_qubits": 59505}]


def _response(**estimation) -> dict:
    est = {"compiled": True, "quantum_work": True, "num_qubits": 8, "physical_qubits": 59505, "attempt_count": 1}
    est.update(estimation)
    return {"verdict": "QUANTUM_ADVANTAGE", "recommended_platform": "QUANTUM",
            "qsharp_code": "operation Main() : Result[] { use q = Qubit[8]; return MResetEachZ(q); }",
            "estimation": est, "resource_estimate_pareto": PARETO_OK}


def test_a_usable_program_passes():
    assert check.problems_with(200, _response()) == []


@pytest.mark.parametrize("change, expected", [
    ({"compiled": False, "error": "compile failed: TypeCk.TyMismatch"}, "did not compile"),
    ({"quantum_work": False, "num_qubits": 0, "physical_qubits": 17}, "does no quantum work"),
    ({"physical_qubits": None, "estimate_error": "no feasible configuration"}, "no resource estimate"),
])
def test_each_unusable_outcome_fails(change, expected):
    found = check.problems_with(200, _response(**change))
    assert found and expected in found[0]


def test_empty_code_fails():
    body = _response()
    body["qsharp_code"] = ""
    assert any("no Q# returned" in p for p in check.problems_with(200, body))


def test_a_failed_pareto_row_fails():
    body = _response()
    body["resource_estimate_pareto"] = PARETO_OK + [{"config": "qubit_gate_us_e4+surface_code", "error": "boom"}]
    assert any("Pareto rows failed" in p for p in check.problems_with(200, body))


def test_http_errors_and_non_quantum_verdicts_fail():
    assert check.problems_with(500, {}) == ["HTTP 500"]
    body = _response()
    body.update(verdict="HPC_PREFERRED", recommended_platform="HPC")
    assert "no Q# is generated" in check.problems_with(200, body)[0]
