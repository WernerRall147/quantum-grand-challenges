// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// Classical modular exponentiation: base^exp mod modulus.
function ModularExponent(baseValue : Int, exponent : Int, modulus : Int) : Int {
    mutable result = 1 % modulus;
    mutable power = baseValue % modulus;
    mutable remaining = exponent;
    while remaining > 0 {
        if (remaining % 2) == 1 {
            set result = (result * power) % modulus;
        }
        set power = (power * power) % modulus;
        set remaining = remaining / 2;
    }
    return result;
}

/// Classical GCD via Euclidean algorithm.
function GCD(a : Int, b : Int) : Int {
    mutable x = a;
    mutable y = b;
    while y > 0 {
        let temp = y;
        set y = x % y;
        set x = temp;
    }
    return x;
}

/// Controlled multiplication by `a` mod 15 on a 4-qubit big-endian register (target[3] is
/// the lowest bit), for every a coprime to 15. Multiplying by 2 mod 15 rotates the four bits
/// one place toward the high end, by 4 two places, by 8 one place toward the low end; and
/// multiplying by 15 - b is multiplying by b and then flipping every bit, because 15 - y is y
/// with its bits flipped. The previous version was right for 2 and 4 only: it multiplied by
/// 13 for both 7 and 8, by 4 for 11 and by 2 for 13. tooling/test_shor_kernel.py checks the
/// whole multiplication table.
operation ControlledMultiplyMod15(a : Int, control : Qubit, target : Qubit[]) : Unit is Adj + Ctl {
    let negate = a == 7 or a == 11 or a == 13 or a == 14;
    let b = negate ? 15 - a | a;
    if b == 2 {
        Controlled SWAP([control], (target[0], target[1]));
        Controlled SWAP([control], (target[1], target[2]));
        Controlled SWAP([control], (target[2], target[3]));
    } elif b == 4 {
        Controlled SWAP([control], (target[0], target[2]));
        Controlled SWAP([control], (target[1], target[3]));
    } elif b == 8 {
        Controlled SWAP([control], (target[2], target[3]));
        Controlled SWAP([control], (target[1], target[2]));
        Controlled SWAP([control], (target[0], target[1]));
    }
    if negate {
        for q in target {
            Controlled X([control], q);
        }
    }
}

/// Apply controlled-U^(2^k) where U is multiplication by 'a' mod 15.
operation ControlledPowerMod15(a : Int, power : Int, control : Qubit, target : Qubit[]) : Unit is Adj + Ctl {
    // Compute a^(2^power) mod 15 classically, then apply one controlled multiply
    let effectiveA = ModularExponent(a, 1 <<< power, 15);
    if (effectiveA != 1) {
        ControlledMultiplyMod15(effectiveA, control, target);
    }
}

/// Inverse QFT on the counting register (big-endian: qubits[0] is the most significant).
/// The QFT applies H and then controlled phases 2 pi / 2^(j - i + 1) to each qubit i in turn,
/// and reverses the register; this undoes the reversal and then each qubit, last first. The
/// previous version went first qubit first with angles 2 pi / 2^(j - i), twice too large, so
/// the counting register came out uniform whatever the period.
operation InverseQFT(qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    for i in 0 .. n / 2 - 1 {
        SWAP(qubits[i], qubits[n - 1 - i]);
    }
    for i in n - 1 .. -1 .. 0 {
        for j in n - 1 .. -1 .. i + 1 {
            let angle = -2.0 * PI() / IntAsDouble(1 <<< (j - i + 1));
            Controlled R1([qubits[j]], (angle, qubits[i]));
        }
        H(qubits[i]);
    }
}

/// Shor's period-finding circuit for N=15.
/// Uses 'countingQubits' phase estimation qubits and 4 work qubits.
/// Returns the measured phase as an integer.
operation ShorPeriodFinding(a : Int, countingQubits : Int) : Int {
    use counting = Qubit[countingQubits];
    use work = Qubit[4];

    // Initialize work register to |1⟩ = |0001⟩
    X(work[3]);

    // Hadamard on counting register
    ApplyToEachCA(H, counting);

    // Controlled modular exponentiation: U^(2^k)|x⟩ = |a^(2^k) * x mod 15⟩
    for k in 0 .. countingQubits - 1 {
        ControlledPowerMod15(a, k, counting[countingQubits - 1 - k], work);
    }

    // Inverse QFT
    InverseQFT(counting);

    // Measure counting register
    mutable result = 0;
    for i in 0 .. countingQubits - 1 {
        if (M(counting[i]) == One) {
            set result += 1 <<< (countingQubits - 1 - i);
        }
    }

    ResetAll(counting);
    ResetAll(work);

    return result;
}

/// Extract period from phase measurement using continued fractions.
function ExtractPeriod(measured : Int, totalPhases : Int, N : Int) : Int {
    if (measured == 0) {
        return 0;
    }
    // Simple fraction reduction: measured/totalPhases ≈ s/r
    let g = GCD(measured, totalPhases);
    let denominator = totalPhases / g;
    if (denominator > 0 and denominator < N) {
        return denominator;
    }
    return 0;
}

@EntryPoint()
operation RunShorFactorization() : Unit {
    Message("=== Shor's Algorithm: Factoring N=15 ===");
    Message("");

    let N = 15;
    let countingQubits = 4;  // 2^4 = 16 phase bins
    let totalPhases = 1 <<< countingQubits;
    let bases = [2, 7, 11];
    let shots = 32;

    for a in bases {
        Message($"--- Base a={a}, N={N} ---");
        let classicalOrder = ModularExponent(a, 1, N);
        Message($"  a^1 mod {N} = {classicalOrder}");

        // Classical verification of period
        mutable period = 1;
        mutable val = a;
        for _ in 1 .. N - 1 {
            if (val != 1) {
                set val = (val * a) % N;
                set period += 1;
            }
        }
        Message($"  Classical period r = {period}");

        // Quantum period finding
        mutable periodCounts = [0, size = N + 1];
        for _ in 1 .. shots {
            let measured = ShorPeriodFinding(a, countingQubits);
            let candidateR = ExtractPeriod(measured, totalPhases, N);
            if (candidateR > 0 and candidateR <= N) {
                set periodCounts w/= candidateR <- periodCounts[candidateR] + 1;
            }
        }

        // Find most common period
        mutable bestR = 0;
        mutable bestCount = 0;
        for r in 1 .. N {
            if (periodCounts[r] > bestCount) {
                set bestCount = periodCounts[r];
                set bestR = r;
            }
        }
        Message($"  Quantum most frequent period: r={bestR} ({bestCount}/{shots} shots)");

        // Factor extraction
        if (bestR > 0 and bestR % 2 == 0) {
            let guess1 = ModularExponent(a, bestR / 2, N) - 1;
            let guess2 = ModularExponent(a, bestR / 2, N) + 1;
            let f1 = GCD(MaxI(guess1, 0), N);
            let f2 = GCD(guess2, N);
            if (f1 > 1 and f1 < N) {
                Message($"  Factor found: {N} = {f1} x {N / f1}");
            } elif (f2 > 1 and f2 < N) {
                Message($"  Factor found: {N} = {f2} x {N / f2}");
            } else {
                Message($"  GCD candidates: gcd({guess1},{N})={f1}, gcd({guess2},{N})={f2}");
            }
        } else {
            Message($"  Period {bestR} is odd or zero; would retry with different base.");
        }
        Message("");
    }

    Message("=== Factoring Complexity ===");
    Message($"Classical trial division: O(sqrt(N)) = O({Floor(Sqrt(IntAsDouble(N)))}) for N={N}");
    Message($"Shor's algorithm: O((log N)^3) = O({3 * 4}) for {countingQubits}-bit modulus");
    Message("Exponential quantum speedup for large N enables breaking RSA.");
}
