"""The agent hooks decide what an agent may do, so test the decisions by running the hooks.

Each test runs .github/hooks/scripts/agent_gates.py the way Copilot does: a JSON payload on
stdin, a decision (or nothing) on stdout. Two properties matter more than any single rule. The
script must always exit 0, because a command preToolUse hook that exits non-zero denies the tool
call and would block every shell command. And it must only deny what it means to: a guard that
blocks `git push` on a feature branch would be switched off within a day.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / ".github" / "hooks" / "scripts" / "agent_gates.py"
CONFIG = REPO / ".github" / "hooks" / "agent-gates.json"


def local_env() -> dict:
    """The environment of a developer's machine: none of the cloud agent's variables."""
    env = dict(os.environ)
    for name in ("COPILOT_AGENT_PROMPT", "GITHUB_COPILOT_API_TOKEN"):
        env.pop(name, None)
    return env


def run(event: str, payload=None, *, raw: str | None = None, cwd: Path = REPO, env: dict | None = None):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), event],
        input=raw if raw is not None else json.dumps(payload),
        capture_output=True, text=True, cwd=cwd, env=env or local_env(), timeout=300,
    )
    assert proc.returncode == 0, f"the hook must always exit 0, got {proc.returncode}: {proc.stderr}"
    out = proc.stdout.strip()
    return json.loads(out) if out else None


def shell(command: str, *, as_string: bool = True) -> dict:
    args = {"command": command}
    return {"toolName": "bash", "toolArgs": json.dumps(args) if as_string else args, "cwd": str(REPO)}


def denied(result) -> bool:
    return bool(result) and result.get("permissionDecision") == "deny"


# --- pre-tool --------------------------------------------------------------------------

DENY = [
    "git push --force",
    "git push -f origin feature",
    "git push origin +feature",
    "git push --force-with-lease origin feature",
    "git push origin main",
    "git push origin HEAD:main",
    "git push origin feature:refs/heads/main",
    "git push --all origin",
    "git push origin --delete main",
    "git -C . push -f",
    "cd sub && git push --force",
    "git clean -fdx",
    "git clean --force -d",
    "rm -rf problems/archived",
    "rm docs/paper/methodology-paper.md",
    'rm "docs/paper/Quantum Grand Challenges - Methodology Paper.pdf"',
    "git rm -r knowledge/Papers",
    "git rm CITATION.cff",
    r"Remove-Item -Recurse -Force problems\archived\03_qae_risk",
    "python -c \"import shutil; shutil.rmtree('docs/paper')\"",
    "rm -rf .git",
    "cd tmp && rm -rf problems/*",
    "find problems/archived -name '*.pyc' -delete",
    "rm problems/01_hubbard/qsharp/HardwareKernel.qs",
    "rm -rf problems/01_hubbard/instances",
    # Hidden inside another command (Copilot code review on #278).
    "bash -c 'rm docs/paper/methodology-paper.md'",
    'sh -c "git push --force"',
    "bash -lc 'cd x; git push origin main'",
    'pwsh -Command "Remove-Item -Recurse docs/paper"',
    r'cmd /c "rmdir /s /q docs\paper"',
    'eval "git push -f"',
    "echo $(rm -rf problems/archived)",
    'echo "`git push --force`"',
    "timeout 30 rm -rf docs/paper",
    # Each entry-point category on the danger list, read from the dependency map.
    "rm problems/01_hubbard/qsharp/src/Main.qs",
    "rm agents/api/main.py",
    "rm .github/workflows/ci-cd.yml",
    "rm problems/01_hubbard/Makefile",
    "rm Dockerfile",
    "rm tooling/ci_validate_qsharp.py",
    "git rm tooling/test_doc_claims.py",
    "rm website/pages/404.tsx",
    "rm tooling/verify_demo_prompts.py",
    "rm problems/01_hubbard/estimates/classical_baseline.json",
    "rm problems/reference_index.json",
    "rm -rf tooling",
    "rm -rf .",
    # Second review round on #278: wrapper options, directory changes, git -C.
    "sudo -u root rm docs/paper/methodology-paper.md",
    "sudo -u root git push -f origin feature",
    "cd tooling && rm ci_validate_qsharp.py",
    "cd problems/01_hubbard/qsharp; rm src/Main.qs",
    "git -C tooling rm ci_validate_qsharp.py",
    "cd - && rm Dockerfile",
    # Third review round: the remote given as an option.
    "git push --repo=origin main",
    "git push --repo origin main",
    'bash -c "python3 -c \\"import shutil; shutil.rmtree(\'docs/paper\')\\""',
]

ALLOW = [
    "git push origin copilot/fix-123",
    "git push -u origin feature",
    "git push --follow-tags origin feature",
    "git push origin main:feature",
    "git clean -n",
    "git clean -nd",
    "rm -rf node_modules",
    "rm build/tmp.txt",
    'grep -rn "rm -rf" problems/archived',
    "echo git push --force",
    "git status",
    "python -m pytest -q",
    "cat docs/paper/methodology-paper.md",
    "git log --format=%H -n 5",
    "git reset --soft HEAD~1",
    "git checkout -- problems/01_hubbard/README.md",
    "git restore --staged .",
    "git stash",
    "git rm --cached tooling/scratch.py",
    "rm -f website/out/index.html",
    "bash -c 'echo hello'",
    "echo '$(rm -rf problems/archived)'",
    'git commit -m "Fix; rm -rf problems/archived is denied now"',
    'git commit -m "Deny \\`git push --force\\` in the hook"',
    "rm -rf tooling/__pycache__",
    "rm docs/agentic-delivery-draft.md",
    "rm tooling/_scratch.py",
    "cd tooling && rm _scratch.py",
    "cd website && rm -rf out",
    "sudo apt-get install -y jq",
    "cd /tmp && rm -rf build",
    "git push --repo=origin feature",
    # Fourth review round: mentioning a Python deletion API is not deleting.
    "git commit -m \"Document os.remove('docs/paper/file.md') behavior\"",
    'grep -rn "shutil.rmtree(" tooling',
]


@pytest.mark.parametrize("command", DENY)
def test_denies(command):
    result = run("pre-tool", shell(command))
    assert denied(result), f"not denied: {command}"
    assert result["permissionDecisionReason"].startswith("agent-gates: ")


@pytest.mark.parametrize("command", ALLOW)
def test_allows(command):
    assert run("pre-tool", shell(command)) is None, f"denied: {command}"


def test_tool_args_as_an_object_work_too():
    assert denied(run("pre-tool", shell("git push --force", as_string=False)))


def test_only_shell_tools_are_judged():
    payload = {"toolName": "view", "toolArgs": json.dumps({"path": "docs/paper/methodology-paper.md"})}
    assert run("pre-tool", payload) is None


@pytest.mark.parametrize("command", ["git reset --hard", "git checkout -- .", "git restore .", "git stash drop",
                                     "git checkout -f main", "git switch --discard-changes main",
                                     "git switch -f main"])
def test_whole_tree_discards_are_denied_on_a_developer_machine_only(command):
    assert denied(run("pre-tool", shell(command), env=local_env()))
    cloud = local_env() | {"COPILOT_AGENT_PROMPT": "Implement #1"}
    assert run("pre-tool", shell(command), env=cloud) is None, (
        "the cloud sandbox holds no one else's work, and the agent may need to roll back"
    )


@pytest.fixture
def repo_on_main(tmp_path: Path) -> Path:
    git = ["git", "-c", "user.email=agent@example.com", "-c", "user.name=agent"]
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "init"], cwd=tmp_path, check=True)
    return tmp_path


def test_a_bare_push_is_judged_by_the_current_branch(repo_on_main: Path):
    payload = {"toolName": "bash", "toolArgs": json.dumps({"command": "git push"}), "cwd": str(repo_on_main)}
    assert denied(run("pre-tool", payload, cwd=repo_on_main))
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=repo_on_main, check=True)
    assert run("pre-tool", payload, cwd=repo_on_main) is None


@pytest.mark.parametrize("raw", ["", "not json", "[]", '{"toolName": 5}', '{"toolArgs": "{"}'])
def test_garbage_input_is_ignored_not_fatal(raw):
    assert run("pre-tool", raw=raw) is None


def test_an_unknown_event_is_ignored():
    assert run("no-such-event", {}) is None


def test_the_configured_command_itself_denies_a_force_push():
    """Run the hook entry exactly as the runtime would, through the shell named in the config."""
    entry = json.loads(CONFIG.read_text(encoding="utf-8"))["hooks"]["preToolUse"][0]
    payload = json.dumps(shell("git push --force"))
    if os.name == "nt":
        argv = ["powershell", "-NoProfile", "-Command", entry["powershell"]]
    else:
        if not shutil.which("python3"):
            pytest.skip("python3 is not on PATH")
        argv = ["bash", "-c", entry["bash"]]
    proc = subprocess.run(argv, input=payload, capture_output=True, text=True, cwd=REPO,
                          env=local_env(), timeout=60)
    assert proc.returncode == 0
    assert '"deny"' in proc.stdout, proc.stdout + proc.stderr


# --- post-tool -------------------------------------------------------------------------


def edit_payload(path: Path, tool: str = "edit") -> dict:
    return {"toolName": tool, "toolArgs": json.dumps({"path": str(path)}), "cwd": str(path.parent)}


def test_a_python_file_that_no_longer_parses_is_reported(tmp_path: Path):
    broken = tmp_path / "broken.py"
    broken.write_text("def f(:\n    return 1\n", encoding="utf-8")
    result = run("post-tool", edit_payload(broken))
    assert result and "broken.py" in result["additionalContext"] and "line 1" in result["additionalContext"]


def test_a_valid_file_is_left_alone(tmp_path: Path):
    good = tmp_path / "good.py"
    good.write_text("def f():\n    return 1\n", encoding="utf-8")
    assert run("post-tool", edit_payload(good)) is None


def test_broken_json_is_reported(tmp_path: Path):
    broken = tmp_path / "data.json"
    broken.write_text('{"a": 1,}', encoding="utf-8")
    assert "data.json" in run("post-tool", edit_payload(broken, "create"))["additionalContext"]


def test_paths_in_a_patch_are_checked(tmp_path: Path):
    broken = tmp_path / "patched.py"
    broken.write_text("x = (\n", encoding="utf-8")
    patch = f"*** Begin Patch\n*** Update File: {broken.name}\n@@\n-x = 1\n+x = (\n*** End Patch\n"
    payload = {"toolName": "apply_patch", "toolArgs": json.dumps({"input": patch}), "cwd": str(tmp_path)}
    assert "patched.py" in run("post-tool", payload)["additionalContext"]


def test_other_tools_are_not_checked(tmp_path: Path):
    broken = tmp_path / "broken.py"
    broken.write_text("def f(:\n", encoding="utf-8")
    assert run("post-tool", edit_payload(broken, "view")) is None


@pytest.mark.parametrize("tool", ["create", "edit", "str_replace", "str_replace_editor", "write",
                                  "multiedit", "create_file", "replace_string_in_file",
                                  "insert_edit_into_file"])
def test_every_edit_tool_is_checked(tmp_path: Path, tool: str):
    broken = tmp_path / "broken.py"
    broken.write_text("def f(:\n", encoding="utf-8")
    assert "broken.py" in run("post-tool", edit_payload(broken, tool))["additionalContext"]


# --- stop ------------------------------------------------------------------------------


@pytest.fixture
def worktree(tmp_path: Path):
    """A clean checkout of HEAD to break things in, leaving the real working tree alone."""
    path = tmp_path / "wt"
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(path), "HEAD"], cwd=REPO,
                   check=True, capture_output=True)
    yield path
    subprocess.run(["git", "worktree", "remove", "--force", str(path)], cwd=REPO, capture_output=True)


def test_stop_is_allowed_once_already_sent_back():
    assert run("stop", {"stop_hook_active": True, "cwd": str(REPO)}) is None


def test_a_new_file_left_out_of_the_dependency_map_sends_the_agent_back(worktree: Path):
    (worktree / "tooling" / "_gate_probe.py").write_text("import json\n", encoding="utf-8")
    result = run("stop", {"cwd": str(worktree), "stop_hook_active": False}, cwd=worktree)
    assert result and result["decision"] == "block"
    assert "docs/depgraph is stale" in result["reason"]
    assert "git add -N tooling/_gate_probe.py" in result["reason"]
    status = subprocess.run(["git", "status", "--porcelain", "--", "docs/depgraph"], cwd=worktree,
                            capture_output=True, text=True, check=True).stdout
    assert status == "", "the gate must check the graph without rewriting it"


def test_python_that_does_not_compile_sends_the_agent_back(worktree: Path):
    (worktree / "tooling" / "_gate_broken.py").write_text("def f(:\n", encoding="utf-8")
    result = run("stop", {"cwd": str(worktree)}, cwd=worktree)
    assert result and "tooling/_gate_broken.py does not compile" in result["reason"]


def _touch_code_without_changing_the_graph(worktree: Path) -> None:
    """A code change that leaves the graph as it is, so the gate runs its graph check."""
    target = worktree / "tooling" / "ci_validate_qsharp.py"
    target.write_text(target.read_text(encoding="utf-8") + "\n# touched\n", encoding="utf-8")


def test_a_developers_own_untracked_notes_do_not_count_as_drift(worktree: Path):
    """graph.json records how many files are tracked. A developer's untracked notes are never
    committed, so counting them reported drift on every stop on a real machine."""
    _touch_code_without_changing_the_graph(worktree)
    (worktree / "my-notes.md").write_text("private\n", encoding="utf-8")
    result = run("stop", {"cwd": str(worktree)}, cwd=worktree, env=local_env())
    assert result is None, result


def test_in_the_cloud_every_new_file_counts(worktree: Path):
    """In the sandbox every untracked file is the agent's and will be committed."""
    _touch_code_without_changing_the_graph(worktree)
    (worktree / "docs" / "new-page.md").write_text("new\n", encoding="utf-8")
    cloud = local_env() | {"COPILOT_AGENT_PROMPT": "Implement #1"}
    result = run("stop", {"cwd": str(worktree)}, cwd=worktree, env=cloud)
    assert result and "docs/depgraph is stale" in result["reason"]
