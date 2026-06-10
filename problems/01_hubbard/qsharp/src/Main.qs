// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Convert.*;
import Std.Math.*;

function SingletEigenvalue(t : Double, u : Double) : Double {
    let discriminant = Sqrt(u * u + 16.0 * t * t);
    // Negative branch gives the singlet (ground) energy for half filling
    return 0.5 * (u - discriminant);
}

function UpperSingletEigenvalue(t : Double, u : Double) : Double {
    let discriminant = Sqrt(u * u + 16.0 * t * t);
    return 0.5 * (u + discriminant);
}

function TripletEigenvalue(u : Double) : Double {
    // Two-site Hubbard triplet state has no double occupation penalty
    return 0.0;
}

/// # Summary
/// Demonstrates VQE ansatz circuit for the two-site Hubbard model.
/// This hardware-efficient ansatz prepares parameterized quantum states
/// for variational ground state energy optimization.
///
/// # Input
/// ## theta0, theta1, theta2
/// Rotation angles for the variational ansatz
/// ## q0, q1
/// Qubits representing the two lattice sites
operation HubbardVQEAnsatz(theta0 : Double, theta1 : Double, theta2 : Double, q0 : Qubit, q1 : Qubit) : Unit is Adj + Ctl {
    // Initialize to |01⟩ state (half-filling: one electron per site)
    X(q0);
    
    // Single-qubit rotations
    Ry(theta0, q0);
    Ry(theta1, q1);
    
    // Entangling layer
    CNOT(q0, q1);
    
    // Additional rotation
    Rz(theta2, q1);
    
    // Second entangling gate
    CNOT(q0, q1);
}

operation ResetAll(qubits : Qubit[]) : Unit {
    for qubit in qubits {
        if (M(qubit) == One) {
            X(qubit);
        }
    }
}

operation MeasurePauliOnce(paulis : Pauli[], register : Qubit[]) : Result {
    mutable measurement = Zero;
    within {
        for idx in 0 .. Length(paulis) - 1 {
            if (paulis[idx] == PauliX) {
                H(register[idx]);
            } elif (paulis[idx] == PauliY) {
                Adjoint S(register[idx]);
                H(register[idx]);
            }
        }
    } apply {
        set measurement = Measure(paulis, register);
    }

    return measurement;
}

function MaxInt(a : Int, b : Int) : Int {
    if (a > b) {
        return a;
    }
    return b;
}

operation MeasurePauliExpectation(theta0 : Double, theta1 : Double, theta2 : Double, paulis : Pauli[], shots : Int) : Double {
    let numShots = MaxInt(1, shots);
    mutable sampleSum = 0.0;

    for _ in 1 .. numShots {
        use register = Qubit[2];
        HubbardVQEAnsatz(theta0, theta1, theta2, register[0], register[1]);

        let measurement = MeasurePauliOnce(paulis, register);
        if (measurement == Zero) {
            set sampleSum += 1.0;
        } else {
            set sampleSum -= 1.0;
        }

        ResetAll(register);
    }

    return sampleSum / IntAsDouble(numShots);
}

operation EstimateHubbardEnergy(t : Double, u : Double, theta0 : Double, theta1 : Double, theta2 : Double, shots : Int) : Double {
    let xxExpectation = MeasurePauliExpectation(theta0, theta1, theta2, [PauliX, PauliX], shots);
    let yyExpectation = MeasurePauliExpectation(theta0, theta1, theta2, [PauliY, PauliY], shots);
    let ziExpectation = MeasurePauliExpectation(theta0, theta1, theta2, [PauliZ, PauliI], shots);
    let izExpectation = MeasurePauliExpectation(theta0, theta1, theta2, [PauliI, PauliZ], shots);

    let hoppingContribution = -t * (xxExpectation + yyExpectation);
    let interactionContribution = 0.5 * u * (ziExpectation + izExpectation);

    return hoppingContribution + interactionContribution;
}

@EntryPoint()
operation RunTwoSiteHubbardAnalysis() : Unit {
    Message("Two-site Hubbard model at half filling (one electron per site)");
    Message("-----------------------------------------------------------");
    Message("");

    let hoppingStrengths = [0.5, 1.0];
    let interactionStrengths = [0.0, 2.0, 4.0, 8.0];

    // Analytical baseline
    Message("ANALYTICAL RESULTS:");
    for t in hoppingStrengths {
        for u in interactionStrengths {
            let gs = SingletEigenvalue(t, u);
            let excited = UpperSingletEigenvalue(t, u);
            let triplet = TripletEigenvalue(u);
            let chargeGap = excited - gs;
            let spinGap = triplet - gs;

            Message($"t = {t}, U = {u}");
            Message($"  Ground state energy (singlet) : {gs}");
            Message($"  Upper singlet energy         : {excited}");
            Message($"  Triplet energy               : {triplet}");
            Message($"  Charge gap Δc                : {chargeGap}");
            Message($"  Spin gap Δs                  : {spinGap}");
        }
    }

    Message("");
    Message("VQE ANSATZ DEMONSTRATION:");
    Message("Preparing variational quantum state with demo parameters");
    
    use q0 = Qubit();
    use q1 = Qubit();
    
    // Demo VQE ansatz with example parameters
    let demoTheta0 = PI() / 4.0;  // pi/4
    let demoTheta1 = PI() / 2.0;  // pi/2
    let demoTheta2 = PI() / 8.0;  // pi/8
    
    HubbardVQEAnsatz(demoTheta0, demoTheta1, demoTheta2, q0, q1);
    Message($"Prepared VQE ansatz with parameters ({demoTheta0}, {demoTheta1}, {demoTheta2})");
    
    Reset(q0);
    Reset(q1);

    let demoEnergy = EstimateHubbardEnergy(1.0, 4.0, demoTheta0, demoTheta1, demoTheta2, 256);
    Message($"Estimated Hubbard energy (t=1.0, U=4.0, shots=256): {demoEnergy}");
    
    Message("");
    Message("Next steps for full VQE implementation:");
    Message("  - Measure Hamiltonian expectation values (XX, YY, ZZ Pauli terms)");
    Message("  - Integrate classical optimizer (COBYLA, SPSA) via Python");
    Message("  - Run Azure Quantum Resource Estimator for circuit resource analysis");
    Message("  - Scale to larger lattices with more sophisticated ansatze");
}


/// QPE for 2-site Hubbard model ground state energy
/// Uses Trotterized Hamiltonian simulation as the unitary
/// Phase register encodes eigenvalue of H = -t(XX+YY) + U/2(ZI+IZ)
operation HubbardQPE(t : Double, u : Double, nPhase : Int, shots : Int) : Double {
    mutable phaseSum = 0.0;
    let nShots = shots < 1 ? 1 | shots;
    for _ in 1..nShots {
        use phase = Qubit[nPhase];
        use sys = Qubit[2];
        // Initial state: half-filling |01>
        X(sys[0]);
        // Hadamard on phase register
        for p in phase { H(p); }
        // Controlled Trotter steps: U^(2^k) for each phase qubit k
        for k in 0..nPhase-1 {
            let power = 1 <<< k;
            for _ in 1..power {
                // Hopping: exp(-i*t*(XX+YY))
                Controlled CNOT([phase[k]], (sys[0], sys[1]));
                Controlled Rz([phase[k]], (2.0 * t, sys[1]));
                Controlled CNOT([phase[k]], (sys[0], sys[1]));
                // Interaction: exp(-i*U/2*(ZI+IZ))
                Controlled Rz([phase[k]], (u / 2.0, sys[0]));
                Controlled Rz([phase[k]], (u / 2.0, sys[1]));
            }
        }
        // Inverse QFT
        for i in 0..nPhase/2-1 { SWAP(phase[i], phase[nPhase-1-i]); }
        for i in 0..nPhase-1 {
            for j in 0..i-1 {
                Controlled R1([phase[j]], (-Std.Math.PI() / IntAsDouble(1 <<< (i - j)), phase[i]));
            }
            H(phase[i]);
        }
        // Measure phase
        mutable phaseVal = 0.0;
        for k in 0..nPhase-1 {
            if M(phase[k]) == One { set phaseVal += 1.0 / IntAsDouble(1 <<< (k + 1)); }
        }
        set phaseSum += phaseVal;
        ResetAll(phase + sys);
    }
    return phaseSum / IntAsDouble(nShots);
}
