// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 09_factorization
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Canon.*;
import Std.Convert.IntAsDouble;
import Std.Measurement.MResetEachZ;

/// Order finding for a = 7 mod 15 (order r = 4), the quantum step of Shor's algorithm.
/// Both registers are little-endian (index 0 is the lowest bit). Counting qubit k controls
/// U^(2^k) for U = multiplication by 7 mod 15; 7^2 = 4 mod 15 and 7^4 = 1, so only counting
/// qubits 0 and 1 control anything. The counting register then reads s * 16 / r, so bits 0
/// and 1 are always Zero and bits 2 and 3 take each of their four values equally often.
/// The previous kernel applied one multiplication, controlled by the qubit that should
/// control U^8, so it did not find the period. tooling/test_shor_kernel.py checks the
/// distribution.
@EntryPoint()
operation ShorKernel() : Result[] {
    use counting = Qubit[4];
    use work = Qubit[4];
    X(work[0]); // |1>
    for q in counting { H(q); }
    // Controlled U: multiply by 7 = multiply by 8 (rotate one place toward the low end),
    // then flip every bit, because 7x = 15 - 8x mod 15.
    Controlled SWAP([counting[0]], (work[0], work[1]));
    Controlled SWAP([counting[0]], (work[1], work[2]));
    Controlled SWAP([counting[0]], (work[2], work[3]));
    for q in work { Controlled X([counting[0]], q); }
    // Controlled U^2: multiply by 4 (rotate two places).
    Controlled SWAP([counting[1]], (work[0], work[2]));
    Controlled SWAP([counting[1]], (work[1], work[3]));
    // Inverse QFT on the little-endian counting register.
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
