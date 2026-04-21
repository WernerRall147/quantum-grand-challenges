"""Validate the QAOA Azure Quantum job manifest contract and referenced artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

ALLOWED_STATUSES = {
    "not_submitted",
    "submitted",
    "running",
    "succeeded",
    "failed",
    "cancelled",
}


def _require_keys(obj: Dict[str, Any], keys: list[str], context: str) -> None:
    for key in keys:
        if key not in obj:
            raise ValueError(f"Missing key '{key}' in {context}")


def _require_int(value: Any, name: str, minimum: int = 1) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return value


def _resolve_rel(root: Path, raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    return (root / candidate).resolve()


def validate_manifest(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Manifest must be a JSON object")

    _require_keys(payload, ["problem_id", "instance_id", "depth", "execution", "backend", "submission", "evidence"], "manifest")

    if payload["problem_id"] != "05_qaoa_maxcut":
        raise ValueError("problem_id must be '05_qaoa_maxcut'")

    if payload["instance_id"] not in {"small", "medium", "large"}:
        raise ValueError("instance_id must be one of: small, medium, large")

    _require_int(payload["depth"], "depth", minimum=1)

    execution = payload["execution"]
    if not isinstance(execution, dict):
        raise ValueError("execution must be an object")
    _require_keys(execution, ["coarse_shots", "refined_shots", "trials"], "execution")
    _require_int(execution["coarse_shots"], "execution.coarse_shots", minimum=1)
    _require_int(execution["refined_shots"], "execution.refined_shots", minimum=1)
    _require_int(execution["trials"], "execution.trials", minimum=1)

    backend = payload["backend"]
    if not isinstance(backend, dict):
        raise ValueError("backend must be an object")
    _require_keys(backend, ["provider", "target_id", "job_name"], "backend")
    for key in ["provider", "target_id", "job_name"]:
        value = backend[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"backend.{key} must be a non-empty string")

    submission = payload["submission"]
    if not isinstance(submission, dict):
        raise ValueError("submission must be an object")
    _require_keys(submission, ["status", "submitted_utc", "job_id"], "submission")
    status = submission["status"]
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"submission.status must be one of {sorted(ALLOWED_STATUSES)}")

    if status != "not_submitted":
        job_id = submission.get("job_id")
        submitted_utc = submission.get("submitted_utc")
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("submission.job_id must be set once status is not_submitted -> submitted/running/terminal")
        if not isinstance(submitted_utc, str) or not submitted_utc.strip():
            raise ValueError("submission.submitted_utc must be set once status is not_submitted")

        workspace = backend.get("workspace")
        if not isinstance(workspace, dict):
            raise ValueError("backend.workspace must be present once status is not_submitted")
        for key in ["subscription_id", "resource_group", "workspace_name", "location"]:
            value = workspace.get(key)
            if value is None or not isinstance(value, str) or not value.strip():
                raise ValueError(f"backend.workspace.{key} must be set once status is not_submitted")

    evidence = payload["evidence"]
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    _require_keys(evidence, ["quantum_baseline", "depth_sweep", "noise_sweep", "summary"], "evidence")

    root = Path(__file__).resolve().parents[1]
    required_paths = {
        "quantum_baseline": evidence["quantum_baseline"],
        "depth_sweep": evidence["depth_sweep"],
        "summary": evidence["summary"],
    }
    for label, raw in required_paths.items():
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f"evidence.{label} must be a non-empty string path")
        resolved = _resolve_rel(root, raw)
        if not resolved.exists():
            raise FileNotFoundError(f"Referenced evidence file not found ({label}): {resolved}")

    noise_raw = evidence.get("noise_sweep")
    if noise_raw is not None:
        if not isinstance(noise_raw, str) or not noise_raw.strip():
            raise ValueError("evidence.noise_sweep must be null or a non-empty string path")
        noise_path = _resolve_rel(root, noise_raw)
        if not noise_path.exists():
            raise FileNotFoundError(f"Referenced evidence file not found (noise_sweep): {noise_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate QAOA Azure Quantum job manifest.")
    parser.add_argument(
        "--manifest",
        default="problems/05_qaoa_maxcut/estimates/azure_job_manifest_small_d3.json",
        help="Path to Azure manifest JSON.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (Path.cwd() / manifest_path).resolve()

    validate_manifest(manifest_path)
    print(f"Azure job manifest validation passed: {manifest_path}")


if __name__ == "__main__":
    main()
