#!/usr/bin/env python3
"""Grover scaling analysis: measure gate counts and success rates at increasing problem sizes.

Produces data for the methodology paper Section 7.3.
"""

import json
import math
import subprocess
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[2]


def count_qasm_gates(qasm_text: str) -> dict:
    """Count gates in an OpenQASM circuit."""
    lines = [l.strip() for l in qasm_text.splitlines()
             if l.strip() and not l.strip().startswith("//")
             and not l.strip().startswith("OPENQASM")
             and not l.strip().startswith("include")]
    
    gate_lines = [l for l in lines if not l.startswith("qreg") and not l.startswith("creg") and not l.startswith("measure")]
    measure_lines = [l for l in lines if l.startswith("measure")]
    
    t_gates = sum(1 for l in gate_lines if l.startswith("t ") or l.startswith("tdg "))
    cx_gates = sum(1 for l in gate_lines if l.startswith("cx ") or l.startswith("ccx ") or l.startswith("cswap "))
    h_gates = sum(1 for l in gate_lines if l.startswith("h "))
    x_gates = sum(1 for l in gate_lines if l.startswith("x "))
    rot_gates = sum(1 for l in gate_lines if any(l.startswith(p) for p in ["rz(", "ry(", "rx(", "r1(", "cp(", "crz(", "cry("]))
    
    return {
        "total_gates": len(gate_lines),
        "cx_gates": cx_gates,
        "t_gates": t_gates,
        "h_gates": h_gates,
        "x_gates": x_gates,
        "rotation_gates": rot_gates,
        "measurements": len(measure_lines),
    }


def generate_grover_qasm(n_qubits: int, target: int, iterations: int) -> str:
    """Generate a Grover search QASM circuit for n qubits."""
    lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{n_qubits}];",
        f"creg c[{n_qubits}];",
        "",
        "// Uniform superposition",
    ]
    for i in range(n_qubits):
        lines.append(f"h q[{i}];")
    
    for it in range(iterations):
        lines.append(f"\n// === Grover iteration {it+1} ===")
        
        # Oracle: mark target state
        lines.append("// Oracle")
        for i in range(n_qubits):
            bit = (target >> (n_qubits - 1 - i)) & 1
            if bit == 0:
                lines.append(f"x q[{i}];")
        
        # Multi-controlled Z via decomposition
        if n_qubits == 2:
            lines.append(f"cz q[0], q[1];")
        elif n_qubits == 3:
            lines.append(f"h q[{n_qubits-1}];")
            lines.append(f"ccx q[0], q[1], q[{n_qubits-1}];")
            lines.append(f"h q[{n_qubits-1}];")
        else:
            # Decompose MCZ using ladder of Toffolis for n>3
            lines.append(f"h q[{n_qubits-1}];")
            # Use T-gate decomposition for larger MCZ
            for i in range(n_qubits - 2):
                lines.append(f"cx q[{i}], q[{n_qubits-1}];")
                lines.append(f"tdg q[{n_qubits-1}];")
                if i + 1 < n_qubits - 1:
                    lines.append(f"cx q[{i+1}], q[{n_qubits-1}];")
                    lines.append(f"t q[{n_qubits-1}];")
            for i in range(n_qubits - 3, -1, -1):
                lines.append(f"cx q[{i}], q[{n_qubits-1}];")
                lines.append(f"tdg q[{n_qubits-1}];")
                if i > 0:
                    lines.append(f"cx q[{i-1}], q[{n_qubits-1}];")
                    lines.append(f"t q[{n_qubits-1}];")
            lines.append(f"t q[{n_qubits-1}];")
            lines.append(f"h q[{n_qubits-1}];")
        
        # Undo X flips
        for i in range(n_qubits):
            bit = (target >> (n_qubits - 1 - i)) & 1
            if bit == 0:
                lines.append(f"x q[{i}];")
        
        # Diffusion operator
        lines.append("// Diffusion")
        for i in range(n_qubits):
            lines.append(f"h q[{i}];")
        for i in range(n_qubits):
            lines.append(f"x q[{i}];")
        
        if n_qubits == 2:
            lines.append(f"cz q[0], q[1];")
        elif n_qubits == 3:
            lines.append(f"h q[{n_qubits-1}];")
            lines.append(f"ccx q[0], q[1], q[{n_qubits-1}];")
            lines.append(f"h q[{n_qubits-1}];")
        else:
            lines.append(f"h q[{n_qubits-1}];")
            for i in range(n_qubits - 2):
                lines.append(f"cx q[{i}], q[{n_qubits-1}];")
                lines.append(f"tdg q[{n_qubits-1}];")
                if i + 1 < n_qubits - 1:
                    lines.append(f"cx q[{i+1}], q[{n_qubits-1}];")
                    lines.append(f"t q[{n_qubits-1}];")
            for i in range(n_qubits - 3, -1, -1):
                lines.append(f"cx q[{i}], q[{n_qubits-1}];")
                lines.append(f"tdg q[{n_qubits-1}];")
                if i > 0:
                    lines.append(f"cx q[{i-1}], q[{n_qubits-1}];")
                    lines.append(f"t q[{n_qubits-1}];")
            lines.append(f"t q[{n_qubits-1}];")
            lines.append(f"h q[{n_qubits-1}];")
        
        for i in range(n_qubits):
            lines.append(f"x q[{i}];")
        for i in range(n_qubits):
            lines.append(f"h q[{i}];")
    
    lines.append("")
    for i in range(n_qubits):
        lines.append(f"measure q[{i}] -> c[{i}];")
    
    return "\n".join(lines)


def main():
    results = []
    
    for n in [3, 4, 5, 6, 7, 8]:
        N = 2 ** n
        theta = math.asin(1.0 / math.sqrt(N))
        optimal_iters = max(1, int(math.pi / (4 * theta) - 0.5))
        target = N // 3  # arbitrary target
        
        # Classical queries needed
        classical_queries = N / 2
        quantum_queries = optimal_iters
        
        # Generate QASM and count gates
        qasm = generate_grover_qasm(n, target, optimal_iters)
        gates = count_qasm_gates(qasm)
        
        row = {
            "qubits": n,
            "keyspace": N,
            "optimal_iterations": optimal_iters,
            "classical_queries": classical_queries,
            "quantum_queries": quantum_queries,
            "speedup_factor": classical_queries / quantum_queries,
            **gates,
        }
        results.append(row)
        
        print(f"n={n:2d}  N={N:>6d}  iters={optimal_iters:>3d}  "
              f"gates={gates['total_gates']:>6d}  "
              f"CX={gates['cx_gates']:>5d}  "
              f"T={gates['t_gates']:>5d}  "
              f"speedup={classical_queries/quantum_queries:.1f}x")
    
    # Save results
    output = {
        "analysis": "grover_scaling",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    
    out_path = REPO / "problems" / "10_post_quantum_cryptography" / "estimates" / "grover_scaling_analysis.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nSaved: {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
