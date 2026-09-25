/// Order finding for a = 7 modulo N = 15, the quantum core of Shor's algorithm: a complete
/// program in the shape the generator must return.
///
/// Factoring an RSA-2048 modulus needs thousands of logical qubits; this is the same circuit
/// on the smallest instance that shows it. The order of 7 mod 15 is r = 4, so the 4-qubit
/// phase register returns m in {0, 4, 8, 12}, with m / 16 = s / r. From r, the classical
/// step gcd(7^(r / 2) - 1, 15) = 3 and gcd(7^(r / 2) + 1, 15) = 5 finishes the factoring.
import Std.Canon.*;
import Std.Math.*;
import Std.Measurement.*;

/// Multiplies a 4-qubit little-endian register holding x in 1..14 by a mod 15.
/// Multiplying by 2 mod 15 rotates the four bits left, and multiplying by 15 - b is
/// multiplying by b and then flipping every bit, because 15 - y is y with its bits flipped.
operation MultiplyMod15(a : Int, register : Qubit[]) : Unit is Adj + Ctl {
    let negate = a == 7 or a == 11 or a == 13 or a == 14;
    let b = negate ? 15 - a | a;
    let rotations = b == 2 ? 1 | (b == 4 ? 2 | (b == 8 ? 3 | 0));
    for _ in 1..rotations {
        SWAP(register[2], register[3]);
        SWAP(register[1], register[2]);
        SWAP(register[0], register[1]);
    }
    if negate {
        ApplyToEachCA(X, register);
    }
}

/// U^power for U = multiplication by 7 mod 15. The power is taken classically, so each
/// phase qubit controls one multiplication, by 7^power mod 15, rather than power of them.
operation MultiplyByPower(power : Int, register : Qubit[]) : Unit is Adj + Ctl {
    MultiplyMod15(ExpModI(7, power, 15), register);
}

operation Main() : Result[] {
    use work = Qubit[4];
    use phase = Qubit[4];
    // The work register starts in |1>, little-endian.
    X(work[0]);
    ApplyQPE(MultiplyByPower, work, phase);
    let results = MResetEachZ(phase);
    ResetAll(work);
    return results;
}
