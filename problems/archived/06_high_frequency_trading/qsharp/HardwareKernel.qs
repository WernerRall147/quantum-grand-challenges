// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 06_high_frequency_trading
// Target profile: Adaptive_RI
//
// Prepares a fixed 2-qubit state (P(|00⟩) = 0.8149) and returns whether the marker flagged
// |00⟩. Repeated shots sample that probability directly; there is no amplitude estimation.

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation HFTKernel() : Result[] {
    use qs = Qubit[2];
    use marker = Qubit();
    // Fixed entangled 2-qubit state (not derived from market data)
    Ry(0.8, qs[0]);
    CNOT(qs[0], qs[1]);
    Ry(0.4, qs[1]);
    CNOT(qs[0], qs[1]);
    // Mark loss state |00⟩
    X(qs[0]); X(qs[1]);
    Controlled X(qs, marker);
    X(qs[0]); X(qs[1]);
    let r = [M(marker)];
    ResetAll(qs); Reset(marker);
    return r;
}
