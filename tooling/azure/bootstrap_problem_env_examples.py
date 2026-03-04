"""Ensure every registered problem has a local .env.azure.example template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_problem_ids(registry_path: Path) -> list[str]:
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    out: list[str] = []
    for row in payload.get("problems", []):
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            out.append(row["id"])
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Create missing .env.azure.example files for all problems.")
    parser.add_argument("--write", action="store_true", default=False, help="Write missing files instead of dry-run.")
    args = parser.parse_args()

    root = _repo_root()
    template = root / "tooling" / "azure" / ".env.azure.example"
    registry = root / "tooling" / "azure" / "problem_registry.json"

    if not template.exists():
        raise SystemExit(f"Template not found: {template}")

    template_text = template.read_text(encoding="utf-8")

    created: list[str] = []
    existing: list[str] = []

    for problem_id in _load_problem_ids(registry):
        target = root / "problems" / problem_id / ".env.azure.example"
        if target.exists():
            existing.append(problem_id)
            continue
        created.append(problem_id)
        if args.write:
            target.write_text(template_text, encoding="utf-8")

    mode = "write" if args.write else "dry-run"
    print(f"Bootstrap mode: {mode}")
    print(f"Existing templates: {len(existing)}")
    print(f"Missing templates: {len(created)}")
    if created:
        print("Affected problem ids:")
        for pid in created:
            print(f"  - {pid}")


if __name__ == "__main__":
    main()
