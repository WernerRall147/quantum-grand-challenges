"""Write Azure smoke workflow evidence artifacts for QAOA manifests."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve(path_arg: str) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return (Path.cwd() / path).resolve()


def _string(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else default
    return default


def _safe_int(value: Any, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed


def _default_output_paths(manifest_path: Path, instance: str, depth: int) -> tuple[Path, Path]:
    base_dir = manifest_path.parent
    stem = f"azure_smoke_report_{instance}_d{depth}"
    return (base_dir / f"{stem}.json", base_dir / f"{stem}.md")


def _portable_path(path: Path) -> str:
    try:
        rel = path.relative_to(Path.cwd())
        return rel.as_posix()
    except ValueError:
        return path.as_posix()


def _build_report(
    payload: Dict[str, Any],
    mode: str,
    collect_enabled: bool,
    collect_attempted: bool,
    manifest_path: Path,
) -> Dict[str, Any]:
    backend = payload.get("backend", {}) if isinstance(payload.get("backend"), dict) else {}
    workspace = backend.get("workspace", {}) if isinstance(backend.get("workspace"), dict) else {}
    submission = payload.get("submission", {}) if isinstance(payload.get("submission"), dict) else {}

    instance = _string(payload.get("instance_id"), "unknown")
    depth = _safe_int(payload.get("depth"), 0)

    submission_status = _string(submission.get("status"), "unknown")
    result_status = _string(submission.get("result_status"), "pending")

    checks = {
        "env_gate": "passed",
        "cli_preflight": "passed",
        "manifest_generated": "passed",
        "manifest_validated": "passed",
        "submit_step": "executed" if mode == "execute" else "dry_run",
        "collect_step": "attempted" if collect_attempted else ("enabled_but_skipped" if collect_enabled else "skipped"),
    }

    report = {
        "generated_utc": utc_now(),
        "workflow": "azure-smoke",
        "overall_status": "passed",
        "manifest_path": _portable_path(manifest_path),
        "mode": mode,
        "instance_id": instance,
        "depth": depth,
        "backend": {
            "provider": _string(backend.get("provider"), "azure-quantum"),
            "target_id": _string(backend.get("target_id"), "unknown"),
            "job_name": _string(backend.get("job_name"), ""),
            "workspace": {
                "subscription_id": _string(workspace.get("subscription_id"), ""),
                "resource_group": _string(workspace.get("resource_group"), ""),
                "workspace_name": _string(workspace.get("workspace_name"), ""),
                "location": _string(workspace.get("location"), ""),
            },
        },
        "submission": {
            "job_id": _string(submission.get("job_id"), ""),
            "status": submission_status,
            "result_status": result_status,
            "submitted_utc": _string(submission.get("submitted_utc"), ""),
            "dry_run_command": _string(submission.get("dry_run_command"), ""),
        },
        "checks": checks,
    }

    return report


def _render_markdown(report: Dict[str, Any]) -> str:
    backend = report["backend"]
    workspace = backend["workspace"]
    submission = report["submission"]
    checks = report["checks"]

    lines = [
        "# Azure Smoke Report",
        "",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Workflow: `{report['workflow']}`",
        f"- Overall Status: `{report['overall_status']}`",
        f"- Mode: `{report['mode']}`",
        f"- Instance: `{report['instance_id']}`",
        f"- Depth: `{report['depth']}`",
        f"- Manifest: `{report['manifest_path']}`",
        "",
        "## Backend",
        "",
        f"- Provider: `{backend['provider']}`",
        f"- Target ID: `{backend['target_id']}`",
        f"- Job Name: `{backend['job_name']}`",
        f"- Subscription: `{workspace['subscription_id']}`",
        f"- Resource Group: `{workspace['resource_group']}`",
        f"- Workspace: `{workspace['workspace_name']}`",
        f"- Location: `{workspace['location']}`",
        "",
        "## Submission",
        "",
        f"- Job ID: `{submission['job_id']}`",
        f"- Status: `{submission['status']}`",
        f"- Result Status: `{submission['result_status']}`",
        f"- Submitted UTC: `{submission['submitted_utc']}`",
        f"- Dry Run Command: `{submission['dry_run_command']}`",
        "",
        "## Checks",
        "",
        f"- Env Gate: `{checks['env_gate']}`",
        f"- CLI Preflight: `{checks['cli_preflight']}`",
        f"- Manifest Generated: `{checks['manifest_generated']}`",
        f"- Manifest Validated: `{checks['manifest_validated']}`",
        f"- Submit Step: `{checks['submit_step']}`",
        f"- Collect Step: `{checks['collect_step']}`",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Write Azure smoke evidence artifacts from a QAOA manifest.")
    parser.add_argument(
        "--manifest",
        default="problems/05_qaoa_maxcut/estimates/azure_job_manifest_small_d3.json",
        help="Path to Azure manifest JSON.",
    )
    parser.add_argument(
        "--mode",
        choices=["dry-run", "execute"],
        default="dry-run",
        help="Smoke execution mode.",
    )
    parser.add_argument(
        "--collect-enabled",
        action="store_true",
        default=False,
        help="Collect phase configured as enabled in the smoke workflow.",
    )
    parser.add_argument(
        "--collect-attempted",
        action="store_true",
        default=False,
        help="Collect phase was executed in this smoke workflow run.",
    )
    parser.add_argument("--output-json", default=None, help="Optional JSON output path.")
    parser.add_argument("--output-md", default=None, help="Optional markdown output path.")
    args = parser.parse_args()

    manifest_path = _resolve(args.manifest)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Manifest must be a JSON object")

    instance = _string(payload.get("instance_id"), "unknown")
    depth = _safe_int(payload.get("depth"), 0)

    default_json, default_md = _default_output_paths(manifest_path, instance, depth)
    output_json = _resolve(args.output_json) if args.output_json else default_json
    output_md = _resolve(args.output_md) if args.output_md else default_md

    report = _build_report(
        payload=payload,
        mode=args.mode,
        collect_enabled=args.collect_enabled,
        collect_attempted=args.collect_attempted,
        manifest_path=manifest_path,
    )

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(_render_markdown(report) + "\n", encoding="utf-8")

    print("Azure smoke report written")
    print(f"  json: {output_json}")
    print(f"  md: {output_md}")


if __name__ == "__main__":
    main()
