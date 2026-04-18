// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 01_hubbard
// Target profile: Adaptive_RI

import Std.Convert.IntAsDouble;
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation HubbardQPEKernel() : Result[] {
    // QPE for 2-site Hubbard ground state energy estimation
    // Phase register (2 qubits) + system register (2 qubits)
    use phase = Qubit[2];
    use sys = Qubit[2];
    // Prepare initial state |01⟩ (half-filling)
    X(sys[0]);
    // QPE: Hadamard on phase qubits
    H(phase[0]);
    H(phase[1]);
    // Controlled Hamiltonian simulation (Trotter step, t=1.0, U=4.0)
    // Controlled-U: hopping term exp(-i*t*XX) + interaction exp(-i*U/2*ZI)
    Controlled CNOT([phase[0]], (sys[0], sys[1]));
    Controlled Rz([phase[0]], (2.0, sys[1]));
    Controlled CNOT([phase[0]], (sys[0], sys[1]));
    // Controlled-U²
    Controlled CNOT([phase[1]], (sys[0], sys[1]));
    Controlled Rz([phase[1]], (4.0, sys[1]));
    Controlled CNOT([phase[1]], (sys[0], sys[1]));
    // Inverse QFT on phase register
    SWAP(phase[0], phase[1]);
    H(phase[0]);
    Controlled R1([phase[0]], (-PI() / 2.0, phase[1]));
    H(phase[1]);
    // Measure phase register (encodes energy eigenvalue)
    let r0 = M(phase[0]);
    let r1 = M(phase[1]);
    ResetAll(sys);
    return [r0, r1];
}
