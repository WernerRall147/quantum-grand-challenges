// Main.qs — Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// Evaluate contact energy for a lattice protein conformation.
function EvaluateContactEnergy(contacts : Double[][], assignment : Int[]) : Double {
    mutable energy = 0.0;
    let n = Length(assignment);
    for i in 0 .. n - 1 {
        for j in i + 1 .. n - 1 {
            let w = contacts[i][j];
            if (AbsD(w) > 1e-12 and assignment[i] == assignment[j]) {
                set energy += w;
            }
        }
    }
    return energy;
}

function BruteForceMinEnergy(contacts : Double[][]) : (Double, Int[]) {
    let n = Length(contacts);
    mutable bestE = 1e15;
    mutable bestA = [0, size = n];
    for bits in 0 .. (1 <<< n) - 1 {
        mutable a = [0, size = n];
        for idx in 0 .. n - 1 { set a w/= idx <- (bits >>> idx) &&& 1; }
        let e = EvaluateContactEnergy(contacts, a);
        if (e < bestE) { set bestE = e; set bestA = a; }
    }
    return (bestE, bestA);
}

operation ApplyFoldingCostLayer(contacts : Double[][], gamma : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    for i in 0 .. n - 1 {
        for j in i + 1 .. n - 1 {
            let w = contacts[i][j];
            if (AbsD(w) > 1e-12) {
                CNOT(qubits[i], qubits[j]);
                Rz(2.0 * gamma * w, qubits[j]);
                CNOT(qubits[i], qubits[j]);
            }
        }
    }
}

operation ApplyFoldingMixer(beta : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
    for q in qubits { Rx(2.0 * beta, q); }
}

operation EvaluateFoldingQaoa(contacts : Double[][], gamma : Double, beta : Double, shots : Int) : (Double, Double, Int[]) {
    let n = Length(contacts);
    mutable totalE = 0.0;
    mutable bestE = 1e15;
    mutable bestA = [0, size = n];
    for _ in 1 .. shots {
        use reg = Qubit[n];
        for q in reg { H(q); }
        ApplyFoldingCostLayer(contacts, gamma, reg);
        ApplyFoldingMixer(beta, reg);
        mutable a = [0, size = n];
        for idx in 0 .. n - 1 { if (M(reg[idx]) == One) { set a w/= idx <- 1; } }
        let e = EvaluateContactEnergy(contacts, a);
        set totalE += e;
        if (e < bestE) { set bestE = e; set bestA = a; }
        ResetAll(reg);
    }
    return (totalE / IntAsDouble(shots), bestE, bestA);
}

@EntryPoint()
operation RunProteinFolding() : Unit {
    Message("=== Protein Folding: QAOA Lattice Conformation Search ===");
    Message("");
    let contacts = [
        [0.0, -1.2, -0.3, 0.0],
        [-1.2, 0.0, -0.8, -0.5],
        [-0.3, -0.8, 0.0, -1.0],
        [0.0, -0.5, -1.0, 0.0]
    ];
    let (classicalBest, classicalA) = BruteForceMinEnergy(contacts);
    Message($"Classical optimal energy: {classicalBest}");
    Message($"Classical assignment: {classicalA}");
    Message("");
    let candidates = [0.1, 0.3, 0.5, 0.7, 0.9];
    let shots = 48;
    mutable bestAvg = 1e15;
    mutable bestG = 0.5;
    mutable bestB = 0.5;
    mutable bestFound = [0, size = 4];
    for g in candidates {
        for b in candidates {
            let (avg, _, a) = EvaluateFoldingQaoa(contacts, g, b, shots);
            if (avg < bestAvg) { set bestAvg = avg; set bestG = g; set bestB = b; set bestFound = a; }
        }
    }
    let qaoaE = EvaluateContactEnergy(contacts, bestFound);
    Message($"QAOA best: {bestFound} (energy={qaoaE})");
    mutable ratio = 1.0;
    if (AbsD(classicalBest) > 1e-10) { set ratio = qaoaE / classicalBest; }
    Message($"Approximation ratio: {ratio}");
    Message("");
    Message("QAOA enables exploration of exponential conformation spaces for protein folding.");
}
