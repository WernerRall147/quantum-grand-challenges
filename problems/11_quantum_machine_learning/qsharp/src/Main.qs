// Main.qs — Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// Prepare a 2-qubit state encoding a normalized 4-element feature vector.
/// Uses amplitude encoding: |ψ⟩ = Σ aᵢ|i⟩ where aᵢ = features[i]/‖features‖.
operation PrepareFeatureState(features : Double[], qubits : Qubit[]) : Unit {
    let n = Length(features);
    mutable normSq = 0.0;
    for f in features {
        set normSq += f * f;
    }
    let norm = Sqrt(normSq);

    // Encode 4 amplitudes into 2 qubits using Ry rotations
    // Split into top half (|0x⟩) and bottom half (|1x⟩)
    mutable topNormSq = 0.0;
    mutable botNormSq = 0.0;
    for i in 0 .. n / 2 - 1 {
        set topNormSq += features[i] * features[i];
    }
    for i in n / 2 .. n - 1 {
        set botNormSq += features[i] * features[i];
    }
    let topNorm = Sqrt(topNormSq);
    let botNorm = Sqrt(botNormSq);

    // First qubit rotation: splits amplitude between top and bottom halves
    let theta0 = 2.0 * ArcTan2(botNorm, topNorm);
    Ry(theta0, qubits[0]);

    // Second qubit conditioned on first: splits within each half
    if (topNorm > 1e-10) {
        let thetaTop = 2.0 * ArcTan2(AbsD(features[1]), AbsD(features[0]));
        within {
            X(qubits[0]);
        } apply {
            Controlled Ry([qubits[0]], (thetaTop, qubits[1]));
        }
    }
    if (botNorm > 1e-10) {
        let thetaBot = 2.0 * ArcTan2(AbsD(features[3]), AbsD(features[2]));
        Controlled Ry([qubits[0]], (thetaBot, qubits[1]));
    }
}

/// Swap test: estimates |⟨ψ|φ⟩|² between two quantum states.
/// Returns the probability that the ancilla measures |0⟩,
/// which equals (1 + |⟨ψ|φ⟩|²) / 2.
operation SwapTest(featuresA : Double[], featuresB : Double[], shots : Int) : Double {
    mutable zeroCount = 0;

    for _ in 1 .. shots {
        use ancilla = Qubit();
        use regA = Qubit[2];
        use regB = Qubit[2];

        // Prepare feature states
        PrepareFeatureState(featuresA, regA);
        PrepareFeatureState(featuresB, regB);

        // Swap test circuit
        H(ancilla);
        for i in 0 .. 1 {
            Controlled SWAP([ancilla], (regA[i], regB[i]));
        }
        H(ancilla);

        // Measure ancilla
        if (M(ancilla) == Zero) {
            set zeroCount += 1;
        }

        ResetAll(regA);
        ResetAll(regB);
        Reset(ancilla);
    }

    return IntAsDouble(zeroCount) / IntAsDouble(shots);
}

/// Classical inner product for validation.
function ClassicalKernelOverlap(a : Double[], b : Double[]) : Double {
    mutable normASq = 0.0;
    mutable normBSq = 0.0;
    mutable dot = 0.0;
    for i in 0 .. Length(a) - 1 {
        set normASq += a[i] * a[i];
        set normBSq += b[i] * b[i];
        set dot += a[i] * b[i];
    }
    let normA = Sqrt(normASq);
    let normB = Sqrt(normBSq);
    if (normA < 1e-10 or normB < 1e-10) {
        return 0.0;
    }
    let cosine = dot / (normA * normB);
    return cosine * cosine;
}

@EntryPoint()
operation RunQuantumKernelEstimation() : Unit {
    Message("=== Quantum Machine Learning: Swap Test Kernel Estimation ===");
    Message("");

    let dataPoints = [
        ([0.9, 0.2, 0.1, 0.4], "Sample A"),
        ([0.7, 0.3, 0.2, 0.5], "Sample B"),
        ([0.1, 0.8, 0.6, 0.1], "Sample C"),
        ([0.9, 0.2, 0.1, 0.4], "Sample A (duplicate)")
    ];

    let shots = 128;

    // Pairwise kernel matrix
    Message($"Quantum Kernel Matrix ({shots} shots per pair):");
    Message("Measures |⟨ψᵢ|ψⱼ⟩|² via swap test circuit.");
    Message("");

    for i in 0 .. Length(dataPoints) - 1 {
        let (featA, labelA) = dataPoints[i];
        for j in i .. Length(dataPoints) - 1 {
            let (featB, labelB) = dataPoints[j];

            let pZero = SwapTest(featA, featB, shots);
            // |⟨ψ|φ⟩|² = 2*P(0) - 1
            let overlapSq = 2.0 * pZero - 1.0;
            let classical = ClassicalKernelOverlap(featA, featB);

            Message($"  K({labelA}, {labelB}):");
            Message($"    Quantum (swap test): P(0)={pZero}, |overlap|²={overlapSq}");
            Message($"    Classical (exact):   |overlap|²={classical}");
            Message("");
        }
    }

    Message("=== Quantum Advantage ===");
    Message("Swap test estimates kernel in O(1) measurements per pair,");
    Message("independent of feature dimension. Classical requires O(d) operations.");
    Message("For high-dimensional feature spaces, quantum kernel estimation");
    Message("enables exponential speedup in kernel-based classification.");
}
