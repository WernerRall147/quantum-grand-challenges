// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 19_quantum_chromodynamics
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation LatticeGaugeKernel() : Result[] {
    use qs = Qubit[4];
    // 3 Trotter steps (β=0.5, h=0.3)
    for _ in 1..3 {
        // ZZ plaquettes
        for i in 0..2 {
            CNOT(qs[i], qs[i+1]);
            Rz(1.0, qs[i+1]);
            CNOT(qs[i], qs[i+1]);
        }
        // Transverse field
        for q in qs { Rx(0.6, q); }
    }
    return MResetEachZ(qs);
}
