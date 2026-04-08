// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 17_nuclear_physics
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation NuclearVQEKernel() : Result[] {
    use qs = Qubit[2];
    X(qs[0]);
    Ry(1.0, qs[0]);
    Ry(0.5, qs[1]);
    CNOT(qs[0], qs[1]);
    Rz(0.3, qs[1]);
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
