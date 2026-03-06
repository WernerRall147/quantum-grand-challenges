"""Validate schema and privacy constraints for website data artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable


SENSITIVE_FIELDS = {
    "job_id",
    "provider",
    "workspace",
    "subscription_id",
    "resource_group",
    "workspace_name",
    "manifest_path",
    "submitted_utc",
    "problem_name",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_required_keys(obj: Dict[str, Any], required: Iterable[str], label: str) -> None:
    missing = [k for k in required if k not in obj]
    if missing:
        raise ValueError(f"{label}: missing keys: {', '.join(missing)}")


def validate_azure_history(path: Path) -> None:
    payload = load_json(path)
    assert_required_keys(payload, ["schema_version", "updated_utc", "runs"], "azureRunHistory")

    runs = payload["runs"]
    if not isinstance(runs, list):
        raise ValueError("azureRunHistory.runs must be a list")

    for idx, row in enumerate(runs):
        if not isinstance(row, dict):
            raise ValueError(f"azureRunHistory.runs[{idx}] must be an object")
        assert_required_keys(
            row,
            ["recorded_utc", "problem_id", "instance_id", "depth", "target_id", "status"],
            f"azureRunHistory.runs[{idx}]",
        )

        present_sensitive = sorted(SENSITIVE_FIELDS.intersection(row.keys()))
        if present_sensitive:
            raise ValueError(
                f"azureRunHistory.runs[{idx}] contains sensitive keys: {', '.join(present_sensitive)}"
            )


def validate_runnable_report(path: Path) -> None:
    payload = load_json(path)
    assert_required_keys(payload, ["generated_utc", "environment", "summary", "problems"], "problemRunnableCorrectnessReport")

    summary = payload["summary"]
    if not isinstance(summary, dict):
        raise ValueError("problemRunnableCorrectnessReport.summary must be an object")
    assert_required_keys(summary, ["total", "passed", "failed"], "problemRunnableCorrectnessReport.summary")

    problems = payload["problems"]
    if not isinstance(problems, list):
        raise ValueError("problemRunnableCorrectnessReport.problems must be a list")

    for idx, row in enumerate(problems):
        if not isinstance(row, dict):
            raise ValueError(f"problemRunnableCorrectnessReport.problems[{idx}] must be an object")
        assert_required_keys(
            row,
            ["problem_id", "problem_name", "classical", "classical_baseline_json", "qsharp", "runnable_and_correct_signal"],
            f"problemRunnableCorrectnessReport.problems[{idx}]",
        )


def main() -> None:
    root = repo_root()
    azure_history = root / "website" / "data" / "azureRunHistory.json"
    runnable_report = root / "website" / "data" / "problemRunnableCorrectnessReport.json"

    validate_azure_history(azure_history)
    validate_runnable_report(runnable_report)

    print("Website data schema validation passed")


if __name__ == "__main__":
    main()
