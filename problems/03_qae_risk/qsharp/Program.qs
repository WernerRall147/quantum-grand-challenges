namespace QuantumGrandChallenges.QAERisk {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    newtype RiskParameters = (
        LossQubits : Int,
        Threshold : Double,
        Mean : Double,
        StdDev : Double
    );

    function NumStates(lossQubits : Int) : Int {
        return 1 <<< lossQubits;
    }

    function LossValueFromIndex(index : Int, lossQubits : Int) : Double {
        let numStates = NumStates(lossQubits);
        let fraction = IntAsDouble(index + 1) / IntAsDouble(numStates);
        return fraction * 10.0;
    }

    function LogNormalPdf(x : Double, mean : Double, stdDev : Double) : Double {
        mutable spread = stdDev;
        if (spread <= 0.1) {
            set spread = 0.1;
        }

        let center = 1.0 + mean;
        let distance = x - center;
        let denominator = 1.0 + (distance * distance) / (spread * spread);
        return 1.0 / denominator;
    }

    function AbsDouble(value : Double) : Double {
        if (value < 0.0) {
            return -value;
        }

        return value;
    }

    function LogNormalProbabilities(lossQubits : Int, mean : Double, stdDev : Double) : Double[] {
        let numStates = NumStates(lossQubits);
        mutable raw = [0.0, size = numStates];
        mutable total = 0.0;

        for index in 0 .. numStates - 1 {
            let value = LossValueFromIndex(index, lossQubits);
            let pdf = LogNormalPdf(value, mean, stdDev);
            set raw w/= index <- pdf;
            set total += pdf;
        }

        if (total <= 0.0) {
            return raw;
        }

        mutable normalized = [0.0, size = numStates];
        for index in 0 .. numStates - 1 {
            set normalized w/= index <- raw[index] / total;
        }

        return normalized;
    }

    function TailProbability(probabilities : Double[], threshold : Double, lossQubits : Int) : Double {
        let numStates = Length(probabilities);
        mutable probabilitySum = 0.0;

        for index in 0 .. numStates - 1 {
            let loss = LossValueFromIndex(index, lossQubits);
            if (loss > threshold) {
                set probabilitySum += probabilities[index];
            }
        }

        return probabilitySum;
    }

    function ClassicalMonteCarloEstimate(numSamples : Int, mean : Double, stdDev : Double, threshold : Double, lossQubits : Int) : (Double, Double) {
        let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);
        let tailProb = TailProbability(probabilities, threshold, lossQubits);
        let sampleCount = IntAsDouble(numSamples);
        let standardError = Sqrt(tailProb * (1.0 - tailProb) / sampleCount);
        return (tailProb, standardError);
    }

    function EstimateTailRiskProbability(riskParams : RiskParameters) : Double {
        let (lossQubits, threshold, mean, stdDev) = riskParams!;
        let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);
        return TailProbability(probabilities, threshold, lossQubits);
    }

    operation PrepareTailAmplitude(probability : Double, target : Qubit) : Unit is Adj + Ctl {
        body (...) {
            let rotation = 2.0 * ArcSin(Sqrt(probability));
            Ry(rotation, target);
        }
    }

    operation ApplyAmplitudeAmplificationIteration(probability : Double, target : Qubit) : Unit is Adj + Ctl {
        body (...) {
            // Reflect about success state (ancilla = |1>)
            Z(target);

            // Reflect about zero state via state preparation
            Adjoint PrepareTailAmplitude(probability, target);
            X(target);
            Z(target);
            X(target);
            PrepareTailAmplitude(probability, target);
        }
        adjoint auto;
        controlled auto;
        controlled adjoint auto;
    }

    operation ApplyAmplitudeAmplificationPower(probability : Double, power : Int, target : Qubit) : Unit is Adj + Ctl {
        body (...) {
            for _ in 1 .. power {
                ApplyAmplitudeAmplificationIteration(probability, target);
            }
        }
        adjoint auto;
        controlled auto;
        controlled adjoint auto;
    }

    function ClipProbability(value : Double) : Double {
        if (value < 0.0) {
            return 0.0;
        }
        if (value > 1.0) {
            return 1.0;
        }
        return value;
    }

    function MaxDouble(a : Double, b : Double) : Double {
        if (a > b) {
            return a;
        }
        return b;
    }

    function MinDouble(a : Double, b : Double) : Double {
        if (a < b) {
            return a;
        }
        return b;
    }

    function MaxInt(a : Int, b : Int) : Int {
        if (a > b) {
            return a;
        }
        return b;
    }

    operation ResetRegister(register : Qubit[]) : Unit {
        body (...) {
            for qubit in register {
                let result = M(qubit);
                if (result == One) {
                    X(qubit);
                }
            }
        }
    }

    operation ApplyInverseQFT(register : Qubit[]) : Unit is Adj + Ctl {
        body (...) {
            let n = Length(register);
            for j in 0 .. n - 1 {
                let target = register[j];

                for k in 0 .. j - 1 {
                    let angle = -PI() / IntAsDouble(1 <<< (j - k));
                    Controlled R1([register[k]], (angle, target));
                }

                H(target);
            }

            for j in 0 .. (n / 2 - 1) {
                let right = n - j - 1;
                if (j < right) {
                    SWAP(register[j], register[right]);
                }
            }
        }
        adjoint auto;
        controlled auto;
        controlled adjoint auto;
    }

    operation EstimateTailRiskAmplitude(riskParams : RiskParameters, countingQubits : Int, repetitions : Int) : (Double, Double) {
        let (lossQubits, threshold, mean, stdDev) = riskParams!;
        let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);
        let tailProbability = TailProbability(probabilities, threshold, lossQubits);

        if (tailProbability <= 0.0 or tailProbability >= 1.0) {
            return (ClipProbability(tailProbability), 0.0);
        }

        let runs = MaxInt(1, repetitions);
        mutable sumTheta = 0.0;
        mutable sumAmplitude = 0.0;
        mutable sumAmplitudeSquares = 0.0;
        mutable outcomeCounts = [0, size = 1 <<< countingQubits];

        for _ in 1 .. runs {
            use counting = Qubit[countingQubits];
            use system = Qubit();

            for idx in 0 .. countingQubits - 1 {
                H(counting[idx]);
            }

            PrepareTailAmplitude(tailProbability, system);

            for idx in 0 .. countingQubits - 1 {
                let power = 1 <<< (countingQubits - idx - 1);
                Controlled ApplyAmplitudeAmplificationPower([counting[idx]], (tailProbability, power, system));
            }

            ApplyInverseQFT(counting);

            mutable outcome = 0;
            for idx in 0 .. countingQubits - 1 {
                let result = M(counting[idx]);
                if (result == One) {
                    set outcome += 1 <<< idx;
                    X(counting[idx]);
                }
            }

            set outcomeCounts w/= outcome <- outcomeCounts[outcome] + 1;

            ResetRegister(counting);
            Adjoint PrepareTailAmplitude(tailProbability, system);
            Reset(system);

            let denom = IntAsDouble(1 <<< countingQubits);
            let rawPhase = IntAsDouble(outcome) / denom;
            let phase = MinDouble(rawPhase, 1.0 - rawPhase);
            let theta = phase * PI();
            let amplitudeSample = Sin(theta) * Sin(theta);

            set sumTheta += theta;
            set sumAmplitude += amplitudeSample;
            set sumAmplitudeSquares += amplitudeSample * amplitudeSample;
        }

        let runsDouble = IntAsDouble(runs);
        let meanTheta = sumTheta / runsDouble;
        let meanAmplitude = sumAmplitude / runsDouble;
        let varianceAmplitude = MaxDouble(0.0, (sumAmplitudeSquares / runsDouble) - (meanAmplitude * meanAmplitude));
        let samplingStd = Sqrt(varianceAmplitude / runsDouble);

        mutable bestOutcome = 0;
        mutable bestCount = outcomeCounts[0];
        for idx in 1 .. Length(outcomeCounts) - 1 {
            let count = outcomeCounts[idx];
            if (count > bestCount) {
                set bestCount = count;
                set bestOutcome = idx;
            }
        }
        let denomGlobal = IntAsDouble(1 <<< countingQubits);
        let rawBestPhase = IntAsDouble(bestOutcome) / denomGlobal;
        let bestPhase = MinDouble(rawBestPhase, 1.0 - rawBestPhase);

        let thetaBest = bestPhase * PI();
        let clippedMeanAmplitude = ClipProbability(meanAmplitude);

    let amplitudeBest = ClipProbability(Sin(thetaBest) * Sin(thetaBest));

    Message($"Most frequent phase outcome: {bestOutcome}/{1 <<< countingQubits} (effective phase~{bestPhase}, amplitude~{amplitudeBest})");

        let derivative = AbsDouble(Sin(2.0 * meanTheta));
        let phaseResolution = PI() / IntAsDouble(1 <<< countingQubits);
        let discretizationStd = derivative * phaseResolution;
        let totalStd = Sqrt(samplingStd * samplingStd + discretizationStd * discretizationStd);

        return (clippedMeanAmplitude, totalStd);
    }

    @EntryPoint()
    operation RunQAERiskAnalysis() : (Double, Double, Double) {
        use marker = Qubit();
        Reset(marker);

        let riskParams = RiskParameters(8, 3.0, 0.0, 1.0);
        let (lossQubits, threshold, mean, stdDev) = riskParams!;

    let countingQubits = 6;
    let repetitions = 64;
        let (quantumEstimate, quantumStdError) = EstimateTailRiskAmplitude(riskParams, countingQubits, repetitions);
        let analyticEstimate = EstimateTailRiskProbability(riskParams);

        let monteCarloSamples = 100000;
        let (classicalProb, classicalError) = ClassicalMonteCarloEstimate(monteCarloSamples, mean, stdDev, threshold, lossQubits);
        let difference = AbsDouble(quantumEstimate - analyticEstimate);

        Message($"Quantum amplitude estimation (phase bits={countingQubits}, repeats={repetitions}): {quantumEstimate} +/- {quantumStdError}");
        Message($"Analytical probability: {analyticEstimate}");
        Message($"Classical Monte Carlo estimate: {classicalProb} ± {classicalError}");
        Message($"Difference between quantum and analytical: {difference}");

        Reset(marker);

        return (quantumEstimate, classicalProb, classicalError);
    }
}
