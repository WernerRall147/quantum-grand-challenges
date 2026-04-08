// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 01_hubbard
// Target profile: Adaptive_RI

import Std.Convert.IntAsDouble;
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation HubbardVQEKernel() : Result[] {
    use qs = Qubit[2];
    // VQE ansatz with fixed parameters (θ₀=1.0, θ₁=0.5, θ₂=0.3)
    X(qs[0]);
    Ry(1.0, qs[0]);
    Ry(0.5, qs[1]);
    CNOT(qs[0], qs[1]);
    Rz(0.3, qs[1]);
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
