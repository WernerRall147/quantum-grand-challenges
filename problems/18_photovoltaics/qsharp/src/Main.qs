// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// Moves the walker one site round the ring. The register is big-endian: the site is
/// 2 * position[0] + position[1] for two qubits, matching the measurement below.
operation IncrementSite(position : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(position);
    // Each bit flips when every less significant bit is 1, most significant first so
    // that each sees the lower bits before they change.
    for i in 0 .. n - 2 {
        Controlled X(position[i + 1 ...], position[i]);
    }
    X(position[n - 1]);
}

/// Discrete-time coined quantum walk for exciton transport on a 4-site ring.
/// The coin qubit sets the direction of each step; the position register holds the site.
operation QuantumWalkStep(coin : Qubit, position : Qubit[], coupling : Double) : Unit is Adj + Ctl {
    // Coin operation (biased Hadamard based on coupling strength)
    Ry(2.0 * coupling, coin);

    // Conditional shift: coin |1> steps right, coin |0> steps left. The previous version
    // swapped the two position qubits in both branches, so the walker moved the same way
    // whatever the coin said and every shot ended on the same site.
    Controlled IncrementSite([coin], position);
    within { X(coin); }
    apply { Controlled Adjoint IncrementSite([coin], position); }
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
