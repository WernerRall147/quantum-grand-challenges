// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 01_hubbard (QPE for the two-site Hubbard ground-state energy)
// Target profile: Adaptive_RI
//
// Two phase qubits of quantum phase estimation (QPE) for the Hamiltonian that
// Main.HubbardQPE uses, with one Trotter step per U so it fits current hardware.
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
operation HubbardQPEKernel() : Result[] {
    // Two-site Hubbard model, t = 1, U = 4, Jordan-Wigner on (1 up, 2 up, 1 down, 2 down).
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
    let coeffs = [-0.5, -0.5, -0.5, -0.5, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0];
    use phase = Qubit[2];
    use sys = Qubit[4];
    // Heitler-London singlet (|1up 2dn> + |1dn 2up>) / sqrt(2).
    H(sys[0]);
    CNOT(sys[0], sys[3]);
    X(sys[1]);
    CNOT(sys[0], sys[1]);
    X(sys[2]);
    CNOT(sys[0], sys[2]);
    ApplyQPE(ApplyEvolutionPower(paulis, coeffs, EvolutionTime(coeffs), 1, _, _), sys, phase);
    // Little-endian phase register: value / 4 is the phase as a fraction of 2 pi.
    let phaseResults = MResetEachZ(phase);
    ResetAll(sys);
    return phaseResults;
}
