namespace QuantumGrandChallenges.Qcd {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function NormalizeGaugeWeights(weights : Double[]) : Double[] {
        mutable total = 0.0;
        for value in weights {
            set total += value;
        }
        if total <= 1e-12 {
            return [0.0, size = Length(weights)];
        }
        let invTotal = 1.0 / total;
        mutable normalized = [0.0, size = Length(weights)];
        for idx in 0 .. Length(weights) - 1 {
            set normalized w/= idx <- weights[idx] * invTotal;
        }
        return normalized;
    }

    function WilsonLoopPreview(betas : Double[], extent : Int) : Double {
        if extent <= 0 or Length(betas) == 0 {
            return 0.0;
        }
        mutable accumulator = 0.0;
        for beta in betas {
            let damping = 1.0 / (1.0 + beta / 6.0);
            set accumulator += damping;
        }
        let scale = IntAsDouble(extent);
        return accumulator / scale;
    }

    @EntryPoint()
    operation RunQcdPrototype() : Unit {
        Message("Quantum chromodynamics scaffold - integrate gauge encoding next.");
        let weights = NormalizeGaugeWeights([0.4, 0.35, 0.25]);
        let preview = WilsonLoopPreview([5.6, 6.0, 5.8], 6);
        Message($"Normalized weights: {weights}");
        Message($"Wilson loop preview value: {preview}");
        use ancilla = Qubit();
        H(ancilla);
        Reset(ancilla);
    }
}
