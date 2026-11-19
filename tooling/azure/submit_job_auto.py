"""Submit an Azure Quantum job from a shared problem manifest (dry-run safe)."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from azure_env import AzureEnvError, load_azure_env
from cli_runner import run_az

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tooling.discover_problems import resolve_problem_dir  # noqa: E402
from tooling.evidence_hashes import problem_source_files  # noqa: E402
from tooling.quantum_provenance import (  # noqa: E402
    build_run_provenance,
    target_profile_for_target,
)


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


def _run_az(args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    return run_az(args, timeout, check=True)


def _provenance(
    payload: dict[str, Any],
    *,
    target_id: str,
    entry_point: str,
    shots: int,
    job_input: Path | None,
    input_format: str,
    status: str,
    job_id: str | None = None,
) -> dict[str, Any]:
    problem_dir = resolve_problem_dir(str(payload["problem_id"]), ROOT)
    source_paths = problem_source_files(problem_dir / "qsharp")
    if not source_paths:
        raise SystemExit(f"No Q# source files found for {payload['problem_id']}")
    return build_run_provenance(
        repo_root=ROOT,
        problem_id=str(payload["problem_id"]),
        entry_point=entry_point,
        source_paths=source_paths,
        execution_mode="azure-quantum",
        target_id=target_id,
        target_profile=target_profile_for_target(target_id),
        shots=shots,
        status=status,
        input_format=input_format,
        qir=job_input,
        job_id=job_id,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit Azure job from generic problem manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--job-input-file", default=None)
    parser.add_argument("--job-input-format", default="qir.v1")
    parser.add_argument("--job-output-format", default=None)
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
    entry_point = args.entry_point or str(backend.get("entry_point") or "qir-embedded")

    cmd = [
        "quantum", "job", "submit",
        "--workspace-name", azure_env["AZURE_QUANTUM_WORKSPACE"],
        "--resource-group", azure_env["AZURE_RESOURCE_GROUP"],
        "--location", azure_env["AZURE_LOCATION"],
        "--target-id", target_id,
        "--job-name", job_name,
        "--shots", str(shots),
        "--output", "json",
    ]

    job_input = _resolve(args.job_input_file) if args.job_input_file else None
    if job_input:
        if not job_input.exists():
            raise SystemExit(f"Job input file not found: {job_input}")
        cmd.extend(["--job-input-file", str(job_input), "--job-input-format", args.job_input_format])

    if args.entry_point:
        cmd.extend(["--entry-point", args.entry_point])

    if args.job_output_format:
        cmd.extend(["--job-output-format", args.job_output_format])

    command_preview = _cmd_to_string(cmd)
    if not args.execute:
        submission["status"] = "not_submitted"
        submission["dry_run_command"] = command_preview
        payload["provenance"] = _provenance(
            payload,
            target_id=target_id,
            entry_point=entry_point,
            shots=shots,
            job_input=job_input,
            input_format=args.job_input_format,
            status="not_submitted",
        )
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print("Azure auto-submit dry run complete")
        print(f"  manifest: {manifest_path}")
        print(f"  command: {command_preview}")
        return

    if not args.job_input_file:
        raise SystemExit("--job-input-file is required with --execute")

    try:
        result = _run_az(cmd, args.az_timeout)
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
    payload["provenance"] = _provenance(
        payload,
        target_id=target_id,
        entry_point=entry_point,
        shots=shots,
        job_input=job_input,
        input_format=args.job_input_format,
        status=submission["status"],
        job_id=job_id,
    )

    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Azure auto-submit complete")
    print(f"  manifest: {manifest_path}")
    print(f"  job_id: {job_id}")


if __name__ == "__main__":
    main()
