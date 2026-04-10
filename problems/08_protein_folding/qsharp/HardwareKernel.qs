// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 08_protein_folding
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation FoldingQaoaKernel() : Result[] {
    use qs = Qubit[3];
    for q in qs { H(q); }
    // ZZ cost interactions
    CNOT(qs[0], qs[1]); Rz(0.6, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[1], qs[2]); Rz(0.8, qs[2]); CNOT(qs[1], qs[2]);
    // Mixer
    for q in qs { Rx(1.0, q); }
    return MResetEachZ(qs);
}
