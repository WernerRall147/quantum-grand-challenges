// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 11_quantum_machine_learning
// Target profile: Adaptive_RI
//
// Swap test between the amplitude encodings of the estimator's vectors a = [1.0, 0.5, 0.3, 0.2]
// and b = [0.8, 0.2, 0.6, 0.1], as in Main.SwapTest: P(ancilla = 0) = (1 + |⟨a|b⟩|²)/2 = 0.9175.
// Until 2026-09-26 this kernel swapped two unrelated product states instead.

import Std.Math.*;
import Std.Measurement.*;

operation EncodeFourFeatures(features : Double[], qubits : Qubit[]) : Unit {
    let top = Sqrt(features[0] * features[0] + features[1] * features[1]);
    let bottom = Sqrt(features[2] * features[2] + features[3] * features[3]);
    Ry(2.0 * ArcTan2(bottom, top), qubits[0]);
    within { X(qubits[0]); }
    apply { Controlled Ry([qubits[0]], (2.0 * ArcTan2(features[1], features[0]), qubits[1])); }
    Controlled Ry([qubits[0]], (2.0 * ArcTan2(features[3], features[2]), qubits[1]));
}

@EntryPoint()
operation SwapTestKernel() : Result[] {
    use ancilla = Qubit();
    use regA = Qubit[2];
    use regB = Qubit[2];
    EncodeFourFeatures([1.0, 0.5, 0.3, 0.2], regA);
    EncodeFourFeatures([0.8, 0.2, 0.6, 0.1], regB);
    // Swap test
    H(ancilla);
    Controlled SWAP([ancilla], (regA[0], regB[0]));
    Controlled SWAP([ancilla], (regA[1], regB[1]));
    H(ancilla);
    let r = [M(ancilla)];
    ResetAll(regA); ResetAll(regB); Reset(ancilla);
    return r;
}
