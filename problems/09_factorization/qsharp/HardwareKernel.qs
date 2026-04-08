// HardwareKernel.qs — Minimal QIR-compatible kernel for Azure Quantum
// Problem: 09_factorization
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Canon.*;
import Std.Convert.IntAsDouble;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation ShorKernel() : Result[] {
    // Simplified period finding for N=15, a=7
    // 4 counting qubits + 4 work qubits
    use counting = Qubit[4];
    use work = Qubit[4];
    X(work[3]); // Init |1⟩
    for q in counting { H(q); }
    // Controlled modular multiplication (simplified for a=7, N=15)
    // U|x⟩ = |7x mod 15⟩ permutation: 1→7→4→13→1, etc.
    Controlled SWAP([counting[3]], (work[0], work[2]));
    Controlled SWAP([counting[3]], (work[1], work[3]));
    Controlled X([counting[3]], work[0]);
    Controlled X([counting[3]], work[1]);
    // Inverse QFT on counting register
    SWAP(counting[0], counting[3]);
    SWAP(counting[1], counting[2]);
    for j in 0..3 {
        for k in 0..j-1 {
            Controlled R1([counting[k]], (-PI() / IntAsDouble(1 <<< (j - k)), counting[j]));
        }
        H(counting[j]);
    }
    let result = MResetEachZ(counting);
    ResetAll(work);
    return result;
}
