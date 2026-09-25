// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 18_photovoltaics
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation QuantumWalkKernel() : Result[] {
    use coin = Qubit();
    use pos = Qubit[2];
    // The exciton starts at site 1 of a 4-site ring; the site is 2 * pos[0] + pos[1].
    // The previous kernel started from |00> and only swapped the position qubits, so the
    // walker never left site 0 and only the coin varied.
    X(pos[1]);
    // 3 steps of quantum walk
    for _ in 1..3 {
        Ry(1.0, coin); // Coin flip
        // Coin |1>: step right (increment the site)
        CCNOT(coin, pos[1], pos[0]);
        CNOT(coin, pos[1]);
        // Coin |0>: step left (decrement the site)
        X(coin);
        CNOT(coin, pos[1]);
        CCNOT(coin, pos[1], pos[0]);
        X(coin);
    }
    return MResetEachZ([coin] + pos);
}
