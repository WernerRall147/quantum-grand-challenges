// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 19_quantum_chromodynamics
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

/// 3 first-order Trotter steps of a 4-site transverse-field Ising chain from |0000>, with
/// beta dt = 0.5 (ZZ couplings) and h dt = 0.3 (transverse field) per step, measuring
/// every site. A spin-chain stand-in, not a gauge theory; the name is historical.
@EntryPoint()
operation LatticeGaugeKernel() : Result[] {
    use qs = Qubit[4];
    for _ in 1..3 {
        // Nearest-neighbour ZZ couplings: exp(-i 0.5 Z_i Z_{i+1})
        for i in 0..2 {
            CNOT(qs[i], qs[i+1]);
            Rz(1.0, qs[i+1]);
            CNOT(qs[i], qs[i+1]);
        }
        // Transverse field: exp(-i 0.3 X)
        for q in qs { Rx(0.6, q); }
    }
    return MResetEachZ(qs);
}
