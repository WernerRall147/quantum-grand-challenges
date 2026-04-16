// Main.qs — Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// VQE ansatz for 2-nucleon system (proton-neutron).
operation NuclearAnsatz(theta0 : Double, theta1 : Double, theta2 : Double, q0 : Qubit, q1 : Qubit) : Unit {
    X(q0);
    Ry(theta0, q0);
    Ry(theta1, q1);
    CNOT(q0, q1);
    Rz(theta2, q1);
    CNOT(q0, q1);
}

operation MeasureNuclearPauli(theta0 : Double, theta1 : Double, theta2 : Double, paulis : Pauli[], shots : Int) : Double {
    mutable sum = 0.0;
    for _ in 1 .. shots {
        use register = Qubit[2];
        NuclearAnsatz(theta0, theta1, theta2, register[0], register[1]);
        let result = Measure(paulis, register);
        if (result == Zero) { set sum += 1.0; } else { set sum -= 1.0; }
        ResetAll(register);
    }
    return sum / IntAsDouble(shots);
}

/// Estimate deuteron binding energy from EFT Hamiltonian.
/// H = c0*I + c1*Z0 + c2*Z1 + c3*Z0Z1 + c4*X0X1
operation EstimateNuclearEnergy(theta0 : Double, theta1 : Double, theta2 : Double, shots : Int) : Double {
    let c0 = -1.25;
    let c1 = 0.35;
    let c2 = -0.28;
    let c3 = 0.22;
    let c4 = 0.08;
    let z0 = MeasureNuclearPauli(theta0, theta1, theta2, [PauliZ, PauliI], shots);
    let z1 = MeasureNuclearPauli(theta0, theta1, theta2, [PauliI, PauliZ], shots);
    let zz = MeasureNuclearPauli(theta0, theta1, theta2, [PauliZ, PauliZ], shots);
    let xx = MeasureNuclearPauli(theta0, theta1, theta2, [PauliX, PauliX], shots);
    return c0 + c1 * z0 + c2 * z1 + c3 * zz + c4 * xx;
}

@EntryPoint()
operation RunNuclearPhysics() : Unit {
    Message("=== Nuclear Physics: VQE Deuteron Binding Energy ===");
    Message("");
    let exactEnergy = -2.22;
    Message($"Experimental deuteron binding: {exactEnergy} MeV");
    let angles = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8];
    let shots = 64;
    mutable bestE = 100.0;
    mutable bestT0 = 0.0;
    mutable bestT1 = 0.0;
    for t0 in angles {
        for t1 in angles {
            let e = EstimateNuclearEnergy(t0, t1, 0.0, shots);
            if (e < bestE) { set bestE = e; set bestT0 = t0; set bestT1 = t1; }
        }
    }
    Message($"VQE nuclear energy: {bestE} MeV");
    Message($"Error: {AbsD(bestE - exactEnergy)} MeV");
    Message("");
    Message("VQE enables ab initio nuclear structure calculations");
    Message("beyond the reach of classical many-body methods.");
}


/// QPE for deuteron binding energy via EFT Hamiltonian
/// H = kinetic + nuclear potential (one-pion exchange)
operation NuclearQPE(coupling : Double, nPhase : Int, shots : Int) : Double {
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
                Controlled CNOT([phase[k]], (sys[0], sys[1]));
                Controlled Rz([phase[k]], (2.0 * coupling, sys[1]));
                Controlled CNOT([phase[k]], (sys[0], sys[1]));
                Controlled Rz([phase[k]], (coupling, sys[0]));
                Controlled Rz([phase[k]], (coupling, sys[1]));
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
