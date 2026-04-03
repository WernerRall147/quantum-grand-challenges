#!/usr/bin/env python3
"""Run each Q# entry point to verify execution, generate circuits, then resource estimates."""

import json
import sys
import time
import traceback
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"


def get_entry_point(problem_name: str) -> str:
    """Map problem names to their entry point expressions."""
    mapping = {
        "01_hubbard": "Main.RunTwoSiteHubbardAnalysis()",
        "02_catalysis": "Main.RunCatalysisAnalysis()",
        "03_qae_risk": "Main.RunQAERiskAnalysis()",
        "04_linear_solvers": "Main.RunLinearSolverBaseline()",
        "05_qaoa_maxcut": "Main.RunQaoaAnalysis([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]], 1, 50, 100)",
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
    return mapping.get(problem_name, "")


def main():
    import qsharp

    problem_dirs = sorted(
        [d for d in PROBLEMS_DIR.iterdir() if d.is_dir() and d.name[:2].isdigit()],
        key=lambda d: d.name,
    )

    print(f"Running {len(problem_dirs)} problem entry points...\n")
    results = []

    for pd in problem_dirs:
        qsharp_dir = pd / "qsharp"
        if not (qsharp_dir / "qsharp.json").exists():
            continue

        entry = get_entry_point(pd.name)
        if not entry:
            print(f"⏭️  {pd.name}: no entry point mapped")
            continue

        r = {"problem": pd.name, "compile": False, "run": False, "error": None, "time": 0}

        try:
            qsharp.init(project_root=str(qsharp_dir))
            r["compile"] = True
        except Exception as e:
            r["error"] = f"Compile: {str(e)[:200]}"
            results.append(r)
            print(f"❌ {pd.name}: compile FAIL — {r['error']}")
            continue

        try:
            start = time.time()
            qsharp.run(entry, 1)
            r["time"] = round(time.time() - start, 2)
            r["run"] = True
            print(f"✅ {pd.name}: ran in {r['time']}s")
        except Exception as e:
            r["error"] = f"Run: {str(e)[:200]}"
            print(f"❌ {pd.name}: run FAIL — {r['error']}")

        results.append(r)

    ok = sum(1 for r in results if r["run"])
    fail = sum(1 for r in results if not r["run"])
    print(f"\nResults: {ok} ran OK, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
