#!/usr/bin/env python3
"""Generate circuit diagrams and resource estimates for all Q# problems.

Saves to each problem's circuits/ directory:
  - circuit.txt    (text-format circuit diagram)
  - estimate.json  (resource estimation results)
"""

import json
import sys
import time
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Import shared discovery helper
from discover_problems import discover_all_problems — must match actual Q# operation signatures
ENTRY_POINTS = {
    "01_hubbard": "Main.EstimateHubbardEnergy(0.5, 2.0, 1.0, 0.5, 0.3, 100)",
    "02_catalysis": "Main.EstimateMolecularEnergy(1.0, 0.5, 0.3, 100)",
    "03_qae_risk": "Main.QAEKernel()",
    "04_linear_solvers": "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)",
    "05_qaoa_maxcut": "Main.EvaluateQaoa([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]], [0.5], [0.5], 50)",
    "06_high_frequency_trading": "Main.EstimateLossProbability([0.05, -0.03, 0.02], 1, 20)",
    "07_drug_discovery": "Main.EstimateBindingEnergy(1.0, 0.5, 0.3, 50)",
    "08_protein_folding": "Main.EvaluateFoldingQaoa([[0.0,1.0],[1.0,0.0]], 0.5, 0.5, 50)",
    "09_factorization": "Main.ShorPeriodFinding(3, 4)",
    "10_post_quantum_cryptography": "Main.GroverKeySearch(3, 5, 20)",
    "11_quantum_machine_learning": "Main.SwapTest([1.0, 0.5, 0.3, 0.2], [0.8, 0.2, 0.6, 0.1], 50)",
    "12_quantum_optimization": "Main.EvaluateQaoa([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], 0.5, 0.5, 1, 50)",
    "13_climate_modeling": "Main.RunHHLClimate(3, 50)",
    "14_materials_discovery": "Main.EstimateBandGap(1.0, -0.5, 0.8, 0.3, 50)",
    "15_database_search": "Main.GroverSearch([7], 4, 3)",
    "16_error_correction": "Main.RunRepetitionCodeCycle(false, 0)",
    "17_nuclear_physics": "Main.EstimateNuclearEnergy(1.0, 0.5, 0.3, 50)",
    "18_photovoltaics": "Main.RunExcitonWalk(10, 0.5, 50)",
    "19_quantum_chromodynamics": "Main.SimulateLatticeGauge(2, 1.0, 0.5, 3, 50)",
    "20_space_mission_planning": "Main.EvaluateQaoaMission([[0.0,1.0,0.5],[1.0,0.0,0.8],[0.5,0.8,0.0]], 0.5, 0.5, 1, 20)",
}

# Simpler circuit-friendly expressions (avoid operations that need too many shots)
CIRCUIT_ENTRY_POINTS = {
    "01_hubbard": "Main.EstimateHubbardEnergy(0.5, 2.0, 1.0, 0.5, 0.3, 1)",
    "02_catalysis": "Main.EstimateMolecularEnergy(1.0, 0.5, 0.3, 1)",
    "03_qae_risk": "Main.QAEKernel()",
    "04_linear_solvers": "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)",
    "15_database_search": "Main.GroverSearch([7], 4, 3)",
}


def generate_for_problem(problem_dir: Path) -> dict:
    """Generate circuit and resource estimate for one problem."""
    import qsharp

    qsharp_dir = problem_dir / "qsharp"
    circuits_dir = problem_dir / "circuits"
    circuits_dir.mkdir(exist_ok=True)

    result = {"problem": problem_dir.name, "circuit": False, "estimate": False, "errors": []}
    name = problem_dir.name

    if not (qsharp_dir / "qsharp.json").exists():
        result["errors"].append("No qsharp.json")
        return result

    try:
        qsharp.init(project_root=str(qsharp_dir))
    except Exception as e:
        result["errors"].append(f"Compile: {str(e)[:200]}")
        return result

    # --- Generate circuit diagram ---
    circuit_expr = CIRCUIT_ENTRY_POINTS.get(name)
    if circuit_expr:
        try:
            circuit = qsharp.circuit(circuit_expr)
            circuit_text = str(circuit)
            (circuits_dir / "circuit.txt").write_text(circuit_text, encoding="utf-8")
            result["circuit"] = True
        except Exception as e:
            result["errors"].append(f"Circuit: {str(e)[:200]}")
    else:
        result["errors"].append("No circuit expression mapped")

    # --- Generate resource estimate ---
    # Resource estimation needs the entry point expression
    entry = ENTRY_POINTS.get(name)
    if entry:
        try:
            estimate = qsharp.estimate(entry)
            # Save key metrics
            summary = {
                "problem": name,
                "entry_point": entry,
                "physical_counts": estimate.get("physicalCounts", {}),
                "logical_counts": estimate.get("logicalCounts", {}),
            }
            (circuits_dir / "estimate.json").write_text(
                json.dumps(summary, indent=2, default=str), encoding="utf-8"
            )
            result["estimate"] = True
        except Exception as e:
            result["errors"].append(f"Estimate: {str(e)[:150]}")

    return result


def main():
    import qsharp

    problem_dirs = discover_all_problems()

    print(f"Generating circuits and estimates for {len(problem_dirs)} problems...\n")
    results = []

    for pd in problem_dirs:
        r = generate_for_problem(pd)
        results.append(r)
        c_icon = "C" if r["circuit"] else "-"
        e_icon = "E" if r["estimate"] else "-"
        errs = "; ".join(r["errors"]) if r["errors"] else ""
        print(f"[{c_icon}{e_icon}] {r['problem']}{' — ' + errs if errs else ''}")

    circuits_ok = sum(1 for r in results if r["circuit"])
    estimates_ok = sum(1 for r in results if r["estimate"])
    print(f"\nSummary: {circuits_ok} circuits, {estimates_ok} estimates generated")


if __name__ == "__main__":
    sys.exit(main() or 0)
