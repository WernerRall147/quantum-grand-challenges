"""Run build/classical/test verification matrix across registered problems."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_registry(root: Path) -> List[Dict[str, str]]:
    registry_path = root / "tooling" / "azure" / "problem_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = payload.get("problems", [])
    return [r for r in rows if isinstance(r, dict) and isinstance(r.get("id"), str)]


def discover_make(root: Path, explicit: str | None) -> str | None:
    if explicit:
        candidate = Path(explicit)
        if candidate.exists():
            return str(candidate)
        return None

    on_path = shutil.which("make")
    if on_path:
        return on_path

    fallback_paths = [
        root / "tools" / "make" / "bin" / "make.exe",
        Path(r"C:\Program Files (x86)\GnuWin32\bin\make.exe"),
        Path(r"C:\Program Files\Git\usr\bin\make.exe"),
    ]
    for path in fallback_paths:
        if path.exists():
            return str(path)
    return None


def tail(text: str, lines: int = 16) -> str:
    chunks = text.strip().splitlines()
    if not chunks:
        return ""
    return "\n".join(chunks[-lines:])


def run_cmd(cmd: List[str], cwd: Path, timeout: int, env: Dict[str, str]) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "status": "timeout",
            "ok": False,
            "returncode": None,
            "stdout_tail": tail(stdout),
            "stderr_tail": tail(stderr),
        }

    stdout_tail = tail(proc.stdout)
    stderr_tail = tail(proc.stderr)
    combined = f"{proc.stdout}\n{proc.stderr}".lower()
    no_rule = "no rule to make target" in combined

    if proc.returncode == 0:
        status = "passed"
        ok = True
    elif no_rule:
        status = "not_defined"
        ok = None
    else:
        status = "failed"
        ok = False

    return {
        "status": status,
        "ok": ok,
        "returncode": proc.returncode,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
    }


def run_make_target(make_exe: str | None, problem_dir: Path, target: str, timeout: int, env: Dict[str, str]) -> Dict[str, Any]:
    if not make_exe:
        return {
            "status": "tool_missing",
            "ok": False,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": "make executable not found",
        }
    return run_cmd([make_exe, target], problem_dir, timeout, env)


def write_markdown(report: Dict[str, Any], path: Path) -> None:
    lines: List[str] = []
    summary = report["summary"]

    lines.append("# Problem Verification Matrix")
    lines.append("")
    lines.append(f"- Generated UTC: `{report['generated_utc']}`")
    lines.append(f"- Total Problems: `{summary['total']}`")
    lines.append(f"- Build Passed: `{summary['build_passed']}`")
    lines.append(f"- Classical Passed: `{summary['classical_passed']}`")
    lines.append(f"- Test Passed: `{summary['test_passed']}`")
    lines.append(f"- Test Missing: `{summary['test_not_defined']}`")
    lines.append("")
    lines.append("## Per Problem")
    lines.append("")
    lines.append("| Problem | Build | Classical | Test |")
    lines.append("| --- | --- | --- | --- |")

    for row in report["problems"]:
        lines.append(
            f"| `{row['problem_id']}` | {row['build']['status']} | {row['classical']['status']} | {row['test']['status']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run build/classical/test matrix for all problems.")
    parser.add_argument("--make-exe", default=None)
    parser.add_argument("--build-timeout", type=int, default=240)
    parser.add_argument("--classical-timeout", type=int, default=240)
    parser.add_argument("--test-timeout", type=int, default=240)
    parser.add_argument("--output-json", default="tooling/reporting/problem_verification_matrix.json")
    parser.add_argument("--output-md", default="tooling/reporting/problem_verification_matrix.md")
    args = parser.parse_args()

    root = repo_root()
    registry = load_registry(root)
    make_exe = discover_make(root, args.make_exe)

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env.setdefault("MPLBACKEND", "Agg")

    rows: List[Dict[str, Any]] = []
    for item in registry:
        problem_id = item["id"]
        problem_dir = root / "problems" / problem_id
        build = run_make_target(make_exe, problem_dir, "build", args.build_timeout, env)
        classical = run_make_target(make_exe, problem_dir, "classical", args.classical_timeout, env)
        test = run_make_target(make_exe, problem_dir, "test", args.test_timeout, env)

        rows.append(
            {
                "problem_id": problem_id,
                "problem_name": item.get("name", problem_id),
                "build": build,
                "classical": classical,
                "test": test,
            }
        )

    summary = {
        "total": len(rows),
        "build_passed": sum(1 for r in rows if r["build"]["status"] == "passed"),
        "classical_passed": sum(1 for r in rows if r["classical"]["status"] == "passed"),
        "test_passed": sum(1 for r in rows if r["test"]["status"] == "passed"),
        "test_not_defined": sum(1 for r in rows if r["test"]["status"] == "not_defined"),
        "test_failed": sum(1 for r in rows if r["test"]["status"] == "failed"),
    }

    report = {
        "generated_utc": utc_now(),
        "environment": {
            "make_exe": make_exe,
        },
        "summary": summary,
        "problems": rows,
    }

    out_json = Path(args.output_json)
    if not out_json.is_absolute():
        out_json = (root / out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    out_md = Path(args.output_md)
    if not out_md.is_absolute():
        out_md = (root / out_md).resolve()
    out_md.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(report, out_md)

    print("Problem verification matrix written")
    print(f"  json: {out_json}")
    print(f"  md: {out_md}")
    print(f"  summary: build={summary['build_passed']}/{summary['total']}, classical={summary['classical_passed']}/{summary['total']}, test={summary['test_passed']} passed, {summary['test_not_defined']} not defined, {summary['test_failed']} failed")


if __name__ == "__main__":
    main()
