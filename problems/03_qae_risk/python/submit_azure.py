#!/usr/bin/env python3
"""Submit a QAE single-shot kernel to Azure Quantum.

Compiles just the hardware-friendly QAEKernel to QIR and submits to
the configured Azure Quantum target (default: quantinuum.sim.h2-1sc).
Multi-shot statistics are handled by the target hardware/simulator.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

try:
    from qdk import qsharp
    from qdk.azure import Workspace
except ImportError:
    print(
        "Error: 'qdk[azure]' is not installed.\n"
        "Install with:  pip install 'qdk[azure]'",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------- Configuration ----------
PROBLEM_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = PROBLEM_DIR / ".env.azure.local"
KERNEL_FILE = PROBLEM_DIR / "qsharp" / "HardwareKernel.qs"
ESTIMATES_DIR = PROBLEM_DIR / "estimates"
ESTIMATES_DIR.mkdir(exist_ok=True)


def load_env(path: Path) -> dict[str, str]:
    """Load KEY=VALUE pairs from a .env file."""
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Submit QAE kernel to Azure Quantum")
    parser.add_argument("--target", default="quantinuum.sim.h2-1sc",
                        help="Azure Quantum target ID (default: quantinuum.sim.h2-1sc)")
    parser.add_argument("--shots", type=int, default=100,
                        help="Number of shots (default: 100)")
    parser.add_argument("--job-name", default=None,
                        help="Job name (auto-generated if not provided)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compile to QIR but don't submit")
    args = parser.parse_args()

    # Load Azure config
    env = load_env(ENV_FILE)
    subscription_id = env.get("AZURE_SUBSCRIPTION_ID", "")
    resource_group = env.get("AZURE_RESOURCE_GROUP", "")
    workspace_name = env.get("AZURE_QUANTUM_WORKSPACE", "")
    location = env.get("AZURE_LOCATION", "eastus")

    if not all([subscription_id, resource_group, workspace_name]):
        print(f"Error: Azure configuration incomplete in {ENV_FILE}", file=sys.stderr)
        print("Required: AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, AZURE_QUANTUM_WORKSPACE", file=sys.stderr)
        return 1

    # ---- Compile QAEKernel to QIR ----
    print(f"Loading hardware kernel from {KERNEL_FILE} ...")
    # Use Adaptive_RI — needed for mid-circuit Reset before final measurement.
    # The Quantinuum simulator supports this profile.
    qsharp.init(target_profile=qsharp.TargetProfile.Adaptive_RI)

    # Load standalone kernel file (no project-wide profile issues)
    source = KERNEL_FILE.read_text(encoding="utf-8")
    qsharp.eval(source)

    print("Compiling QAEKernel to QIR (Adaptive_RI profile) ...")
    qir = qsharp.compile("QAEKernel()")
    print("QIR compilation succeeded.")

    if args.dry_run:
        print("[Dry run] Skipping Azure submission.")
        return 0

    # ---- Submit to Azure Quantum ----
    print(f"Connecting to Azure Quantum workspace '{workspace_name}' ...")
    workspace = Workspace(
        subscription_id=subscription_id,
        resource_group=resource_group,
        name=workspace_name,
        location=location,
    )

    target = workspace.get_targets(args.target)
    job_name = args.job_name or f"03_qae-risk-qdk-{datetime.now():%Y%m%d-%H%M%S}"
    print(f"Submitting job '{job_name}' to {args.target} ({args.shots} shots) ...")

    job = target.submit(qir, job_name, shots=args.shots)
    print(f"Job submitted: {job.id}")
    print(f"Monitor with: az quantum job show --job-id \"{job.id}\" --workspace-name \"{workspace_name}\" --resource-group \"{resource_group}\" -o table")
    print()
    print("Waiting for completion ...")

    job.wait_until_completed()
    status = job.details.status
    print(f"Job status: {status}")

    if status != "Succeeded":
        print(f"Job did not succeed. Status: {status}", file=sys.stderr)
        return 1

    # ---- Retrieve and process results ----
    results = job.get_results()
    print(f"\nRaw results: {json.dumps(results, indent=2)[:2000]}")

    # Save results
    result_file = ESTIMATES_DIR / f"azure_qae_{datetime.now():%Y%m%d_%H%M%S}.json"
    result_payload = {
        "job_id": job.id,
        "job_name": job_name,
        "target": args.target,
        "shots": args.shots,
        "status": status,
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }
    result_file.write_text(json.dumps(result_payload, indent=2), encoding="utf-8")
    print(f"\nResults saved to {result_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
