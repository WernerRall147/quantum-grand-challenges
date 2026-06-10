// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 02_catalysis (QPE for H₂ ground state energy, STO-3G)
// Target profile: Adaptive_RI
//
// Hamiltonian: H = g₀I + g₁Z₀ + g₂Z₁ + g₃Z₀Z₁ + g₄X₀X₁ + g₅Y₀Y₁
// QPE extracts eigenphase encoding ground state energy.

import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation CatalysisQPEKernel() : Result[] {
    use phase = Qubit[2];
    use sys = Qubit[2];
    // Hartree-Fock initial state |01⟩
    X(sys[0]);
    // QPE phase register
    H(phase[0]);
    H(phase[1]);
    // Controlled Hamiltonian simulation (Trotter, R=0.75Å)
    Controlled CNOT([phase[0]], (sys[0], sys[1]));
    Controlled Rz([phase[0]], (0.8, sys[1]));
    Controlled CNOT([phase[0]], (sys[0], sys[1]));
    Controlled CNOT([phase[1]], (sys[0], sys[1]));
    Controlled Rz([phase[1]], (1.6, sys[1]));
    Controlled CNOT([phase[1]], (sys[0], sys[1]));
    // Inverse QFT
    SWAP(phase[0], phase[1]);
    H(phase[0]);
    Controlled R1([phase[0]], (-PI() / 2.0, phase[1]));
    H(phase[1]);
    let r0 = M(phase[0]);
    let r1 = M(phase[1]);
    ResetAll(sys);
    return [r0, r1];
}
