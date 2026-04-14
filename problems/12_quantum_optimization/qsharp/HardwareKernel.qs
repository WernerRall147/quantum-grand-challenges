// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 12_quantum_optimization
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation SchedulingQaoaKernel() : Result[] {
    use qs = Qubit[4];
    for q in qs { H(q); }
    // ZZ cost (job conflicts, gamma=0.7)
    CNOT(qs[0], qs[1]); Rz(1.4, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[1], qs[2]); Rz(1.4, qs[2]); CNOT(qs[1], qs[2]);
    CNOT(qs[2], qs[3]); Rz(1.4, qs[3]); CNOT(qs[2], qs[3]);
    // Mixer (beta=0.7)
    for q in qs { Rx(1.4, q); }
    return MResetEachZ(qs);
}
