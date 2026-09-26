// Main.qs  Modern QDK project format

import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;
import Std.Measurement.*;

/// Time per controlled-evolution step: U = exp(i A τ) with τ = 2π/8, fixed whatever the clock size.
/// With m clock bits the total evolution time is τ·2^m, so the clock value y estimates
/// λ ≈ 8y/2^m with resolution 8/2^m: each extra bit halves the eigenvalue error. Eigenvalues
/// must stay below 8 or their phases wrap. A step that shrank with the clock (2π/2^m) would
/// keep the resolution at 1 however many bits were added.
function EvolutionStep() : Double {
    return 2.0 * PI() / 8.0;
}

/// The eigenvalue that clock value y represents with m clock bits.
function EigenvalueFromClock(value : Int, precisionBits : Int) : Double {
    return 8.0 * IntAsDouble(value) / IntAsDouble(1 <<< precisionBits);
}

operation PrepareRHSState(rhs : Double[], qubit : Qubit) : Unit is Adj + Ctl {
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
    let baseTime = EvolutionStep();
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
        let lambdaEstimate = EigenvalueFromClock(value, n);
        if c <= lambdaEstimate {
            within { ApplyZeroMask(value, clock); }
            apply { Controlled Ry(clock, (2.0 * ArcSin(c / lambdaEstimate), ancilla)); }
        }
    }
}

function ClimateDiffusionMatrix() : Double[][] { return [[2.0, -1.0], [-1.0, 2.0]]; }
function ClimateRhs() : Double[] { return [1.0, 0.0]; }

operation PrepareHHLState2x2(matrix : Double[][], rhs : Double[], precisionBits : Int, system : Qubit, clock : Qubit[], ancilla : Qubit) : Unit is Adj {
    PrepareRHSState(rhs, system);
    QuantumPhaseEstimation(matrix, system, clock);
    ControlledEigenvalueInversion(clock, ancilla, 1.0);
    Adjoint QuantumPhaseEstimation(matrix, system, clock);
}

operation ClimateHHLJointSample() : Result[] {
    use system = Qubit();
    use clock = Qubit[3];
    use ancilla = Qubit();
    PrepareHHLState2x2(ClimateDiffusionMatrix(), ClimateRhs(), 3, system, clock, ancilla);
    let ancillaResult = MResetZ(ancilla);
    let systemResult = MResetZ(system);
    ResetAll(clock);
    return [ancillaResult, systemResult];
}

operation HHLClimateSolutionSample() : Result {
    mutable systemResult = Zero;
    mutable success = false;
    while not success {
        let sample = ClimateHHLJointSample();
        set systemResult = sample[1];
        set success = sample[0] == One;
    }
    return systemResult;
}

operation RunHHLClimate(precisionBits : Int, shots : Int) : Double {
    mutable successCount = 0;
    for _ in 1 .. shots {
        use system = Qubit();
        use clock = Qubit[precisionBits];
        use ancilla = Qubit();
        PrepareHHLState2x2(ClimateDiffusionMatrix(), ClimateRhs(), precisionBits, system, clock, ancilla);
        if MResetZ(ancilla) == One { set successCount += 1; }
        MResetZ(system);
        ResetAll(clock);
    }
    return IntAsDouble(successCount) / IntAsDouble(shots);
}

@EntryPoint()
operation RunClimateModeling() : Unit {
    Message("=== Climate Modeling: 2x2 diffusion HHL demonstration ===");
    Message("The matrix is [[2,-1],[-1,2]], the two-point finite-difference Laplacian.");
    Message("The RHS is [1,0]. After post-selection the exact solution distribution is [0.8, 0.2].");
    let successRate = RunHHLClimate(3, 128);
    Message($"Estimated ancilla success rate from 128 shots: {successRate}");
}
