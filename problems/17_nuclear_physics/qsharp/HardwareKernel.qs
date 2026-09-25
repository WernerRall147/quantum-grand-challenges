// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 17_nuclear_physics (QPE for the deuteron ground-state energy)
// Target profile: Adaptive_RI
//
// Two phase qubits of quantum phase estimation (QPE) for the Hamiltonian that
// Main.NuclearQPE uses, with one Trotter step per U so it fits current hardware.
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
operation NuclearQPEKernel() : Result[] {
    // Deuteron, leading-order pionless EFT, two-state basis (Dumitrescu et al. 2018), MeV.
    let paulis = [[PauliZ, PauliI], [PauliI, PauliZ], [PauliX, PauliX], [PauliY, PauliY]];
    let coeffs = [0.218291, -6.125, -2.143304, -2.143304];
    use phase = Qubit[2];
    use sys = Qubit[2];
    X(sys[0]);
    ApplyQPE(ApplyEvolutionPower(paulis, coeffs, EvolutionTime(coeffs), 1, _, _), sys, phase);
    // Little-endian phase register: value / 4 is the phase as a fraction of 2 pi.
    let phaseResults = MResetEachZ(phase);
    ResetAll(sys);
    return phaseResults;
}
