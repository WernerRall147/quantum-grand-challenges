namespace QuantumGrandChallenges.PostQuantumCryptography {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function NormalizeScores(scores : Double[]) : Double[] {
        mutable sumAbs = 0.0;
        for score in scores {
            set sumAbs += AbsD(score);
        }
        if sumAbs <= 1e-12 {
            return [0.0, size = Length(scores)];
        }
        mutable normalized = [0.0, size = Length(scores)];
        for idx in 0 .. Length(scores) - 1 {
            set normalized w/= idx <- scores[idx] / sumAbs;
        }
        return normalized;
    }

    function PrefixWeights(weights : Double[]) : Double[] {
        mutable prefix = [0.0, size = Length(weights)];
        mutable running = 0.0;
        for idx in 0 .. Length(weights) - 1 {
            set running += weights[idx];
            set prefix w/= idx <- running;
        }
        return prefix;
    }

    operation PreviewAmplitudeBoost(weights : Double[]) : Unit {
        use control = Qubit();
        H(control);
        // Placeholder: Grover iterate would be applied using the weight distribution.
        Reset(control);
    }

    @EntryPoint()
    operation RunPostQuantumPrototype() : Unit {
        Message("Quantum PQC attack analysis placeholder – integrate amplitude amplification later.");
        let rawScores = [0.52, 0.33, 0.11, 0.04];
        let normalized = NormalizeScores(rawScores);
        let prefix = PrefixWeights(normalized);
        Message($"Normalized oracle success probabilities: {normalized}");
        Message($"Prefix distribution for sampler preview: {prefix}");

        PreviewAmplitudeBoost(normalized);

        mutable l2 = 0.0;
        for value in normalized {
            set l2 += value * value;
        }
        Message($"L2 norm of oracle distribution: {Sqrt(l2)}");
    }
}
