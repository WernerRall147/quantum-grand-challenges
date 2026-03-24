namespace QuantumGrandChallenges.PostQuantumCryptography {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    /// Marks a target key index with a phase flip (Grover oracle).
    operation MarkTargetKey(targetIndex : Int, qubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        within {
            for i in 0 .. n - 1 {
                if ((targetIndex &&& (1 <<< (n - 1 - i))) == 0) {
                    X(qubits[i]);
                }
            }
        } apply {
            Controlled Z(qubits[0 .. n - 2], qubits[n - 1]);
        }
    }

    /// Standard diffusion operator: reflect about the uniform superposition.
    operation DiffusionOperator(qubits : Qubit[]) : Unit is Adj + Ctl {
        within {
            ApplyToEachCA(H, qubits);
            ApplyToEachCA(X, qubits);
        } apply {
            Controlled Z(qubits[0 .. Length(qubits) - 2], qubits[Length(qubits) - 1]);
        }
    }

    /// Single Grover iteration: oracle + diffusion.
    operation GroverIteration(targetIndex : Int, qubits : Qubit[]) : Unit is Adj + Ctl {
        MarkTargetKey(targetIndex, qubits);
        DiffusionOperator(qubits);
    }

    /// Run a Grover search for a target key in a keyspace of 2^numQubits.
    /// Returns the number of shots that found the target out of totalShots.
    operation GroverKeySearch(numQubits : Int, targetIndex : Int, totalShots : Int) : (Int, Int) {
        let N = 1 <<< numQubits;
        let theta = ArcSin(1.0 / Sqrt(IntAsDouble(N)));
        let optimalIters = Floor(PI() / (4.0 * theta) - 0.5);
        let iterations = MaxI(1, optimalIters);

        mutable successes = 0;

        for _ in 1 .. totalShots {
            use qubits = Qubit[numQubits];

            // Uniform superposition over keyspace
            ApplyToEachCA(H, qubits);

            // Grover iterations
            for _ in 1 .. iterations {
                GroverIteration(targetIndex, qubits);
            }

            // Measure
            mutable result = 0;
            for i in 0 .. numQubits - 1 {
                if (M(qubits[i]) == One) {
                    set result += 1 <<< (numQubits - 1 - i);
                }
            }

            if (result == targetIndex) {
                set successes += 1;
            }

            ResetAll(qubits);
        }

        return (successes, iterations);
    }

    /// Classical brute-force: expected queries to find a target in keyspace of size N.
    function ClassicalSearchCost(keyspaceBits : Int) : Double {
        return IntAsDouble(1 <<< keyspaceBits) / 2.0;
    }

    /// Quantum Grover: expected queries ~ (pi/4) * sqrt(N).
    function QuantumSearchCost(keyspaceBits : Int) : Double {
        let N = IntAsDouble(1 <<< keyspaceBits);
        return PI() / 4.0 * Sqrt(N);
    }

    @EntryPoint()
    operation RunPostQuantumAnalysis() : Unit {
        Message("=== Post-Quantum Cryptography: Grover Key Search Attack ===");
        Message("");

        // Demonstrate on small keyspaces where simulation is tractable
        let testCases = [
            (3, 5, "8-key space"),
            (4, 11, "16-key space"),
            (5, 22, "32-key space")
        ];
        let shots = 64;

        for (numQubits, targetKey, label) in testCases {
            let N = 1 <<< numQubits;
            let classicalCost = ClassicalSearchCost(numQubits);
            let quantumCost = QuantumSearchCost(numQubits);
            let speedup = classicalCost / quantumCost;

            Message($"--- {label}: {numQubits} qubits, N={N}, target=|{targetKey}> ---");
            Message($"  Classical expected queries: {classicalCost}");
            Message($"  Quantum expected queries:   {quantumCost}");
            Message($"  Quadratic speedup factor:   {speedup}x");

            let (successes, iterations) = GroverKeySearch(numQubits, targetKey, shots);
            let successRate = IntAsDouble(successes) / IntAsDouble(shots) * 100.0;
            Message($"  Grover iterations used:     {iterations}");
            Message($"  Success rate ({shots} shots):    {successes}/{shots} ({successRate}%)");
            Message("");
        }

        // Project to cryptographic keyspaces
        Message("=== Projected Attack Costs (Symmetric Ciphers) ===");
        for bits in [64, 128, 256] {
            let classicalCost = ClassicalSearchCost(bits);
            let quantumCost = QuantumSearchCost(bits);
            Message($"  AES-{bits}: Classical 2^{bits - 1} queries, Quantum ~2^{bits / 2} queries");
        }
        Message("");
        Message("Grover provides quadratic speedup: 128-bit security reduced to 64-bit equivalent.");
        Message("This motivates NIST PQC standards requiring Grover-resistant key sizes.");
    }
}
