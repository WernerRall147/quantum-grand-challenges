// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 14_materials_discovery (QPE for a tight-binding dimer energy level)
// Target profile: Adaptive_RI
//
// Two phase qubits of quantum phase estimation (QPE) for the Hamiltonian that
// Main.BandGapQPE uses, with one Trotter step per U so it fits current hardware.
// tooling/test_qpe_kernels.py checks sampled outcomes against exact diagonalization.

import Std.Canon.ApplyQPE;
import Std.Convert.IntAsDouble;
import Std.Math.*;
import Std.Measurement.MResetEachZ;

/// One symmetric Trotter step exp(-i H' dt); Exp(P, theta, qs) applies exp(i theta P).
operation ApplyTrotterStep(paulis : Pauli[][], coeffs : Double[], dt : Double, register : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(coeffs);
    for j in 0..n - 1 {
        Exp(paulis[j], -coeffs[j] * dt / 2.0, register);
    }
    for j in (n - 1)..-1..0 {
        Exp(paulis[j], -coeffs[j] * dt / 2.0, register);
    }
}

operation ApplyEvolutionPower(paulis : Pauli[][], coeffs : Double[], tau : Double, steps : Int, power : Int, register : Qubit[]) : Unit is Adj + Ctl {
    let dt = tau / IntAsDouble(steps);
    for _ in 1..power * steps {
        ApplyTrotterStep(paulis, coeffs, dt, register);
    }
}

/// tau = pi / (2 * sum |coeffs|), so the measured phase cannot wrap.
function EvolutionTime(coeffs : Double[]) : Double {
    mutable lambda = 0.0;
    for c in coeffs {
        lambda += AbsD(c);
    }
    return PI() / (2.0 * lambda);
}

@EntryPoint()
operation MaterialsQPEKernel() : Result[] {
    // Tight-binding dimer: e1 = 1.0, e2 = -0.5, t = 0.8, V = 0.3.
    let paulis = [[PauliZ, PauliI], [PauliI, PauliZ], [PauliX, PauliX], [PauliY, PauliY], [PauliZ, PauliZ]];
    let coeffs = [1.0, -0.5, 0.8, 0.8, 0.3];
    use phase = Qubit[2];
    use sys = Qubit[2];
    // Site-localised one-electron state |10>.
    X(sys[0]);
    ApplyQPE(ApplyEvolutionPower(paulis, coeffs, EvolutionTime(coeffs), 1, _, _), sys, phase);
    // Little-endian phase register: value / 4 is the phase as a fraction of 2 pi.
    let phaseResults = MResetEachZ(phase);
    ResetAll(sys);
    return phaseResults;
}
