#!/usr/bin/env python3
"""Generate circuit diagrams and resource estimates for all Q# problems.

Saves to each problem's circuits/ directory:
  - circuit.txt    (text-format circuit diagram)
  - estimate.json  (resource estimation results)
"""

import json
import sys
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

from discover_problems import discover_all_problems
from estimator_config import ENTRY_POINTS

# Curated subset of problems with circuit-friendly expressions
# (drawable without ballooning shot/iteration counts).
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
    ep = ENTRY_POINTS.get(name)
    if ep is not None:
        try:
            entry = ep.expr()
            estimate = qsharp.estimate(entry)
            data = estimate.data() if hasattr(estimate, "data") else estimate
            summary = {
                "problem": name,
                "entry_point": entry,
                "physical_counts": data.get("physicalCounts", {}) if isinstance(data, dict) else {},
                "logical_counts": data.get("logicalCounts", {}) if isinstance(data, dict) else {},
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
