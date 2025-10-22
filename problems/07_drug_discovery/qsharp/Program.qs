namespace QuantumGrandChallenges.DrugDiscovery {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function NormalizeWeights(weights : Double[]) : Double[] {
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

    @EntryPoint()
    operation RunDrugDiscoveryPrototype() : Unit {
        Message("Quantum drug discovery workflow placeholder – integrate VQE/chemistry later.");
        let rawWeights = [1.2, 0.9, 0.7, 0.4];
        let normalized = NormalizeWeights(rawWeights);
        Message($"Previewing {Length(normalized)} fragment weights; first component = {normalized[0]}");

        use ancilla = Qubit();
        H(ancilla);
        Reset(ancilla);

        mutable total = 0.0;
        for value in normalized {
            set total += value;
        }
        Message($"Sum of normalized weights: {total}");
    }
}
