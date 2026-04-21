// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 15_database_search
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Canon.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation GroverSearchKernel() : Result[] {
    use qs = Qubit[4];
    for q in qs { H(q); }
    // 3 Grover iterations for N=16, M=1 (optimal ~ π/4·√16 ≈ 3)
    for _ in 1..3 {
        // Oracle: mark |0111⟩ = 7
        X(qs[0]);
        Controlled Z(qs[0..2], qs[3]);
        X(qs[0]);
        // Diffusion
        for q in qs { H(q); X(q); }
        Controlled Z(qs[0..2], qs[3]);
        for q in qs { X(q); H(q); }
    }
    return MResetEachZ(qs);
}
