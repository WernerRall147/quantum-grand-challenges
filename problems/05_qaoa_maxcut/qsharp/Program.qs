namespace QuantumGrandChallenges.QaoaMaxCut {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function EvaluateCut(weights : Double[][], assignment : Int[]) : Double {
        mutable cutValue = 0.0;
        let n = Length(assignment);
        for i in 0..n - 1 {
            for j in i + 1..n - 1 {
                let weight = weights[i][j];
                if AbsD(weight) > 1e-12 and assignment[i] != assignment[j] {
                    set cutValue += weight;
                }
            }
        }
        return cutValue;
    }

    function MaxCutExact(weights : Double[][]) : (Double, Int[]) {
        let n = Length(weights);
        mutable bestValue = -1.0;
        mutable bestAssignment = [0, size = n];

        for bitPattern in 0 .. 2^n - 1 {
            mutable assignment = [0, size = n];
            for idx in 0..n - 1 {
                let bit = (bitPattern >>> idx) &&& 1;
                set assignment w/= idx <- bit;
            }

            let cut = EvaluateCut(weights, assignment);
            if cut > bestValue {
                set bestValue = cut;
                set bestAssignment = assignment;
            }
        }

        return (bestValue, bestAssignment);
    }

    operation ApplyCostLayer(weights : Double[][], gamma : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        for i in 0..n - 1 {
            for j in i + 1..n - 1 {
                let weight = weights[i][j];
                if AbsD(weight) > 1e-12 {
                    Exp([PauliZ, PauliZ], -gamma * weight, [qubits[i], qubits[j]]);
                }
            }
        }
    }

    operation ApplyMixerLayer(beta : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
        for qubit in qubits {
            Rx(2.0 * beta, qubit);
        }
    }

    operation EvaluateQaoa(weights : Double[][], betas : Double[], gammas : Double[], shots : Int) : (Double, Double, Int[]) {
        let depth = Length(betas);
        if depth != Length(gammas) {
            fail "Number of betas must equal number of gammas.";
        }

        let n = Length(weights);
        mutable totalValue = 0.0;
        mutable bestObserved = -1.0;
        mutable bestAssignment = [0, size = n];

        for _ in 1..shots {
            use register = Qubit[n];

            for qubit in register {
                H(qubit);
            }

            for layer in 0..depth - 1 {
                ApplyCostLayer(weights, gammas[layer], register);
                ApplyMixerLayer(betas[layer], register);
            }

            mutable assignment = [0, size = n];
            for idx in 0..n - 1 {
                if M(register[idx]) == One {
                    set assignment w/= idx <- 1;
                }
            }

            let cutValue = EvaluateCut(weights, assignment);
            set totalValue += cutValue;
            if cutValue > bestObserved {
                set bestObserved = cutValue;
                set bestAssignment = assignment;
            }

            ResetAll(register);
        }

        return (totalValue / IntAsDouble(shots), bestObserved, bestAssignment);
    }

    operation OptimizeDepthOne(weights : Double[][], coarseShots : Int) : (Double, Double, Double, Double, Int[]) {
        let gammaCandidates = [0.1, 0.3, 0.5, 0.7, 0.9];
        let betaCandidates = [0.1, 0.3, 0.5, 0.7, 0.9];

        mutable bestExpectation = -1.0;
        mutable bestGamma = 0.1;
        mutable bestBeta = 0.1;
        mutable sampleBest = -1.0;
        mutable sampleAssignment = [0, size = Length(weights)];

        for gamma in gammaCandidates {
            for beta in betaCandidates {
                let (expectation, bestValue, assignment) = EvaluateQaoa(weights, [beta], [gamma], coarseShots);
                if expectation > bestExpectation {
                    set bestExpectation = expectation;
                    set bestGamma = gamma;
                    set bestBeta = beta;
                    set sampleBest = bestValue;
                    set sampleAssignment = assignment;
                }
            }
        }

        return (bestBeta, bestGamma, bestExpectation, sampleBest, sampleAssignment);
    }

    operation RunQaoaAnalysis(
        weights : Double[][],
        depth : Int,
        coarseShots : Int,
        refinedShots : Int
    ) : (Double, Int[], Double, Double, Double, Double, Int[], Double, Double, Int[]) {
        let (optimalValue, optimalAssignment) = MaxCutExact(weights);

        if depth != 1 {
            fail "Only depth-1 QAOA is supported in the current prototype.";
        }

        let (bestBeta, bestGamma, coarseExpectation, coarseSample, coarseAssignment) =
            OptimizeDepthOne(weights, coarseShots);

        let (refinedExpectation, refinedSample, refinedAssignment) =
            EvaluateQaoa(weights, [bestBeta], [bestGamma], refinedShots);

        return (
            optimalValue,
            optimalAssignment,
            bestBeta,
            bestGamma,
            coarseExpectation,
            coarseSample,
            coarseAssignment,
            refinedExpectation,
            refinedSample,
            refinedAssignment
        );
    }
}
