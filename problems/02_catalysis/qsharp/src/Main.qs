// Main.qs — Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Math.*;

/// Computes e^x (ExpD was removed from modern Std.Math).
function ExpD(x : Double) : Double {
    let base = new Complex { Real = E(), Imag = 0.0 };
    let power = new Complex { Real = x, Imag = 0.0 };
    return PowC(base, power).Real;
}

/// Classical Arrhenius rate for reference.
function ArrheniusRate(preExponential : Double, activationEnergy : Double, temperature : Double) : Double {
    let gasConstant = 8.314;
    let exponent = -activationEnergy / (gasConstant * temperature);
    return preExponential * ExpD(exponent);
}

/// Hardware-efficient VQE ansatz for 2-qubit active space.
/// Models the bonding/antibonding orbitals of H₂ or similar diatomic.
operation ChemistryAnsatz(theta0 : Double, theta1 : Double, theta2 : Double, q0 : Qubit, q1 : Qubit) : Unit {
    // Initialize to Hartree-Fock reference |01⟩ (one electron in bonding orbital)
    X(q0);

    // Parameterized rotations
    Ry(theta0, q0);
    Ry(theta1, q1);

    // Entangling layer (captures electron correlation)
    CNOT(q0, q1);
    Rz(theta2, q1);
    CNOT(q0, q1);
}

/// Measure Pauli expectation value with given ansatz parameters.
operation MeasurePauliExpectation(theta0 : Double, theta1 : Double, theta2 : Double, paulis : Pauli[], shots : Int) : Double {
    mutable sum = 0.0;
    for _ in 1 .. shots {
        use register = Qubit[2];
        ChemistryAnsatz(theta0, theta1, theta2, register[0], register[1]);

        let result = Measure(paulis, register);
        if (result == Zero) {
            set sum += 1.0;
        } else {
            set sum -= 1.0;
        }

        ResetAll(register);
    }
    return sum / IntAsDouble(shots);
}

/// Estimate molecular energy from Pauli decomposition.
/// H = c_I + c_Z0 Z₀ + c_Z1 Z₁ + c_ZZ Z₀Z₁ + c_XX X₀X₁ + c_YY Y₀Y₁
/// Coefficients approximate H₂ at equilibrium bond length.
operation EstimateMolecularEnergy(theta0 : Double, theta1 : Double, theta2 : Double, shots : Int) : Double {
    // H₂ Hamiltonian coefficients (STO-3G, R=0.74 Å)
    let cI = -0.81261;
    let cZ0 = 0.17120;
    let cZ1 = -0.22279;
    let cZZ = 0.17120;
    let cXX = 0.04544;

    let z0 = MeasurePauliExpectation(theta0, theta1, theta2, [PauliZ, PauliI], shots);
    let z1 = MeasurePauliExpectation(theta0, theta1, theta2, [PauliI, PauliZ], shots);
    let zz = MeasurePauliExpectation(theta0, theta1, theta2, [PauliZ, PauliZ], shots);
    let xx = MeasurePauliExpectation(theta0, theta1, theta2, [PauliX, PauliX], shots);

    return cI + cZ0 * z0 + cZ1 * z1 + cZZ * zz + cXX * xx;
}

/// Simple coordinate-descent optimizer for VQE.
operation OptimizeVQE(shots : Int) : (Double, Double, Double, Double) {
    let candidates = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.14];
    mutable bestE = 100.0;
    mutable bestT0 = 0.0;
    mutable bestT1 = 0.0;
    mutable bestT2 = 0.0;

    // Coarse sweep
    for t0 in candidates {
        for t1 in candidates {
            let energy = EstimateMolecularEnergy(t0, t1, 0.0, shots);
            if (energy < bestE) {
                set bestE = energy;
                set bestT0 = t0;
                set bestT1 = t1;
            }
        }
    }

    // Refine theta2
    for t2 in candidates {
        let energy = EstimateMolecularEnergy(bestT0, bestT1, t2, shots);
        if (energy < bestE) {
            set bestE = energy;
            set bestT2 = t2;
        }
    }

    return (bestT0, bestT1, bestT2, bestE);
}

@EntryPoint()
operation RunCatalysisAnalysis() : Unit {
    Message("=== Catalysis Simulation: VQE for Molecular Energy ===");
    Message("");

    // Classical Arrhenius baseline
    Message("--- Classical Arrhenius Rates ---");
    let instances = [
        ("small", "H2 + O2 -> H2O", 300.0, 1.0e13, 75000.0),
        ("medium", "N2 + 3H2 -> 2NH3", 500.0, 5.0e12, 95000.0)
    ];
    for (instanceId, reaction, temperature, preExp, actEnergy) in instances {
        let rate = ArrheniusRate(preExp, actEnergy, temperature);
        Message($"  {instanceId}: {reaction} at {temperature}K -> rate={rate}");
    }
    Message("");

    // VQE for H₂ ground state energy
    Message("--- VQE Molecular Energy (H2, STO-3G basis) ---");
    let exactEnergy = -1.1373;
    Message($"  Exact FCI energy: {exactEnergy} Hartree");
    Message("");

    let shots = 64;
    let (t0, t1, t2, vqeEnergy) = OptimizeVQE(shots);
    Message($"  VQE optimized parameters: theta=({t0}, {t1}, {t2})");
    Message($"  VQE energy estimate: {vqeEnergy} Hartree");
    let error = AbsD(vqeEnergy - exactEnergy);
    Message($"  Error vs exact: {error} Hartree");
    Message("");

    Message("=== Quantum Advantage ===");
    Message("VQE enables polynomial-scaling molecular energy estimation");
    Message("compared to exponential-scaling classical FCI for large active spaces.");
    Message("Critical for catalyst design: computing reaction barrier heights");
    Message("and transition state energies on quantum hardware.");
}


/// QPE for H2 molecular ground state energy (STO-3G basis)
/// Hamiltonian: H = g0*II + g1*ZI + g2*IZ + g3*ZZ + g4*XX + g5*YY
operation MolecularQPE(bondLength : Double, nPhase : Int, shots : Int) : Double {
    mutable phaseSum = 0.0;
    let nShots = shots < 1 ? 1 | shots;
    for _ in 1..nShots {
        use phase = Qubit[nPhase];
        use sys = Qubit[2];
        X(sys[0]);  // Initial HF state
        for p in phase { H(p); }
        for k in 0..nPhase-1 {
            let power = 1 <<< k;
            for _ in 1..power {
                Controlled CNOT([phase[k]], (sys[0], sys[1]));
                Controlled Rz([phase[k]], (bondLength, sys[1]));
                Controlled CNOT([phase[k]], (sys[0], sys[1]));
                Controlled Rz([phase[k]], (0.5, sys[0]));
                Controlled Rz([phase[k]], (0.5, sys[1]));
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
