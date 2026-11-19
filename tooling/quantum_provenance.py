"""Portable provenance for local and Azure Quantum executions."""

from __future__ import annotations

import hashlib
import importlib.metadata
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

if __package__:
    from .evidence_hashes import file_digest, problem_source_files
else:
    from evidence_hashes import file_digest, problem_source_files

PROVENANCE_SCHEMA_VERSION = "1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def bytes_sha256(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def qir_sha256(qir: Any) -> str:
    if isinstance(qir, Path):
        return bytes_sha256(qir.read_bytes())
    return bytes_sha256(str(qir))


def source_file_hashes(paths: Iterable[Path], repo_root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in paths:
        resolved = path.resolve()
        relative = resolved.relative_to(repo_root.resolve()).as_posix()
        hashes[relative] = file_digest(resolved)
    return hashes


def problem_submission_source_files(qsharp_dir: Path) -> list[Path]:
    """Include project files and root-level standalone hardware adapters."""
    return sorted(
        set(problem_source_files(qsharp_dir)) | set(qsharp_dir.glob("*.qs"))
    )


def repository_state(repo_root: Path) -> dict[str, Any]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    ).stdout
    return {
        "source_revision": revision,
        "worktree_dirty": bool(status.strip()),
    }


def installed_qdk_version() -> str:
    return importlib.metadata.version("qdk")


def target_profile_for_target(target_id: str) -> str | None:
    normalized = target_id.lower()
    if "quantinuum" in normalized:
        return "Adaptive_RI"
    if "ionq" in normalized or "rigetti" in normalized:
        return "Base"
    return None


def build_run_provenance(
    *,
    repo_root: Path,
    problem_id: str,
    entry_point: str,
    source_paths: Iterable[Path],
    execution_mode: str,
    target_id: str | None,
    target_profile: str | None,
    shots: int,
    status: str,
    input_format: str = "qir.v1",
    expected_target_profile: str | None = None,
    qir: Any | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Build a source-bound record for a simulator or Quantum job.

    The caller controls where the record is stored. Job IDs belong only in
    private or gitignored stores; public website data must omit the argument.
    """
    input_hash = qir_sha256(qir) if qir is not None else None
    record: dict[str, Any] = {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "recorded_utc": utc_now(),
        "problem_id": problem_id,
        "entry_point": entry_point,
        "execution_mode": execution_mode,
        "target_id": target_id,
        "target_profile": target_profile,
        "expected_target_profile": expected_target_profile,
        "shots": shots,
        "status": status,
        "qdk_version": installed_qdk_version(),
        "source_files": source_file_hashes(source_paths, repo_root),
        "input_format": input_format,
        "input_sha256": input_hash,
        "qir_sha256": input_hash if "qir" in input_format.lower() else None,
        **repository_state(repo_root),
    }
    if job_id is not None:
        record["job_id"] = job_id
    return record
