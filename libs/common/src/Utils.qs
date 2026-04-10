// Utils.qs — Shared quantum operations for Quantum Grand Challenges.
//
// Modern QDK (qsharp 1.27+): flat file namespace, `import Std.*` syntax.

import Std.Arrays.*;
import Std.Convert.*;
import Std.Math.*;

/// Prepares a uniform superposition over n qubits.
operation PrepareUniformSuperposition(qubits : Qubit[]) : Unit is Adj + Ctl {
    for q in qubits {
        H(q);
    }
}

/// Controlled rotation around Z-axis with angle 2π / 2^power.
operation ControlledZRotationByPower(control : Qubit, target : Qubit, power : Int) : Unit is Adj + Ctl {
    let angle = 2.0 * PI() / IntAsDouble(2 ^ power);
    Controlled Rz([control], (angle, target));
}

/// Quantum Fourier Transform (big-endian, qubits[0] = MSB).
operation QuantumFourierTransform(qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    for i in 0..n - 1 {
        H(qubits[i]);
        for j in i + 1..n - 1 {
            ControlledZRotationByPower(qubits[j], qubits[i], j - i);
        }
    }
    for i in 0..n / 2 - 1 {
        SWAP(qubits[i], qubits[n - 1 - i]);
    }
}

/// Grover diffusion operator — reflects amplitudes around their average.
operation DiffusionOperator(qubits : Qubit[]) : Unit is Adj + Ctl {
    within {
        PrepareUniformSuperposition(qubits);
        for q in qubits { X(q); }
    } apply {
        Controlled Z(qubits[0..Length(qubits) - 2], qubits[Length(qubits) - 1]);
    }
}

/// Default marking oracle — marks the all-ones state.
operation MarkingOracle(qubits : Qubit[], target : Qubit) : Unit is Adj + Ctl {
    Controlled X(qubits, target);
}

/// Single Grover iteration: oracle then diffusion.
operation GroverIteration(oracle : ((Qubit[], Qubit) => Unit is Adj + Ctl), qubits : Qubit[], auxiliary : Qubit) : Unit {
    oracle(qubits, auxiliary);
    DiffusionOperator(qubits);
}

function ClipProbability(value : Double) : Double {
    if value < 0.0 { return 0.0; }
    if value > 1.0 { return 1.0; }
    return value;
}

operation ApplyAllOnesPhase(qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    if n == 0 {
        ()
    } elif n == 1 {
        Z(qubits[0]);
    } else {
        Controlled Z(qubits[0..n - 2], qubits[n - 1]);
    }
}

operation ReflectAboutZero(register : Qubit[]) : Unit is Adj + Ctl {
    within {
        for q in register { X(q); }
    } apply {
        ApplyAllOnesPhase(register);
    }
}

operation ReflectAboutState(statePrep : Qubit[] => Unit is Adj + Ctl, register : Qubit[]) : Unit is Adj + Ctl {
    within {
        statePrep(register);
    } apply {
        ReflectAboutZero(register);
    }
    Adjoint statePrep(register);
}

operation GroverOperator(
    statePrep : Qubit[] => Unit is Adj + Ctl,
    oracle : (Qubit[], Qubit) => Unit is Adj + Ctl,
    register : Qubit[],
    marker : Qubit
) : Unit is Adj + Ctl {
    within {
        X(marker);
        H(marker);
    } apply {
        oracle(register, marker);
        ReflectAboutState(statePrep, register);
    }
}

operation GroverOperatorPower(
    statePrep : Qubit[] => Unit is Adj + Ctl,
    oracle : (Qubit[], Qubit) => Unit is Adj + Ctl,
    power : Int,
    register : Qubit[],
    marker : Qubit
) : Unit is Adj + Ctl {
    if power <= 0 {
        ()
    } else {
        for _ in 1..power {
            GroverOperator(statePrep, oracle, register, marker);
        }
    }
}

/// Quantum amplitude estimation via QPE + Grover operator.
operation AmplitudeEstimation(
    oracle : ((Qubit[], Qubit) => Unit is Adj + Ctl),
    statePrep : (Qubit[] => Unit is Adj + Ctl),
    precision : Int,
    qubits : Qubit[],
    auxiliary : Qubit
) : Double {
    if precision <= 0 {
        fail "Amplitude estimation requires at least one precision qubit.";
    }

    use precisionRegister = Qubit[precision];

    for q in precisionRegister { H(q); }
    statePrep(qubits);

    for idx in 0..precision - 1 {
        let power = 1 <<< idx;
        Controlled GroverOperatorPower([precisionRegister[idx]], (statePrep, oracle, power, qubits, auxiliary));
    }

    Adjoint QuantumFourierTransform(precisionRegister);

    mutable results = [Zero, size = precision];
    for idx in 0..precision - 1 {
        set results w/= idx <- M(precisionRegister[idx]);
    }
    let phaseInt = ResultArrayAsInt(results);

    ResetAll(precisionRegister);
    Reset(auxiliary);
    ResetAll(qubits);

    let phase = IntAsDouble(phaseInt) / IntAsDouble(1 <<< precision);
    let theta = phase * PI();
    let amplitude = Sin(theta) * Sin(theta);
    return ClipProbability(amplitude);
}

/// Converts measurement result array to integer (MSB first).
function ResultArrayAsInt(results : Result[]) : Int {
    mutable output = 0;
    let nBits = Length(results);
    for i in 0..nBits - 1 {
        if results[i] == One {
            set output += 2 ^ (nBits - 1 - i);
        }
    }
    return output;
}

/// Wraps an operation in a controlled form.
operation MakeControlled(op : (Qubit[] => Unit is Adj + Ctl), controls : Qubit[], targets : Qubit[]) : Unit is Adj + Ctl {
    Controlled op(controls, targets);
}
