#!/usr/bin/env python3
"""Deterministic gates for Copilot agents working in this repository.

Wired up in .github/hooks/agent-gates.json, which Copilot cloud agent, Copilot CLI and Copilot
sessions in VS Code load (they share one hook implementation). One subcommand per hook event:

  pre-tool   preToolUse   Deny a few shell commands that destroy work or bypass review.
  post-tool  postToolUse  After an edit, say at once if the file no longer parses.
  stop       agentStop    Before the agent finishes, run the cheap checks CI fails on and,
                          if one fails, send the agent back with the fix. Once per stop.

Everything here fails open. A command preToolUse hook that exits non-zero DENIES the tool
call, so an unhandled exception would block every shell command the agent tries. main()
therefore catches everything, prints nothing on error and always exits 0, and the hook
config adds `|| true` as a second line of defence. Only an explicit decision printed to
stdout changes what the agent does.

Stdlib only: the cloud sandbox may run this with the system python3, before or without
the project's dependencies.
"""

from __future__ import annotations

import fnmatch
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

# --- payload helpers -------------------------------------------------------------------

SHELL_TOOLS = {"bash", "powershell", "shell", "execute", "run_in_terminal"}
# The configured matchers in agent-gates.json must cover every name here;
# tooling/test_agent_harness.py checks that they do.
EDIT_TOOLS = {
    "create", "edit", "str_replace", "str_replace_editor", "apply_patch", "write", "multiedit",
    "create_file", "replace_string_in_file", "insert_edit_into_file",
}


def tool_name(payload: dict) -> str:
    return str(payload.get("toolName") or payload.get("tool_name") or "").lower()


def tool_args(payload: dict):
    """toolArgs arrives as a JSON string in the documented examples, or as an object."""
    args = payload.get("toolArgs", payload.get("tool_input"))
    if isinstance(args, str):
        try:
            return json.loads(args)
        except ValueError:
            return args
    return args


def shell_command(payload: dict) -> str | None:
    if tool_name(payload) not in SHELL_TOOLS:
        return None
    args = tool_args(payload)
    if isinstance(args, str):
        return args
    if isinstance(args, dict):
        for key in ("command", "cmd", "script", "input"):
            if isinstance(args.get(key), str):
                return args[key]
    return None


# --- pre-tool: the deny rules ----------------------------------------------------------

# The danger list in docs/initiatives/repo-cleanup.md has two halves. Its entry points
# (workflows, Makefiles, the Dockerfile, pytest files, Next.js pages, Q# projects, manual
# tools, the scripts those surfaces run, the API's routes) are already inventoried by the
# dependency map, so they are read from docs/depgraph rather than listed twice. Its published
# artifacts are patterns, below.
ARTIFACTS = [re.compile(p, re.I) for p in (
    r"(^|/)problems/archived(/|$)",
    r"(^|/)problems/[^/]+/(instances|estimates|circuits)(/|$)",
    r"(^|/)problems/reference_index\.json$",
    r"(^|/)docs/paper(/|$)",
    r"(^|/)docs/objective-kpis\.json$",
    r"(^|/)website/data(/|$)",
    r"(^|/)knowledge/papers(/|$)",
    r"(^|/)citation\.cff$",
    r"\.pdf$",
    r"(^|/)hardwarekernel\.qs$",
    r"(^|/)\.git(/|$)",
)]
# Paths a wildcard argument is tested against, so `rm -rf problems/*` is caught too.
ARTIFACT_EXAMPLES = (
    "problems/archived", "problems/archived/03_qae_risk/README.md", "docs/paper",
    "docs/paper/methodology-paper.md", "knowledge/Papers", "CITATION.cff", "paper.pdf",
    "problems/01_hubbard/qsharp/HardwareKernel.qs", "problems/01_hubbard/instances/small.yaml",
    "problems/01_hubbard/estimates/classical_baseline.json", "website/data/x.json", ".git",
)
DANGER = "danger list (docs/initiatives/repo-cleanup.md): deleting this needs an explicit human OK"
DELETE_VERBS = {"rm", "rmdir", "del", "erase", "rd", "remove-item", "ri", "unlink", "shred"}
WRAPPERS = {"sudo", "xargs", "env", "command", "nohup", "time", "nice", "exec", "timeout"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish"}
POWERSHELLS = {"pwsh", "pwsh.exe", "powershell", "powershell.exe"}
INLINE_FLAGS = {"-c", "-lc", "-ic", "-Command", "-command", "/c", "/C"}
SUBSTITUTION = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
PY_DELETE = re.compile(r"rmtree\(|os\.remove\(|os\.unlink\(|\.unlink\(|os\.rmdir\(")
PATH_LIKE = re.compile(r"[\w./\\:-]+")
GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
SHORT_FORCE = re.compile(r"-[a-zA-Z]*f[a-zA-Z]*")


def segments(command: str) -> list[str]:
    """Split on ; && || | and newlines, but not inside quotes, so `bash -c 'a; b'` stays whole."""
    parts, buf, quote, i = [], [], None, 0
    while i < len(command):
        ch = command[i]
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            elif ch == "\\" and quote == '"' and i + 1 < len(command):
                buf.append(command[i + 1])
                i += 1
        elif ch in "'\"":
            quote = ch
            buf.append(ch)
        elif command.startswith(("&&", "||"), i):
            parts.append("".join(buf))
            buf = []
            i += 1
        elif ch in ";|\n":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    parts.append("".join(buf))
    return [part.strip() for part in parts if part.strip()]


def tokens(segment: str) -> list[str]:
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def command_verb(toks: list[str]) -> str:
    """The program a segment runs, past `sudo`, `timeout 30`, `VAR=value` and the like."""
    for tok in toks:
        if tok in WRAPPERS or tok.startswith("-") or re.fullmatch(r"[A-Za-z_]\w*=.*", tok) \
                or re.fullmatch(r"\d+[smhd]?", tok):
            continue
        return Path(tok.replace("\\", "/")).name.lower()
    return ""


def verbs(toks: list[str]) -> set[str]:
    """Programs a segment may run.

    Past a wrapper such as `sudo -u root`, options take values this parser cannot tell from
    the program name, so every token counts. That errs towards denying, which is the safe side.
    """
    if toks and Path(toks[0].replace("\\", "/")).name.lower() in WRAPPERS:
        return {Path(t.replace("\\", "/")).name.lower() for t in toks}
    return {command_verb(toks)}


def next_cwd(toks: list[str], cwd: Path | None) -> Path | None:
    """The directory after `cd`/`pushd`/`Set-Location`, or None when it cannot be known."""
    args = [t for t in toks[1:] if not t.startswith("-")]
    if not args or args[0] == "-" or args[0].startswith(("~", "$")):
        return None
    target = Path(normalise(args[0]))
    if target.is_absolute():
        return target
    return cwd / target if cwd is not None else None


def nested_commands(segment: str, toks: list[str]) -> list[str]:
    """Commands hidden inside this one: `bash -c '...'`, `pwsh -Command ...`, `eval`, $(...)."""
    inner = substitutions(segment)
    verb = command_verb(toks)
    if verb == "eval":
        inner.append(" ".join(toks[1:]))
    elif verb in SHELLS or verb in POWERSHELLS or verb in ("cmd", "cmd.exe"):
        for i, tok in enumerate(toks[:-1]):
            if tok in INLINE_FLAGS:
                inner.append(toks[i + 1] if verb in SHELLS else " ".join(toks[i + 1:]))
                break
    return [command for command in inner if command.strip()]


def deletion_targets(segment: str, toks: list[str]) -> list[str]:
    """Arguments of a delete command, or [] when the segment deletes nothing.

    Paths are taken both from shlex (quotes resolved) and from a plain whitespace split,
    because POSIX shlex reads the backslashes in a Windows path as escapes.
    """
    names = verbs(toks)
    if names & DELETE_VERBS or ("find" in names and ("-delete" in toks or "rm" in toks)):
        return toks[1:] + segment.split()[1:]
    if PY_DELETE.search(segment):
        return PATH_LIKE.findall(segment)
    return []


def substitutions(segment: str) -> list[str]:
    """Commands in $(...) and backticks, which the shell runs before the command itself.

    Like bash: nothing inside single quotes is expanded, and an escaped backtick is a literal.
    """
    text = re.sub(r"'[^']*'", "''", segment).replace("\\`", "")
    return [a or b for a, b in SUBSTITUTION.findall(text)]


def normalise(path: str) -> str:
    path = path.strip().strip("'\"").replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def is_artifact(token: str) -> bool:
    path = normalise(token)
    if not path or path.startswith("-"):
        return False
    if any(ch in path for ch in "*?["):
        return any(fnmatch.fnmatch(example.lower(), path.lower()) for example in ARTIFACT_EXAMPLES)
    return any(pattern.search(path) for pattern in ARTIFACTS)


def map_entry_points(repo: Path) -> set[str]:
    """Entry points on the danger list, as the dependency map records them."""
    found = {"agents/api/main.py"}  # the API's routes; build_graph.py roots it specially
    try:
        surfaces = json.loads((repo / "docs" / "depgraph" / "entry-points.json").read_text(encoding="utf-8"))
        graph = json.loads((repo / "docs" / "depgraph" / "graph.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return found
    for files in surfaces.values():
        found.update(files)
    runners = {f for key in ("workflows", "makefiles", "dockerfile") for f in surfaces.get(key, [])}
    found.update(dst for src, dst in graph.get("edges", []) if src in runners)
    return found


class Protected:
    """Whether deleting a path needs a human: published artifacts and the map's entry points.

    The map is read only when a command actually deletes something, so ordinary commands
    pay nothing for it.
    """

    def __init__(self, cwd: str):
        self.cwd = Path(cwd)
        self._repo: Path | None = None
        self._files: set[str] | None = None

    def repo(self) -> Path:
        if self._repo is None:
            top = ""
            try:
                top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=self.cwd,
                                     capture_output=True, text=True, timeout=5).stdout.strip()
            except Exception:
                pass
            self._repo = Path(top) if top else self.cwd
        return self._repo

    def files(self) -> set[str]:
        if self._files is None:
            self._files = map_entry_points(self.repo())
        return self._files

    def __call__(self, token: str, cwd: Path | None) -> bool:
        """`cwd` is where the command runs; None when a `cd` made it unknowable."""
        if is_artifact(token):
            return True
        path = normalise(token)
        if not path or path.startswith("-") or "://" in path:
            return False
        if cwd is None:
            # Unknown directory (`cd -`, `cd $DIR`): match on the path's tail, erring on
            # the side of asking a human.
            tail = path.lstrip("/").rstrip("/")
            return bool(tail) and any(f == tail or f.endswith("/" + tail) or f.startswith(tail + "/")
                                      for f in self.files())
        try:
            candidate = Path(path)
            absolute = candidate if candidate.is_absolute() else cwd / candidate
            rel = Path(os.path.relpath(absolute, self.repo())).as_posix().rstrip("/")
        except ValueError:
            return False  # another drive on Windows
        if rel.startswith(".."):
            return False
        if rel in ("", "."):
            return True  # the whole repository
        if any(ch in rel for ch in "*?["):
            return any(fnmatch.fnmatch(f, rel) for f in self.files())
        return rel in self.files() or any(f.startswith(rel + "/") for f in self.files())


def git_call(toks: list[str]) -> tuple[str, list[str], str | None] | None:
    """(subcommand, args, -C directory) for a `git ...` call, past git's global options."""
    for i, tok in enumerate(toks):
        if Path(tok).name.lower() in ("git", "git.exe"):
            j, workdir = i + 1, None
            while j < len(toks) and toks[j].startswith("-"):
                if toks[j] == "-C" and j + 1 < len(toks):
                    workdir = toks[j + 1]
                j += 2 if toks[j] in GIT_GLOBAL_WITH_VALUE else 1
            return (toks[j], toks[j + 1:], workdir) if j < len(toks) else None
    return None


def current_branch(cwd: str) -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd,
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip()
    except Exception:
        return ""


def in_cloud_agent() -> bool:
    # Set in the cloud agent's sandbox (hooks reference, "Cloud agent execution environment").
    return bool(os.environ.get("COPILOT_AGENT_PROMPT") or os.environ.get("GITHUB_COPILOT_API_TOKEN"))


def push_problem(args: list[str], cwd: str) -> str | None:
    options = [a for a in args if a.startswith("-")]
    refspecs = [a for a in args if not a.startswith("-")][1:]  # the first positional is the remote
    if any(o in ("--force", "-f") or o.startswith("--force-with-lease") or SHORT_FORCE.fullmatch(o)
           for o in options) or any(r.startswith("+") for r in refspecs):
        return "force-pushing rewrites published history; push a new commit instead"
    if any(o in ("--all", "--mirror") for o in options):
        return "--all and --mirror push every branch, including main"
    branch = current_branch(cwd)
    for ref in refspecs or ["HEAD"]:
        target = ref.split(":")[-1] if ":" in ref else ref
        if target.startswith("refs/heads/"):
            target = target[len("refs/heads/"):]
        if target in ("HEAD", "@"):
            target = branch
        if target in ("main", "master"):
            return "main only changes through a reviewed pull request; push a branch and open a PR"
    return None


def git_problem(sub: str, args: list[str], cwd: str) -> str | None:
    if sub == "push":
        return push_problem(args, cwd)
    if sub == "clean" and any(a == "--force" or SHORT_FORCE.fullmatch(a) for a in args):
        return ("git clean -f deletes untracked files, which on a developer's machine include "
                "their own uncommitted work; delete the specific files you created")
    if in_cloud_agent():
        return None  # the sandbox holds no one else's uncommitted work
    if sub == "reset" and "--hard" in args:
        return ("git reset --hard discards every uncommitted change, including the user's own; "
                "revert the files you changed one by one")
    if sub in ("checkout", "restore") and any(a in (".", ":/", "*") for a in args) \
            and "--staged" not in args:
        return ("this discards every uncommitted change in the tree, including the user's own; "
                "restore the files you changed one by one")
    if (sub == "checkout" and any(a in ("-f", "--force") for a in args)) \
            or (sub == "switch" and any(a in ("-f", "--force", "--discard-changes") for a in args)):
        return ("a forced checkout or switch discards every uncommitted change, including the "
                "user's own; commit or restore your own files first")
    if sub == "stash" and args[:1] and args[0] in ("drop", "clear"):
        return "dropping a stash destroys work that may not be yours"
    return None


CD_VERBS = {"cd", "pushd", "chdir", "set-location", "sl"}


def deny_reason(command: str, cwd: str | Path | None, protects: Protected | None = None,
                depth: int = 0) -> str | None:
    here = Path(cwd) if cwd is not None else None
    protects = protects or Protected(str(here or os.getcwd()))
    if depth > 4:
        return None
    # Python code passed with -c contains `;` and quotes; check it whole before splitting.
    if PY_DELETE.search(command) and any(protects(p, here) for p in PATH_LIKE.findall(command)):
        return DANGER
    for segment in segments(command):
        toks = tokens(segment)
        if not toks:
            continue
        if command_verb(toks) in CD_VERBS:
            here = next_cwd(toks, here)  # `cd tooling && rm x.py` deletes tooling/x.py
            continue
        for inner in nested_commands(segment, toks):
            reason = deny_reason(inner, here, protects, depth + 1)
            if reason:
                return reason
        call = git_call(toks)
        if call and verbs(toks) & {"git", "git.exe"}:
            sub, args, workdir = call
            where = here if workdir is None else next_cwd(["cd", workdir], here)
            if sub == "rm" and any(protects(a, where) for a in args + segment.split()[2:]):
                return DANGER
            reason = git_problem(sub, args, str(where or protects.repo()))
            if reason:
                return reason
            continue
        if any(protects(t, here) for t in deletion_targets(segment, toks)):
            return DANGER
    return None


def pre_tool(payload: dict) -> dict | None:
    command = shell_command(payload)
    if not command:
        return None
    reason = deny_reason(command, str(payload.get("cwd") or os.getcwd()))
    if not reason:
        return None
    return {"permissionDecision": "deny",
            "permissionDecisionReason": f"agent-gates: {reason}. See the Rules section of AGENTS.md."}


# --- post-tool: does the edited file still parse? ---------------------------------------

PATCH_FILE = re.compile(r"^\*\*\* (?:Add|Update) File: (.+)$", re.M)


def edited_paths(payload: dict) -> list[str]:
    if tool_name(payload) not in EDIT_TOOLS:
        return []
    args = tool_args(payload)
    paths: list[str] = []
    if isinstance(args, dict):
        for key in ("path", "file_path", "filePath", "filename", "file"):
            if isinstance(args.get(key), str):
                paths.append(args[key])
        text = args.get("input") or args.get("patch")
        if isinstance(text, str):
            paths.extend(PATCH_FILE.findall(text))
    elif isinstance(args, str):
        paths.extend(PATCH_FILE.findall(args))
    return paths


def parse_problem(path: Path) -> str | None:
    if not path.is_file():
        return None
    suffix = path.suffix.lower()
    if suffix not in (".py", ".json", ".ipynb", ".yml", ".yaml", ".toml"):
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return f"not valid UTF-8 ({exc.reason})"
    try:
        if suffix == ".py":
            compile(text, str(path), "exec")
        elif suffix in (".json", ".ipynb"):
            json.loads(text)
        elif suffix in (".yml", ".yaml"):
            try:
                import yaml  # type: ignore
            except ImportError:
                return None
            yaml.safe_load(text)
        else:
            try:
                import tomllib
            except ImportError:
                return None
            tomllib.loads(text)
    except SyntaxError as exc:
        return f"line {exc.lineno}: {exc.msg}"
    except Exception as exc:
        return (str(exc).splitlines() or [type(exc).__name__])[0][:300]
    return None


def post_tool(payload: dict) -> dict | None:
    base = Path(str(payload.get("cwd") or os.getcwd()))
    problems = []
    for raw in edited_paths(payload):
        path = Path(raw) if Path(raw).is_absolute() else base / raw
        problem = parse_problem(path)
        if problem:
            problems.append(f"{raw} no longer parses ({problem})")
    if not problems:
        return None
    return {"additionalContext": "agent-gates: " + "; ".join(problems)
            + ". Fix this before making further changes."}


# --- stop: the checks CI would fail on ---------------------------------------------------

CODE_SUFFIXES = {".py", ".qs", ".ts", ".tsx"}


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, timeout=30)
    return out.stdout if out.returncode == 0 else ""


def changed_files(repo: Path) -> tuple[set[str], bool]:
    """Files changed on this branch: uncommitted, plus committed since the default branch.

    The flag is False when the committed part could not be worked out (no remote default
    branch to compare with), so the caller runs the whole-repository checks anyway.
    """
    files: set[str] = set()
    entries = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0")
    skip_next = False
    for entry in entries:
        if skip_next:
            skip_next = False
            continue
        if len(entry) > 3:
            files.add(entry[3:])
            skip_next = entry[0] in "RC"  # a rename is followed by its source path
    for ref in ("origin/HEAD", "origin/main", "origin/master"):
        base = git(repo, "merge-base", "HEAD", ref).strip()
        if base:
            files.update(git(repo, "diff", "--name-only", base, "HEAD").split("\n"))
            files.discard("")
            return files, True
    return files, False


def untracked_for_graph(repo: Path) -> list[str]:
    """Untracked files that CI will see in the dependency graph once the agent commits.

    In the cloud sandbox every untracked file is the agent's and gets committed. On a
    developer's machine untracked files include the developer's own notes, which are never
    committed; counting them would report drift on every stop, because graph.json records
    the number of tracked files. There, only untracked code counts.
    """
    files = [f for f in git(repo, "ls-files", "--others", "--exclude-standard").split("\n") if f]
    if in_cloud_agent():
        return files
    return [f for f in files if Path(f).suffix in CODE_SUFFIXES
            or Path(f).name in ("Makefile", "Dockerfile", "package.json")
            or f.startswith(".github/workflows/")]


def depgraph_drift(repo: Path) -> str | None:
    """Rebuild the dependency graph into a temp dir and compare it with docs/depgraph.

    The same computation as the depgraph-drift workflow, without touching the working
    tree. Files the agent has not added yet are counted as tracked (see untracked_for_graph):
    build_graph.py on its own would not see them, so a brand-new file would pass here and
    fail in CI.
    """
    script = repo / "tooling" / "depgraph" / "build_graph.py"
    out_dir = repo / "docs" / "depgraph"
    if not script.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_agent_gates_build_graph", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    untracked = untracked_for_graph(repo)
    tracked = module.git_tracked_files
    module.git_tracked_files = lambda: sorted(set(tracked()) | set(untracked))
    with tempfile.TemporaryDirectory() as tmp:
        module.OUT_DIR = Path(tmp)
        stdout = sys.stdout
        with open(os.devnull, "w") as devnull:
            sys.stdout = devnull
            try:
                module.main()
            finally:
                sys.stdout = stdout
        stale = sorted(
            p.name for p in Path(tmp).iterdir()
            if not (out_dir / p.name).is_file()
            or (out_dir / p.name).read_bytes().replace(b"\r\n", b"\n") != p.read_bytes()
        )
    if not stale:
        return None
    new_code = [f for f in untracked if Path(f).suffix in CODE_SUFFIXES]
    add_first = (f" It reads tracked files only, so run `git add -N {' '.join(new_code[:5])}` first."
                 if new_code else "")
    return (f"docs/depgraph is stale ({', '.join(stale)}). Run "
            f"`python tooling/depgraph/build_graph.py` and commit docs/depgraph/.{add_first}")


def python_syntax(repo: Path, files: set[str]) -> list[str]:
    problems = []
    for rel in sorted(files):
        if rel.endswith(".py"):
            problem = parse_problem(repo / rel)
            if problem:
                problems.append(f"{rel} does not compile ({problem})")
    return problems


def workflow_problems(repo: Path) -> list[str]:
    """The checks ci-cd.yml's "Validate workflow YAML" step makes."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return []
    problems = []
    for path in sorted((repo / ".github" / "workflows").glob("*.y*ml")):
        rel = path.relative_to(repo).as_posix()
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            problems.append(f"{rel} does not parse ({str(exc).splitlines()[0]})")
            continue
        if not isinstance(doc, dict) or not doc.get("jobs") or (True not in doc and "on" not in doc):
            problems.append(f"{rel} needs `on:` and `jobs:`, or GitHub registers it and never runs it")
        elif not doc.get("name"):
            problems.append(f"{rel} has no `name:`, so GitHub shows the file path instead")
    return problems


def run_check(repo: Path, argv: list[str], label: str, timeout: int) -> str | None:
    try:
        out = subprocess.run(argv, cwd=repo, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    if out.returncode == 0:
        return None
    # stdout carries the failure summary; stderr is mostly warnings, so it is the fallback.
    lines = [line for line in out.stdout.splitlines() if line.strip()] \
        or [line for line in out.stderr.splitlines() if line.strip()]
    return f"{label} failed:\n    " + "\n    ".join(lines[-6:])


def stop(payload: dict) -> dict | None:
    if payload.get("stop_hook_active") or payload.get("stopHookActive"):
        return None  # already sent back once for this stop; CI is the backstop
    start = Path(str(payload.get("cwd") or os.getcwd()))
    repo = Path(git(start, "rev-parse", "--show-toplevel").strip() or start)
    files, known = changed_files(repo)
    if known and not files:
        return None

    def touched(predicate) -> bool:
        return not known or any(predicate(f) for f in files)

    problems: list[str] = python_syntax(repo, files)
    if touched(lambda f: Path(f).suffix in CODE_SUFFIXES or Path(f).name in ("Makefile", "Dockerfile")
               or f.startswith(".github/workflows/") or f == "website/package.json"):
        try:
            drift = depgraph_drift(repo)
        except Exception:
            drift = None
        if drift:
            problems.append(drift)
    if touched(lambda f: f.startswith(".github/workflows/")):
        problems += workflow_problems(repo)
    if any(f.endswith(".qs") or f.endswith("qsharp.json") for f in files) \
            and (repo / "tooling" / "ci_validate_qsharp.py").is_file():
        problem = run_check(repo, [sys.executable, "tooling/ci_validate_qsharp.py"],
                            "Q# compilation (`python tooling/ci_validate_qsharp.py`)", 120)
        if problem:
            problems.append(problem)
    if any(Path(f).name.startswith("test_") or Path(f).name in ("conftest.py", "pytest.ini")
           for f in files) and (repo / "tooling" / "test_doc_claims.py").is_file():
        problem = run_check(repo, [sys.executable, "-m", "pytest", "tooling/test_doc_claims.py",
                                   "-q", "-p", "no:cacheprovider", "--no-header"],
                            "Documented test counts (`python -m pytest tooling/test_doc_claims.py -q`)", 150)
        if problem:
            problems.append(problem)
    if not problems:
        return None
    return {
        "decision": "block",
        "reason": "agent-gates: before you finish, CI would fail on this:\n- "
                  + "\n- ".join(problems)
                  + "\nFix these and verify, then finish. If this session is a review or a plan "
                    "and should not change files, report them as findings instead.",
    }


# --- entry point -----------------------------------------------------------------------

HANDLERS = {"pre-tool": pre_tool, "post-tool": post_tool, "stop": stop}


def main(argv: list[str]) -> int:
    try:
        handler = HANDLERS.get(argv[1] if len(argv) > 1 else "")
        if handler is None:
            return 0
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict):
            return 0
        result = handler(payload)
        if result:
            sys.stdout.write(json.dumps(result) + "\n")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
