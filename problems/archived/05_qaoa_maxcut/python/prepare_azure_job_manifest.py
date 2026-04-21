"""Generate an Azure Quantum execution contract manifest for QAOA Max-Cut."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional


def _pick_noise_depth(instance_id: str) -> Optional[int]:
    if instance_id == "small":
        return 3
    if instance_id in {"medium", "large"}:
        return 2
    return None


def _relative_str(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Azure Quantum job manifest for QAOA Max-Cut.")
    parser.add_argument("--instance", default="small", help="Instance id (small/medium/large).")
    parser.add_argument("--depth", type=int, default=3, help="QAOA depth to associate with this manifest.")
    parser.add_argument("--coarse-shots", type=int, default=24)
    parser.add_argument("--refined-shots", type=int, default=96)
    parser.add_argument("--trials", type=int, default=6)
    parser.add_argument("--provider", default="azure-quantum")
    parser.add_argument("--target-id", default="microsoft.estimator")
    parser.add_argument("--job-name", default=None, help="Optional explicit job name.")
    parser.add_argument("--subscription-id", default=None)
    parser.add_argument("--resource-group", default=None)
    parser.add_argument("--workspace-name", default=None)
    parser.add_argument("--location", default=None)
    parser.add_argument("--status", default="not_submitted")
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output path. Defaults to estimates/azure_job_manifest_<instance>_d<depth>.json",
    )
    args = parser.parse_args()

    if args.depth < 1:
        raise ValueError("depth must be >= 1")
    if args.coarse_shots < 1 or args.refined_shots < 1 or args.trials < 1:
        raise ValueError("shots/trials must be >= 1")

    root = Path(__file__).resolve().parents[1]
    estimates_dir = root / "estimates"

    quantum_baseline = estimates_dir / f"quantum_baseline_{args.instance}_d{args.depth}.json"
    depth_sweep = estimates_dir / f"depth_sweep_{args.instance}.json"
    summary = estimates_dir / "quantum_classical_summary.md"

    noise_depth = _pick_noise_depth(args.instance)
    noise_sweep = estimates_dir / f"noise_sweep_{args.instance}_d{noise_depth}.json" if noise_depth else None

    if not quantum_baseline.exists():
        raise FileNotFoundError(f"Missing quantum baseline artifact: {quantum_baseline}")
    if not depth_sweep.exists():
        raise FileNotFoundError(f"Missing depth sweep artifact: {depth_sweep}")
    if not summary.exists():
        raise FileNotFoundError(f"Missing summary artifact: {summary}")

    if noise_sweep is not None and not noise_sweep.exists():
        noise_sweep = None

    job_name = args.job_name or f"qaoa-{args.instance}-d{args.depth}"

    payload = {
        "problem_id": "05_qaoa_maxcut",
        "instance_id": str(args.instance),
        "depth": int(args.depth),
        "execution": {
            "coarse_shots": int(args.coarse_shots),
            "refined_shots": int(args.refined_shots),
            "trials": int(args.trials),
        },
        "backend": {
            "provider": str(args.provider),
            "target_id": str(args.target_id),
            "job_name": job_name,
            "workspace": {
                "subscription_id": args.subscription_id,
                "resource_group": args.resource_group,
                "workspace_name": args.workspace_name,
                "location": args.location,
            },
        },
        "submission": {
            "status": str(args.status),
            "submitted_utc": None,
            "job_id": None,
            "result_status": None,
        },
        "evidence": {
            "quantum_baseline": _relative_str(quantum_baseline, root),
            "depth_sweep": _relative_str(depth_sweep, root),
            "noise_sweep": _relative_str(noise_sweep, root) if noise_sweep else None,
            "summary": _relative_str(summary, root),
        },
    }

    out_path = Path(args.out).resolve() if args.out else estimates_dir / f"azure_job_manifest_{args.instance}_d{args.depth}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    try:
        rel = out_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel = out_path
    print(f"Wrote Azure job manifest: {rel}")


if __name__ == "__main__":
    main()
