#!/usr/bin/env python3
"""Generate resource estimation JSON for all Q# problems using qsharp.estimate().

Saves estimate.json to each problem's circuits/ directory.
"""

import json
import sys
import time
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Entry points for resource estimation
ENTRY_POINTS = {
    "01_hubbard": "Main.RunTwoSiteHubbardAnalysis()",
    "02_catalysis": "Main.RunCatalysisAnalysis()",
    "03_qae_risk": "Main.RunQAERiskAnalysis()",
    "04_linear_solvers": "Main.RunLinearSolverBaseline()",
    "05_qaoa_maxcut": "Main.RunDefaultQaoa()",
    "06_high_frequency_trading": "Main.RunHFTAnalysis()",
    "07_drug_discovery": "Main.RunDrugDiscovery()",
    "08_protein_folding": "Main.RunProteinFolding()",
    "09_factorization": "Main.RunShorFactorization()",
    "10_post_quantum_cryptography": "Main.RunPostQuantumAnalysis()",
    "11_quantum_machine_learning": "Main.RunQuantumKernelEstimation()",
    "12_quantum_optimization": "Main.RunSchedulingOptimization()",
    "13_climate_modeling": "Main.RunClimateModeling()",
    "14_materials_discovery": "Main.RunMaterialsDiscovery()",
    "15_database_search": "Main.RunGroverDemonstration()",
    "16_error_correction": "Main.RunQECDemonstration()",
    "17_nuclear_physics": "Main.RunNuclearPhysics()",
    "18_photovoltaics": "Main.RunPhotovoltaics()",
    "19_quantum_chromodynamics": "Main.RunQCDSimulation()",
    "20_space_mission_planning": "Main.RunMissionOptimization()",
}


def main():
    import qsharp

    problem_dirs = sorted(
        [d for d in PROBLEMS_DIR.iterdir() if d.is_dir() and d.name[:2].isdigit()],
        key=lambda d: d.name,
    )

    ok = 0
    fail = 0

    for pd in problem_dirs:
        qsharp_dir = pd / "qsharp"
        circuits_dir = pd / "circuits"
        circuits_dir.mkdir(exist_ok=True)

        if not (qsharp_dir / "qsharp.json").exists():
            continue

        name = pd.name

        try:
            qsharp.init(project_root=str(qsharp_dir))
        except Exception as e:
            print(f"XX {name}: compile error — {str(e)[:100]}")
            fail += 1
            continue

        try:
            entry = ENTRY_POINTS.get(name, "")
            if not entry:
                print(f"-- {name}: no entry point mapped")
                continue
            estimate = qsharp.estimate(entry)
            # Extract key metrics
            pc = estimate.get("physicalCounts", {})
            lc = estimate.get("logicalCounts", {})
            bd = pc.get("breakdown", {})

            summary = {
                "problem": name,
                "physicalQubits": pc.get("physicalQubits"),
                "runtime": pc.get("runtime"),
                "rqops": pc.get("rqops"),
                "logicalQubits": bd.get("algorithmicLogicalQubits"),
                "logicalDepth": lc.get("logicalDepth"),
                "tCount": lc.get("tCount"),
                "rotationCount": lc.get("rotationCount"),
                "cczCount": lc.get("cczCount"),
                "measurementCount": lc.get("measurementCount"),
                "numQubits": lc.get("numQubits"),
            }

            out_path = circuits_dir / "estimate.json"
            out_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

            pq = summary.get("physicalQubits", "?")
            lq = summary.get("logicalQubits", "?")
            tc = summary.get("tCount", "?")
            print(f"OK {name}: {pq} physical qubits, {lq} logical qubits, {tc} T-gates")
            ok += 1

        except Exception as e:
            err = str(e)[:150]
            print(f"XX {name}: {err}")
            fail += 1

    print(f"\nDone: {ok} estimates generated, {fail} failed")


if __name__ == "__main__":
    sys.exit(main() or 0)
