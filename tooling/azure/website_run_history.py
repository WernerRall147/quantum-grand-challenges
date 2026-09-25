"""One merge rule for website/data/azureRunHistory.json, shared by every writer.

The website file has more than one writer. The nightly audit and collect_job.py used to
rebuild it from tooling/azure/run_history.json alone, a record that stopped being updated
in March, so each rebuild deleted the runs only the website file held: 107 of 130 (#241).
Both now write through write_website_history, which merges instead of replacing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def run_key(row: Dict[str, Any]) -> tuple[str, str, str, str]:
    # Website rows carry no job id, so identity is the tuple every writer records.
    return (
        str(row.get("recorded_utc", "")),
        str(row.get("problem_id", "")),
        str(row.get("target_id", "")),
        str(row.get("instance_id", "")),
    )


def merge_website_history(existing: Dict[str, Any], rebuilt: Dict[str, Any]) -> Dict[str, Any]:
    """Union of the runs already published and the runs a writer rebuilt.

    A rebuilt row updates the published row it describes, field by field, so fields only
    the website file records (a note, a shot count) survive. Published rows the writer
    did not rebuild are kept unchanged.
    """
    published = [row for row in existing.get("runs", []) if isinstance(row, dict)]
    rebuilt_runs = [row for row in rebuilt.get("runs", []) if isinstance(row, dict)]
    rebuilt_keys = {run_key(row) for row in rebuilt_runs}

    first_published: Dict[tuple[str, str, str, str], Dict[str, Any]] = {}
    for row in published:
        first_published.setdefault(run_key(row), row)

    merged = [{**first_published.get(run_key(row), {}), **row} for row in rebuilt_runs]
    merged += [row for row in published if run_key(row) not in rebuilt_keys]
    merged.sort(key=lambda row: str(row.get("recorded_utc", "")))
    return {**rebuilt, "runs": merged}


def write_website_history(path: Path, rebuilt: Dict[str, Any]) -> Dict[str, Any]:
    """Merge ``rebuilt`` into the history at ``path`` and write the result."""
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(existing, dict):
            raise ValueError(f"{path} is not a JSON object; refusing to overwrite it")
        rebuilt = merge_website_history(existing, rebuilt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rebuilt, indent=2) + "\n", encoding="utf-8")
    return rebuilt
