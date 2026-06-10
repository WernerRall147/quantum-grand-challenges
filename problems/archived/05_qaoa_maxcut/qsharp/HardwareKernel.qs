// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 05_qaoa_maxcut
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation QaoaMaxCutKernel() : Result[] {
    use qs = Qubit[3];
    // Init: uniform superposition
    for q in qs { H(q); }
    // Cost layer (triangle graph, γ=0.5)
    // Edge 0-1
    CNOT(qs[0], qs[1]); Rz(1.0, qs[1]); CNOT(qs[0], qs[1]);
    // Edge 0-2
    CNOT(qs[0], qs[2]); Rz(1.0, qs[2]); CNOT(qs[0], qs[2]);
    // Edge 1-2
    CNOT(qs[1], qs[2]); Rz(1.0, qs[2]); CNOT(qs[1], qs[2]);
    // Mixer layer (β=0.5)
    for q in qs { Rx(1.0, q); }
    return MResetEachZ(qs);
}
