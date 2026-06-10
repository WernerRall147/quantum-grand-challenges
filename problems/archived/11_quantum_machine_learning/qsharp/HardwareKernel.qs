// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 11_quantum_machine_learning
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation SwapTestKernel() : Result[] {
    use ancilla = Qubit();
    use regA = Qubit[2];
    use regB = Qubit[2];
    // Encode feature vectors
    Ry(1.2, regA[0]); Ry(0.6, regA[1]);
    Ry(0.9, regB[0]); Ry(0.4, regB[1]);
    // Swap test
    H(ancilla);
    Controlled SWAP([ancilla], (regA[0], regB[0]));
    Controlled SWAP([ancilla], (regA[1], regB[1]));
    H(ancilla);
    let r = [M(ancilla)];
    ResetAll(regA); ResetAll(regB); Reset(ancilla);
    return r;
}
