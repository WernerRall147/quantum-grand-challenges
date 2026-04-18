// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 14_materials_discovery (QPE band gap estimation)
// Target profile: Adaptive_RI
//
// QPE extracts eigenphase of tight-binding Hamiltonian for band structure.

import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation MaterialsQPEKernel() : Result[] {
    use phase = Qubit[2];
    use sys = Qubit[2];
    // Valence band filled reference
    X(sys[0]);
    H(phase[0]);
    H(phase[1]);
    // Controlled tight-binding Hamiltonian (hopping + on-site)
    Controlled CNOT([phase[0]], (sys[0], sys[1]));
    Controlled Rz([phase[0]], (0.6, sys[1]));
    Controlled CNOT([phase[0]], (sys[0], sys[1]));
    Controlled Rz([phase[0]], (-1.0, sys[0]));
    Controlled CNOT([phase[1]], (sys[0], sys[1]));
    Controlled Rz([phase[1]], (1.2, sys[1]));
    Controlled CNOT([phase[1]], (sys[0], sys[1]));
    Controlled Rz([phase[1]], (-2.0, sys[0]));
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
