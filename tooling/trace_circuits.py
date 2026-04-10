#!/usr/bin/env python3
"""Generate traced circuit diagrams using qsharp dump_circuit().

Uses trace_circuit=True to record gates as they execute on the simulator,
then dump_circuit() to get the actual gate-level ASCII diagram.
This produces real circuits, not abstract operation descriptions.
"""

import sys
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Q# expressions that create the quantum circuit to trace.
# Each should allocate qubits, run the core operation, and reset.
TRACE_EXPRESSIONS = {
    "01_hubbard":
        "use qs = Qubit[2]; Main.HubbardVQEAnsatz(1.0, 0.5, 0.3, qs[0], qs[1]); ResetAll(qs)",
    "02_catalysis":
        "use qs = Qubit[2]; Main.ChemistryAnsatz(1.0, 0.5, 0.3, qs[0], qs[1]); ResetAll(qs)",
    "04_linear_solvers":
        "{ let _ = Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3); }",
    "05_qaoa_maxcut":
        "use qs = Qubit[3]; ApplyToEach(H, qs); Main.ApplyCostLayer([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], 0.5, qs); Main.ApplyMixerLayer(0.5, qs); ResetAll(qs)",
    "06_high_frequency_trading":
        "use qs = Qubit[2]; use m = Qubit(); Main.PrepareMarketState([0.3, 0.7], qs); Main.MarkLossStates(1, qs, m); Reset(m); ResetAll(qs)",
    "07_drug_discovery":
        "use qs = Qubit[2]; Main.BindingAnsatz(1.0, 0.5, 0.3, qs[0], qs[1]); ResetAll(qs)",
    "08_protein_folding":
        "use qs = Qubit[3]; ApplyToEach(H, qs); Main.ApplyFoldingCostLayer([[0.0,1.0,0.5],[1.0,0.0,0.8],[0.5,0.8,0.0]], 0.5, qs); Main.ApplyFoldingMixer(0.5, qs); ResetAll(qs)",
    "09_factorization":
        "Main.RunShorFactorization()",
    "10_post_quantum_cryptography":
        "use qs = Qubit[3]; ApplyToEach(H, qs); Main.MarkTargetKey(5, qs); Main.DiffusionOperator(qs); ResetAll(qs)",
    "11_quantum_machine_learning":
        "use ra = Qubit[2]; Main.PrepareFeatureState([1.0, 0.5, 0.3, 0.8], ra); ResetAll(ra)",
    "12_quantum_optimization":
        "use qs = Qubit[3]; ApplyToEach(H, qs); Main.ApplyCostLayer([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], 0.5, qs); Main.ApplyMixerLayer(0.5, qs); ResetAll(qs)",
    "13_climate_modeling":
        "{ let _ = Main.RunHHLClimate(3, 50); }",
    "14_materials_discovery":
        "use qs = Qubit[2]; Main.BandGapAnsatz(1.0, 0.5, 0.3, qs[0], qs[1]); ResetAll(qs)",
    "15_database_search":
        "{ let _ = Main.GroverSearch([7], 4, 3); }",
    "16_error_correction":
        "use (d, a1, a2) = (Qubit(), Qubit(), Qubit()); H(d); Main.Encode3BitRepetition(d, a1, a2); ResetAll([d, a1, a2])",
    "17_nuclear_physics":
        "use qs = Qubit[2]; Main.NuclearAnsatz(1.0, 0.5, 0.3, qs[0], qs[1]); ResetAll(qs)",
    "18_photovoltaics":
        "use c = Qubit(); use p = Qubit[2]; Main.QuantumWalkStep(c, p, 0.5); Reset(c); ResetAll(p)",
    "19_quantum_chromodynamics":
        "use qs = Qubit[4]; Main.TrotterGaugeStep(0.5, 0.3, qs); ResetAll(qs)",
    "20_space_mission_planning":
        "use qs = Qubit[3]; ApplyToEach(H, qs); Main.ApplyCostLayer([[0.0,1.0,0.5],[1.0,0.0,0.8],[0.5,0.8,0.0]], 0.5, qs); Main.ApplyMixerLayer(0.5, qs); ResetAll(qs)",
}


def main():
    import qsharp

    ok = 0
    fail = 0

    for name, expr in sorted(TRACE_EXPRESSIONS.items()):
        qsharp_dir = PROBLEMS_DIR / name / "qsharp"
        circuits_dir = PROBLEMS_DIR / name / "circuits"
        circuits_dir.mkdir(exist_ok=True)

        try:
            qsharp.init(project_root=str(qsharp_dir), trace_circuit=True)
            qsharp.eval(expr)
            circuit = qsharp.dump_circuit()
            circuit_text = str(circuit).strip()

            if circuit_text:
                # Read existing hand-drawn header if present
                existing = (circuits_dir / "circuit.txt").read_text(encoding="utf-8")
                # Extract just the header (up to first blank line after ===)
                header_lines = []
                for line in existing.splitlines():
                    header_lines.append(line)
                    if line.startswith("===") and len(header_lines) > 1:
                        break

                header = "\n".join(header_lines)
                full = f"{header}\n\nTraced gate-level circuit (from QDK simulator):\n\n{circuit_text}\n"
                (circuits_dir / "circuit.txt").write_text(full, encoding="utf-8")

                gate_lines = len(circuit_text.splitlines())
                print(f"OK {name}: {gate_lines} gate lines")
                ok += 1
            else:
                print(f"-- {name}: empty circuit (no gates traced)")
                fail += 1
        except Exception as e:
            err = str(e)[:150]
            print(f"XX {name}: {err}")
            fail += 1

    print(f"\nDone: {ok} traced, {fail} failed")


if __name__ == "__main__":
    sys.exit(main() or 0)
