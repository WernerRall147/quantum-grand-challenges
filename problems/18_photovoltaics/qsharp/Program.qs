namespace QuantumGrandChallenges.Photovoltaics {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;

    function NormalizeSpectrum(samples : Double[]) : Double[] {
        mutable total = 0.0;
        for value in samples {
            set total += value;
        }
        if total <= 1e-12 {
            return [0.0, size = Length(samples)];
        }
        let invTotal = 1.0 / total;
        mutable normalized = [0.0, size = Length(samples)];
        for idx in 0 .. Length(samples) - 1 {
            set normalized w/= idx <- samples[idx] * invTotal;
        }
        return normalized;
    }

    function PreviewExcitonWalk(layers : Int, baseCoupling : Double) : Double {
        if layers <= 0 {
            return 0.0;
        }
        mutable accumulator = 0.0;
        for idx in 0 .. layers - 1 {
            let scaling = baseCoupling / (1.0 + IntAsDouble(idx));
            set accumulator += scaling;
        }
        return accumulator;
    }

    @EntryPoint()
    operation RunPhotovoltaicPrototype() : Unit {
    Message("Quantum photovoltaics scaffold - integrate exciton network simulation next.");
        let spectrum = NormalizeSpectrum([0.2, 0.35, 0.45]);
        Message($"Normalized absorption bins: {spectrum}");
        let preview = PreviewExcitonWalk(6, 0.9);
        Message($"Preview coupling strength: {preview}");
        use ancilla = Qubit();
        Reset(ancilla);
    }
}
