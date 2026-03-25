#!/usr/bin/env python3
"""Run real resource estimation using the modern Q# Python package.

Estimates resource requirements for OpenQASM circuits using qsharp.estimate().
Produces standardized JSON output compatible with the existing estimation pipeline.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Circuits to estimate (QASM files that passed Quantinuum H2-1SC validation)
CIRCUITS = [
    {
        "problem_id": "01_hubbard",
        "name": "Hubbard VQE ZZ",
        "qasm_file": "problems/01_hubbard/estimates/hubbard_vqe_zz.qasm",
        "algorithm": "vqe",
    },
    {
        "problem_id": "05_qaoa_maxcut",
        "name": "QAOA MaxCut d1",
        "qasm_file": "problems/05_qaoa_maxcut/estimates/qaoa_small_d1.qasm",
        "algorithm": "qaoa",
    },
    {
        "problem_id": "10_post_quantum_cryptography",
        "name": "Grover Key Search",
        "qasm_file": "problems/10_post_quantum_cryptography/estimates/grover_keysearch_4q.qasm",
        "algorithm": "grover",
    },
    {
        "problem_id": "12_quantum_optimization",
        "name": "QAOA Scheduling",
        "qasm_file": "problems/12_quantum_optimization/estimates/qaoa_scheduling_4q.qasm",
        "algorithm": "qaoa",
    },
    {
        "problem_id": "15_database_search",
        "name": "Grover Database Search",
        "qasm_file": "problems/15_database_search/estimates/grover_4qubit.qasm",
        "algorithm": "grover",
    },
    {
        "problem_id": "16_error_correction",
        "name": "QEC Repetition Code",
        "qasm_file": "problems/16_error_correction/estimates/repetition_code_3q.qasm",
        "algorithm": "qec",
    },
]


def estimate_qasm(qasm_path: Path) -> dict:
    """Estimate resources for an OpenQASM circuit using the modern Q# package."""
    try:
        import qsharp
    except ImportError:
        print("ERROR: qsharp package not installed. Run: pip install qsharp", file=sys.stderr)
        sys.exit(1)

    qasm_text = qasm_path.read_text(encoding="utf-8")

    try:
        result = qsharp.estimate(qasm_text, params={"errorBudget": 0.001})
        return result
    except Exception as e:
        print(f"  Warning: qsharp.estimate() failed: {e}", file=sys.stderr)
        return None


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    results = []

    for circuit in CIRCUITS:
        qasm_path = REPO / circuit["qasm_file"]
        if not qasm_path.exists():
            print(f"  Skipping {circuit['name']}: {qasm_path} not found")
            continue

        print(f"Estimating {circuit['name']} ({circuit['problem_id']})...")
        est = estimate_qasm(qasm_path)

        if est is None:
            print(f"  Failed - using fallback gate count from QASM")
            # Fallback: count gates from QASM
            qasm_text = qasm_path.read_text(encoding="utf-8")
            lines = [l.strip() for l in qasm_text.splitlines() if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("OPENQASM") and not l.strip().startswith("include")]
            gate_lines = [l for l in lines if not l.startswith("qreg") and not l.startswith("creg") and not l.startswith("measure")]
            measure_lines = [l for l in lines if l.startswith("measure")]
            t_gates = sum(1 for l in gate_lines if l.startswith("t ") or l.startswith("tdg "))
            cx_gates = sum(1 for l in gate_lines if l.startswith("cx ") or l.startswith("ccx "))
            h_gates = sum(1 for l in gate_lines if l.startswith("h "))
            rz_gates = sum(1 for l in gate_lines if l.startswith("rz(") or l.startswith("ry(") or l.startswith("rx(") or l.startswith("r1("))

            est_data = {
                "problem_id": circuit["problem_id"],
                "algorithm": circuit["algorithm"],
                "source": "qasm_gate_count",
                "metrics": {
                    "total_gates": len(gate_lines),
                    "t_gates": t_gates,
                    "cx_gates": cx_gates,
                    "h_gates": h_gates,
                    "rotation_gates": rz_gates,
                    "measurements": len(measure_lines),
                    "qubits": None,  # parse from qreg
                },
                "timestamp": timestamp,
            }

            # Parse qubit count
            for l in lines:
                if l.startswith("qreg"):
                    import re
                    m = re.search(r"\[(\d+)\]", l)
                    if m:
                        q = int(m.group(1))
                        if est_data["metrics"]["qubits"] is None:
                            est_data["metrics"]["qubits"] = q
                        else:
                            est_data["metrics"]["qubits"] += q
        else:
            est_data = {
                "problem_id": circuit["problem_id"],
                "algorithm": circuit["algorithm"],
                "source": "qsharp_resource_estimator",
                "raw": est,
                "timestamp": timestamp,
            }

        results.append(est_data)

        # Save per-problem
        out_dir = REPO / "problems" / circuit["problem_id"] / "estimates"
        out_file = out_dir / f"real_resource_estimate_{timestamp}.json"
        out_file.write_text(json.dumps(est_data, indent=2, default=str), encoding="utf-8")
        print(f"  Saved to {out_file.relative_to(REPO)}")

    # Summary
    summary_path = REPO / "tooling" / "estimator" / "output" / f"real_estimates_{timestamp}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"\nSummary: {summary_path.relative_to(REPO)}")
    print(f"Estimated {len(results)} circuits")


if __name__ == "__main__":
    main()
