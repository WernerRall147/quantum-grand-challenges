// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 02_catalysis (H₂ VQE with STO-3G Hamiltonian)
// Target profile: Adaptive_RI
//
// Hamiltonian: H = g₀I + g₁Z₀ + g₂Z₁ + g₃Z₀Z₁ + g₄X₀X₁ + g₅Y₀Y₁
// Coefficients at R=0.75Å (near equilibrium): g₀=-0.81, g₁=0.17, g₂=-0.17, g₃=0.17, g₄=-0.04, g₅=-0.04
// This kernel measures the XX term (electron correlation).

import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation CatalysisVQEKernel() : Result[] {
    use qs = Qubit[2];
    // Hartree-Fock |01⟩ reference + parameterized ansatz
    X(qs[0]);
    Ry(0.9, qs[0]);   // θ₀: bonding orbital rotation
    Ry(0.6, qs[1]);   // θ₁: antibonding mixing
    CNOT(qs[0], qs[1]);
    Rz(0.4, qs[1]);   // θ₂: correlation phase
    CNOT(qs[0], qs[1]);
    // Rotate to X-basis for ⟨X₀X₁⟩ measurement
    H(qs[0]);
    H(qs[1]);
    return MResetEachZ(qs);
}
