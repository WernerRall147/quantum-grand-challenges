// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;
import Std.Measurement.*;

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
    let yy = MeasurePauli(theta0, theta1, theta2, [PauliY, PauliY], shots);

    return onsite1 * z0 + onsite2 * z1 + hopping * (xx + yy) + interaction * zz;
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
        Message($"  QPE band gap (8 phase bits): {BandGapQPE(onsite1, onsite2, hopping, interaction, 8, 8)} eV");
        Message("");
    }

    Message("=== Quantum Advantage ===");
    Message("VQE enables accurate band structure calculations for complex materials");
    Message("where classical DFT fails (strongly correlated systems, defect states).");
    Message("Key application: screening battery cathode and photovoltaic materials.");
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

/// Tight-binding dimer with one electron, H = e1 Z0 + e2 Z1 + t (X0X1 + Y0Y1) + V Z0Z1.
/// The bonding and antibonding one-electron levels are the valence and conduction bands,
/// and the band gap is their difference.
function BandHamiltonian(onsite1 : Double, onsite2 : Double, hopping : Double, interaction : Double) : (Pauli[][], Double[], Double) {
    let paulis = [[PauliZ, PauliI], [PauliI, PauliZ], [PauliX, PauliX], [PauliY, PauliY], [PauliZ, PauliZ]];
    let coeffs = [onsite1, onsite2, hopping, hopping, interaction];
    return (paulis, coeffs, 0.0);
}

/// Trotter steps per U: Trotter error below half the 10-bit phase resolution.
function BandTrotterSteps() : Int {
    return 4;
}

/// One QPE run from a site-localised one-electron state ([1, 0] or [0, 1]).
operation BandQPEOutcome(onsite1 : Double, onsite2 : Double, hopping : Double, interaction : Double, site : Int[], nPhase : Int) : Int {
    let (paulis, coeffs, _) = BandHamiltonian(onsite1, onsite2, hopping, interaction);
    return MeasureEnergyPhase(paulis, coeffs, PrepareBasisState(site, _), 2, nPhase, BandTrotterSteps());
}

/// The most frequent phase-register value more than one bin away from `avoid`.
function ModeOutcomeAwayFrom(outcomes : Int[], nPhase : Int, avoid : Int) : Int {
    let size = 1 <<< nPhase;
    mutable kept : Int[] = [];
    for outcome in outcomes {
        let distance = AbsI(outcome - avoid);
        if distance > 1 and distance < size - 1 {
            kept += [outcome];
        }
    }
    return Length(kept) > 0 ? ModeOutcome(kept, nPhase) | avoid;
}

/// Band gap by QPE. Each site-localised one-electron state overlaps one level more than the
/// other whenever e1 differs from e2: the most frequent outcome from |10> is the first level,
/// and the most frequent outcome from |01> away from that level is the second. Excluding
/// the first level stops a few unlucky shots from collapsing the gap to zero.
operation BandGapQPE(onsite1 : Double, onsite2 : Double, hopping : Double, interaction : Double, nPhase : Int, shots : Int) : Double {
    let (_, coeffs, offset) = BandHamiltonian(onsite1, onsite2, hopping, interaction);
    let tau = EvolutionTime(coeffs);
    mutable fromFirst : Int[] = [];
    mutable fromSecond : Int[] = [];
    for _ in 1..(shots < 1 ? 1 | shots) {
        fromFirst += [BandQPEOutcome(onsite1, onsite2, hopping, interaction, [1, 0], nPhase)];
        fromSecond += [BandQPEOutcome(onsite1, onsite2, hopping, interaction, [0, 1], nPhase)];
    }
    let first = ModeOutcome(fromFirst, nPhase);
    let second = ModeOutcomeAwayFrom(fromSecond, nPhase, first);
    return AbsD(PhaseToEnergy(second, nPhase, tau, offset) - PhaseToEnergy(first, nPhase, tau, offset));
}
