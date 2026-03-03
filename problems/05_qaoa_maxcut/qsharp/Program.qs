namespace QuantumGrandChallenges.QaoaMaxCut {
    open Microsoft.Quantum.Arrays;
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

    function ReplaceAt(values : Double[], index : Int, value : Double) : Double[] {
        mutable copy = values;
        set copy w/= index <- value;
        return copy;
    }

    operation OptimizeByCoordinateSearch(
        weights : Double[][],
        depth : Int,
        coarseShots : Int,
        passes : Int
    ) : (Double[], Double[], Double, Double, Int[]) {
        let gammaCandidates = [0.1, 0.3, 0.5, 0.7, 0.9];
        let betaCandidates = [0.1, 0.3, 0.5, 0.7, 0.9];

        mutable bestGammas = [0.5, size = depth];
        mutable bestBetas = [0.5, size = depth];
        mutable bestExpectation = -1.0;
        mutable sampleBest = -1.0;
        mutable sampleAssignment = [0, size = Length(weights)];

        let (seedExpectation, seedSample, seedAssignment) =
            EvaluateQaoa(weights, bestBetas, bestGammas, coarseShots);
        set bestExpectation = seedExpectation;
        set sampleBest = seedSample;
        set sampleAssignment = seedAssignment;

        for _pass in 1..passes {
            for layer in 0..depth - 1 {
                mutable gammaExpectation = bestExpectation;
                mutable gammaChoice = bestGammas[layer];
                mutable gammaSample = sampleBest;
                mutable gammaAssignment = sampleAssignment;

                for gamma in gammaCandidates {
                    let trialGammas = ReplaceAt(bestGammas, layer, gamma);
                    let (expectation, bestValue, assignment) =
                        EvaluateQaoa(weights, bestBetas, trialGammas, coarseShots);
                    if expectation > gammaExpectation {
                        set gammaExpectation = expectation;
                        set gammaChoice = gamma;
                        set gammaSample = bestValue;
                        set gammaAssignment = assignment;
                    }
                }
                set bestGammas = ReplaceAt(bestGammas, layer, gammaChoice);
                set bestExpectation = gammaExpectation;
                set sampleBest = gammaSample;
                set sampleAssignment = gammaAssignment;

                mutable betaExpectation = bestExpectation;
                mutable betaChoice = bestBetas[layer];
                mutable betaSample = sampleBest;
                mutable betaAssignment = sampleAssignment;

                for beta in betaCandidates {
                    let trialBetas = ReplaceAt(bestBetas, layer, beta);
                    let (expectation, bestValue, assignment) =
                        EvaluateQaoa(weights, trialBetas, bestGammas, coarseShots);
                    if expectation > betaExpectation {
                        set betaExpectation = expectation;
                        set betaChoice = beta;
                        set betaSample = bestValue;
                        set betaAssignment = assignment;
                    }
                }
                set bestBetas = ReplaceAt(bestBetas, layer, betaChoice);
                set bestExpectation = betaExpectation;
                set sampleBest = betaSample;
                set sampleAssignment = betaAssignment;
            }
        }

        let (finalExpectation, finalSample, finalAssignment) =
            EvaluateQaoa(weights, bestBetas, bestGammas, coarseShots);
        if finalExpectation > bestExpectation {
            set bestExpectation = finalExpectation;
            set sampleBest = finalSample;
            set sampleAssignment = finalAssignment;
        }

        return (bestBetas, bestGammas, bestExpectation, sampleBest, sampleAssignment);
    }

    operation RunQaoaAnalysis(
        weights : Double[][],
        depth : Int,
        coarseShots : Int,
        refinedShots : Int
    ) : (Double, Int[], Double[], Double[], Double, Double, Int[], Double, Double, Int[]) {
        let (optimalValue, optimalAssignment) = MaxCutExact(weights);

        if depth < 1 {
            fail "Depth must be at least 1.";
        }

        let (bestBetas, bestGammas, coarseExpectation, coarseSample, coarseAssignment) =
            OptimizeByCoordinateSearch(weights, depth, coarseShots, 2);

        let (refinedExpectation, refinedSample, refinedAssignment) =
            EvaluateQaoa(weights, bestBetas, bestGammas, refinedShots);

        return (
            optimalValue,
            optimalAssignment,
            bestBetas,
            bestGammas,
            coarseExpectation,
            coarseSample,
            coarseAssignment,
            refinedExpectation,
            refinedSample,
            refinedAssignment
        );
    }
}
