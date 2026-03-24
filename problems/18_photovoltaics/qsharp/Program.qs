namespace QuantumGrandChallenges.Photovoltaics {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    /// Discrete-time quantum walk for exciton transport on a 4-site chain.
    /// Coin qubit controls direction, position register tracks site.
    operation QuantumWalkStep(coin : Qubit, position : Qubit[], coupling : Double) : Unit is Adj + Ctl {
        // Coin operation (biased Hadamard based on coupling strength)
        Ry(2.0 * coupling, coin);

        // Conditional shift: if coin=|0>, shift left; if coin=|1>, shift right
        within { X(coin); }
        apply {
            for i in 0 .. Length(position) - 2 {
                Controlled SWAP([coin], (position[i], position[i + 1]));
            }
        }
        for i in 0 .. Length(position) - 2 {
            Controlled SWAP([coin], (position[Length(position) - 2 - i], position[Length(position) - 1 - i]));
        }
    }

    /// Run exciton quantum walk and measure final position distribution.
    operation RunExcitonWalk(steps : Int, coupling : Double, shots : Int) : Int[] {
        let nSites = 2; // 2 position qubits = 4 sites
        mutable counts = [0, size = 1 <<< nSites];

        for _ in 1 .. shots {
            use coin = Qubit();
            use position = Qubit[nSites];

            // Initialize exciton at site 1 (|01>)
            X(position[1]);

            // Quantum walk steps
            for _ in 1 .. steps {
                QuantumWalkStep(coin, position, coupling);
            }

            // Measure position
            mutable site = 0;
            for i in 0 .. nSites - 1 {
                if (M(position[i]) == One) {
                    set site += 1 <<< (nSites - 1 - i);
                }
            }
            set counts w/= site <- counts[site] + 1;

            Reset(coin);
            ResetAll(position);
        }
        return counts;
    }

    @EntryPoint()
    operation RunPhotovoltaics() : Unit {
        Message("=== Photovoltaics: Quantum Walk Exciton Transport ===");
        Message("");
        let couplings = [0.3, 0.6, 0.9];
        let steps = 4;
        let shots = 128;

        for coupling in couplings {
            Message($"--- Coupling strength: {coupling} ---");
            let counts = RunExcitonWalk(steps, coupling, shots);
            for site in 0 .. Length(counts) - 1 {
                let prob = IntAsDouble(counts[site]) / IntAsDouble(shots) * 100.0;
                Message($"  Site {site}: {counts[site]}/{shots} ({prob}%)");
            }
            Message("");
        }

        Message("Quantum walks model coherent exciton transport in organic photovoltaics,");
        Message("capturing interference effects that classical random walks miss.");
    }
}
