// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;
import Std.Measurement.*;

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

/// Energy of the ansatz state for the deuteron Hamiltonian DeuteronHamiltonian defines:
/// H = c0*I + c1*Z0 + c2*Z1 + c4*(X0X1 + Y0Y1), in MeV.
operation EstimateNuclearEnergy(theta0 : Double, theta1 : Double, theta2 : Double, shots : Int) : Double {
    let c0 = 5.906709;
    let c1 = 0.218291;
    let c2 = -6.125;
    let c4 = -2.143304;
    let z0 = MeasureNuclearPauli(theta0, theta1, theta2, [PauliZ, PauliI], shots);
    let z1 = MeasureNuclearPauli(theta0, theta1, theta2, [PauliI, PauliZ], shots);
    let xx = MeasureNuclearPauli(theta0, theta1, theta2, [PauliX, PauliX], shots);
    let yy = MeasureNuclearPauli(theta0, theta1, theta2, [PauliY, PauliY], shots);
    return c0 + c1 * z0 + c2 * z1 + c4 * (xx + yy);
}

@EntryPoint()
operation RunNuclearPhysics() : Unit {
    Message("=== Nuclear Physics: VQE Deuteron Binding Energy ===");
    Message("");
    let exactEnergy = -1.749;
    Message($"Exact ground energy in this two-state basis: {exactEnergy} MeV (experimental binding energy: -2.224 MeV)");
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
    Message($"Error vs exact: {AbsD(bestE - exactEnergy)} MeV");
    Message($"QPE ground-state energy (8 phase bits): {NuclearQPE(8, 8)} MeV");
    Message("");
    Message("VQE enables ab initio nuclear structure calculations");
    Message("beyond the reach of classical many-body methods.");
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

/// Deuteron in a two-state harmonic-oscillator basis from leading-order pionless effective
/// field theory (Dumitrescu et al., Phys. Rev. Lett. 120, 210501, 2018), in MeV:
///   H = 5.906709 I + 0.218291 Z0 - 6.125 Z1 - 2.143304 (X0X1 + Y0Y1).
/// Its ground energy is -1.749 MeV. The experimental binding energy, -2.224 MeV, is
/// approached only as the basis grows.
function DeuteronHamiltonian() : (Pauli[][], Double[], Double) {
    let paulis = [[PauliZ, PauliI], [PauliI, PauliZ], [PauliX, PauliX], [PauliY, PauliY]];
    let coeffs = [0.218291, -6.125, -2.143304, -2.143304];
    return (paulis, coeffs, 5.906709);
}

/// Trotter steps per U: Trotter error below half the 10-bit phase resolution.
function DeuteronTrotterSteps() : Int {
    return 8;
}

/// One QPE run from |10> (overlap 0.91 with the ground state).
operation NuclearQPEOutcome(nPhase : Int) : Int {
    let (paulis, coeffs, _) = DeuteronHamiltonian();
    return MeasureEnergyPhase(paulis, coeffs, PrepareBasisState([1, 0], _), 2, nPhase, DeuteronTrotterSteps());
}

/// Deuteron ground-state energy by QPE.
operation NuclearQPE(nPhase : Int, shots : Int) : Double {
    let (_, coeffs, offset) = DeuteronHamiltonian();
    mutable outcomes : Int[] = [];
    for _ in 1..(shots < 1 ? 1 | shots) {
        outcomes += [NuclearQPEOutcome(nPhase)];
    }
    return PhaseToEnergy(ModeOutcome(outcomes, nPhase), nPhase, EvolutionTime(coeffs), offset);
}
