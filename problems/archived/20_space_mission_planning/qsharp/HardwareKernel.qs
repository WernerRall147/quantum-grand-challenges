// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 20_space_mission_planning
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation MissionQaoaKernel() : Result[] {
    use qs = Qubit[3];
    for q in qs { H(q); }
    // Cost: single-qubit Z bias + pairwise ZZ (gamma=1.0)
    Rz(0.8, qs[0]); Rz(1.2, qs[1]); Rz(0.6, qs[2]);
    CNOT(qs[0], qs[1]); Rz(2.0, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[1], qs[2]); Rz(1.6, qs[2]); CNOT(qs[1], qs[2]);
    // Mixer (beta=0.7)
    for q in qs { Rx(1.4, q); }
    return MResetEachZ(qs);
}
