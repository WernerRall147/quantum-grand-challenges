// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 12_quantum_optimization
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation SchedulingQaoaKernel() : Result[] {
    use qs = Qubit[4];
    for q in qs { H(q); }
    // Toy four-job Ising/QUBO scheduling penalty from Main.RunSchedulingOptimization.
    // The cost layer uses this repository's same-side penalty convention,
    // gamma_standard = 2 gamma for exp(-i gamma_standard C).
    // gamma = 0.3141592653589793; beta = 1.2566370614359172.
    CNOT(qs[0], qs[1]); Rz(0.6283185307179586, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[0], qs[2]); Rz(0.3141592653589793, qs[2]); CNOT(qs[0], qs[2]);
    CNOT(qs[0], qs[3]); Rz(0.12566370614359174, qs[3]); CNOT(qs[0], qs[3]);
    CNOT(qs[1], qs[2]); Rz(0.7539822368615503, qs[2]); CNOT(qs[1], qs[2]);
    CNOT(qs[1], qs[3]); Rz(0.5026548245743669, qs[3]); CNOT(qs[1], qs[3]);
    CNOT(qs[2], qs[3]); Rz(0.37699111843077515, qs[3]); CNOT(qs[2], qs[3]);
    for q in qs { Rx(2.5132741228718345, q); }
    return MResetEachZ(qs);
}
