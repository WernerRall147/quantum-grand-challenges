// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 17_nuclear_physics (QPE deuteron binding energy)
// Target profile: Adaptive_RI
//
// QPE extracts eigenphase of nuclear EFT Hamiltonian.
// Experimental deuteron binding energy: -2.22 MeV

import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation NuclearQPEKernel() : Result[] {
    use phase = Qubit[2];
    use sys = Qubit[2];
    // Proton-neutron initial state
    X(sys[0]);
    H(phase[0]);
    H(phase[1]);
    // Controlled nuclear Hamiltonian simulation
    Controlled CNOT([phase[0]], (sys[0], sys[1]));
    Controlled Rz([phase[0]], (0.44, sys[1]));
    Controlled CNOT([phase[0]], (sys[0], sys[1]));
    Controlled CNOT([phase[1]], (sys[0], sys[1]));
    Controlled Rz([phase[1]], (0.88, sys[1]));
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
