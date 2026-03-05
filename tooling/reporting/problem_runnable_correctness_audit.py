"""Run runnable/correctness audit across all registered problems."""

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


def tail(text: str, lines: int = 20) -> str:
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
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout_tail": tail(proc.stdout),
            "stderr_tail": tail(proc.stderr),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "ok": False,
            "returncode": None,
            "stdout_tail": tail(stdout),
            "stderr_tail": tail(stderr),
            "timed_out": True,
        }


def has_dotnet6() -> bool:
    try:
        proc = subprocess.run(["dotnet", "--list-runtimes"], capture_output=True, text=True, check=False, timeout=20)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return "Microsoft.NETCore.App 6." in proc.stdout


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit all problems for runnable/correctness signals.")
    parser.add_argument("--classical-timeout", type=int, default=120)
    parser.add_argument("--qsharp-timeout", type=int, default=180)
    parser.add_argument("--include-qsharp", action="store_true", default=False)
    parser.add_argument("--make-exe", default=None)
    parser.add_argument("--output", default="tooling/reporting/problem_runnable_correctness_report.json")
    args = parser.parse_args()

    root = repo_root()
    registry = load_registry(root)

    make_exe = discover_make(root, args.make_exe)
    dotnet_exe = shutil.which("dotnet")
    dotnet6_available = has_dotnet6() if dotnet_exe else False

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env.setdefault("MPLBACKEND", "Agg")

    rows: List[Dict[str, Any]] = []
    for item in registry:
        problem_id = item["id"]
        problem_dir = root / "problems" / problem_id

        makefile_exists = (problem_dir / "Makefile").exists()
        classical_cmd = [make_exe, "classical"] if make_exe else []

        if make_exe and makefile_exists:
            classical = run_cmd(classical_cmd, problem_dir, args.classical_timeout, env)
        else:
            classical = {
                "ok": False,
                "returncode": None,
                "stdout_tail": "",
                "stderr_tail": "make or Makefile not available",
                "timed_out": False,
            }

        baseline_json = problem_dir / "estimates" / "classical_baseline.json"
        baseline_valid = False
        baseline_error = ""
        if baseline_json.exists():
            try:
                json.loads(baseline_json.read_text(encoding="utf-8"))
                baseline_valid = True
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                baseline_error = str(exc)

        qsharp_dir = problem_dir / "qsharp"
        qsharp_attempted = bool(args.include_qsharp and dotnet_exe and qsharp_dir.exists())
        if qsharp_attempted and dotnet6_available:
            qsharp = run_cmd([dotnet_exe, "build", "--configuration", "Release"], qsharp_dir, args.qsharp_timeout, env)
        elif qsharp_attempted and not dotnet6_available:
            qsharp = {
                "ok": False,
                "returncode": None,
                "stdout_tail": "",
                "stderr_tail": ".NET 6 runtime missing",
                "timed_out": False,
            }
        else:
            qsharp = {
                "ok": None,
                "returncode": None,
                "stdout_tail": "",
                "stderr_tail": "not attempted",
                "timed_out": False,
            }

        runnable = bool(classical.get("ok")) and baseline_valid
        if args.include_qsharp:
            runnable = runnable and bool(qsharp.get("ok"))

        rows.append(
            {
                "problem_id": problem_id,
                "problem_name": item.get("name", problem_id),
                "classical": classical,
                "classical_baseline_json": {
                    "path": baseline_json.as_posix(),
                    "exists": baseline_json.exists(),
                    "valid_json": baseline_valid,
                    "error": baseline_error,
                },
                "qsharp": {
                    "attempted": qsharp_attempted,
                    **qsharp,
                },
                "runnable_and_correct_signal": runnable,
            }
        )

    passed = sum(1 for r in rows if r["runnable_and_correct_signal"])
    payload = {
        "generated_utc": utc_now(),
        "environment": {
            "make_available": bool(make_exe),
            "dotnet_available": bool(dotnet_exe),
            "dotnet6_available": dotnet6_available,
            "qsharp_included": bool(args.include_qsharp),
        },
        "summary": {
            "total": len(rows),
            "passed": passed,
            "failed": len(rows) - passed,
        },
        "problems": rows,
    }

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = (root / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # Mirror report into website data for dashboard rendering.
    website_path = root / "website" / "data" / "problemRunnableCorrectnessReport.json"
    website_path.parent.mkdir(parents=True, exist_ok=True)
    website_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Runnable/correctness audit written")
    print(f"  output: {out_path}")
    print(f"  website: {website_path}")
    print(f"  passed: {passed}/{len(rows)}")


if __name__ == "__main__":
    main()
