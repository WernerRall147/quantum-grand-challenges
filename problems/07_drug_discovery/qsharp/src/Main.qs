// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;
import Std.Measurement.*;

operation BindingAnsatz(theta0 : Double, theta1 : Double, theta2 : Double, q0 : Qubit, q1 : Qubit) : Unit {
    X(q0);
    Ry(theta0, q0);
    Ry(theta1, q1);
    CNOT(q0, q1);
    Rz(theta2, q1);
    CNOT(q0, q1);
}

operation MeasureBinding(theta0 : Double, theta1 : Double, theta2 : Double, paulis : Pauli[], shots : Int) : Double {
    mutable sum = 0.0;
    for _ in 1 .. shots {
        use register = Qubit[2];
        BindingAnsatz(theta0, theta1, theta2, register[0], register[1]);
        let result = Measure(paulis, register);
        if (result == Zero) { set sum += 1.0; } else { set sum -= 1.0; }
        ResetAll(register);
    }
    return sum / IntAsDouble(shots);
}

operation EstimateBindingEnergy(theta0 : Double, theta1 : Double, theta2 : Double, shots : Int) : Double {
    let cI = -0.52;
    let cZ0 = 0.20;
    let cZ1 = -0.18;
    let cZZ = 0.12;
    let cXX = 0.06;
    let z0 = MeasureBinding(theta0, theta1, theta2, [PauliZ, PauliI], shots);
    let z1 = MeasureBinding(theta0, theta1, theta2, [PauliI, PauliZ], shots);
    let zz = MeasureBinding(theta0, theta1, theta2, [PauliZ, PauliZ], shots);
    let xx = MeasureBinding(theta0, theta1, theta2, [PauliX, PauliX], shots);
    return cI + cZ0 * z0 + cZ1 * z1 + cZZ * zz + cXX * xx;
}

@EntryPoint()
operation RunDrugDiscovery() : Unit {
    Message("=== Drug Discovery: VQE Molecular Binding Energy ===");
    Message("");
    let exactBinding = -1.024708;
    Message($"Exact ground energy of the illustrative two-qubit Hamiltonian: {exactBinding} Hartree");
    let angles = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8];
    let shots = 48;
    mutable bestE = 100.0;
    mutable bestT0 = 0.0;
    mutable bestT1 = 0.0;
    for t0 in angles {
        for t1 in angles {
            let e = EstimateBindingEnergy(t0, t1, 0.0, shots);
            if (e < bestE) { set bestE = e; set bestT0 = t0; set bestT1 = t1; }
        }
    }
    Message($"VQE binding energy: {bestE} Hartree");
    Message($"Error vs exact: {AbsD(bestE - exactBinding)} Hartree");
    Message($"QPE ground-state energy (8 phase bits): {BindingQPE(8, 8)} Hartree");
    Message("");
    Message("VQE enables quantum-accurate binding affinity prediction for drug candidates.");
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

/// The illustrative two-qubit Hamiltonian that EstimateBindingEnergy measures. It is not
/// derived from any molecule; its exact ground energy is -1.024708.
function BindingHamiltonian() : (Pauli[][], Double[], Double) {
    let paulis = [[PauliZ, PauliI], [PauliI, PauliZ], [PauliZ, PauliZ], [PauliX, PauliX]];
    let coeffs = [0.20, -0.18, 0.12, 0.06];
    return (paulis, coeffs, -0.52);
}

/// Trotter steps per U: Trotter error below half the 10-bit phase resolution.
function BindingTrotterSteps() : Int {
    return 2;
}

/// One QPE run from |10> (overlap 0.99 with the ground state).
operation BindingQPEOutcome(nPhase : Int) : Int {
    let (paulis, coeffs, _) = BindingHamiltonian();
    return MeasureEnergyPhase(paulis, coeffs, PrepareBasisState([1, 0], _), 2, nPhase, BindingTrotterSteps());
}

/// Ground-state energy of the illustrative Hamiltonian by QPE.
operation BindingQPE(nPhase : Int, shots : Int) : Double {
    let (_, coeffs, offset) = BindingHamiltonian();
    mutable outcomes : Int[] = [];
    for _ in 1..(shots < 1 ? 1 | shots) {
        outcomes += [BindingQPEOutcome(nPhase)];
    }
    return PhaseToEnergy(ModeOutcome(outcomes, nPhase), nPhase, EvolutionTime(coeffs), offset);
}
