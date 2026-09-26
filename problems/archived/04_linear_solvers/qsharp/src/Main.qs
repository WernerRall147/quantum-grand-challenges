// Main.qs  Modern QDK project format

import Std.Arrays.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;
import Std.Measurement.*;

function Determinant2x2(matrix : Double[][]) : Double {
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0];
}

function SolveSymmetric2x2(matrix : Double[][], rhs : Double[]) : Double[] {
    let det = Determinant2x2(matrix);
    if AbsD(det) < 1e-12 { fail "Matrix is singular."; }
    let a = matrix[0][0];
    let b = matrix[0][1];
    let d = matrix[1][1];
    return [(d * rhs[0] - b * rhs[1]) / det, (-b * rhs[0] + a * rhs[1]) / det];
}

function ConditionNumberSymmetric2x2(matrix : Double[][]) : Double {
    let a = matrix[0][0];
    let b = matrix[0][1];
    let d = matrix[1][1];
    let delta = Sqrt((a - d) * (a - d) + 4.0 * b * b);
    let lambdaMax = 0.5 * (a + d + delta);
    let lambdaMin = 0.5 * (a + d - delta);
    return lambdaMax / lambdaMin;
}

function ResidualNorm(matrix : Double[][], solution : Double[], rhs : Double[]) : Double {
    let r0 = matrix[0][0] * solution[0] + matrix[0][1] * solution[1] - rhs[0];
    let r1 = matrix[1][0] * solution[0] + matrix[1][1] * solution[1] - rhs[1];
    return Sqrt(r0 * r0 + r1 * r1);
}

function EvolutionTime(precisionBits : Int) : Double {
    // With U = exp(i A t), t = 2π / 2^m makes an m-bit clock value y represent λ ≈ y.
    return 2.0 * PI() / IntAsDouble(1 <<< precisionBits);
}

operation PrepareRHSState(rhs : Double[], qubit : Qubit) : Unit is Adj + Ctl {
    if Length(rhs) != 2 { fail "This HHL demonstration supports 2D RHS vectors only."; }
    let norm = Sqrt(rhs[0] * rhs[0] + rhs[1] * rhs[1]);
    if norm < 1e-12 { fail "RHS vector must be nonzero."; }
    Ry(2.0 * ArcTan2(rhs[1] / norm, rhs[0] / norm), qubit);
}

operation ControlledExactEvolution2x2(matrix : Double[][], time : Double, control : Qubit, system : Qubit) : Unit is Adj {
    let a = matrix[0][0];
    let b = matrix[0][1];
    let d = matrix[1][1];
    let identity = 0.5 * (a + d);
    let z = 0.5 * (a - d);
    let x = b;
    let radius = Sqrt(z * z + x * x);
    R1(identity * time, control);
    if radius > 1e-12 {
        let axisAngle = ArcTan2(x, z);
        Controlled Ry([control], (-axisAngle, system));
        Controlled Rz([control], (-2.0 * radius * time, system));
        Controlled Ry([control], (axisAngle, system));
    }
}

operation QuantumFourierTransform(register : Qubit[]) : Unit is Adj + Ctl {
    // Big-endian QFT with final bit reversal. register[0] is the most significant bit.
    let n = Length(register);
    for j in 0 .. n - 1 {
        H(register[j]);
        for k in j + 1 .. n - 1 {
            Controlled R1([register[k]], (PI() / IntAsDouble(1 <<< (k - j)), register[j]));
        }
    }
    for j in 0 .. (n / 2 - 1) {
        let right = n - j - 1;
        if j < right { SWAP(register[j], register[right]); }
    }
}

operation QuantumPhaseEstimation(matrix : Double[][], system : Qubit, clock : Qubit[]) : Unit is Adj {
    let n = Length(clock);
    let baseTime = EvolutionTime(n);
    for q in clock { H(q); }
    for idx in 0 .. n - 1 {
        let power = 1 <<< (n - 1 - idx);
        ControlledExactEvolution2x2(matrix, baseTime * IntAsDouble(power), clock[idx], system);
    }
    Adjoint QuantumFourierTransform(clock);
}

operation ApplyZeroMask(value : Int, register : Qubit[]) : Unit is Adj {
    let n = Length(register);
    for idx in 0 .. n - 1 {
        let shift = n - 1 - idx;
        if (((value >>> shift) &&& 1) == 0) { X(register[idx]); }
    }
}

operation ControlledEigenvalueInversion(clock : Qubit[], ancilla : Qubit, c : Double) : Unit is Adj {
    let n = Length(clock);
    let size = 1 <<< n;
    for value in 1 .. size - 1 {
        let lambdaEstimate = IntAsDouble(value);
        if c <= lambdaEstimate {
            let theta = 2.0 * ArcSin(c / lambdaEstimate);
            within { ApplyZeroMask(value, clock); }
            apply { Controlled Ry(clock, (theta, ancilla)); }
        }
    }
}

operation PrepareHHLState2x2(matrix : Double[][], rhs : Double[], precisionBits : Int, system : Qubit, clock : Qubit[], ancilla : Qubit) : Unit is Adj {
    if Length(clock) != precisionBits { fail "Clock register length does not match precisionBits."; }
    PrepareRHSState(rhs, system);
    QuantumPhaseEstimation(matrix, system, clock);
    ControlledEigenvalueInversion(clock, ancilla, 1.0);
    Adjoint QuantumPhaseEstimation(matrix, system, clock);
}

operation HHLJointSample2x2(matrix : Double[][], rhs : Double[], precisionBits : Int) : Result[] {
    use system = Qubit();
    use clock = Qubit[precisionBits];
    use ancilla = Qubit();
    PrepareHHLState2x2(matrix, rhs, precisionBits, system, clock, ancilla);
    let ancillaResult = MResetZ(ancilla);
    let systemResult = MResetZ(system);
    ResetAll(clock);
    return [ancillaResult, systemResult];
}

operation HHLSolve2x2(matrix : Double[][], rhs : Double[], precisionBits : Int) : Result {
    mutable systemResult = Zero;
    mutable success = false;
    while not success {
        let sample = HHLJointSample2x2(matrix, rhs, precisionBits);
        set systemResult = sample[1];
        set success = sample[0] == One;
    }
    return systemResult;
}

operation HHLSuccessSample2x2(matrix : Double[][], rhs : Double[], precisionBits : Int) : Result {
    let sample = HHLJointSample2x2(matrix, rhs, precisionBits);
    return sample[0];
}

@EntryPoint()
operation RunLinearSolverBaseline() : Unit {
    Message("=== 2x2 Linear System Solver: textbook HHL demonstration ===");
    let matrix = [[4.0, -1.0], [-1.0, 3.0]];
    let rhs = [15.0, 10.0];
    let classicalSolution = SolveSymmetric2x2(matrix, rhs);
    let conditionNumber = ConditionNumberSymmetric2x2(matrix);
    let residual = ResidualNorm(matrix, classicalSolution, rhs);
    Message($"Matrix A: [[{matrix[0][0]}, {matrix[0][1]}], [{matrix[1][0]}, {matrix[1][1]}]]");
    Message($"RHS b: [{rhs[0]}, {rhs[1]}]");
    Message($"Classical solution: x = [{classicalSolution[0]}, {classicalSolution[1]}]");
    Message($"Condition number κ(A): {conditionNumber}");
    Message($"Residual ||Ax - b||: {residual}");
    Message("The HHL circuit uses exact controlled exp(i A t 2^k), clock inversion, inverse QPE and post-selection.");
    let result = HHLSolve2x2(matrix, rhs, 3);
    Message($"One post-selected system sample from the 3-bit HHL circuit: {result}");
}
