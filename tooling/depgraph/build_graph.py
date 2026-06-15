"""Deterministic dependency mapper for the repo (Phase 1).

Builds a file/module-level dependency + reachability graph from the git-tracked
source using only the Python standard library, so results are deterministic and
reproducible (no grimp/madge/vulture install required for the baseline). Emits
JSON artifacts under docs/depgraph/ that Claude and humans can read directly:

  graph.json              nodes + edges (python imports, ts imports, invocations)
  reverse-index.json      who references each file ("who uses X")
  entry-points.json       the root set (workflows, Makefiles, Dockerfile, pytest,
                          npm/next, Q# entry points)
  cleanup-candidates.json code files unreachable from any entry point, each with
                          evidence (no inbound edges) and risk flags (danger list)

Reachability rule: a code file is "used" if it is an entry point, is invoked by an
entry-point surface (Makefile / workflow / Dockerfile / npm), or is imported
(transitively) by a used file. Everything else is a candidate - but candidates that
match the danger list are marked needs_review, never safe_review.

Run:  python tooling/depgraph/build_graph.py
Re-run after any change so new files always land in the graph.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from collections import defaultdict, deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs" / "depgraph"

CODE_EXTS = {".py", ".qs", ".ts", ".tsx"}

# Danger-list path/name patterns: candidates matching these are needs_review, not
# safe_review (see docs/initiatives/repo-cleanup.md).
PROTECTED_PATH_RE = re.compile(
    r"(^|/)(docs/paper/|problems/archived/|\.github/|infrastructure/)"
    r"|(^|/)(conftest\.py|__init__\.py)$"
)
DYNAMIC_IMPORT_RE = re.compile(r"importlib|__import__|import_module|getattr\(")


def git_tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line.strip() for line in out.splitlines() if line.strip()]


def to_module(path: str) -> str:
    """Repo-relative .py path -> dotted module name (root is importable)."""
    p = path[:-3] if path.endswith(".py") else path
    p = p[:-9] if p.endswith("/__init__") else p
    return p.replace("/", ".")


def module_dir_pkg(path: str) -> str:
    """Dotted package of the directory containing a .py file (for relative imports)."""
    parts = path.split("/")[:-1]
    return ".".join(parts)


def py_import_targets(tree: ast.AST, pkg: str) -> set[str]:
    """Candidate dotted targets imported by a module (resolved against the map later)."""
    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                targets.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                base_parts = pkg.split(".") if pkg else []
                up = node.level - 1
                base_parts = base_parts[: len(base_parts) - up] if up else base_parts
                base = ".".join(base_parts)
                mod = f"{base}.{node.module}" if node.module else base
            else:
                mod = node.module or ""
            if mod:
                targets.add(mod)
                for alias in node.names:
                    targets.add(f"{mod}.{alias.name}")  # submodule case
    return targets


def ts_import_targets(text: str, path: str) -> set[str]:
    """Resolve relative TS/TSX imports to repo-relative files."""
    targets: set[str] = set()
    here = Path(path).parent
    for m in re.finditer(r"""(?:import|from)\s+['"](\.[^'"]+)['"]""", text):
        rel = m.group(1)
        base = (here / rel).as_posix()
        for cand in (base, base + ".ts", base + ".tsx",
                     base + "/index.ts", base + "/index.tsx"):
            norm = Path(cand).as_posix()
            targets.add(norm)
    return targets


def qs_is_entry(text: str) -> bool:
    return "@EntryPoint" in text or re.search(r"operation\s+Main\b", text) is not None


def referenced_paths(text: str) -> set[str]:
    """Repo-relative file paths and `python -m module` refs mentioned in a surface file."""
    refs: set[str] = set()
    for m in re.finditer(r"[A-Za-z0-9_./-]+\.py\b", text):
        refs.add(m.group(0).lstrip("./"))
    for m in re.finditer(r"-m\s+([A-Za-z0-9_.]+)", text):
        refs.add("MODULE:" + m.group(1))
    return refs


def main() -> None:
    tracked = git_tracked_files()
    tracked_set = set(tracked)

    py_files = [f for f in tracked if f.endswith(".py")]
    ts_files = [f for f in tracked if f.endswith((".ts", ".tsx"))]
    qs_files = [f for f in tracked if f.endswith(".qs")]
    code_files = [f for f in tracked if Path(f).suffix in CODE_EXTS]

    # Python module -> file map
    mod_to_file: dict[str, str] = {to_module(f): f for f in py_files}

    edges: set[tuple[str, str]] = set()        # (referencer, referenced)
    file_text: dict[str, str] = {}

    def read(f: str) -> str:
        if f not in file_text:
            try:
                file_text[f] = (REPO / f).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                file_text[f] = ""
        return file_text[f]

    def resolve_module(target: str) -> str | None:
        """Longest-prefix resolution of a dotted import target to a tracked file."""
        parts = target.split(".")
        for i in range(len(parts), 0, -1):
            cand = ".".join(parts[:i])
            if cand in mod_to_file:
                return mod_to_file[cand]
        return None

    # --- Python import edges ---
    py_unparsable: list[str] = []
    for f in py_files:
        src = read(f)
        try:
            tree = ast.parse(src, filename=f)
        except SyntaxError:
            py_unparsable.append(f)
            continue
        pkg = module_dir_pkg(f)
        f_dir = Path(f).parent.as_posix()
        for target in py_import_targets(tree, pkg):
            dst = resolve_module(target)
            if dst is None and "." not in target:
                # Bare-name sibling import (scripts run from their own directory and
                # import a neighbour by basename, relying on sys.path). Deterministic
                # same-directory resolution.
                sib = f"{f_dir}/{target}.py" if f_dir and f_dir != "." else f"{target}.py"
                if sib in tracked_set:
                    dst = sib
            if dst and dst != f:
                edges.add((f, dst))

    # --- TS import edges ---
    for f in ts_files:
        for dst in ts_import_targets(read(f), f):
            if dst in tracked_set and dst != f:
                edges.add((f, dst))

    # --- Entry-point surfaces + invocation edges ---
    entry_points: dict[str, list[str]] = {
        "workflows": [], "makefiles": [], "dockerfile": [], "pytest": [],
        "npm_next": [], "qsharp": [],
    }
    roots: set[str] = set()

    def add_invocations(surface: str) -> None:
        surface_dir = Path(surface).parent.as_posix()
        text = read(surface)
        for ref in referenced_paths(text):
            if ref.startswith("MODULE:"):
                dst = resolve_module(ref[len("MODULE:"):])
            else:
                # Resolve relative to the surface's own directory first (per-problem
                # Makefiles use paths like "python/classical_baseline.py"), then the
                # repo root, then a unique global suffix match.
                cands = []
                if surface_dir and surface_dir != ".":
                    cands.append(f"{surface_dir}/{ref}")
                cands.append(ref)
                dst = next((c for c in cands if c in tracked_set), None)
                if dst is None:
                    hits = [t for t in tracked if t.endswith("/" + ref)]
                    dst = hits[0] if len(hits) == 1 else None
            if dst:
                edges.add((surface, dst))
                roots.add(dst)

    for f in tracked:
        if f.startswith(".github/workflows/") and f.endswith((".yml", ".yaml")):
            entry_points["workflows"].append(f); roots.add(f); add_invocations(f)
        elif Path(f).name == "Makefile":
            entry_points["makefiles"].append(f); roots.add(f); add_invocations(f)
        elif Path(f).name == "Dockerfile":
            entry_points["dockerfile"].append(f); roots.add(f); add_invocations(f)
        elif f == "website/package.json":
            entry_points["npm_next"].append(f); roots.add(f)

    # pytest discovers tests + conftest
    for f in py_files:
        name = Path(f).name
        if name == "conftest.py" or name.startswith("test_") or "/tests/" in f:
            entry_points["pytest"].append(f); roots.add(f)

    # Next.js file-routing: website/pages/** are entry points
    for f in ts_files:
        if f.startswith("website/pages/"):
            entry_points["npm_next"].append(f); roots.add(f)

    # Q#: each .qs whose project (nearest qsharp.json) has an entry point is reachable
    qsharp_projects = {f[: -len("qsharp.json")].rstrip("/")
                       for f in tracked if f.endswith("qsharp.json")}
    project_has_entry: dict[str, bool] = defaultdict(bool)
    for f in qs_files:
        if qs_is_entry(read(f)):
            for proj in qsharp_projects:
                if f.startswith(proj + "/"):
                    project_has_entry[proj] = True
    for f in qs_files:
        proj = next((p for p in qsharp_projects if f.startswith(p + "/")), None)
        if proj is not None:
            roots.add(f)  # belongs to a real Q# project -> protected/used
            entry_points["qsharp"].append(f)

    # Dockerfile runs the API module explicitly; ensure it is a root
    api_main = "agents/api/main.py"
    if api_main in tracked_set:
        roots.add(api_main)

    # --- Reachability (BFS over edges from roots) ---
    adj: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
    reachable: set[str] = set()
    queue = deque(roots)
    reachable.update(roots)
    while queue:
        cur = queue.popleft()
        for nxt in adj[cur]:
            if nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    # --- Reverse index ---
    reverse: dict[str, list[str]] = defaultdict(list)
    for a, b in sorted(edges):
        reverse[b].append(a)

    # --- Candidates (unreachable code files) + risk flags ---
    candidates = []
    for f in sorted(code_files):
        if f in reachable:
            continue
        text = read(f)
        flags = []
        if f.endswith(".qs"):
            flags.append("qsharp")
        if "if __name__ == " in text:
            flags.append("cli_main")
        if DYNAMIC_IMPORT_RE.search(text):
            flags.append("dynamic_import")
        if PROTECTED_PATH_RE.search(f):
            flags.append("protected_path")
        if f in reverse:
            flags.append("has_inbound_non_root")
        category = "needs_review" if flags else "safe_review"
        candidates.append({
            "file": f,
            "inbound": reverse.get(f, []),
            "risk_flags": flags,
            "category": category,
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    graph = {
        "repo_relative_root": ".",
        "counts": {
            "tracked": len(tracked), "code_files": len(code_files),
            "python": len(py_files), "qsharp": len(qs_files), "ts": len(ts_files),
            "edges": len(edges), "roots": len(roots), "reachable": len(reachable),
        },
        "nodes": sorted(code_files),
        "edges": sorted([list(e) for e in edges]),
    }
    def write_json(name: str, obj: object) -> None:
        # LF + trailing newline + UTF-8 so output is byte-identical on Windows and
        # Linux (the CI drift check diffs this against a fresh run).
        (OUT_DIR / name).write_text(
            json.dumps(obj, indent=2) + "\n", encoding="utf-8", newline="\n")

    write_json("graph.json", graph)
    write_json("reverse-index.json", {k: v for k, v in sorted(reverse.items())})
    write_json("entry-points.json", {k: sorted(set(v)) for k, v in entry_points.items()})
    write_json("cleanup-candidates.json", {
        "summary": {
            "total_candidates": len(candidates),
            "safe_review": sum(1 for c in candidates if c["category"] == "safe_review"),
            "needs_review": sum(1 for c in candidates if c["category"] == "needs_review"),
            "python_unparsable": sorted(py_unparsable),
        },
        "candidates": candidates,
    })

    print("Dependency graph written to docs/depgraph/")
    print(f"  tracked={len(tracked)} code={len(code_files)} edges={len(edges)} "
          f"roots={len(roots)} reachable={len(reachable)}")
    print(f"  candidates={len(candidates)} "
          f"(safe_review={sum(1 for c in candidates if c['category']=='safe_review')}, "
          f"needs_review={sum(1 for c in candidates if c['category']=='needs_review')})")


if __name__ == "__main__":
    main()
