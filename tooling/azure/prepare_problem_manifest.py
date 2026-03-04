"""Prepare a shared Azure Quantum job manifest for any problem directory."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve(path_arg: str) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return (Path.cwd() / path).resolve()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_registry() -> Dict[str, Dict[str, str]]:
    registry_path = Path(__file__).resolve().parent / "problem_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    out: Dict[str, Dict[str, str]] = {}
    for row in payload.get("problems", []):
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            out[row["id"]] = {
                "name": str(row.get("name", row["id"])),
                "default_target_id": str(row.get("default_target_id", "microsoft.estimator")),
            }
    return out


def _candidate_evidence_paths(problem_dir: Path, instance: str, depth: int) -> List[Path]:
    estimates = problem_dir / "estimates"
    return [
        estimates / f"quantum_baseline_{instance}_d{depth}.json",
        estimates / "quantum_estimate_ensemble.json",
        estimates / "quantum_estimate.json",
        estimates / "latest.json",
        estimates / "classical_baseline.json",
    ]


def _find_first_existing(paths: List[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def _portable(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare generic Azure manifest for a problem.")
    parser.add_argument("--problem", required=True, help="Problem folder id, e.g. 03_qae_risk")
    parser.add_argument("--instance", default="small")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--target-id", default=None)
    parser.add_argument("--evidence-file", default=None)
    parser.add_argument("--manifest", default=None, help="Optional explicit output path")
    args = parser.parse_args()

    root = _repo_root()
    registry = _load_registry()
    if args.problem not in registry:
        raise SystemExit(f"Unknown problem id '{args.problem}'. Add it to tooling/azure/problem_registry.json.")

    problem_dir = root / "problems" / args.problem
    if not problem_dir.exists():
        raise SystemExit(f"Problem directory not found: {problem_dir}")

    if args.evidence_file:
        evidence_path = _resolve(args.evidence_file)
        if not evidence_path.exists():
            raise SystemExit(f"Evidence file not found: {evidence_path}")
    else:
        evidence_path = _find_first_existing(_candidate_evidence_paths(problem_dir, args.instance, args.depth))
        if evidence_path is None:
            raise SystemExit(
                "No evidence file found automatically. Provide --evidence-file explicitly for this problem/instance."
            )

    if args.manifest:
        manifest_path = _resolve(args.manifest)
    else:
        manifest_path = problem_dir / "estimates" / f"azure_job_manifest_{args.instance}_d{args.depth}.json"

    manifest: Dict[str, Any] = {
        "manifest_version": "1.0",
        "generated_utc": utc_now(),
        "problem_id": args.problem,
        "problem_name": registry[args.problem]["name"],
        "instance_id": args.instance,
        "depth": args.depth,
        "backend": {
            "provider": "azure-quantum",
            "target_id": args.target_id or registry[args.problem]["default_target_id"],
            "job_name": f"{args.problem}-{args.instance}-d{args.depth}",
            "workspace": {
                "subscription_id": None,
                "resource_group": None,
                "workspace_name": None,
                "location": None,
            },
        },
        "execution": {
            "shots": args.shots,
            "refined_shots": args.shots,
            "trials": args.trials,
        },
        "evidence": {
            "primary_artifact": _portable(evidence_path, root),
            "related_artifacts": [],
        },
        "submission": {
            "status": "not_submitted",
            "submitted_utc": None,
            "job_id": None,
            "result_status": None,
            "dry_run_command": None,
        },
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("Prepared Azure manifest")
    print(f"  problem: {args.problem}")
    print(f"  manifest: {manifest_path}")
    print(f"  evidence: {evidence_path}")


if __name__ == "__main__":
    main()
