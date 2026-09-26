// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 20_space_mission_planning
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation MissionQaoaKernel() : Result[] {
    use qs = Qubit[4];
    for q in qs { H(q); }
    // Toy four-leg mission QUBO from Main.RunMissionOptimization.
    // Single-qubit rotations encode the option delta-v bias; all six ZZ
    // pairs encode the time-window conflict penalty. Optimized p=1 angles:
    // gamma = 0.667588438887831; beta = 1.3940817400304706.
    Rz(0.46731190722148175, qs[0]);
    Rz(0.2670353755551324, qs[1]);
    Rz(0.46731190722148175, qs[2]);
    Rz(0.3337942194439155, qs[3]);
    CNOT(qs[0], qs[1]); Rz(0.3337942194439155, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[0], qs[2]); Rz(0.3337942194439155, qs[2]); CNOT(qs[0], qs[2]);
    CNOT(qs[0], qs[3]); Rz(0.3337942194439155, qs[3]); CNOT(qs[0], qs[3]);
    CNOT(qs[1], qs[2]); Rz(0.3337942194439155, qs[2]); CNOT(qs[1], qs[2]);
    CNOT(qs[1], qs[3]); Rz(0.3337942194439155, qs[3]); CNOT(qs[1], qs[3]);
    CNOT(qs[2], qs[3]); Rz(0.3337942194439155, qs[3]); CNOT(qs[2], qs[3]);
    for q in qs { Rx(2.788163480060941, q); }
    return MResetEachZ(qs);
}
