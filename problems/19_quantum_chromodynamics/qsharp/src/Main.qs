// Main.qs  Migrated to modern QDK (qsharp.json project format)
//
// What this computes: Trotterized real-time evolution of a transverse-field Ising chain,
// H = beta * sum_i Z_i Z_{i+1} + h * sum_i X_i, from |0...0>, measuring the product of Z
// over all sites. It is a spin-chain stand-in for the lattice gauge dynamics this problem
// is about, not a gauge theory: there are no gauge fields and no Gauss's law, and the 1D
// transverse-field Ising chain maps to free fermions, so it is classically solvable at any
// size. The operation names are historical. tooling/test_ising_chain_kernel.py checks the
// sampled results against exact evolution of the same Trotter circuit.

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// One first-order Trotter step of the transverse-field Ising chain:
/// CNOT, Rz(2 beta dt), CNOT applies exp(-i beta dt Z_i Z_{i+1}) to each bond, and
/// Rx(2 h dt) applies exp(-i h dt X_i) to each site.
operation TrotterGaugeStep(beta : Double, h : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    // Nearest-neighbour ZZ couplings
    for i in 0 .. n - 2 {
        CNOT(qubits[i], qubits[i + 1]);
        Rz(2.0 * beta, qubits[i + 1]);
        CNOT(qubits[i], qubits[i + 1]);
    }
    // Transverse field
    for i in 0 .. n - 1 {
        Rx(2.0 * h, qubits[i]);
    }
}

/// Measures every qubit and returns the product of their Z eigenvalues, +1 or -1.
/// Earlier versions called this a Wilson loop; it is a Z-parity string.
operation MeasureZParity(qubits : Qubit[]) : Double {
    mutable parity = 1.0;
    for q in qubits {
        if (M(q) == One) {
            set parity = parity * (-1.0);
        }
    }
    return parity;
}

/// Evolves |0...0> under the chain Hamiltonian for unit time in `trotterSteps` steps and
/// returns the sample mean of the Z-parity over `shots` runs.
operation SimulateLatticeGauge(nSites : Int, beta : Double, h : Double, trotterSteps : Int, shots : Int) : Double {
    mutable paritySum = 0.0;
    for _ in 1 .. shots {
        use lattice = Qubit[nSites];

        for _ in 1 .. trotterSteps {
            TrotterGaugeStep(beta / IntAsDouble(trotterSteps), h / IntAsDouble(trotterSteps), lattice);
        }

        set paritySum += MeasureZParity(lattice);

        ResetAll(lattice);
    }
    return paritySum / IntAsDouble(shots);
}

@EntryPoint()
operation RunQCDSimulation() : Unit {
    Message("=== Transverse-field Ising chain: a stand-in for lattice gauge dynamics ===");
    Message("");
    let nSites = 4;
    let trotterSteps = 5;
    let shots = 128;

    // Sweep the ZZ coupling
    let betas = [0.5, 1.0, 2.0, 4.0, 6.0];
    let h = 0.3; // transverse field

    Message($"Chain: {nSites} sites, {trotterSteps} Trotter steps, h={h}, evolved for unit time from |0000>");
    Message("");
    for beta in betas {
        let parity = SimulateLatticeGauge(nSites, beta, h, trotterSteps, shots);
        Message($"  beta={beta}: <product of Z> = {parity}");
    }
    Message("");
    Message("A stronger ZZ coupling makes single spin flips off-resonant, so the state stays");
    Message("closer to |0000> and the parity closer to 1.");
    Message("");
    Message("This chain has no gauge fields and is classically solvable (it maps to free");
    Message("fermions). The case for quantum simulation rests on interacting gauge theories");
    Message("in more dimensions, which this kernel does not model.");
}
