// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 16_error_correction
// Target profile: Adaptive_RI

import Std.Measurement.*;

@EntryPoint()
operation QECKernel() : Result[] {
    use data = Qubit();
    use anc1 = Qubit();
    use anc2 = Qubit();
    // Prepare superposition state to protect
    H(data);
    // Encode: 3-bit repetition code
    CNOT(data, anc1);
    CNOT(data, anc2);
    // Introduce error on qubit 1 (simulated)
    X(anc1);
    // Syndrome extraction
    use syn = Qubit[2];
    CNOT(data, syn[0]); CNOT(anc1, syn[0]);
    CNOT(anc1, syn[1]); CNOT(anc2, syn[1]);
    // Measure syndrome and correct
    let s0 = M(syn[0]);
    let s1 = M(syn[1]);
    // Correction based on syndrome
    if s0 == One and s1 == One { X(anc1); }
    elif s0 == One { X(data); }
    elif s1 == One { X(anc2); }
    // Decode and measure
    CNOT(data, anc2); CNOT(data, anc1);
    let r = [MResetZ(data)];
    Reset(anc1); Reset(anc2); ResetAll(syn);
    return r;
}
