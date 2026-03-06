"""Ensure checked-in verification matrix matches a freshly generated matrix on key fields."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(report: Dict[str, Any]) -> Dict[str, Any]:
    problems = report.get("problems", [])
    normalized_rows = []
    for row in problems:
        normalized_rows.append(
            {
                "problem_id": str(row.get("problem_id", "")),
                "build": str((row.get("build") or {}).get("status", "")),
                "classical": str((row.get("classical") or {}).get("status", "")),
                "test": str((row.get("test") or {}).get("status", "")),
            }
        )

    normalized_rows.sort(key=lambda r: r["problem_id"])
    return {
        "summary": report.get("summary", {}),
        "problems": normalized_rows,
    }


def main() -> None:
    root = repo_root()
    checked_in = root / "tooling" / "reporting" / "problem_verification_matrix.json"

    if not checked_in.exists():
        raise SystemExit(f"Missing checked-in matrix: {checked_in}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_json = Path(tmp_dir) / "matrix.json"
        tmp_md = Path(tmp_dir) / "matrix.md"

        cmd = [
            sys.executable,
            str(root / "tooling" / "reporting" / "run_problem_verification_matrix.py"),
            "--output-json",
            str(tmp_json),
            "--output-md",
            str(tmp_md),
        ]
        subprocess.run(cmd, check=True, cwd=str(root))

        expected = normalize(load_json(checked_in))
        actual = normalize(load_json(tmp_json))

    if expected != actual:
        print("Verification matrix is stale or inconsistent.")
        print("Expected summary:", expected.get("summary", {}))
        print("Actual summary:", actual.get("summary", {}))

        expected_rows = {r["problem_id"]: r for r in expected.get("problems", [])}
        actual_rows = {r["problem_id"]: r for r in actual.get("problems", [])}
        all_ids = sorted(set(expected_rows) | set(actual_rows))

        mismatches = 0
        for pid in all_ids:
            if expected_rows.get(pid) != actual_rows.get(pid):
                mismatches += 1
                print(f"- {pid}: expected={expected_rows.get(pid)}, actual={actual_rows.get(pid)}")
                if mismatches >= 10:
                    print("... additional mismatches omitted")
                    break
        raise SystemExit(1)

    print("Verification matrix freshness check passed")


if __name__ == "__main__":
    main()
