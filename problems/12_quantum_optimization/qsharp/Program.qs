namespace QuantumGrandChallenges.QuantumOptimization {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function NormalizeCoefficients(costs : Double[]) : Double[] {
        mutable squared = 0.0;
        for cost in costs {
            set squared += cost * cost;
        }
        if squared <= 1e-12 {
            return [0.0, size = Length(costs)];
        }
        let scale = 1.0 / Sqrt(squared);
        mutable normalized = [0.0, size = Length(costs)];
        for idx in 0 .. Length(costs) - 1 {
            set normalized w/= idx <- costs[idx] * scale;
        }
        return normalized;
    }

    function CumulativePenalties(weights : Double[]) : Double[] {
        mutable penalties = [0.0, size = Length(weights)];
        mutable running = 0.0;
        for idx in 0 .. Length(weights) - 1 {
            set running += weights[idx];
            set penalties w/= idx <- running;
        }
        return penalties;
    }

    operation PreviewQaoaLayer(costAngles : Double[], mixerAngles : Double[]) : Double {
        let normalized = NormalizeCoefficients(costAngles);
        mutable expectation = 0.0;
        for idx in 0 .. Length(normalized) - 1 {
            let cost = normalized[idx];
            let mixer = mixerAngles[MinI(idx, Length(mixerAngles) - 1)];
            set expectation += cost * Cos(mixer);
        }

        use ancilla = Qubit();
        H(ancilla);
        // Placeholder: a controlled phase separator would go here.
        Reset(ancilla);

        return expectation;
    }

    @EntryPoint()
    operation RunQuantumOptimizationPrototype() : Unit {
        Message("Quantum optimization scaffold – integrate full QAOA later.");
        let costAngles = [2.4, 1.8, 3.1, 2.0];
        let mixerAngles = [0.7, 0.5, 0.9];
        let expectation = PreviewQaoaLayer(costAngles, mixerAngles);
        Message($"Layer energy preview: {expectation}");

        let penalties = CumulativePenalties([1.0, 1.2, 1.4, 1.1]);
        Message($"Cumulative penalty schedule: {penalties}");
    }
}
