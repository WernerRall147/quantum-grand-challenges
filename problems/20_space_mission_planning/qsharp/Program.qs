namespace QuantumGrandChallenges.SpaceMission {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function NormalizeWeights(weights : Double[]) : Double[] {
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

    function AnnealingSchedule(steps : Int, depth : Double) : Double[] {
        if steps <= 1 {
            return [depth];
        }
        let count = MaxI(steps, 1);
        mutable values = [0.0, size = count];
        for idx in 0 .. count - 1 {
            let fraction = IntAsDouble(idx) / IntAsDouble(count - 1);
            let eased = fraction * fraction * (3.0 - 2.0 * fraction);
            set values w/= idx <- eased * depth;
        }
        return values;
    }

    function BudgetPreview(schedule : Double[], penalty : Double) : Double {
        if Length(schedule) == 0 {
            return penalty;
        }
        mutable accumulator = 0.0;
        for value in schedule {
            set accumulator += value;
        }
        let average = accumulator / IntAsDouble(Length(schedule));
        return average + penalty;
    }

    @EntryPoint()
    operation RunMissionPrototype() : Unit {
        Message("Space mission planning scaffold - integrate quantum search encoding next.");
        let weights = NormalizeWeights([0.5, 0.3, 0.2]);
        let schedule = AnnealingSchedule(8, 1.0);
        let preview = BudgetPreview(schedule, 0.15);
        Message($"Normalized weights: {weights}");
        Message($"Budget preview: {preview}");
        use ancilla = Qubit();
        H(ancilla);
        Reset(ancilla);
    }
}
