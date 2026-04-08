// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 14_materials_discovery (VQE band gap estimation)
// Target profile: Adaptive_RI
//
// Tight-binding Hamiltonian: H = ε₁Z₁ + ε₂Z₂ + t(X₁X₂ + Y₁Y₂) + V·Z₁Z₂
// Default: ε₁=-1.0, ε₂=-0.5, t=0.3, V=0.1 (silicon-like)
// This kernel measures valence band (XX term for inter-orbital hopping).

import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation MaterialsVQEKernel() : Result[] {
    use qs = Qubit[2];
    // Band gap ansatz: valence band filled |10⟩ reference
    X(qs[0]);
    Ry(0.8, qs[0]);   // θ₀: valence orbital rotation
    Ry(0.6, qs[1]);   // θ₁: conduction orbital mixing
    CNOT(qs[0], qs[1]);
    Rz(0.2, qs[1]);   // θ₂: inter-band correlation
    CNOT(qs[0], qs[1]);
    // Rotate to X-basis for ⟨X₀X₁⟩ hopping term measurement
    H(qs[0]);
    H(qs[1]);
    return MResetEachZ(qs);
}
