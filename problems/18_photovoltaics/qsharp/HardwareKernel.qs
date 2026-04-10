// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 18_photovoltaics
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation QuantumWalkKernel() : Result[] {
    use coin = Qubit();
    use pos = Qubit[2];
    // 3 steps of quantum walk
    for _ in 1..3 {
        Ry(1.0, coin); // Coin flip
        // Conditional shift right
        Controlled SWAP([coin], (pos[0], pos[1]));
        // Conditional shift left
        X(coin);
        Controlled SWAP([coin], (pos[0], pos[1]));
        X(coin);
    }
    return MResetEachZ([coin] + pos);
}
