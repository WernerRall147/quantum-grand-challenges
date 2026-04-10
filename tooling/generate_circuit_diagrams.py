#!/usr/bin/env python3
"""Generate text-format circuit diagrams for all Q# problems using qsharp.circuit().

Saves circuit.txt to each problem's circuits/ directory.
"""

import sys
import time
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Map problem → (entry_expression_for_circuit)
# These should be lightweight operations suitable for circuit tracing
# Avoid heavy shot-based loops that cause timeouts
CIRCUIT_EXPRESSIONS = {
    "01_hubbard": "Main.HubbardVQEAnsatz(1.0, 0.5, 0.3, _, _)",
    "02_catalysis": "Main.ChemistryAnsatz(1.0, 0.5, 0.3, _, _)",
    "03_qae_risk": "Main.IQAERound(Main.LogNormalProbabilities(4, 0.0, 1.0), 2.5, 4, 1)",
    "04_linear_solvers": "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)",
    "05_qaoa_maxcut": "Main.ApplyCostLayer([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], 0.5, _)",
    "06_high_frequency_trading": "Main.PrepareMarketState(_)",
    "07_drug_discovery": "Main.BindingAnsatz(1.0, 0.5, 0.3, _, _)",
    "08_protein_folding": "Main.ApplyFoldingCostLayer([[0.0,1.0],[1.0,0.0]], 0.5, _)",
    "09_factorization": "Main.InverseQFT(_)",
    "10_post_quantum_cryptography": "Main.DiffusionOperator(_)",
    "11_quantum_machine_learning": "Main.PrepareFeatureState([1.0, 0.5, 0.3], _)",
    "12_quantum_optimization": "Main.ApplyCostLayer([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], 0.5, _)",
    "13_climate_modeling": "Main.TrotterStep(0.5, _)",
    "14_materials_discovery": "Main.BandGapAnsatz(1.0, 0.5, 0.3, _, _)",
    "15_database_search": "Main.DiffusionOperator(_)",
    "16_error_correction": "Main.Encode3BitRepetition(_, _, _)",
    "17_nuclear_physics": "Main.NuclearAnsatz(1.0, 0.5, 0.3, _, _)",
    "18_photovoltaics": "Main.QuantumWalkStep(_, _, 0.5)",
    "19_quantum_chromodynamics": "Main.TrotterGaugeStep(0.5, 0.5, _)",
    "20_space_mission_planning": "Main.ApplyCostLayer([[0.0,1.0],[1.0,0.0]], 0.5, _)",
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
        expr = CIRCUIT_EXPRESSIONS.get(name)
        if not expr:
            print(f"-- {name}: no circuit expression")
            continue

        try:
            qsharp.init(project_root=str(qsharp_dir))
        except Exception as e:
            print(f"XX {name}: compile error — {str(e)[:100]}")
            fail += 1
            continue

        try:
            circuit = qsharp.circuit(expr)
            circuit_text = str(circuit)
            if not circuit_text.strip():
                # Try operation= form for qubit-parameterized ops
                op_name = expr.split("(")[0].replace("Main.", "")
                try:
                    circuit = qsharp.circuit(operation=op_name)
                    circuit_text = str(circuit)
                except Exception:
                    pass
            if not circuit_text.strip():
                # Fallback: use the entry point
                try:
                    circuit = qsharp.circuit()
                    circuit_text = str(circuit)
                except Exception:
                    pass
            out_path = circuits_dir / "circuit.txt"
            out_path.write_text(circuit_text, encoding="utf-8")
            lines = len(circuit_text.strip().splitlines()) if circuit_text.strip() else 0
            print(f"OK {name}: {lines} lines saved to circuits/circuit.txt")
            ok += 1
        except Exception as e:
            # If the specific expression fails, try just the entry point
            err_msg = str(e)[:150]
            try:
                circuit = qsharp.circuit()
                circuit_text = str(circuit)
                out_path = circuits_dir / "circuit.txt"
                out_path.write_text(circuit_text, encoding="utf-8")
                lines = len(circuit_text.splitlines())
                print(f"OK {name}: {lines} lines (from entry point)")
                ok += 1
            except Exception as e2:
                print(f"XX {name}: {err_msg}")
                fail += 1

    print(f"\nDone: {ok} circuits generated, {fail} failed")


if __name__ == "__main__":
    sys.exit(main() or 0)
