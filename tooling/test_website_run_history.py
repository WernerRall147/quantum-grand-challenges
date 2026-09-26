"""No writer of the website run history may delete runs from it (#241).

`website/data/azureRunHistory.json` has several writers. `update_website_data.py` appends
runs to it. The nightly `audit_azure_run_history_metrics.py` and `collect_job.py` used to
rebuild it from `tooling/azure/run_history.json`, a record that stopped being updated in
March; the nightly branch that did this cut the file from 130 runs to 23, and a single
collect would have cut it to 24.

These tests run the writers themselves against copies of the files, because the bug was in
what they wrote, not in anything a reader of their source would notice.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AZURE_DIR = REPO_ROOT / "tooling" / "azure"
AUDIT = REPO_ROOT / "tooling" / "reporting" / "audit_azure_run_history_metrics.py"
SOURCE = AZURE_DIR / "run_history.json"
WEBSITE = REPO_ROOT / "website" / "data" / "azureRunHistory.json"


def _key(row: dict) -> tuple[str, str, str, str]:
    return (
        str(row.get("recorded_utc", "")),
        str(row.get("problem_id", "")),
        str(row.get("target_id", "")),
        str(row.get("instance_id", "")),
    )


def _run_audit(tmp_path: Path, source: dict, website: dict) -> dict:
    source_path = tmp_path / "run_history.json"
    website_path = tmp_path / "azureRunHistory.json"
    source_path.write_text(json.dumps(source), encoding="utf-8")
    website_path.write_text(json.dumps(website), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT),
            "--run-history", str(source_path),
            "--website-history", str(website_path),
            "--output-json", str(tmp_path / "audit.json"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(website_path.read_text(encoding="utf-8"))


def test_audit_keeps_every_committed_website_run(tmp_path: Path) -> None:
    """Run against the committed files: no website run may disappear."""
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    website = json.loads(WEBSITE.read_text(encoding="utf-8"))

    before = {_key(row) for row in website["runs"]}
    after = [_key(row) for row in _run_audit(tmp_path, source, website)["runs"]]

    lost = before - set(after)
    assert not lost, f"the audit deleted {len(lost)} of {len(before)} website runs"
    assert len(after) == len(set(after)), "the audit duplicated runs it should have merged"
    assert set(after) == before | {_key(row) for row in source["runs"]}


def test_audited_rows_replace_the_website_rows_they_describe(tmp_path: Path) -> None:
    """A run in both files takes the audited values; website-only runs and fields are kept."""
    shared = {
        "recorded_utc": "2026-03-05T10:00:00Z",
        "problem_id": "05_qaoa_maxcut",
        "target_id": "rigetti.sim.qvm",
        "instance_id": "small",
        "status": "succeeded",
    }
    audited = {**shared, "runtime_seconds": 1.5, "queue_seconds": 2.0, "duration_seconds": 3.5}
    website_only = {
        "recorded_utc": "2026-04-13T10:00:00Z",
        "problem_id": "15_database_search",
        "target_id": "quantinuum.sim.h2-1e",
        "instance_id": "small",
        "status": "succeeded",
    }
    source = {"schema_version": "1.0", "updated_utc": "", "runs": [audited]}
    website = {
        "schema_version": "1.0",
        "updated_utc": "",
        "runs": [{**shared, "note": "only the website records this"}, website_only],
    }

    runs = {_key(row): row for row in _run_audit(tmp_path, source, website)["runs"]}

    assert len(runs) == 2
    assert runs[_key(shared)]["runtime_seconds"] == 1.5
    assert runs[_key(shared)]["metrics_status"] == "available"
    assert runs[_key(shared)]["note"] == "only the website records this"
    assert runs[_key(website_only)]["status"] == "succeeded"


@pytest.fixture
def collect_job(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """collect_job.py pointed at copies of the committed history files."""
    monkeypatch.syspath_prepend(str(AZURE_DIR))
    module = importlib.import_module("collect_job")
    source_copy = tmp_path / "run_history.json"
    website_copy = tmp_path / "azureRunHistory.json"
    source_copy.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    website_copy.write_text(WEBSITE.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(module, "RUN_HISTORY_PATH", source_copy)
    monkeypatch.setattr(module, "WEBSITE_HISTORY_PATH", website_copy)
    return module


def _succeeded_payload(job_id: str) -> dict:
    return {
        "problem_id": "15_database_search",
        "problem_name": "Database Search",
        "instance_id": "small",
        "depth": 1,
        "backend": {"provider": "azure-quantum", "target_id": "quantinuum.sim.h2-1e", "workspace": {}},
        "submission": {"status": "succeeded", "job_id": job_id, "submitted_utc": "2026-09-25T00:00:00Z"},
    }


def test_collecting_a_new_job_adds_it_without_deleting_history(collect_job, tmp_path: Path) -> None:
    before = {_key(row) for row in json.loads(WEBSITE.read_text(encoding="utf-8"))["runs"]}

    collect_job._record_successful_run(_succeeded_payload("new-job-for-test"), tmp_path / "manifest.json")

    after = json.loads(collect_job.WEBSITE_HISTORY_PATH.read_text(encoding="utf-8"))["runs"]
    lost = before - {_key(row) for row in after}
    assert not lost, f"collecting one job deleted {len(lost)} of {len(before)} website runs"
    assert len(after) == len(before) + 1


def test_recollecting_a_known_job_updates_it_without_deleting_history(collect_job, tmp_path: Path) -> None:
    before = {_key(row) for row in json.loads(WEBSITE.read_text(encoding="utf-8"))["runs"]}
    known = json.loads(SOURCE.read_text(encoding="utf-8"))["runs"][0]

    collect_job._record_successful_run(
        _succeeded_payload(known["job_id"]), tmp_path / "manifest.json", {"runtime_seconds": 9.5}
    )

    after = {
        _key(row): row
        for row in json.loads(collect_job.WEBSITE_HISTORY_PATH.read_text(encoding="utf-8"))["runs"]
    }
    lost = before - set(after)
    assert not lost, f"re-collecting one job deleted {len(lost)} of {len(before)} website runs"
    assert after[_key(known)]["runtime_seconds"] == 9.5
