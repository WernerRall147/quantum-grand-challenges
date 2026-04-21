"""Submit a QAOA Azure job via Azure CLI with a dry-run-safe default."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from azure_env import AzureEnvError, load_azure_env


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_status(raw: str) -> str:
    normalized = raw.strip().lower()
    if normalized in {"waiting", "queued", "executing"}:
        return "running"
    if normalized in {"submitted", "running", "succeeded", "failed", "cancelled"}:
        return normalized
    return "submitted"


def _cmd_to_string(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def _resolve(path_arg: str) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return (Path.cwd() / path).resolve()


def _safe_int(value: Any, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if parsed > 0 else fallback


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit QAOA Azure job and update manifest metadata.")
    parser.add_argument(
        "--manifest",
        default="problems/05_qaoa_maxcut/estimates/azure_job_manifest_small_d3.json",
        help="Path to Azure manifest JSON.",
    )
    parser.add_argument(
        "--env-file",
        default="problems/05_qaoa_maxcut/.env.azure.local",
        help="Path to manual Azure env file.",
    )
    parser.add_argument(
        "--job-input-file",
        default=None,
        help="Path to job input file for Azure submission (required with --execute).",
    )
    parser.add_argument("--job-input-format", default="qir.v1")
    parser.add_argument("--entry-point", default=None)
    parser.add_argument("--target-id", default=None)
    parser.add_argument("--job-name", default=None)
    parser.add_argument("--shots", type=int, default=None)
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Actually run az quantum job submit. Without this flag, only dry-run preview is performed.",
    )
    parser.add_argument("--az-timeout", type=int, default=120)
    args = parser.parse_args()

    manifest_path = _resolve(args.manifest)
    env_path = _resolve(args.env_file)

    try:
        azure_env = load_azure_env(env_path)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise SystemExit(f"Azure auto-submit blocked: {exc}")

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Manifest must be a JSON object")

    backend = payload.setdefault("backend", {})
    workspace = backend.setdefault("workspace", {})

    instance = str(payload.get("instance_id", "unknown")).strip() or "unknown"
    depth = _safe_int(payload.get("depth"), 1)
    execution = payload.setdefault("execution", {})

    target_id = args.target_id or azure_env.get("AZURE_QUANTUM_TARGET_ID") or str(backend.get("target_id") or "microsoft.estimator")
    job_name = args.job_name or str(backend.get("job_name") or f"qaoa-{instance}-d{depth}")
    shots = args.shots if args.shots and args.shots > 0 else _safe_int(execution.get("refined_shots"), 100)

    backend["provider"] = azure_env.get("AZURE_QUANTUM_PROVIDER", "azure-quantum")
    backend["target_id"] = target_id
    backend["job_name"] = job_name
    workspace["subscription_id"] = azure_env["AZURE_SUBSCRIPTION_ID"]
    workspace["resource_group"] = azure_env["AZURE_RESOURCE_GROUP"]
    workspace["workspace_name"] = azure_env["AZURE_QUANTUM_WORKSPACE"]
    workspace["location"] = azure_env["AZURE_LOCATION"]

    submission = payload.setdefault("submission", {})

    cmd = [
        "az",
        "quantum",
        "job",
        "submit",
        "--workspace-name",
        azure_env["AZURE_QUANTUM_WORKSPACE"],
        "--resource-group",
        azure_env["AZURE_RESOURCE_GROUP"],
        "--location",
        azure_env["AZURE_LOCATION"],
        "--target-id",
        target_id,
        "--job-name",
        job_name,
        "--shots",
        str(shots),
        "--output",
        "json",
    ]

    if args.job_input_file:
        input_path = _resolve(args.job_input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Job input file not found: {input_path}")
        cmd.extend(["--job-input-file", str(input_path), "--job-input-format", args.job_input_format])

    if args.entry_point:
        cmd.extend(["--entry-point", args.entry_point])

    command_preview = _cmd_to_string(cmd)

    if not args.execute:
        submission["status"] = "not_submitted"
        submission["submitted_utc"] = submission.get("submitted_utc")
        submission["job_id"] = submission.get("job_id")
        submission["result_status"] = submission.get("result_status")
        submission["dry_run_command"] = command_preview

        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print("Azure auto-submit dry run complete (no submission performed)")
        print(f"  manifest: {manifest_path}")
        print(f"  command: {command_preview}")
        return

    if not args.job_input_file:
        raise ValueError("--job-input-file is required when --execute is used")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=args.az_timeout,
        )
    except FileNotFoundError:
        raise SystemExit("Azure auto-submit failed: 'az' command not found on PATH.")
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else str(exc)
        raise SystemExit(f"Azure auto-submit failed: {detail}")
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(f"Azure auto-submit timed out: {exc}")

    response = json.loads(result.stdout)
    if not isinstance(response, dict):
        raise ValueError("Azure CLI returned invalid submit response")

    job_id = str(response.get("id", "")).strip()
    if not job_id:
        raise ValueError("Azure CLI submit response did not include job id")

    submission["status"] = _normalize_status(str(response.get("status", "submitted")))
    submission["submitted_utc"] = utc_now()
    submission["job_id"] = job_id
    submission["result_status"] = None
    submission["dry_run_command"] = command_preview

    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Azure auto-submit complete: {manifest_path}")
    print(f"  job_id: {job_id}")
    print(f"  status: {submission['status']}")


if __name__ == "__main__":
    main()
