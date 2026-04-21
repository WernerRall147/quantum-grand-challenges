// Main.qs — Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// Evaluate a weighted tardiness cost for a given binary assignment.
/// Each qubit represents machine assignment (0 or 1) for a job.
/// Cost penalizes overloaded machines via pairwise ZZ interactions.
function EvaluateScheduleCost(weights : Double[][], assignment : Int[]) : Double {
    mutable cost = 0.0;
    let n = Length(assignment);
    for i in 0 .. n - 1 {
        for j in i + 1 .. n - 1 {
            let w = weights[i][j];
            if (AbsD(w) > 1e-12 and assignment[i] == assignment[j]) {
                // Penalty when two heavy jobs land on the same machine
                set cost += w;
            }
        }
    }
    return cost;
}

/// Classical brute-force: find the minimum cost assignment.
function BruteForceMinCost(weights : Double[][]) : (Double, Int[]) {
    let n = Length(weights);
    mutable bestCost = 1e15;
    mutable bestAssignment = [0, size = n];
    for bits in 0 .. (1 <<< n) - 1 {
        mutable assignment = [0, size = n];
        for idx in 0 .. n - 1 {
            set assignment w/= idx <- (bits >>> idx) &&& 1;
        }
        let cost = EvaluateScheduleCost(weights, assignment);
        if (cost < bestCost) {
            set bestCost = cost;
            set bestAssignment = assignment;
        }
    }
    return (bestCost, bestAssignment);
}

/// QAOA cost layer: exp(-i * gamma * w_ij * Z_i Z_j) for each edge.
operation ApplyCostLayer(weights : Double[][], gamma : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
    let n = Length(qubits);
    for i in 0 .. n - 1 {
        for j in i + 1 .. n - 1 {
            let w = weights[i][j];
            if (AbsD(w) > 1e-12) {
                // ZZ interaction via CNOT-Rz-CNOT decomposition
                CNOT(qubits[i], qubits[j]);
                Rz(2.0 * gamma * w, qubits[j]);
                CNOT(qubits[i], qubits[j]);
            }
        }
    }
}

/// QAOA mixer layer: Rx(2*beta) on each qubit.
operation ApplyMixerLayer(beta : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
    for qubit in qubits {
        Rx(2.0 * beta, qubit);
    }
}

/// Evaluate a single QAOA circuit: returns (average cost, best cost, best assignment).
operation EvaluateQaoa(weights : Double[][], gamma : Double, beta : Double, depth : Int, shots : Int) : (Double, Double, Int[]) {
    let n = Length(weights);
    mutable totalCost = 0.0;
    mutable bestCost = 1e15;
    mutable bestAssignment = [0, size = n];

    for _ in 1 .. shots {
        use register = Qubit[n];

        // Uniform superposition
        for q in register {
            H(q);
        }

        // QAOA layers
        for _ in 1 .. depth {
            ApplyCostLayer(weights, gamma, register);
            ApplyMixerLayer(beta, register);
        }

        // Measure
        mutable assignment = [0, size = n];
        for idx in 0 .. n - 1 {
            if (M(register[idx]) == One) {
                set assignment w/= idx <- 1;
            }
        }

        let cost = EvaluateScheduleCost(weights, assignment);
        set totalCost += cost;
        if (cost < bestCost) {
            set bestCost = cost;
            set bestAssignment = assignment;
        }

        ResetAll(register);
    }

    return (totalCost / IntAsDouble(shots), bestCost, bestAssignment);
}

/// Simple parameter sweep to find best gamma/beta.
operation OptimizeQaoa(weights : Double[][], depth : Int, shots : Int) : (Double, Double, Double, Int[]) {
    let candidates = [0.1, 0.3, 0.5, 0.7, 0.9];
    mutable bestGamma = 0.5;
    mutable bestBeta = 0.5;
    mutable bestAvgCost = 1e15;
    mutable bestAssignment = [0, size = Length(weights)];

    for gamma in candidates {
        for beta in candidates {
            let (avgCost, _, assignment) = EvaluateQaoa(weights, gamma, beta, depth, shots);
            if (avgCost < bestAvgCost) {
                set bestAvgCost = avgCost;
                set bestGamma = gamma;
                set bestBeta = beta;
                set bestAssignment = assignment;
            }
        }
    }

    return (bestGamma, bestBeta, bestAvgCost, bestAssignment);
}

@EntryPoint()
operation RunSchedulingOptimization() : Unit {
    Message("=== Quantum Optimization: QAOA for Weighted Job Scheduling ===");
    Message("");

    // 4-job, 2-machine scheduling as pairwise penalty weights.
    // w[i][j] = penalty when jobs i and j are assigned to the same machine.
    // Higher weight = jobs compete more for the same resource.
    let weights = [
        [0.0, 1.0, 0.5, 0.2],
        [1.0, 0.0, 1.2, 0.8],
        [0.5, 1.2, 0.0, 0.6],
        [0.2, 0.8, 0.6, 0.0]
    ];
    let n = Length(weights);

    // Classical brute-force baseline
    let (classicalBest, classicalAssignment) = BruteForceMinCost(weights);
    Message($"Classical brute-force (N={n} jobs, 2^{n}={1 <<< n} assignments):");
    Message($"  Optimal cost: {classicalBest}");
    Message($"  Assignment:   {classicalAssignment}");
    Message("");

    // QAOA depth-1
    let depth = 1;
    let shots = 48;
    let (gamma, beta, avgCost, qaoaAssignment) = OptimizeQaoa(weights, depth, shots);
    Message($"QAOA depth-{depth} ({shots} shots per parameter pair):");
    Message($"  Best gamma={gamma}, beta={beta}");
    Message($"  Average cost: {avgCost}");
    Message($"  Best found:   {qaoaAssignment}");
    let qaoaBestCost = EvaluateScheduleCost(weights, qaoaAssignment);
    Message($"  Best cost:    {qaoaBestCost}");
    Message("");

    mutable approxRatio = 1.0;
    if (classicalBest > 1e-10) {
        set approxRatio = qaoaBestCost / classicalBest;
    }
    Message($"  Approximation ratio: {approxRatio} (1.0 = optimal)");
    Message("");
    Message("QAOA provides heuristic optimization with potential quantum advantage");
    Message("for large-scale scheduling problems beyond classical solver reach.");
}
