// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// HHL-style state preparation for RHS vector |b>.
operation PrepareRHS(b0 : Double, b1 : Double, qubit : Qubit) : Unit is Adj + Ctl {
    let angle = 2.0 * ArcTan2(b1, b0);
    Ry(angle, qubit);
}

/// Simple Hamiltonian simulation step via Trotter decomposition.
operation TrotterStep(t : Double, system : Qubit) : Unit is Adj + Ctl {
    Rz(2.0 * t, system);
    Rx(t, system);
}

/// Phase estimation for eigenvalue extraction.
operation PhaseEstimation(precision : Qubit[], system : Qubit, dt : Double) : Unit {
    for k in 0 .. Length(precision) - 1 {
        H(precision[k]);
    }
    for k in 0 .. Length(precision) - 1 {
        let power = 1 <<< k;
        for _ in 1 .. power {
            Controlled TrotterStep([precision[k]], (dt, system));
        }
    }
    // Inverse QFT on precision register
    let n = Length(precision);
    for i in 0 .. n / 2 - 1 { SWAP(precision[i], precision[n - 1 - i]); }
    for i in 0 .. n - 1 {
        for j in i + 1 .. n - 1 {
            let angle = -2.0 * PI() / IntAsDouble(1 <<< (j - i));
            Controlled R1([precision[j]], (angle, precision[i]));
        }
        H(precision[i]);
    }
}

/// Run a simplified HHL iteration for a 2x2 climate diffusion system.
operation RunHHLClimate(precisionBits : Int, shots : Int) : Double {
    mutable successCount = 0;
    for _ in 1 .. shots {
        use precision = Qubit[precisionBits];
        use system = Qubit();
        use ancilla = Qubit();

        // Load |b> (temperature forcing vector)
        PrepareRHS(0.8, 0.6, system);

        // Phase estimation
        PhaseEstimation(precision, system, 0.5);

        // Controlled rotation for eigenvalue inversion
        for k in 0 .. precisionBits - 1 {
            Controlled Ry([precision[k]], (0.3 / IntAsDouble(k + 1), ancilla));
        }

        if (M(ancilla) == One) { set successCount += 1; }

        ResetAll(precision);
        Reset(system);
        Reset(ancilla);
    }
    return IntAsDouble(successCount) / IntAsDouble(shots);
}

@EntryPoint()
operation RunClimateModeling() : Unit {
    Message("=== Climate Modeling: HHL for Diffusion PDE ===");
    Message("");
    Message("Solving 2x2 thermal diffusion system via HHL algorithm.");
    Message("");
    let precisionBits = 3;
    let shots = 128;
    let successRate = RunHHLClimate(precisionBits, shots);
    Message($"HHL success rate ({shots} shots, {precisionBits} precision bits): {successRate}");
    Message($"Successful inversions: {successRate * IntAsDouble(shots)}");
    Message("");
    Message("HHL provides exponential speedup for sparse linear systems");
    Message("enabling large-scale climate PDE simulations on quantum hardware.");
}
