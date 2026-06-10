// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 10_post_quantum_cryptography
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Canon.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation GroverKeyKernel() : Result[] {
    use qs = Qubit[3];
    // Grover search for target=5 (|101⟩) in 3-qubit space
    for q in qs { H(q); }
    // 1 Grover iteration (optimal for N=8, M=1: ~2 iterations, use 1 for small circuit)
    // Oracle: flip phase of |101⟩
    X(qs[1]);
    Controlled Z(qs[0..1], qs[2]);
    X(qs[1]);
    // Diffusion
    for q in qs { H(q); X(q); }
    Controlled Z(qs[0..1], qs[2]);
    for q in qs { X(q); H(q); }
    return MResetEachZ(qs);
}
