"""Q# output validation tests  verify quantum programs produce scientifically reasonable results.

These tests run each Q# entry point via the qsharp Python package and check
that the output contains expected markers (algorithm name, key metrics, etc.).
"""

import os
import re
import sys
from pathlib import Path

import pytest

try:
    import qsharp
except ImportError:
    pytest.skip("qsharp package not installed", allow_module_level=True)

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Map problem → (entry point, expected output patterns)
VALIDATION_CASES = {
    "01_hubbard": (
        "Main.RunTwoSiteHubbardAnalysis()",
        [r"Hubbard", r"VQE", r"ground.state|energy"],
    ),
    "02_catalysis": (
        "Main.RunCatalysisAnalysis()",
        [r"catalysis|H₂|hydrogen", r"VQE|energy"],
    ),
    "05_qaoa_maxcut": (
        "Main.RunQaoaAnalysis([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]], 1, 50, 100)",
        [r"\d+\.\d+", r"\["],  # Returns numeric tuples with cut values and assignments
    ),
    "09_factorization": (
        "Main.RunShorFactorization()",
        [r"Shor|factor", r"15|period"],
    ),
    "15_database_search": (
        "Main.RunGroverDemonstration()",
        [r"Grover|search", r"found|success"],
    ),
    "16_error_correction": (
        "Main.RunQECDemonstration()",
        [r"error.correction|repetition|QEC", r"correct"],
    ),
}


@pytest.fixture(params=list(VALIDATION_CASES.keys()), ids=list(VALIDATION_CASES.keys()))
def qsharp_problem(request):
    return request.param


def test_qsharp_output_validation(qsharp_problem, capsys):
    """Run a Q# program and verify output contains expected scientific content."""
    entry_point, patterns = VALIDATION_CASES[qsharp_problem]
    qsharp_dir = PROBLEMS_DIR / qsharp_problem / "qsharp"

    assert qsharp_dir.is_dir(), f"No qsharp/ directory for {qsharp_problem}"
    assert (qsharp_dir / "qsharp.json").is_file(), f"No qsharp.json for {qsharp_problem}"

    # Compile and run
    qsharp.init(project_root=str(qsharp_dir))

    # Collect Message() output via callback
    messages = []
    qsharp.init(project_root=str(qsharp_dir))

    result = qsharp.run(entry_point, shots=1, on_result=lambda r: None)
    output = str(result)

    # For some problems, Message() output goes to stdout
    captured = capsys.readouterr()
    output = output + " " + captured.out + " " + captured.err

    # Verify at least one pattern per expected category matches
    for pattern in patterns:
        assert re.search(pattern, output, re.IGNORECASE), (
            f"Expected pattern '{pattern}' not found in output for {qsharp_problem}.\n"
            f"Output (first 500 chars): {output[:500]}"
        )
