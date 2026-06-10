// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// VQE ansatz for 2-qubit tight-binding model of a material unit cell.
/// Models valence/conduction band orbitals.
operation BandGapAnsatz(theta0 : Double, theta1 : Double, theta2 : Double, q0 : Qubit, q1 : Qubit) : Unit {
    // Reference state: valence band filled |10⟩
    X(q0);

    // Parameterized rotations (orbital mixing)
    Ry(theta0, q0);
    Ry(theta1, q1);

    // Entangling layer (inter-orbital coupling)
    CNOT(q0, q1);
    Rz(theta2, q1);
    CNOT(q0, q1);
}

/// Measure Pauli term expectation.
operation MeasurePauli(theta0 : Double, theta1 : Double, theta2 : Double, paulis : Pauli[], shots : Int) : Double {
    mutable sum = 0.0;
    for _ in 1 .. shots {
        use register = Qubit[2];
        BandGapAnsatz(theta0, theta1, theta2, register[0], register[1]);
        let result = Measure(paulis, register);
        if (result == Zero) { set sum += 1.0; } else { set sum -= 1.0; }
        ResetAll(register);
    }
    return sum / IntAsDouble(shots);
}

/// Estimate ground state energy via tight-binding Hamiltonian.
/// H = ε₁Z₁ + ε₂Z₂ + t(X₁X₂ + Y₁Y₂) + V·Z₁Z₂
operation EstimateBandEnergy(theta0 : Double, theta1 : Double, theta2 : Double, onsite1 : Double, onsite2 : Double, hopping : Double, interaction : Double, shots : Int) : Double {
    let z0 = MeasurePauli(theta0, theta1, theta2, [PauliZ, PauliI], shots);
    let z1 = MeasurePauli(theta0, theta1, theta2, [PauliI, PauliZ], shots);
    let zz = MeasurePauli(theta0, theta1, theta2, [PauliZ, PauliZ], shots);
    let xx = MeasurePauli(theta0, theta1, theta2, [PauliX, PauliX], shots);

    return onsite1 * z0 + onsite2 * z1 + hopping * xx + interaction * zz;
}

/// Estimate band gap = E(conduction) - E(valence) by running VQE twice.
operation EstimateBandGap(onsite1 : Double, onsite2 : Double, hopping : Double, interaction : Double, shots : Int) : (Double, Double, Double) {
    let angles = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8];

    // Find ground state (valence band)
    mutable bestValence = 100.0;
    mutable bestT0v = 0.0;
    mutable bestT1v = 0.0;
    for t0 in angles {
        for t1 in angles {
            let e = EstimateBandEnergy(t0, t1, 0.0, onsite1, onsite2, hopping, interaction, shots);
            if (e < bestValence) {
                set bestValence = e;
                set bestT0v = t0;
                set bestT1v = t1;
            }
        }
    }

    // Approximate conduction band: use orthogonal ansatz region
    mutable bestConduction = 100.0;
    for t0 in angles {
        for t1 in angles {
            let e = EstimateBandEnergy(t0, t1, PI(), onsite1, onsite2, hopping, interaction, shots);
            if (e > bestValence and e < bestConduction) {
                set bestConduction = e;
            }
        }
    }

    let gap = bestConduction - bestValence;
    return (bestValence, bestConduction, gap);
}

@EntryPoint()
operation RunMaterialsDiscovery() : Unit {
    Message("=== Materials Discovery: VQE Band Gap Estimation ===");
    Message("");

    // Tight-binding parameters for a simple 2-orbital model
    let materials = [
        ("Silicon-like", -1.0, -0.5, 0.3, 0.1),
        ("Wide-gap",     -1.5, -0.3, 0.5, 0.15),
        ("Narrow-gap",   -0.8, -0.7, 0.15, 0.05)
    ];
    let shots = 48;

    for (name, onsite1, onsite2, hopping, interaction) in materials {
        Message($"--- {name} material ---");
        Message($"  Parameters: e1={onsite1}, e2={onsite2}, t={hopping}, V={interaction}");

        let (valence, conduction, gap) = EstimateBandGap(onsite1, onsite2, hopping, interaction, shots);
        Message($"  Valence band energy:    {valence} eV");
        Message($"  Conduction band energy: {conduction} eV");
        Message($"  Band gap estimate:      {gap} eV");
        Message("");
    }

    Message("=== Quantum Advantage ===");
    Message("VQE enables accurate band structure calculations for complex materials");
    Message("where classical DFT fails (strongly correlated systems, defect states).");
    Message("Key application: screening battery cathode and photovoltaic materials.");
}


/// QPE for band gap estimation via tight-binding Hamiltonian
/// Simulates H = on-site + hopping terms
operation BandGapQPE(onSite : Double, hopping : Double, nPhase : Int, shots : Int) : Double {
    mutable phaseSum = 0.0;
    let nShots = shots < 1 ? 1 | shots;
    for _ in 1..nShots {
        use phase = Qubit[nPhase];
        use sys = Qubit[2];
        X(sys[0]);
        for p in phase { H(p); }
        for k in 0..nPhase-1 {
            let power = 1 <<< k;
            for _ in 1..power {
                Controlled Rz([phase[k]], (onSite, sys[0]));
                Controlled Rz([phase[k]], (onSite, sys[1]));
                Controlled CNOT([phase[k]], (sys[0], sys[1]));
                Controlled Rz([phase[k]], (2.0 * hopping, sys[1]));
                Controlled CNOT([phase[k]], (sys[0], sys[1]));
            }
        }
        for i in 0..nPhase/2-1 { SWAP(phase[i], phase[nPhase-1-i]); }
        for i in 0..nPhase-1 {
            for j in 0..i-1 {
                Controlled R1([phase[j]], (-Std.Math.PI() / IntAsDouble(1 <<< (i - j)), phase[i]));
            }
            H(phase[i]);
        }
        mutable phaseVal = 0.0;
        for k in 0..nPhase-1 {
            if M(phase[k]) == One { set phaseVal += 1.0 / IntAsDouble(1 <<< (k + 1)); }
        }
        set phaseSum += phaseVal;
        ResetAll(phase + sys);
    }
    return phaseSum / IntAsDouble(nShots);
}
