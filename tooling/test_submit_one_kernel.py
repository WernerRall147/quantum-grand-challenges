"""The Azure Friday demo kernel lives under problems/archived/, and the original
submitter could not see it.

`azure_submit_kernels.py` iterates `os.listdir(PROBLEMS_DIR)` and checks
`PROBLEMS_DIR / d / "qsharp" / "HardwareKernel.qs"`. For `15_database_search`
that path does not exist - the problem is archived - so the loop `continue`s and
the script prints "No successful submissions" and exits 0. Asking it to submit
the demo kernel looked like a no-op rather than an error.

These tests pin the behaviour that fixed it: resolution must reach into
problems/archived/, and a genuinely absent problem must fail loudly.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tooling"))

from submit_one_kernel import find_kernel  # noqa: E402

DEMO_PROBLEM = "15_database_search"


def test_finds_kernel_for_archived_demo_problem():
    """The Azure Friday kernel is archived; resolution must still reach it."""
    kernel = find_kernel(DEMO_PROBLEM)
    assert kernel.exists()
    assert "archived" in kernel.parts, (
        f"{DEMO_PROBLEM} is expected under problems/archived/; got {kernel}"
    )


def test_resolved_kernel_is_the_grover_entry_point():
    """Guard against resolving some other problem's kernel by accident."""
    code = find_kernel(DEMO_PROBLEM).read_text(encoding="utf-8")
    assert "operation GroverSearchKernel()" in code


def test_missing_problem_fails_loudly():
    """A typo must not look like 'nothing to submit'."""
    with pytest.raises(SystemExit) as excinfo:
        find_kernel("99_does_not_exist")
    assert "no HardwareKernel.qs" in str(excinfo.value)


def test_original_submitter_still_cannot_see_archived_problems():
    """Documents *why* this module exists, so the duplication is not 'tidied away'.

    If archiving changes and `problems/15_database_search` appears, this fails and
    whoever changed it can retire submit_one_kernel.py deliberately.
    """
    assert not (REPO / "problems" / DEMO_PROBLEM / "qsharp" / "HardwareKernel.qs").exists(), (
        "15_database_search is no longer archived - azure_submit_kernels.py can now "
        "see it, so re-evaluate whether submit_one_kernel.py is still needed."
    )


def test_help_runs_without_azure_credentials():
    """--help must not require the azure SDK or a login."""
    result = subprocess.run(
        [sys.executable, str(REPO / "tooling" / "submit_one_kernel.py"), "--help"],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "--expect" in result.stdout
