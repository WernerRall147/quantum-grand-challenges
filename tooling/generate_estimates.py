#!/usr/bin/env python3
"""Generate resource estimation JSON for all Q# problems using qsharp.estimate().

Saves estimate.json to each problem's circuits/ directory.
"""

import json
import sys
import time
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Import shared discovery helper
from discover_problems import discover_all_problems

# Single-shot kernel operations per problem
ENTRY_POINTS = {
    "01_hubbard": "Main.EstimateHubbardEnergy(0.5, 2.0, 1.0, 0.5, 0.3, 1)",
    "02_catalysis": "Main.EstimateMolecularEnergy(1.0, 0.5, 0.3, 1)",
    "03_qae_risk": "Main.QAEKernel()",
    "04_linear_solvers": "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)",
    "05_qaoa_maxcut": "Main.EvaluateQaoa([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]], [0.5], [0.5], 1)",
    "06_high_frequency_trading": "Main.EstimateLossProbability([0.05, -0.03, 0.02], 1, 1)",
    "07_drug_discovery": "Main.EstimateBindingEnergy(1.0, 0.5, 0.3, 1)",
    "08_protein_folding": "Main.EvaluateFoldingQaoa([[0.0,1.0],[1.0,0.0]], 0.5, 0.5, 1)",
    "09_factorization": "Main.ShorPeriodFinding(3, 4)",
    "10_post_quantum_cryptography": "Main.GroverKeySearch(3, 5, 1)",
    "11_quantum_machine_learning": "Main.SwapTest([1.0, 0.5, 0.3, 0.2], [0.8, 0.2, 0.6, 0.1], 1)",
    "12_quantum_optimization": "Main.EvaluateQaoa([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], 0.5, 0.5, 1, 1)",
    "13_climate_modeling": "Main.RunHHLClimate(3, 1)",
    "14_materials_discovery": "Main.EstimateBandGap(1.0, -0.5, 0.8, 0.3, 1)",
    "15_database_search": "Main.GroverSearch([7], 4, 3)",
    "16_error_correction": "Main.RunRepetitionCodeCycle(false, 0)",
    "17_nuclear_physics": "Main.EstimateNuclearEnergy(1.0, 0.5, 0.3, 1)",
    "18_photovoltaics": "Main.RunExcitonWalk(10, 0.5, 1)",
    "19_quantum_chromodynamics": "Main.SimulateLatticeGauge(2, 1.0, 0.5, 3, 1)",
    "20_space_mission_planning": "Main.EvaluateQaoaMission([[0.0,1.0,0.5],[1.0,0.0,0.8],[0.5,0.8,0.0]], 0.5, 0.5, 1, 1)",
}


def main():
    import qsharp

    problem_dirs = discover_all_problems()

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
