// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Canon.*;
import Std.Convert.*;
import Std.Math.*;
import Std.Measurement.*;

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
//
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
    Message($"VQE energy of the two-qubit toy ansatz Hamiltonian (not the Hubbard model): {demoEnergy}");
    let qpeEnergy = HubbardQPE(1.0, 4.0, 8, 8);
    Message($"QPE ground-state energy, Jordan-Wigner Hubbard model (t=1.0, U=4.0, 8 phase bits): {qpeEnergy}");
    Message($"Exact singlet energy: {SingletEigenvalue(1.0, 4.0)}");
    
    Message("");
    Message("Next steps for full VQE implementation:");
    Message("  - Measure Hamiltonian expectation values (XX, YY, ZZ Pauli terms)");
    Message("  - Integrate classical optimizer (COBYLA, SPSA) via Python");
    Message("  - Run Azure Quantum Resource Estimator for circuit resource analysis");
    Message("  - Scale to larger lattices with more sophisticated ansatze");
}


// ---------------------------------------------------------------------------
// Quantum phase estimation (QPE) of the problem Hamiltonian
//
// H = offset * I + sum_j coeffs[j] * paulis[j]. The identity part only shifts every
// energy, so it is added back classically. U = exp(-i (H - offset) tau) is built from
// symmetric (second-order) Trotter steps, with tau = pi / (2 * lambda) and lambda the
// sum of |coeffs|, so |(E - offset) tau| <= pi / 2 and the measured phase cannot wrap.
// tooling/test_qpe_kernels.py checks the sampled outcomes against exact diagonalization.
// ---------------------------------------------------------------------------

/// One symmetric Trotter step exp(-i (H - offset) dt). Exp(P, theta, qs) applies exp(i theta P).
operation ApplyTrotterStep(paulis : Pauli[][], coeffs : Double[], dt : Double, register : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(coeffs);
    for j in 0..n - 1 {
        Exp(paulis[j], -coeffs[j] * dt / 2.0, register);
    }
    for j in (n - 1)..-1..0 {
        Exp(paulis[j], -coeffs[j] * dt / 2.0, register);
    }
}

/// U^power for U = exp(-i (H - offset) tau), each U made of `steps` Trotter steps.
operation ApplyEvolutionPower(paulis : Pauli[][], coeffs : Double[], tau : Double, steps : Int, power : Int, register : Qubit[]) : Unit is Adj + Ctl {
    let dt = tau / IntAsDouble(steps);
    for _ in 1..power * steps {
        ApplyTrotterStep(paulis, coeffs, dt, register);
    }
}

function EvolutionTime(coeffs : Double[]) : Double {
    mutable lambda = 0.0;
    for c in coeffs {
        lambda += AbsD(c);
    }
    return PI() / (2.0 * lambda);
}

/// Energy for a phase-register value; ApplyQPE writes phase / 2pi as a little-endian integer.
function PhaseToEnergy(outcome : Int, nPhase : Int, tau : Double, offset : Double) : Double {
    mutable theta = 2.0 * PI() * IntAsDouble(outcome) / IntAsDouble(1 <<< nPhase);
    if theta > PI() {
        theta -= 2.0 * PI();
    }
    return offset - theta / tau;
}

/// The most frequent phase-register value.
function ModeOutcome(outcomes : Int[], nPhase : Int) : Int {
    mutable counts = [0, size = 1 <<< nPhase];
    for outcome in outcomes {
        counts[outcome] += 1;
    }
    mutable best = 0;
    for m in 1..Length(counts) - 1 {
        if counts[m] > counts[best] {
            best = m;
        }
    }
    return best;
}

/// X on every qubit whose bit is 1.
operation PrepareBasisState(bits : Int[], register : Qubit[]) : Unit {
    for i in 0..Length(bits) - 1 {
        if bits[i] == 1 {
            X(register[i]);
        }
    }
}

/// One QPE run from the state `prepare` makes; returns the phase-register value.
operation MeasureEnergyPhase(paulis : Pauli[][], coeffs : Double[], prepare : (Qubit[] => Unit), nSystem : Int, nPhase : Int, steps : Int) : Int {
    use phase = Qubit[nPhase];
    use sys = Qubit[nSystem];
    prepare(sys);
    ApplyQPE(ApplyEvolutionPower(paulis, coeffs, EvolutionTime(coeffs), steps, _, _), sys, phase);
    let outcome = MeasureInteger(phase);
    ResetAll(sys);
    return outcome;
}

/// Two-site Fermi-Hubbard model, Jordan-Wigner encoded on four qubits ordered
/// (site 1 up, site 2 up, site 1 down, site 2 down):
///   H = -t sum_s (c+_1s c_2s + h.c.) + U (n_1up n_1dn + n_2up n_2dn)
///     = -t/2 (X0X1 + Y0Y1 + X2X3 + Y2Y3) + U/4 (Z0Z2 + Z1Z3 - Z0 - Z1 - Z2 - Z3) + U/2.
/// At half filling its lowest energy is SingletEigenvalue(t, u) above.
function HubbardHamiltonian(t : Double, u : Double) : (Pauli[][], Double[], Double) {
    let paulis = [
        [PauliX, PauliX, PauliI, PauliI],
        [PauliY, PauliY, PauliI, PauliI],
        [PauliI, PauliI, PauliX, PauliX],
        [PauliI, PauliI, PauliY, PauliY],
        [PauliZ, PauliI, PauliZ, PauliI],
        [PauliI, PauliZ, PauliI, PauliZ],
        [PauliZ, PauliI, PauliI, PauliI],
        [PauliI, PauliZ, PauliI, PauliI],
        [PauliI, PauliI, PauliZ, PauliI],
        [PauliI, PauliI, PauliI, PauliZ]
    ];
    let coeffs = [-t / 2.0, -t / 2.0, -t / 2.0, -t / 2.0, u / 4.0, u / 4.0, -u / 4.0, -u / 4.0, -u / 4.0, -u / 4.0];
    return (paulis, coeffs, u / 2.0);
}

/// Heitler-London singlet (|1up 2dn> + |1dn 2up>) / sqrt(2): two electrons, total spin zero.
/// The Jordan-Wigner sign makes the spin singlet the + combination in this ordering.
/// Particle number and spin are conserved, so QPE stays in this sector; at U = 4t the
/// state overlaps the ground state with probability 0.85 and has no triplet component.
operation PrepareValenceBondSinglet(register : Qubit[]) : Unit {
    H(register[0]);
    CNOT(register[0], register[3]);
    X(register[1]);
    CNOT(register[0], register[1]);
    X(register[2]);
    CNOT(register[0], register[2]);
}

/// Trotter steps per U, chosen so the Trotter error in the ground-state energy is below
/// half the 10-bit phase resolution; tooling/test_qpe_kernels.py re-checks the bound.
function HubbardTrotterSteps() : Int {
    return 2;
}

/// One QPE run for the two-site Hubbard model; returns the phase-register value.
operation HubbardQPEOutcome(t : Double, u : Double, nPhase : Int) : Int {
    let (paulis, coeffs, _) = HubbardHamiltonian(t, u);
    return MeasureEnergyPhase(paulis, coeffs, PrepareValenceBondSinglet, 4, nPhase, HubbardTrotterSteps());
}

/// Ground-state energy by QPE: the most frequent energy over `shots` runs (one run for shots = 1).
operation HubbardQPE(t : Double, u : Double, nPhase : Int, shots : Int) : Double {
    let (_, coeffs, offset) = HubbardHamiltonian(t, u);
    mutable outcomes : Int[] = [];
    for _ in 1..(shots < 1 ? 1 | shots) {
        outcomes += [HubbardQPEOutcome(t, u, nPhase)];
    }
    return PhaseToEnergy(ModeOutcome(outcomes, nPhase), nPhase, EvolutionTime(coeffs), offset);
}
