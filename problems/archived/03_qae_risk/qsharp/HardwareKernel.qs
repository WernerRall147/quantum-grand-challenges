// HardwareKernel.qs  Minimal QAE kernel for Azure Quantum hardware/simulator.
//
// Contains only the operations needed for a single-shot QAE round.
// All classical post-processing (phase → probability, statistics)
// is handled by the Python driver (submit_azure.py).
//
// Target profile: Adaptive_RI (mid-circuit Reset for ancilla cleanup).

import Std.Convert.IntAsDouble;
import Std.Measurement.MResetEachZ;
import Std.Math.*;
import Std.Canon.ApplyToEachCA;

// ---- Runtime parameters (inlined from RuntimeConfig) ----
// Sized for hardware/syntax-checker submission (small instance).
// 2 loss qubits = 4 discrete levels, 2 precision bits.
// Total: 2 + 2 + 1 marker = 5 logical qubits + ancilla.
function RuntimeLossQubits() : Int { return 2; }
function RuntimeThreshold() : Double { return 2.5; }
function RuntimeMean() : Double { return 0.0; }
function RuntimeStdDev() : Double { return 1.0; }
function RuntimePrecisionBits() : Int { return 2; }

// ---- Distribution helpers (pure functions  no hardware restriction) ----

function NumStates(lossQubits : Int) : Int {
    return 1 <<< lossQubits;
}

function LossValueFromIndex(index : Int, lossQubits : Int) : Double {
    let numStates = NumStates(lossQubits);
    let fraction = IntAsDouble(index + 1) / IntAsDouble(numStates);
    return fraction * 10.0;
}

function ExpD(x : Double) : Double {
    let base = new Complex { Real = E(), Imag = 0.0 };
    let power = new Complex { Real = x, Imag = 0.0 };
    return PowC(base, power).Real;
}

function LogNormalPdf(x : Double, mean : Double, stdDev : Double) : Double {
    if (x <= 1e-15) { return 0.0; }
    mutable sigma = stdDev;
    if (sigma <= 0.01) { set sigma = 0.01; }
    let logX = Log(x);
    let diff = logX - mean;
    let exponent = -(diff * diff) / (2.0 * sigma * sigma);
    return ExpD(exponent) / (x * sigma * Sqrt(2.0 * PI()));
}

function LogNormalProbabilities(lossQubits : Int, mean : Double, stdDev : Double) : Double[] {
    let numStates = NumStates(lossQubits);
    mutable raw = [0.0, size = numStates];
    mutable total = 0.0;
    for index in 0 .. numStates - 1 {
        let value = LossValueFromIndex(index, lossQubits);
        let pdf = LogNormalPdf(value, mean, stdDev);
        set raw w/= index <- pdf;
        set total += pdf;
    }
    if (total <= 0.0) { return raw; }
    mutable normalized = [0.0, size = numStates];
    for index in 0 .. numStates - 1 {
        set normalized w/= index <- raw[index] / total;
    }
    return normalized;
}

// ---- State preparation ----

function NormalizedAmplitudes(probabilities : Double[], numStates : Int) : Double[] {
    mutable amplitudes = [0.0, size = numStates];
    mutable sumSquares = 0.0;
    for i in 0 .. numStates - 1 {
        let amplitude = Sqrt(probabilities[i]);
        set amplitudes w/= i <- amplitude;
        set sumSquares += amplitude * amplitude;
    }
    if (sumSquares > 0.0) {
        let norm = Sqrt(sumSquares);
        for i in 0 .. numStates - 1 {
            set amplitudes w/= i <- amplitudes[i] / norm;
        }
    }
    return amplitudes;
}

function SplitAndNormalize(amplitudes : Double[], half : Int) : (Double[], Double[], Double, Double) {
    mutable leftAmps = [0.0, size = half];
    mutable rightAmps = [0.0, size = half];
    for i in 0 .. half - 1 {
        set leftAmps w/= i <- amplitudes[i];
        set rightAmps w/= i <- amplitudes[i + half];
    }
    mutable leftNorm = 0.0;
    mutable rightNorm = 0.0;
    for i in 0 .. half - 1 {
        set leftNorm += leftAmps[i] * leftAmps[i];
        set rightNorm += rightAmps[i] * rightAmps[i];
    }
    set leftNorm = Sqrt(leftNorm);
    set rightNorm = Sqrt(rightNorm);
    if (leftNorm > 1e-10) {
        for i in 0 .. half - 1 { set leftAmps w/= i <- leftAmps[i] / leftNorm; }
    }
    if (rightNorm > 1e-10) {
        for i in 0 .. half - 1 { set rightAmps w/= i <- rightAmps[i] / rightNorm; }
    }
    return (leftAmps, rightAmps, leftNorm, rightNorm);
}

operation ApplyMultiplexRotations(amplitudes : Double[], qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    if (n > 0) {
        if (n == 1) {
            let angle = 2.0 * ArcTan2(amplitudes[1], amplitudes[0]);
            Ry(angle, qubits[0]);
        } else {
            let half = Length(amplitudes) / 2;
            let (leftAmps, rightAmps, leftNorm, rightNorm) = SplitAndNormalize(amplitudes, half);
            let angle = 2.0 * ArcTan2(rightNorm, leftNorm);
            Ry(angle, qubits[0]);
            within { X(qubits[0]); }
            apply { Controlled ApplyMultiplexRotations([qubits[0]], (leftAmps, qubits[1...])); }
            Controlled ApplyMultiplexRotations([qubits[0]], (rightAmps, qubits[1...]));
        }
    }
}

operation PrepareDistributionState(probabilities : Double[], lossQubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(lossQubits);
    let numStates = 1 <<< n;
    let amplitudes = NormalizedAmplitudes(probabilities, numStates);
    ApplyMultiplexRotations(amplitudes, lossQubits);
}

// ---- Oracle ----

operation OracleTailMarking(threshold : Double, lossQubits : Int, register : Qubit[], marker : Qubit) : Unit is Adj + Ctl {
    let n = Length(register);
    for index in 0 .. (1 <<< n) - 1 {
        let lossValue = LossValueFromIndex(index, lossQubits);
        if (lossValue > threshold) {
            within {
                for bitIdx in 0 .. n - 1 {
                    let bit = (index >>> (n - 1 - bitIdx)) &&& 1;
                    if (bit == 0) { X(register[bitIdx]); }
                }
            } apply {
                Controlled X(register, marker);
            }
        }
    }
}

// ---- Grover and QPE building blocks ----

operation ApplyAllOnesPhase(qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    if (n == 0) { }
    elif (n == 1) { Z(qubits[0]); }
    else { Controlled Z(qubits[0..n - 2], qubits[n - 1]); }
}

operation ReflectAboutZero(register : Qubit[]) : Unit is Adj + Ctl {
    within { ApplyToEachCA(X, register); }
    apply { ApplyAllOnesPhase(register); }
}

operation ReflectAboutState(statePrep : Qubit[] => Unit is Adj + Ctl, register : Qubit[]) : Unit is Adj + Ctl {
    within { statePrep(register); }
    apply { ReflectAboutZero(register); }
}

operation GroverOperator(
    statePrep : Qubit[] => Unit is Adj + Ctl,
    oracle : (Qubit[], Qubit) => Unit is Adj + Ctl,
    lossRegister : Qubit[],
    marker : Qubit
) : Unit is Adj + Ctl {
    ReflectAboutState(statePrep, lossRegister);
    oracle(lossRegister, marker);
}

operation GroverOperatorPower(
    statePrep : Qubit[] => Unit is Adj + Ctl,
    oracle : (Qubit[], Qubit) => Unit is Adj + Ctl,
    power : Int,
    lossRegister : Qubit[],
    marker : Qubit
) : Unit is Adj + Ctl {
    for _ in 1 .. power {
        GroverOperator(statePrep, oracle, lossRegister, marker);
    }
}

operation QuantumFourierTransform(register : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(register);
    for j in 0 .. n - 1 {
        H(register[j]);
        for k in j + 1 .. n - 1 {
            let angle = PI() / IntAsDouble(1 <<< (k - j));
            Controlled R1([register[k]], (angle, register[j]));
        }
    }
    for j in 0 .. (n / 2 - 1) {
        let right = n - j - 1;
        if (j < right) { SWAP(register[j], register[right]); }
    }
}

operation QuantumPhaseEstimationQAE(
    statePrep : Qubit[] => Unit is Adj + Ctl,
    oracle : (Qubit[], Qubit) => Unit is Adj + Ctl,
    precisionQubits : Qubit[],
    lossRegister : Qubit[],
    marker : Qubit
) : Unit {
    for q in precisionQubits { H(q); }
    statePrep(lossRegister);
    X(marker);
    H(marker);
    let n = Length(precisionQubits);
    for idx in 0 .. n - 1 {
        let power = 1 <<< (n - 1 - idx);
        Controlled GroverOperatorPower(
            [precisionQubits[idx]],
            (statePrep, oracle, power, lossRegister, marker)
        );
    }
    Adjoint QuantumFourierTransform(precisionQubits);
}

// ---- Entry point: single-shot QAE kernel ----

@EntryPoint()
operation QAEKernel() : Result[] {
    let lossQubits = RuntimeLossQubits();
    let threshold = RuntimeThreshold();
    let mean = RuntimeMean();
    let stdDev = RuntimeStdDev();
    let precisionBits = RuntimePrecisionBits();

    let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);

    use precisionReg = Qubit[precisionBits];
    use lossReg = Qubit[lossQubits];
    use marker = Qubit();

    let statePrep = PrepareDistributionState(probabilities, _);
    let oracle = OracleTailMarking(threshold, lossQubits, _, _);

    QuantumPhaseEstimationQAE(statePrep, oracle, precisionReg, lossReg, marker);

    ResetAll(lossReg);
    Reset(marker);

    return MResetEachZ(precisionReg);
}

// ---- IQAE kernel: single Grover-amplified round ----
// Uses k=0 (no Grover iterations) by default.
// The Python driver runs multiple shots and controls k adaptively.
// NO precision register, NO QFT  just loss + marker qubits.

operation IQAEKernelK0() : Result {
    let lossQubits = RuntimeLossQubits();
    let threshold = RuntimeThreshold();
    let mean = RuntimeMean();
    let stdDev = RuntimeStdDev();
    let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);

    use lossReg = Qubit[lossQubits];
    use marker = Qubit();

    let statePrep = PrepareDistributionState(probabilities, _);
    let oracle = OracleTailMarking(threshold, lossQubits, _, _);

    // A = Oracle ∘ StatePrep
    statePrep(lossReg);
    oracle(lossReg, marker);

    // k=0: no Grover iterations, just measure
    let result = M(marker);
    ResetAll(lossReg);
    Reset(marker);
    return result;
}
