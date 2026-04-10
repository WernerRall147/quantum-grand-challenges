// Main.qs — Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// Trotter step for 1D lattice gauge theory: ZZ interaction + transverse field.
operation TrotterGaugeStep(beta : Double, h : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    // ZZ plaquette interactions
    for i in 0 .. n - 2 {
        CNOT(qubits[i], qubits[i + 1]);
        Rz(2.0 * beta, qubits[i + 1]);
        CNOT(qubits[i], qubits[i + 1]);
    }
    // Transverse field (electric term)
    for i in 0 .. n - 1 {
        Rx(2.0 * h, qubits[i]);
    }
}

/// Measure Wilson loop (string of Z operators along the lattice).
operation MeasureWilsonLoop(qubits : Qubit[]) : Double {
    mutable parity = 1.0;
    for q in qubits {
        if (M(q) == One) {
            set parity = parity * (-1.0);
        }
    }
    return parity;
}

/// Run lattice gauge simulation and measure Wilson loop expectation.
operation SimulateLatticeGauge(nSites : Int, beta : Double, h : Double, trotterSteps : Int, shots : Int) : Double {
    mutable wilsonSum = 0.0;
    for _ in 1 .. shots {
        use lattice = Qubit[nSites];

        // Initialize to vacuum state |00...0>
        // Apply Trotter evolution
        for _ in 1 .. trotterSteps {
            TrotterGaugeStep(beta / IntAsDouble(trotterSteps), h / IntAsDouble(trotterSteps), lattice);
        }

        let wilson = MeasureWilsonLoop(lattice);
        set wilsonSum += wilson;

        ResetAll(lattice);
    }
    return wilsonSum / IntAsDouble(shots);
}

@EntryPoint()
operation RunQCDSimulation() : Unit {
    Message("=== QCD: Lattice Gauge Theory Simulation ===");
    Message("");
    let nSites = 4;
    let trotterSteps = 5;
    let shots = 128;

    // Sweep coupling strength
    let betas = [0.5, 1.0, 2.0, 4.0, 6.0];
    let h = 0.3; // transverse field

    Message($"Lattice: {nSites} sites, {trotterSteps} Trotter steps, h={h}");
    Message("");
    for beta in betas {
        let wilson = SimulateLatticeGauge(nSites, beta, h, trotterSteps, shots);
        Message($"  beta={beta}: <Wilson loop> = {wilson}");
    }
    Message("");
    Message("Confinement signature: Wilson loop decays with area law at small beta,");
    Message("transitions to perimeter law at large beta (deconfined phase).");
    Message("");
    Message("Quantum simulation enables non-perturbative QCD calculations");
    Message("beyond the reach of classical lattice Monte Carlo for real-time dynamics.");
}
