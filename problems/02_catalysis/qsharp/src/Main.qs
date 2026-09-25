// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Math.*;
import Std.Measurement.*;

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

/// Electronic energy of the ansatz state for the H2 Hamiltonian MolecularHamiltonian defines:
/// H = c_I + c_Z0 Z0 + c_Z1 Z1 + c_ZZ Z0Z1 + c_XX X0X1 (parity mapping, two-qubit reduction).
operation EstimateMolecularEnergy(theta0 : Double, theta1 : Double, theta2 : Double, shots : Int) : Double {
    // H2 Hamiltonian coefficients (STO-3G, R = 0.735 angstrom), as in MolecularHamiltonian
    let cI = -1.052373245772859;
    let cZ0 = 0.39793742484318045;
    let cZ1 = -0.39793742484318045;
    let cZZ = -0.01128010425623538;
    let cXX = 0.18093119978423156;

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
    let exactEnergy = -1.137306;
    Message($"  Exact FCI energy: {exactEnergy} Hartree");
    Message("");

    let shots = 64;
    let (t0, t1, t2, vqeEnergy) = OptimizeVQE(shots);
    Message($"  VQE optimized parameters: theta=({t0}, {t1}, {t2})");
    let vqeTotal = vqeEnergy + NuclearRepulsionEnergy();
    Message($"  VQE energy estimate (with nuclear repulsion): {vqeTotal} Hartree");
    let error = AbsD(vqeTotal - exactEnergy);
    Message($"  Error vs exact: {error} Hartree");
    let qpeEnergy = MolecularQPE(8, 8);
    Message($"  QPE energy estimate (8 phase bits): {qpeEnergy} Hartree");
    Message("");

    Message("=== Quantum Advantage ===");
    Message("VQE enables polynomial-scaling molecular energy estimation");
    Message("compared to exponential-scaling classical FCI for large active spaces.");
    Message("Critical for catalyst design: computing reaction barrier heights");
    Message("and transition state energies on quantum hardware.");
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

/// H2 in STO-3G at 0.735 angstrom, parity-mapped with two-qubit reduction (qubit 0 first).
/// Its ground energy is -1.857275 Ha; adding the nuclear repulsion 0.719969 Ha gives
/// -1.137306 Ha, the full-CI energy. tooling/test_qpe_kernels.py checks both numbers.
function MolecularHamiltonian() : (Pauli[][], Double[], Double) {
    let paulis = [[PauliZ, PauliI], [PauliI, PauliZ], [PauliZ, PauliZ], [PauliX, PauliX]];
    let coeffs = [0.39793742484318045, -0.39793742484318045, -0.01128010425623538, 0.18093119978423156];
    return (paulis, coeffs, -1.052373245772859);
}

function NuclearRepulsionEnergy() : Double {
    return 0.7199689944489797;
}

/// Trotter steps per U: Trotter error below half the 10-bit phase resolution.
function MolecularTrotterSteps() : Int {
    return 4;
}

/// One QPE run from the Hartree-Fock state |10> (overlap 0.99 with the ground state).
operation MolecularQPEOutcome(nPhase : Int) : Int {
    let (paulis, coeffs, _) = MolecularHamiltonian();
    return MeasureEnergyPhase(paulis, coeffs, PrepareBasisState([1, 0], _), 2, nPhase, MolecularTrotterSteps());
}

/// Total H2 ground-state energy (electronic plus nuclear repulsion) by QPE.
operation MolecularQPE(nPhase : Int, shots : Int) : Double {
    let (_, coeffs, offset) = MolecularHamiltonian();
    mutable outcomes : Int[] = [];
    for _ in 1..(shots < 1 ? 1 | shots) {
        outcomes += [MolecularQPEOutcome(nPhase)];
    }
    return PhaseToEnergy(ModeOutcome(outcomes, nPhase), nPhase, EvolutionTime(coeffs), offset) + NuclearRepulsionEnergy();
}
