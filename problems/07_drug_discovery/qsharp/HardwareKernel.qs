// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 07_drug_discovery (VQE molecular binding energy)
// Target profile: Adaptive_RI
//
// Hamiltonian: H = -0.52·I + 0.20·Z₀ - 0.18·Z₁ + 0.12·Z₀Z₁ + 0.06·X₀X₁
// This kernel measures the ZZ term (inter-orbital correlation).

import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation DrugBindingKernel() : Result[] {
    use qs = Qubit[2];
    // Binding ansatz: parameterized unitary for ligand-receptor interaction
    X(qs[0]);
    Ry(1.2, qs[0]);   // θ₀: ligand orbital rotation
    Ry(0.4, qs[1]);   // θ₁: receptor orbital mixing
    CNOT(qs[0], qs[1]);
    Rz(0.5, qs[1]);   // θ₂: binding correlation phase
    CNOT(qs[0], qs[1]);
    // ZZ-basis measurement: CNOT maps Z₀Z₁ parity onto qubit 1
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
