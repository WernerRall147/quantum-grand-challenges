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

import re
import subprocess
import sys
import types
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


def test_local_target_finds_the_marked_state_without_azure():
    """The homepage walkthrough's first run: the local simulator, no account, same table."""
    result = subprocess.run(
        [sys.executable, str(REPO / "tooling" / "submit_one_kernel.py"), DEMO_PROBLEM, "local",
         "--shots", "100", "--expect", "0, 1, 1, 1"],
        capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "the marked state was found" in result.stdout


MY_WORKSPACE = "/subscriptions/0000/resourceGroups/mine/providers/Microsoft.Quantum/Workspaces/mine"


def fake_azure(monkeypatch, offered):
    """Stand in for azure.identity and qdk.azure, so no login or network is needed.

    `offered` lists the target names the fake workspace has. Returns what the tool
    passed in.
    """
    import submit_one_kernel as tool

    seen = {}

    class Job:
        details = types.SimpleNamespace(id="job-1")

        def get_results(self, timeout_secs):
            # The SDK returns each outcome's share, not its count, for the v2 results format.
            return {"[0, 1, 1, 1]": 0.94, "[1, 1, 0, 1]": 0.06}

    class Target:
        def __init__(self, name):
            self.name = name

        def submit(self, qir, name, shots):
            seen["submitted"] = (qir, shots)
            return Job()

    class Workspace:
        def __init__(self, resource_id, location, credential):
            seen.update(resource_id=resource_id, location=location, credential=credential)

        def get_targets(self, name=None):
            # Like the SDK: one match is a target, anything else a list.
            matches = [Target(n) for n in offered if name in (None, n)]
            return matches[0] if name and len(matches) == 1 else matches

    fake_qdk_azure = types.ModuleType("qdk.azure")
    fake_qdk_azure.Workspace = Workspace
    fake_identity = types.ModuleType("azure.identity")
    fake_identity.AzureCliCredential = lambda **kwargs: kwargs
    monkeypatch.setitem(sys.modules, "qdk.azure", fake_qdk_azure)
    monkeypatch.setitem(sys.modules, "azure.identity", fake_identity)
    monkeypatch.setattr(tool, "compile_kernel", lambda kernel, target: ("GroverSearchKernel", "qir"))
    monkeypatch.setattr(sys, "argv", [
        "submit_one_kernel.py", DEMO_PROBLEM, "rigetti.sim.qvm",
        "--resource-id", MY_WORKSPACE, "--expect", "0, 1, 1, 1",
    ])
    return tool, seen


def test_your_own_workspace_is_used_as_given(monkeypatch, capsys):
    """A visitor's resource ID reaches the SDK unchanged, under their own login."""
    tool, seen = fake_azure(monkeypatch, offered=["rigetti.sim.qvm", "ionq.simulator"])

    assert tool.main() == 0
    assert seen["resource_id"] == MY_WORKSPACE
    assert seen["location"] is None, "the SDK looks a visitor's region up; forcing eastus breaks other regions"
    assert seen["credential"] == {}, "a visitor's own login, not this project's tenant"
    assert seen["submitted"] == ("qir", 100)
    out = capsys.readouterr().out
    assert re.search(r"\[0, 1, 1, 1\]\s+94\s+94\.0%", out), "shares are shown as counts out of the shots\n" + out
    assert "the marked state was found" in out


def test_missing_target_names_what_the_workspace_offers(monkeypatch):
    """A workspace without the provider must say so, not crash on a list."""
    tool, seen = fake_azure(monkeypatch, offered=["quantinuum.sim.h2-1e"])

    with pytest.raises(SystemExit) as excinfo:
        tool.main()
    assert "rigetti.sim.qvm is not in this workspace" in str(excinfo.value)
    assert "quantinuum.sim.h2-1e" in str(excinfo.value)
    assert "submitted" not in seen
