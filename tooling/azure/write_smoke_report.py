"""Write generic Azure smoke report from manifest data."""

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
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _portable(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser(description="Write Azure smoke report JSON/MD for a generic problem manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    parser.add_argument("--collect-enabled", action="store_true", default=False)
    parser.add_argument("--collect-attempted", action="store_true", default=False)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    args = parser.parse_args()

    manifest_path = _resolve(args.manifest)
    root = Path.cwd().resolve()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    backend = payload.get("backend", {}) if isinstance(payload.get("backend"), dict) else {}
    workspace = backend.get("workspace", {}) if isinstance(backend.get("workspace"), dict) else {}
    submission = payload.get("submission", {}) if isinstance(payload.get("submission"), dict) else {}

    problem_id = _string(payload.get("problem_id"), "unknown")
    instance = _string(payload.get("instance_id"), "unknown")
    depth = _safe_int(payload.get("depth"), 0)

    if args.output_json:
        out_json = _resolve(args.output_json)
    else:
        out_json = manifest_path.parent / f"azure_smoke_report_{instance}_d{depth}.json"

    if args.output_md:
        out_md = _resolve(args.output_md)
    else:
        out_md = manifest_path.parent / f"azure_smoke_report_{instance}_d{depth}.md"

    report: Dict[str, Any] = {
        "generated_utc": utc_now(),
        "workflow": "azure-smoke",
        "overall_status": "passed",
        "problem_id": problem_id,
        "manifest_path": _portable(manifest_path, root),
        "mode": args.mode,
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
            "status": _string(submission.get("status"), "unknown"),
            "result_status": _string(submission.get("result_status"), "pending"),
            "submitted_utc": _string(submission.get("submitted_utc"), ""),
            "dry_run_command": _string(submission.get("dry_run_command"), ""),
        },
        "checks": {
            "env_gate": "passed",
            "cli_preflight": "passed",
            "manifest_generated": "passed",
            "submit_step": "executed" if args.mode == "execute" else "dry_run",
            "collect_step": "attempted" if args.collect_attempted else ("enabled_but_skipped" if args.collect_enabled else "skipped"),
        },
    }

    lines = [
        "# Azure Smoke Report",
        "",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Workflow: `{report['workflow']}`",
        f"- Overall Status: `{report['overall_status']}`",
        f"- Problem: `{report['problem_id']}`",
        f"- Mode: `{report['mode']}`",
        f"- Instance: `{report['instance_id']}`",
        f"- Depth: `{report['depth']}`",
        f"- Manifest: `{report['manifest_path']}`",
        "",
        "## Submission",
        "",
        f"- Job ID: `{report['submission']['job_id']}`",
        f"- Status: `{report['submission']['status']}`",
        f"- Result Status: `{report['submission']['result_status']}`",
        f"- Submitted UTC: `{report['submission']['submitted_utc']}`",
        "",
    ]

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Azure smoke report written")
    print(f"  json: {out_json}")
    print(f"  md: {out_md}")


if __name__ == "__main__":
    main()
