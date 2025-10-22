namespace QuantumGrandChallenges.ProteinFolding {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function NormalizeContactWeights(weights : Double[]) : Double[] {
        mutable total = 0.0;
        for value in weights {
            set total += AbsD(value);
        }
        if total <= 1e-12 {
            return [0.0, size = Length(weights)];
        }
        mutable normalized = [0.0, size = Length(weights)];
        for idx in 0 .. Length(weights) - 1 {
            set normalized w/= idx <- weights[idx] / total;
        }
        return normalized;
    }

    function BuildPrefixAmplitudes(weights : Double[]) : Double[] {
        mutable prefix = [0.0, size = Length(weights)];
        mutable running = 0.0;
        for idx in 0 .. Length(weights) - 1 {
            set running += weights[idx];
            set prefix w/= idx <- running;
        }
        return prefix;
    }

    operation PreviewAmplitudeSeed(weights : Double[]) : Unit {
        use ancilla = Qubit();
        H(ancilla);
        // Placeholder for future controlled rotations driven by contact amplitudes.
        Reset(ancilla);
    }

    @EntryPoint()
    operation RunProteinFoldingPrototype() : Unit {
        Message("Quantum protein folding workflow placeholder – integrate amplitude encoding later.");
        let rawWeights = [0.45, 0.35, 0.15, 0.05];
        let normalized = NormalizeContactWeights(rawWeights);
        let prefix = BuildPrefixAmplitudes(normalized);
        Message($"Preview normalized contact weights: {normalized}");
        Message($"Prefix cumulative amplitudes: {prefix}");

        PreviewAmplitudeSeed(normalized);

        mutable normSquared = 0.0;
        for value in normalized {
            set normSquared += value * value;
        }
        Message($"L2 norm of the contact distribution: {Sqrt(normSquared)}");
    }
}
