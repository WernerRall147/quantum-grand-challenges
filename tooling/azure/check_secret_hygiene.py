"""Enforce Azure secret hygiene and local env file rules."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _problem_ids(root: Path) -> list[str]:
    import json

    payload = json.loads((root / "tooling" / "azure" / "problem_registry.json").read_text(encoding="utf-8"))
    return [row["id"] for row in payload.get("problems", []) if isinstance(row, dict) and isinstance(row.get("id"), str)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Azure secret hygiene and env template coverage.")
    args = parser.parse_args()
    _ = args

    root = _repo_root()
    tracked = _tracked_files(root)

    failures: list[str] = []

    if "**/.env.azure.local" not in (root / ".gitignore").read_text(encoding="utf-8"):
        failures.append("Missing required .gitignore pattern: **/.env.azure.local")

    tracked_local_env = [p for p in tracked if p.endswith(".env.azure.local")]
    if tracked_local_env:
        failures.append("Tracked local Azure env files detected:")
        failures.extend([f"  - {p}" for p in tracked_local_env])

    missing_templates: list[str] = []
    for pid in _problem_ids(root):
        # A problem may live at problems/<pid> (active) or
        # problems/archived/<pid> (archived per the Troyer restructure).
        candidate_paths = [
            root / "problems" / pid / ".env.azure.example",
            root / "problems" / "archived" / pid / ".env.azure.example",
        ]
        if not any(path.exists() for path in candidate_paths):
            missing_templates.append(f"problems/{pid}/.env.azure.example (or problems/archived/{pid}/)")

    if missing_templates:
        failures.append("Missing per-problem .env.azure.example files:")
        failures.extend([f"  - {p}" for p in missing_templates])

    if failures:
        print("Azure secret hygiene check FAILED")
        for line in failures:
            print(line)
        raise SystemExit(1)

    print("Azure secret hygiene check passed")
    print("  - .gitignore has **/.env.azure.local")
    print("  - no tracked .env.azure.local files")
    print("  - per-problem .env.azure.example files exist for all registered problems")


if __name__ == "__main__":
    main()
