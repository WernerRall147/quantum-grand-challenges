// HardwareKernel.qs  QIR-compatible HHL kernel for Azure Quantum
// Problem: 04_linear_solvers
// Target profile: Adaptive_RI


import Std.Convert.*;
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

operation PrepareRHSState(rhs0 : Double, rhs1 : Double, qubit : Qubit) : Unit is Adj + Ctl {
    let norm = Sqrt(rhs0 * rhs0 + rhs1 * rhs1);
    Ry(2.0 * ArcTan2(rhs1 / norm, rhs0 / norm), qubit);
}

operation ControlledExactEvolution2x2(a : Double, b : Double, d : Double, time : Double, control : Qubit, system : Qubit) : Unit is Adj {
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

operation QuantumPhaseEstimation(a : Double, b : Double, d : Double, system : Qubit, clock : Qubit[]) : Unit is Adj {
    let n = Length(clock);
    let baseTime = EvolutionStep();
    for q in clock { H(q); }
    for idx in 0 .. n - 1 {
        let power = 1 <<< (n - 1 - idx);
        ControlledExactEvolution2x2(a, b, d, baseTime * IntAsDouble(power), clock[idx], system);
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

operation PrepareHHLState(a : Double, b : Double, d : Double, rhs0 : Double, rhs1 : Double, system : Qubit, clock : Qubit[], ancilla : Qubit) : Unit is Adj {
    PrepareRHSState(rhs0, rhs1, system);
    QuantumPhaseEstimation(a, b, d, system, clock);
    ControlledEigenvalueInversion(clock, ancilla, 1.0);
    Adjoint QuantumPhaseEstimation(a, b, d, system, clock);
}

@EntryPoint()
operation HHLKernel() : Result[] {
    use system = Qubit();
    use clock = Qubit[3];
    use ancilla = Qubit();
    PrepareHHLState(4.0, -1.0, 3.0, 15.0, 10.0, system, clock, ancilla);
    let ancillaResult = MResetZ(ancilla);
    let systemResult = MResetZ(system);
    ResetAll(clock);
    return [ancillaResult, systemResult];
}
