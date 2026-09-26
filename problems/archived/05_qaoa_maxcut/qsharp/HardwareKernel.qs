// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 05_qaoa_maxcut
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation QaoaMaxCutKernel() : Result[] {
    use qs = Qubit[3];
    for q in qs { H(q); }
    // Triangle MaxCut cost layer at optimized p=1 angles.
    // This repository's MaxCut convention applies CNOT-Rz(2 gamma)-CNOT,
    // so gamma_standard in exp(-i gamma_standard C) is -2 gamma.
    // gamma = 2.827433388230814; beta = 0.3141592653589793.
    CNOT(qs[0], qs[1]); Rz(5.654866776461628, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[0], qs[2]); Rz(5.654866776461628, qs[2]); CNOT(qs[0], qs[2]);
    CNOT(qs[1], qs[2]); Rz(5.654866776461628, qs[2]); CNOT(qs[1], qs[2]);
    for q in qs { Rx(0.6283185307179586, q); }
    return MResetEachZ(qs);
}
