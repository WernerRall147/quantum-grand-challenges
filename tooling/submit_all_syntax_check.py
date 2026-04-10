#!/usr/bin/env python3
"""Submit all 20 Q# problems to the Quantinuum H2-1SC syntax checker.

Each problem is compiled to QIR (Adaptive_RI profile) and submitted.
The syntax checker validates compilation but returns all-zeros (free tier).
Results are saved to each problem's estimates/ directory.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Subscription config
SUBSCRIPTION_ID = "82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3"
RESOURCE_GROUP = "Quantum-Grand-Challenges"
WORKSPACE_NAME = "Quantum-Grand-Challenges"
LOCATION = "eastus"
TARGET = "quantinuum.sim.h2-1sc"
SHOTS = 10  # Syntax checker: minimal shots (returns all-zeros anyway)


KERNEL_ENTRY = {
    "01_hubbard": "HubbardVQEKernel",
    "02_catalysis": "ChemistryVQEKernel",
    "03_qae_risk": "IQAEKernelK0",
    "04_linear_solvers": None,  # Uses full entry point (compiles OK)
    "05_qaoa_maxcut": "QaoaMaxCutKernel",
    "06_high_frequency_trading": "HFTKernel",
    "07_drug_discovery": "DrugBindingKernel",
    "08_protein_folding": "FoldingQaoaKernel",
    "09_factorization": "ShorKernel",
    "10_post_quantum_cryptography": "GroverKeyKernel",
    "11_quantum_machine_learning": "SwapTestKernel",
    "12_quantum_optimization": "SchedulingQaoaKernel",
    "13_climate_modeling": "ClimateHHLKernel",
    "14_materials_discovery": "MaterialsVQEKernel",
    "15_database_search": "GroverSearchKernel",
    "16_error_correction": "QECKernel",
    "17_nuclear_physics": "NuclearVQEKernel",
    "18_photovoltaics": "QuantumWalkKernel",
    "19_quantum_chromodynamics": "LatticeGaugeKernel",
    "20_space_mission_planning": "MissionQaoaKernel",
}


def main():
    from qdk import qsharp
    from qdk.azure import Workspace

    dry_run = "--dry-run" in sys.argv

    problem_dirs = sorted(
        [d for d in PROBLEMS_DIR.iterdir() if d.is_dir() and d.name[:2].isdigit()],
        key=lambda d: d.name,
    )

    print(f"Connecting to Azure Quantum workspace '{WORKSPACE_NAME}' ...")
    ws = Workspace(
        subscription_id=SUBSCRIPTION_ID,
        resource_group=RESOURCE_GROUP,
        name=WORKSPACE_NAME,
        location=LOCATION,
    )
    target = ws.get_targets(TARGET)
    print(f"Target: {TARGET}\n")

    results = []

    for pd in problem_dirs:
        qsharp_dir = pd / "qsharp"
        name = pd.name

        if not (qsharp_dir / "qsharp.json").exists():
            continue

        # Compile to QIR from HardwareKernel.qs
        kernel_name = KERNEL_ENTRY.get(name)

        try:
            if kernel_name:
                # Use standalone kernel file
                kernel_file = qsharp_dir / "HardwareKernel.qs"
                if not kernel_file.exists():
                    print(f"-- {name}: no HardwareKernel.qs, skipping")
                    continue
                qsharp.init(target_profile=qsharp.TargetProfile.Adaptive_RI)
                qsharp.eval(kernel_file.read_text(encoding="utf-8"))
                qir = qsharp.compile(f"{kernel_name}()")
            else:
                # Use project entry point (e.g. 04_linear_solvers)
                entry = ENTRY_POINTS.get(name, "")
                if not entry:
                    print(f"-- {name}: no entry point, skipping")
                    continue
                qsharp.init(
                    project_root=str(qsharp_dir),
                    target_profile=qsharp.TargetProfile.Adaptive_RI,
                )
                qir = qsharp.compile(entry)
            print(f"OK {name}: QIR compiled")
        except Exception as e:
            err = str(e)[:120]
            print(f"XX {name}: compile failed — {err}")
            results.append({"problem": name, "status": "compile_error", "error": err})
            continue

        if dry_run:
            results.append({"problem": name, "status": "dry_run"})
            continue

        # Submit to syntax checker
        try:
            job_name = f"{name}-qdk-sc-{datetime.now(timezone.utc):%Y%m%d}"
            job = target.submit(qir, job_name, shots=SHOTS)
            print(f"   Submitted: {job.id} ({job_name})")

            job.wait_until_completed()
            status = str(job.details.status)
            job_results = job.get_results()

            result = {
                "problem": name,
                "job_id": job.id,
                "job_name": job_name,
                "status": status,
                "target": TARGET,
                "shots": SHOTS,
                "results": job_results,
                "generated_utc": datetime.now(timezone.utc).isoformat(),
            }
            results.append(result)

            # Save to problem's estimates dir
            est_dir = pd / "estimates"
            est_dir.mkdir(exist_ok=True)
            out_file = est_dir / f"azure_syntax_check_{datetime.now(timezone.utc):%Y%m%d}.json"
            out_file.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

            status_icon = "OK" if "Succeeded" in status else "!!"
            print(f"   {status_icon} Status: {status}")

        except Exception as e:
            err = str(e)[:120]
            print(f"   !! Submit failed: {err}")
            results.append({"problem": name, "status": "submit_error", "error": err})

    # Summary
    succeeded = sum(1 for r in results if "Succeeded" in r.get("status", ""))
    failed = sum(1 for r in results if "error" in r.get("status", "").lower())
    print(f"\nDone: {succeeded} succeeded, {failed} failed, {len(results)} total")


if __name__ == "__main__":
    sys.exit(main() or 0)
