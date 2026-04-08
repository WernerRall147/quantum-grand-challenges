// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 04_linear_solvers
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Convert.IntAsDouble;
import Std.Measurement.*;

/// Simplified HHL kernel: QPE + eigenvalue inversion + measurement.
/// Solves a 2x2 system with a 3-qubit precision register.
@EntryPoint()
operation HHLKernel() : Result[] {
    use sys = Qubit();
    use prec = Qubit[3];
    use anc = Qubit();

    // Encode RHS: |b⟩
    Ry(1.176, sys);  // arctan(b1/b0)

    // Phase estimation
    for q in prec { H(q); }
    for k in 0..2 {
        let power = 1 <<< k;
        for _ in 1..power {
            // Controlled Hamiltonian simulation (Trotter step)
            Controlled Rz([prec[k]], (-0.5, sys));
            Controlled H([prec[k]], sys);
            Controlled Rz([prec[k]], (1.0, sys));
            Controlled H([prec[k]], sys);
            Controlled Rz([prec[k]], (-0.5, sys));
        }
    }

    // Inverse QFT
    SWAP(prec[0], prec[2]);
    for j in 0..2 {
        for k in 0..j-1 {
            Controlled R1([prec[k]], (-PI() / IntAsDouble(1 <<< (j - k)), prec[j]));
        }
        H(prec[j]);
    }

    // Eigenvalue inversion: C-Ry on ancilla
    for k in 0..2 {
        Controlled Ry([prec[k]], (0.125 / IntAsDouble(k + 1), anc));
    }

    // Measure ancilla (post-select on |1⟩ for solution)
    let result = [M(anc)];
    ResetAll(prec);
    Reset(sys);
    Reset(anc);
    return result;
}
