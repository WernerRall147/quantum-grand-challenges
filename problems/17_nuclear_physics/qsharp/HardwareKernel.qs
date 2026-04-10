// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 17_nuclear_physics (VQE deuteron binding energy)
// Target profile: Adaptive_RI
//
// EFT Hamiltonian: H = -1.25·I + 0.35·Z₀ - 0.28·Z₁ + 0.22·Z₀Z₁ + 0.08·X₀X₁
// Experimental deuteron binding energy: -2.22 MeV
// This kernel measures the ZZ term (nucleon-nucleon correlation).

import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation NuclearVQEKernel() : Result[] {
    use qs = Qubit[2];
    // Nuclear ansatz: proton-neutron system
    X(qs[0]);
    Ry(1.4, qs[0]);   // θ₀: proton state rotation
    Ry(0.3, qs[1]);   // θ₁: neutron mixing
    CNOT(qs[0], qs[1]);
    Rz(0.15, qs[1]);  // θ₂: NN correlation phase
    CNOT(qs[0], qs[1]);
    // ZZ-basis measurement: CNOT maps Z₀Z₁ parity onto qubit 1
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
