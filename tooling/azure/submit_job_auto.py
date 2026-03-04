"""Submit an Azure Quantum job from a shared problem manifest (dry-run safe)."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from azure_env import AzureEnvError, load_azure_env


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _status(raw: str) -> str:
    normalized = raw.strip().lower()
    if normalized in {"waiting", "queued", "executing"}:
        return "running"
    if normalized in {"submitted", "running", "succeeded", "failed", "cancelled"}:
        return normalized
    return "submitted"


def _cmd_to_string(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit Azure job from generic problem manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--job-input-file", default=None)
    parser.add_argument("--job-input-format", default="qir.v1")
    parser.add_argument("--entry-point", default=None)
    parser.add_argument("--target-id", default=None)
    parser.add_argument("--job-name", default=None)
    parser.add_argument("--shots", type=int, default=None)
    parser.add_argument("--execute", action="store_true", default=False)
    parser.add_argument("--az-timeout", type=int, default=120)
    args = parser.parse_args()

    manifest_path = _resolve(args.manifest)
    env_path = _resolve(args.env_file)

    try:
        azure_env = load_azure_env(env_path)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise SystemExit(f"Azure auto-submit blocked: {exc}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    backend = payload.setdefault("backend", {})
    workspace = backend.setdefault("workspace", {})
    execution = payload.setdefault("execution", {})
    submission = payload.setdefault("submission", {})

    target_id = args.target_id or azure_env.get("AZURE_QUANTUM_TARGET_ID") or str(backend.get("target_id") or "microsoft.estimator")
    job_name = args.job_name or str(backend.get("job_name") or f"{payload.get('problem_id', 'problem')}-{payload.get('instance_id', 'instance')}")
    shots = args.shots if args.shots and args.shots > 0 else _safe_int(execution.get("refined_shots"), 100)

    backend["provider"] = azure_env.get("AZURE_QUANTUM_PROVIDER", "azure-quantum")
    backend["target_id"] = target_id
    backend["job_name"] = job_name
    workspace["subscription_id"] = azure_env["AZURE_SUBSCRIPTION_ID"]
    workspace["resource_group"] = azure_env["AZURE_RESOURCE_GROUP"]
    workspace["workspace_name"] = azure_env["AZURE_QUANTUM_WORKSPACE"]
    workspace["location"] = azure_env["AZURE_LOCATION"]

    cmd = [
        "az", "quantum", "job", "submit",
        "--workspace-name", azure_env["AZURE_QUANTUM_WORKSPACE"],
        "--resource-group", azure_env["AZURE_RESOURCE_GROUP"],
        "--location", azure_env["AZURE_LOCATION"],
        "--target-id", target_id,
        "--job-name", job_name,
        "--shots", str(shots),
        "--output", "json",
    ]

    if args.job_input_file:
        job_input = _resolve(args.job_input_file)
        if not job_input.exists():
            raise SystemExit(f"Job input file not found: {job_input}")
        cmd.extend(["--job-input-file", str(job_input), "--job-input-format", args.job_input_format])

    if args.entry_point:
        cmd.extend(["--entry-point", args.entry_point])

    command_preview = _cmd_to_string(cmd)
    if not args.execute:
        submission["status"] = "not_submitted"
        submission["dry_run_command"] = command_preview
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print("Azure auto-submit dry run complete")
        print(f"  manifest: {manifest_path}")
        print(f"  command: {command_preview}")
        return

    if not args.job_input_file:
        raise SystemExit("--job-input-file is required with --execute")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=args.az_timeout)
    except FileNotFoundError:
        raise SystemExit("Azure auto-submit failed: 'az' command not found on PATH.")
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else str(exc)
        raise SystemExit(f"Azure auto-submit failed: {detail}")
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(f"Azure auto-submit timed out: {exc}")

    response = json.loads(result.stdout)
    job_id = str(response.get("id", "")).strip()
    if not job_id:
        raise SystemExit("Azure submit response did not include job id")

    submission["status"] = _status(str(response.get("status", "submitted")))
    submission["submitted_utc"] = utc_now()
    submission["job_id"] = job_id
    submission["result_status"] = None
    submission["dry_run_command"] = command_preview

    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Azure auto-submit complete")
    print(f"  manifest: {manifest_path}")
    print(f"  job_id: {job_id}")


if __name__ == "__main__":
    main()
