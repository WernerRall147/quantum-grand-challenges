namespace QuantumGrandChallenges.QuantumML {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function NormalizeVector(samples : Double[]) : Double[] {
        mutable normSquared = 0.0;
        for value in samples {
            set normSquared += value * value;
        }
        if normSquared <= 1e-12 {
            return [0.0, size = Length(samples)];
        }
        let scale = 1.0 / Sqrt(normSquared);
        mutable normalized = [0.0, size = Length(samples)];
        for idx in 0 .. Length(samples) - 1 {
            set normalized w/= idx <- samples[idx] * scale;
        }
        return normalized;
    }

    function PrefixSums(weights : Double[]) : Double[] {
        mutable prefix = [0.0, size = Length(weights)];
        mutable running = 0.0;
        for idx in 0 .. Length(weights) - 1 {
            set running += weights[idx];
            set prefix w/= idx <- running;
        }
        return prefix;
    }

    operation PreviewKernelOverlap(sampleA : Double[], sampleB : Double[]) : Double {
        let vectorA = NormalizeVector(sampleA);
        let vectorB = NormalizeVector(sampleB);

        mutable overlap = 0.0;
        for idx in 0 .. Length(vectorA) - 1 {
            set overlap += vectorA[idx] * vectorB[idx];
        }

        use ancilla = Qubit();
        H(ancilla);
        // Placeholder: a swap test would be applied here using ancilla as control.
        Reset(ancilla);

        return overlap;
    }

    @EntryPoint()
    operation RunQuantumMLPrototype() : Unit {
        Message("Quantum kernel workflow placeholder – integrate swap tests later.");
        let sampleA = [0.9, 0.2, -0.1, 0.4];
        let sampleB = [0.7, -0.3, 0.2, 0.5];
        let overlap = PreviewKernelOverlap(sampleA, sampleB);
        Message($"Inner product preview: {overlap}");

        let prefix = PrefixSums([0.5, 0.6, 0.7, 0.8]);
        Message($"Cumulative kernel score preview: {prefix}");
    }
}
