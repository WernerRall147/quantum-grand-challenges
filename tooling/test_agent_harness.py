"""The agent harness is configuration, and configuration fails silently.

GitHub and VS Code both ignore an unrecognised tool name in an agent profile, so a typo removes
a tool from the agent without a warning. A hook file with invalid JSON is dropped whole. A setup
workflow whose job is not called `copilot-setup-steps` never runs, and the agent then works in an
environment that differs from CI's. A link in AGENTS.md to a renamed skill sends every agent to
nothing. A command preToolUse hook that exits non-zero denies the tool call, so a hook entry
without its fail-open guard can block every shell command an agent tries.

These tests read the files the way the runtimes do and fail on those mistakes. What the hooks
decide is tested by running them, in tooling/test_agent_hooks.py.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
AGENTS_DIR = REPO / ".github" / "agents"
SKILLS_DIR = REPO / ".github" / "skills"
HOOKS_DIR = REPO / ".github" / "hooks"
WORKFLOWS = REPO / ".github" / "workflows"
SETUP_STEPS = WORKFLOWS / "copilot-setup-steps.yml"
ISSUE_FORM = REPO / ".github" / "ISSUE_TEMPLATE" / "agent-task.yml"

AGENT_FILES = sorted(AGENTS_DIR.glob("*.md"))
SKILL_DIRS = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())

# Custom agents configuration reference (GitHub) and custom agent file structure (VS Code).
AGENT_KEYS = {
    "name", "description", "target", "tools", "model", "disable-model-invocation",
    "user-invocable", "infer", "mcp-servers", "metadata", "handoffs", "argument-hint",
    "agents", "hooks",
}
TOOL_ALIASES = {
    "execute", "shell", "bash", "powershell", "read", "notebookread", "edit", "multiedit",
    "write", "notebookedit", "search", "grep", "glob", "agent", "custom-agent", "task", "web",
    "websearch", "webfetch", "todo", "todowrite",
}
MCP_TOOL = re.compile(r"^[a-z0-9_.-]+/(\*|[a-z0-9_-]+)$", re.I)
SKILL_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
HOOK_EVENTS = {
    "sessionStart", "sessionEnd", "userPromptSubmitted", "userPromptTransformed", "preToolUse",
    "postToolUse", "postToolUseFailure", "agentStop", "subagentStart", "subagentStop",
    "errorOccurred", "preCompact", "permissionRequest", "notification",
}

# Documents whose links and repository paths must resolve.
LINKED_DOCS = [
    REPO / "AGENTS.md", REPO / "CLAUDE.md", REPO / "REVIEW.md",
    REPO / ".github" / "copilot-instructions.md", REPO / "docs" / "agentic-delivery.md",
    *sorted((REPO / "docs" / "adr").glob("*.md")), *AGENT_FILES,
    *(d / "SKILL.md" for d in SKILL_DIRS),
]
# Build output a document may name before it exists.
GENERATED = ("website/out", "website/node_modules", "website/public/viz")
PLACEHOLDER = re.compile(r"[<>*{}]|NNNN|NN_|YYYY|\.\.\.")


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", text, re.S)
    assert match, f"{path.relative_to(REPO)} has no YAML frontmatter"
    meta = yaml.safe_load(match.group(1))
    assert isinstance(meta, dict), f"{path.relative_to(REPO)} frontmatter is not a mapping"
    return meta, match.group(2)


def agent_names() -> set[str]:
    return {frontmatter(p)[0]["name"] for p in AGENT_FILES}


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def install_lines(text: str) -> list[str]:
    return [line.strip().removeprefix("run:").strip()
            for line in text.splitlines()
            if re.search(r"\bpip install numpy\b", line)]


# --- the instruction files -------------------------------------------------------------


def test_every_tool_reads_the_same_guide():
    assert (REPO / "AGENTS.md").is_file()
    assert "@AGENTS.md" in (REPO / "CLAUDE.md").read_text(encoding="utf-8").splitlines(), (
        "CLAUDE.md must import AGENTS.md so Claude reads the same rules"
    )
    assert "AGENTS.md" in (REPO / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
    assert (REPO / "REVIEW.md").is_file(), "Copilot code review reads REVIEW.md"


# --- custom agents ---------------------------------------------------------------------


def test_there_are_agents_to_check():
    assert len(AGENT_FILES) >= 4 and len(SKILL_DIRS) >= 4


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.name)
def test_agent_profile_is_well_formed(path: Path):
    assert re.fullmatch(r"[A-Za-z0-9._-]+\.agent\.md", path.name), (
        "GitHub allows only . - _ a-z A-Z 0-9 in the file name; VS Code needs .agent.md"
    )
    meta, body = frontmatter(path)
    unknown = set(meta) - AGENT_KEYS
    assert not unknown, f"unknown frontmatter keys {sorted(unknown)}: a typo is silently ignored"
    assert isinstance(meta.get("description"), str) and meta["description"].strip()
    assert isinstance(meta.get("name"), str) and meta["name"].strip()
    assert body.strip() and len(body) <= 30_000, "the prompt is limited to 30,000 characters"


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.name)
def test_agent_tools_are_names_the_runtimes_know(path: Path):
    tools = frontmatter(path)[0].get("tools")
    if tools is None:
        return  # all tools
    if isinstance(tools, str):
        tools = [t.strip() for t in tools.split(",")]
    unknown = [t for t in tools if t.lower() not in TOOL_ALIASES and not MCP_TOOL.match(t)]
    assert not unknown, f"{unknown} would be silently ignored, removing the tool from the agent"


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.name)
def test_handoffs_point_at_agents_that_exist(path: Path):
    names = agent_names() | {"agent"}
    for handoff in frontmatter(path)[0].get("handoffs") or []:
        assert {"label", "agent", "prompt"} <= set(handoff), handoff
        assert handoff["agent"] in names, f"handoff to unknown agent {handoff['agent']!r}"


def test_agent_names_are_unique():
    names = [frontmatter(p)[0]["name"] for p in AGENT_FILES]
    assert len(names) == len(set(names)), names


# --- skills ----------------------------------------------------------------------------


@pytest.mark.parametrize("skill", SKILL_DIRS, ids=lambda p: p.name)
def test_skill_is_well_formed(skill: Path):
    path = skill / "SKILL.md"
    assert path.is_file(), "a skill is discovered by its SKILL.md"
    meta, body = frontmatter(path)
    assert meta.get("name") == skill.name, "the skill name must match its folder"
    assert SKILL_NAME.match(skill.name) and len(skill.name) <= 64
    description = meta.get("description")
    assert isinstance(description, str) and 0 < len(description) <= 1024, (
        "the description is how an agent decides to load the skill"
    )
    assert set(meta) <= {"name", "description", "license", "allowed-tools", "metadata"}
    assert body.strip()


# --- the roster in AGENTS.md matches the files ------------------------------------------


def test_agents_md_lists_every_agent_and_skill_and_nothing_else():
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    linked_agents = set(re.findall(r"\]\(\.github/agents/([^)]+)\)", text))
    linked_skills = set(re.findall(r"\]\(\.github/skills/([^/)]+)/SKILL\.md\)", text))
    assert linked_agents == {p.name for p in AGENT_FILES}
    assert linked_skills == {p.name for p in SKILL_DIRS}


# --- links and paths resolve -----------------------------------------------------------


def _top_level() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True)
    return {line.split("/")[0] for line in out.stdout.splitlines() if line}


def _path_tokens(text: str):
    for span in re.findall(r"`([^`\n]+)`", text):
        for token in re.split(r"[\s\"'=(),;]+", span):
            token = token.rstrip(".:")
            if token and not PLACEHOLDER.search(token) and not token.startswith(("http", "-", "$")):
                yield token


@pytest.mark.parametrize("doc", LINKED_DOCS, ids=lambda p: p.relative_to(REPO).as_posix())
def test_links_resolve(doc: Path):
    text = doc.read_text(encoding="utf-8")
    broken = []
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if not (doc.parent / target.split("#")[0]).exists():
            broken.append(target)
    assert not broken, f"links that resolve to nothing: {broken}"


@pytest.mark.parametrize("doc", LINKED_DOCS, ids=lambda p: p.relative_to(REPO).as_posix())
def test_repository_paths_exist(doc: Path):
    top = _top_level()
    missing = []
    for token in _path_tokens(doc.read_text(encoding="utf-8")):
        path = token.rstrip("/")
        first = path.split("/")[0]
        if first not in top or ("/" not in path and "." not in path):
            continue
        if path.startswith(GENERATED):
            continue
        if not (REPO / path).exists():
            missing.append(token)
    assert not missing, f"paths named in backticks that do not exist: {sorted(set(missing))}"


# --- hooks -----------------------------------------------------------------------------


def test_there_is_a_hook_file():
    assert sorted(HOOKS_DIR.glob("*.json")), "no .github/hooks/*.json"


@pytest.mark.parametrize("path", sorted(HOOKS_DIR.glob("*.json")), ids=lambda p: p.name)
def test_hook_file_is_valid_and_fails_open(path: Path):
    config = json.loads(path.read_text(encoding="utf-8"))
    assert config.get("version") == 1, "a file without version 1 is rejected whole"
    assert isinstance(config.get("hooks"), dict) and config["hooks"]
    for event, entries in config["hooks"].items():
        assert event in HOOK_EVENTS, f"unknown hook event {event!r}"
        assert isinstance(entries, list) and entries
        for entry in entries:
            assert entry.get("type", "command") == "command"
            assert entry.get("bash"), "the cloud agent runs only the bash command"
            assert entry.get("powershell"), "Copilot CLI on Windows runs the powershell command"
            if "matcher" in entry:
                re.compile(entry["matcher"])
            assert isinstance(entry.get("timeoutSec", 30), int) and entry.get("timeoutSec", 30) > 0
            for script in re.findall(r"[\w./-]+\.py", entry["bash"] + " " + entry["powershell"]):
                assert (REPO / script).is_file(), f"hook runs {script}, which does not exist"
            # A crash or non-zero exit denies the tool call; only an explicit decision may.
            assert entry["bash"].rstrip().endswith("|| true"), entry["bash"]
            assert entry["powershell"].rstrip().endswith("exit 0"), entry["powershell"]


def test_hook_script_is_not_a_cleanup_candidate():
    candidates = json.loads((REPO / "docs" / "depgraph" / "cleanup-candidates.json").read_text(encoding="utf-8"))
    paths = {c.get("path") or c.get("file") for c in candidates["candidates"]}
    assert ".github/hooks/scripts/agent_gates.py" not in paths, (
        "the runtime calls the hook script, but nothing imports it; it needs a line in "
        "tooling/depgraph/manual_entrypoints.txt or a cleanup could delete it"
    )


# --- the agent's environment matches CI -------------------------------------------------


def test_setup_steps_job_is_one_copilot_will_run():
    workflow = load_yaml(SETUP_STEPS)
    assert list(workflow["jobs"]) == ["copilot-setup-steps"], "Copilot runs only this job name"
    job = workflow["jobs"]["copilot-setup-steps"]
    allowed = {"runs-on", "permissions", "steps", "services", "snapshot", "timeout-minutes"}
    assert set(job) <= allowed, f"Copilot ignores {sorted(set(job) - allowed)}"
    assert job.get("timeout-minutes", 59) <= 59
    triggers = workflow.get("on", workflow.get(True))
    assert "workflow_dispatch" in triggers, "it must be runnable by hand from the Actions tab"


def test_agent_codespace_and_ci_install_the_same_packages():
    ci = install_lines((WORKFLOWS / "ci-cd.yml").read_text(encoding="utf-8"))
    setup = install_lines(SETUP_STEPS.read_text(encoding="utf-8"))
    devcontainer = install_lines((REPO / ".devcontainer" / "setup.sh").read_text(encoding="utf-8"))
    documented = install_lines((REPO / "AGENTS.md").read_text(encoding="utf-8"))
    assert len(ci) == 1, ci
    assert setup == ci, "the cloud agent would test against different packages from CI"
    assert devcontainer == ci, "a codespace would test against different packages from CI"
    assert documented == ci, "AGENTS.md quotes an install line CI does not use"


def test_agent_codespace_and_deploy_use_the_same_node():
    deploy = re.search(r"node-version:\s*'?(\d+)", (WORKFLOWS / "deploy-website.yml").read_text(encoding="utf-8"))
    setup = re.search(r"node-version:\s*'?(\d+)", SETUP_STEPS.read_text(encoding="utf-8"))
    container = json.loads((REPO / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8"))
    node = container["features"]["ghcr.io/devcontainers/features/node:1"]["version"]
    assert deploy and setup and deploy.group(1) == setup.group(1) == str(node)


@pytest.mark.parametrize("path", sorted(WORKFLOWS.glob("*.y*ml")), ids=lambda p: p.name)
def test_workflow_is_one_github_will_run(path: Path):
    """The same checks as the "Validate workflow YAML" step in ci-cd.yml."""
    doc = load_yaml(path)
    assert isinstance(doc, dict)
    assert doc.get("name"), "without a name GitHub shows the file path"
    assert True in doc or "on" in doc, "no triggers"
    assert doc.get("jobs"), "no jobs"


# --- the issue form --------------------------------------------------------------------


def test_agent_task_form_asks_for_a_checkable_specification():
    form = load_yaml(ISSUE_FORM)
    assert form.get("name") and form.get("description") and "agent-task" in form.get("labels", [])
    fields = [item for item in form["body"] if item.get("type") != "markdown"]
    ids = [item["id"] for item in fields]
    assert len(ids) == len(set(ids)), "duplicate field ids"
    required = {item["id"] for item in fields if item.get("validations", {}).get("required")}
    assert {"objective", "acceptance", "risk"} <= required
    for item in fields:
        if item["type"] == "dropdown":
            assert item["attributes"]["options"]
