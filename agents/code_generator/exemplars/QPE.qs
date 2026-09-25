/// Ground-state energy of H2 by quantum phase estimation (QPE): a complete program in the
/// shape the generator must return.
///
/// H2 in STO-3G at 0.735 angstrom, parity-mapped to two qubits (qubit 0 first):
/// H = offset + sum_j coeffs[j] * paulis[j], offset = -1.052373 Ha. Its ground energy is
/// -1.857275 Ha; adding the nuclear repulsion 0.719969 Ha gives -1.137306 Ha, the full-CI
/// value. A larger molecule or lattice model is the same program with more terms and qubits.
///
/// U = exp(-i (H - offset) tau) is built from symmetric Trotter steps, with
/// tau = pi / (2 * sum |coeffs|) so that the phase cannot wrap. The phase register returns
/// m = phase * 2^n as a little-endian integer (m = 13 of 64 here), and
/// E = offset - 2 pi m / (2^n tau), taking m - 2^n when m > 2^(n - 1).
import Std.Canon.*;
import Std.Convert.*;
import Std.Math.*;
import Std.Measurement.*;

function HamiltonianTerms() : (Pauli[][], Double[]) {
    let paulis = [[PauliZ, PauliI], [PauliI, PauliZ], [PauliZ, PauliZ], [PauliX, PauliX]];
    let coeffs = [0.39793742484318045, -0.39793742484318045, -0.01128010425623538, 0.18093119978423156];
    return (paulis, coeffs);
}

function EvolutionTime(coeffs : Double[]) : Double {
    mutable lambda = 0.0;
    for c in coeffs {
        set lambda += AbsD(c);
    }
    return PI() / (2.0 * lambda);
}

/// One symmetric Trotter step exp(-i H dt). Exp(paulis, theta, qubits) applies
/// exp(i theta P) for a Pauli[] and a Qubit[] of the same length. To control an operation
/// by hand, pass the controls and then ONE tuple of its arguments:
/// Controlled Exp([control], (paulis[j], theta, register)).
operation TrotterStep(paulis : Pauli[][], coeffs : Double[], dt : Double, register : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(coeffs);
    for j in 0..n - 1 {
        Exp(paulis[j], -coeffs[j] * dt / 2.0, register);
    }
    for j in (n - 1)..-1..0 {
        Exp(paulis[j], -coeffs[j] * dt / 2.0, register);
    }
}

/// U^power. ApplyQPE calls this with power = 2^k for phase qubit k and adds the controls.
operation EvolutionPower(power : Int, register : Qubit[]) : Unit is Adj + Ctl {
    let (paulis, coeffs) = HamiltonianTerms();
    let steps = 4;
    let dt = EvolutionTime(coeffs) / IntAsDouble(steps);
    for _ in 1..power * steps {
        TrotterStep(paulis, coeffs, dt, register);
    }
}

operation Main() : Result[] {
    use system = Qubit[2];
    use phase = Qubit[6];
    // Hartree-Fock reference |10>: its overlap with the ground state is 0.99.
    X(system[0]);
    ApplyQPE(EvolutionPower, system, phase);
    let results = MResetEachZ(phase);
    ResetAll(system);
    return results;
}
