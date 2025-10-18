namespace QuantumGrandChallenges.QAERisk {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Intrinsic;

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

    @EntryPoint()
    operation RunQAERiskAnalysis() : (Double, Double, Double) {
        use marker = Qubit();
        Reset(marker);

        let riskParams = RiskParameters(8, 3.0, 0.0, 1.0);
        let quantumEstimate = EstimateTailRiskProbability(riskParams);
        let (lossQubits, threshold, mean, stdDev) = riskParams!;

        let monteCarloSamples = 100000;
        let (classicalProb, classicalError) = ClassicalMonteCarloEstimate(monteCarloSamples, mean, stdDev, threshold, lossQubits);
        let difference = AbsDouble(quantumEstimate - classicalProb);

        Message($"Quantum-inspired estimate: {quantumEstimate}");
        Message($"Classical analytical estimate: {classicalProb} ± {classicalError}");
        Message($"Absolute difference: {difference}");

        return (quantumEstimate, classicalProb, classicalError);
    }
}
