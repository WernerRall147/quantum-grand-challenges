"""The generator's exemplars must be right, whole, and chosen for the algorithm asked for.

Production telemetry, 2026-09-01 to 2026-09-25: the evaluator named the algorithm in prose,
the exemplar lookup was an exact dictionary key, and so all 29 requests got the default
exemplar - the first 3,500 characters of the Hubbard program, which were VQE code, for QPE
and Shor requests alike. The cut itself landed mid-statement in two of the references.
Two of three Shor requests then came back as classical trial division.

These check that each exemplar computes what it says, arrives in the prompt whole, and is
the one a production algorithm string selects.
"""

from __future__ import annotations

import collections
import json
import math
import re
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from agents.code_generator.compiler_hints import cited_names, hints_for  # noqa: E402
from agents.code_generator.generate import (  # noqa: E402
    _QSHARP_THREAD,
    REFERENCE_BUDGET,
    REFERENCE_IMPLEMENTATIONS,
    complete_prefix,
    resolve_reference,
)

qsharp = pytest.importorskip("qdk.qsharp")

EXEMPLARS = REPO / "agents" / "code_generator" / "exemplars"

# Every distinct algorithm string the production evaluator passed to the generator,
# 2026-09-01 to 2026-09-25, verbatim from Application Insights.
PRODUCTION_ALGORITHMS = {
    "Preparing Eigenstates and Thermal States, followed by fault-tolerant Quantum Phase Estimation (QPE)": "QPE",
    "Preparing Eigenstates and Thermal States, followed by Quantum Phase Estimation (QPE)": "QPE",
    "Shor's Algorithm": "Shor",
    "Preparing Eigenstates and Thermal States, implemented with fault-tolerant Quantum Phase Estimation (QPE)": "QPE",
    "Quantum Phase Estimation (QPE) with multiconfigurational eigenstate preparation": "QPE",
    "Preparing Eigenstates and Thermal States": "QPE",
    "Preparing Eigenstates and Thermal States, using fault-tolerant ground-state preparation followed by Quantum Phase Estimation (QPE)": "QPE",
    "Preparing Eigenstates and Thermal States, implemented with fault-tolerant Quantum Phase Estimation and quantum Gibbs/thermal-state preparation; use open-quantum-system simulation for solvent or bath effects": "QPE",
    "Fault-tolerant Quantum Phase Estimation (QPE) with multiconfigurational ground-state preparation; eigenstate/thermal-state preparation methods as the state-preparation component": "QPE",
    "Quantum Phase Estimation (QPE) with a chemistry state-preparation routine; alternatively, fault-tolerant eigenstate preparation": "QPE",
    "Quantum Phase Estimation (QPE) with fault-tolerant ground-state preparation; finite-temperature extensions for thermal states": "QPE",
    "Preparing Eigenstates and Thermal States, implemented with fault-tolerant quantum phase estimation and quantum ground-state preparation": "QPE",
    "Preparing Eigenstates and Thermal States followed by Quantum Phase Estimation (QPE)": "QPE",
    "Quantum Phase Estimation with fault-tolerant eigenstate preparation; use VQE or adiabatic/imaginary-time preparation only as a state-preparation heuristic": "QPE",
    "Fault-tolerant Quantum Phase Estimation (QPE) with multiconfigurational eigenstate preparation; use eigenstate/thermal-state preparation methods as the state-initialization component": "QPE",
    "Quantum Phase Estimation with qubitization and multiconfigurational eigenstate preparation": "QPE",
    "Fault-tolerant Quantum Phase Estimation (QPE) with quantum eigenstate preparation, preceded by active-space reduction and a multiconfigurational trial state": "QPE",
    "Fault-tolerant Quantum Phase Estimation (QPE) with quantum eigenstate preparation; use qubitization or interaction-picture Hamiltonian simulation": "QPE",
    "Fault-tolerant Quantum Phase Estimation (QPE) with multiconfigurational eigenstate preparation; quantum simulation using qubitized Hamiltonian or interaction-picture techniques": "QPE",
    "Fault-tolerant Quantum Phase Estimation (QPE) preceded by multiconfigurational eigenstate preparation": "QPE",
    "Quantum Phase Estimation (QPE) preceded by fault-tolerant eigenstate preparation, with quantum chemistry Hamiltonian simulation": "QPE",
    "Shor's algorithm": "Shor",
    "Quantum Phase Estimation (QPE) with multiconfigurational ground-state preparation, using adiabatic state preparation or a selected-configuration trial state": "QPE",
    "Preparing Eigenstates and Thermal States, implemented through fault-tolerant Quantum Phase Estimation (QPE) for final energy estimation": "QPE",
}


def _on_qsharp_thread(fn, *args):
    """The interpreter is thread-bound, and the generator keeps it on its own thread."""
    return _QSHARP_THREAD.submit(fn, *args).result()


def _project(source: str) -> None:
    root = Path(tempfile.mkdtemp())
    (root / "qsharp.json").write_text("{}")
    (root / "src").mkdir()
    (root / "src" / "Main.qs").write_text(source, encoding="utf-8")
    _on_qsharp_thread(lambda: qsharp.init(project_root=str(root)))


def _run(expr: str, shots: int):
    return _on_qsharp_thread(lambda: qsharp.run(expr, shots=shots))


def _eval(expr: str):
    return _on_qsharp_thread(lambda: qsharp.eval(expr))


def _little_endian(results) -> list[int]:
    return [sum(1 << i for i, r in enumerate(shot) if str(r) == "One") for shot in results]


# --- the exemplars compute what they say -----------------------------------------------

def test_the_qpe_exemplar_finds_the_h2_ground_energy():
    _project((EXEMPLARS / "QPE.qs").read_text(encoding="utf-8"))
    counts = collections.Counter(_little_endian(_run("Main.Main()", 200)))
    mode, hits = counts.most_common(1)[0]
    # 0.99 overlap of |10> with the ground state puts nearly every shot on one bin.
    assert hits >= 160, counts
    coeffs = [0.39793742484318045, -0.39793742484318045, -0.01128010425623538, 0.18093119978423156]
    tau = math.pi / (2 * sum(abs(c) for c in coeffs))
    theta = 2 * math.pi * mode / 64
    energy = -1.052373245772859 - (theta - 2 * math.pi if theta > math.pi else theta) / tau
    resolution = 2 * math.pi / (64 * tau)
    assert abs(energy - (-1.857275)) < resolution / 2
    assert energy + 0.7199689944489797 == pytest.approx(-1.137306, abs=resolution / 2)


def test_the_shor_exemplar_multiplies_modulo_15():
    _project((EXEMPLARS / "Shor.qs").read_text(encoding="utf-8"))
    wrong = []
    for a in (1, 2, 4, 7, 8, 11, 13, 14):
        for x in range(1, 15):
            flips = " ".join(f"X(r[{i}]);" for i in range(4) if x >> i & 1)
            got = _eval(f"{{ use r = Qubit[4]; {flips} Main.MultiplyMod15({a}, r); MeasureInteger(r) }}")
            if got != a * x % 15:
                wrong.append((a, x, got))
    assert wrong == []


def test_the_shor_exemplar_reads_the_order_of_7_mod_15():
    _project((EXEMPLARS / "Shor.qs").read_text(encoding="utf-8"))
    counts = collections.Counter(_little_endian(_run("Main.Main()", 200)))
    # r = 4, so the 4-bit phase register reads s * 16 / 4 for s = 0..3.
    assert set(counts) == {0, 4, 8, 12}, counts


@pytest.mark.parametrize("name", ["QPE.qs", "Shor.qs"])
def test_each_exemplar_is_estimable_and_does_quantum_work(name):
    """The shape the generator must return: Main() : Result[], estimable, several qubits."""
    from agents.code_generator.generate import QSharpCodeGenerator

    source = (EXEMPLARS / name).read_text(encoding="utf-8")
    assert re.search(r"^operation Main\(\) : Result\[\]", source, re.M)
    est = QSharpCodeGenerator.compile_and_estimate(QSharpCodeGenerator.__new__(QSharpCodeGenerator), source)
    assert est["compiled"] is True
    assert est["num_qubits"] >= 8
    assert est["physical_qubits"] > 17


# --- the exemplars reach the prompt whole ----------------------------------------------

@pytest.mark.parametrize("key", sorted(REFERENCE_IMPLEMENTATIONS))
def test_every_reference_arrives_whole_and_compiles(key):
    """A cut exemplar showed the model helpers it never saw, and code ending mid-statement."""
    source = (REPO / REFERENCE_IMPLEMENTATIONS[key]).read_text(encoding="utf-8")
    assert len(source) <= REFERENCE_BUDGET, f"{key} no longer fits the budget; it would be cut"
    assert complete_prefix(source) == source
    _project(source)


def _balanced(text: str) -> bool:
    body = re.sub(r'\$?"(?:[^"\\\n]|\\.)*"', '""', re.sub(r"//[^\n]*", "", text))
    return body.count("{") == body.count("}") and body.count("(") == body.count(")")


@pytest.mark.parametrize("path", [
    "problems/01_hubbard/qsharp/src/Main.qs",
    "problems/09_factorization/qsharp/src/Main.qs",
    "libs/qdk_samples/HiddenShift.qs",
])
def test_a_long_file_is_cut_between_declarations(path):
    """The files the old `text[:3500]` cut mid-statement, and one with a multi-line signature."""
    cut = complete_prefix((REPO / path).read_text(encoding="utf-8"), budget=3500)
    assert len(cut) <= 3500
    assert _balanced(cut)
    assert cut.rstrip().endswith(("}", ";"))
    assert not cut.rstrip().splitlines()[-1].lstrip().startswith("@")


def test_a_declaration_longer_than_the_budget_is_kept_whole():
    source = "import Std.Math.*;\n\noperation Main() : Result[] {\n" + "    let x = 1;\n" * 50 + "    return [];\n}\n"
    assert complete_prefix(source, budget=100) == source


# --- the right exemplar for the algorithm asked for ------------------------------------

@pytest.mark.parametrize("algorithm, expected", sorted(PRODUCTION_ALGORITHMS.items()))
def test_production_algorithm_strings_select_the_right_exemplar(algorithm, expected):
    assert resolve_reference(algorithm) == expected


@pytest.mark.parametrize("algorithm, expected", [
    ("Trotterized Hamiltonian simulation of a lattice gauge theory", "Trotter"),
    ("Variational Quantum Eigensolver (VQE) for the ground state energy", "VQE"),
    ("Grover's search with amplitude amplification", "Grover"),
    ("Quantum Phase Estimation with a double-factorized Hamiltonian", "QPE"),
    ("QAOA", "QPE"),
    ("", "QPE"),
    ("Shor", "Shor"),
])
def test_the_first_family_named_wins(algorithm, expected):
    """The evaluator names the primary algorithm first and alternatives after it."""
    assert resolve_reference(algorithm) == expected


# --- the repair is told the fix for the errors that failed every attempt ---------------

@pytest.mark.parametrize("error, fix", [
    ("x type error `-> expected (Pauli[], Double, Qubit[]), found Double", "Controlled Exp([control], ([PauliZ], theta, [q]))"),
    ("x type error `-> expected (Int, Int, Qubit), found (Int, Double, Qubit, Qubit)", "R1(theta, qubit)"),
    ("x type error `-> expected Double, found Int", "IntAsDouble(n)"),
    ("x type error `-> expected BigInt, found Int", "IntAsBigInt(n)"),
    ("Qdk.Qsc.LogicSeparation.ExprFobidden", "function"),
])
def test_the_measured_failures_get_a_named_fix(error, fix):
    assert fix in hints_for(error)


def test_an_unrecognised_error_gets_no_invented_advice():
    assert hints_for("Qdk.Qsc.Parse.MissingSemi expected `;`") == ""


def test_every_callable_a_hint_names_exists():
    exported = set(json.loads((REPO / "libs" / "qdk_stdlib" / "exports.json").read_text(encoding="utf-8"))["all"])
    names = cited_names()
    assert {"Exp", "R1", "IntAsDouble", "ApplyQPE"} <= names
    assert names - exported == set()
