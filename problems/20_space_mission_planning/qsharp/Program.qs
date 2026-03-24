namespace QuantumGrandChallenges.SpaceMission {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    /// Evaluate trajectory cost: sum of delta-v penalties for selected legs.
    /// Each qubit selects one of two trajectory options for each mission leg.
    function EvaluateTrajectory(deltaV : Double[][], assignment : Int[]) : Double {
        mutable cost = 0.0;
        let n = Length(assignment);
        for i in 0 .. n - 1 {
            // Each leg has two options: assignment[i]=0 (fast, high dV) or 1 (slow, low dV)
            set cost += deltaV[i][assignment[i]];
        }
        // Penalty for conflicting time windows (pairwise)
        for i in 0 .. n - 1 {
            for j in i + 1 .. n - 1 {
                if (assignment[i] == assignment[j]) {
                    set cost += 0.5;  // Time window conflict penalty
                }
            }
        }
        return cost;
    }

    /// Classical brute-force: find minimum cost trajectory.
    function BruteForceOptimal(deltaV : Double[][]) : (Double, Int[]) {
        let n = Length(deltaV);
        mutable bestCost = 1e15;
        mutable bestAssignment = [0, size = n];
        for bits in 0 .. (1 <<< n) - 1 {
            mutable assignment = [0, size = n];
            for idx in 0 .. n - 1 {
                set assignment w/= idx <- (bits >>> idx) &&& 1;
            }
            let cost = EvaluateTrajectory(deltaV, assignment);
            if (cost < bestCost) {
                set bestCost = cost;
                set bestAssignment = assignment;
            }
        }
        return (bestCost, bestAssignment);
    }

    /// QAOA cost layer: encodes trajectory penalties as ZZ and Z interactions.
    operation ApplyCostLayer(deltaV : Double[][], gamma : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        // Single-qubit Z rotations for delta-v costs
        for i in 0 .. n - 1 {
            let bias = (deltaV[i][0] - deltaV[i][1]) / 2.0;
            Rz(2.0 * gamma * bias, qubits[i]);
        }
        // Pairwise ZZ for time window conflict penalties
        for i in 0 .. n - 1 {
            for j in i + 1 .. n - 1 {
                CNOT(qubits[i], qubits[j]);
                Rz(gamma * 0.5, qubits[j]);
                CNOT(qubits[i], qubits[j]);
            }
        }
    }

    /// QAOA mixer layer.
    operation ApplyMixerLayer(beta : Double, qubits : Qubit[]) : Unit is Adj + Ctl {
        for q in qubits {
            Rx(2.0 * beta, q);
        }
    }

    /// Evaluate one QAOA circuit run.
    operation EvaluateQaoaMission(deltaV : Double[][], gamma : Double, beta : Double, depth : Int, shots : Int) : (Double, Double, Int[]) {
        let n = Length(deltaV);
        mutable totalCost = 0.0;
        mutable bestCost = 1e15;
        mutable bestAssignment = [0, size = n];

        for _ in 1 .. shots {
            use register = Qubit[n];
            for q in register { H(q); }
            for _ in 1 .. depth {
                ApplyCostLayer(deltaV, gamma, register);
                ApplyMixerLayer(beta, register);
            }
            mutable assignment = [0, size = n];
            for idx in 0 .. n - 1 {
                if (M(register[idx]) == One) {
                    set assignment w/= idx <- 1;
                }
            }
            let cost = EvaluateTrajectory(deltaV, assignment);
            set totalCost += cost;
            if (cost < bestCost) {
                set bestCost = cost;
                set bestAssignment = assignment;
            }
            ResetAll(register);
        }
        return (totalCost / IntAsDouble(shots), bestCost, bestAssignment);
    }

    @EntryPoint()
    operation RunMissionOptimization() : Unit {
        Message("=== Space Mission Planning: QAOA Trajectory Optimization ===");
        Message("");

        // 4 mission legs, each with 2 trajectory options (delta-v in km/s)
        // Option 0 = fast transfer (high delta-v), Option 1 = slow transfer (low delta-v)
        let deltaV = [
            [2.5, 1.8],   // LEO -> GTO
            [1.2, 0.8],   // GTO -> Lunar orbit
            [3.1, 2.4],   // Lunar -> Mars transfer
            [1.5, 1.0]    // Mars orbit insertion
        ];
        let n = Length(deltaV);

        let (classicalBest, classicalAssignment) = BruteForceOptimal(deltaV);
        Message($"Classical brute-force ({1 <<< n} trajectories):");
        Message($"  Optimal delta-v cost: {classicalBest} km/s");
        Message($"  Assignment: {classicalAssignment}");
        Message("");

        // QAOA parameter sweep
        let candidates = [0.1, 0.3, 0.5, 0.7, 0.9];
        let shots = 48;
        mutable bestGamma = 0.5;
        mutable bestBeta = 0.5;
        mutable bestAvg = 1e15;
        mutable bestFound = [0, size = n];

        for gamma in candidates {
            for beta in candidates {
                let (avg, _, assignment) = EvaluateQaoaMission(deltaV, gamma, beta, 1, shots);
                if (avg < bestAvg) {
                    set bestAvg = avg;
                    set bestGamma = gamma;
                    set bestBeta = beta;
                    set bestFound = assignment;
                }
            }
        }

        let qaoaCost = EvaluateTrajectory(deltaV, bestFound);
        Message($"QAOA depth-1 ({shots} shots/pair):");
        Message($"  Best gamma={bestGamma}, beta={bestBeta}");
        Message($"  Best found: {bestFound} (cost={qaoaCost} km/s)");
        Message("");

        mutable ratio = 1.0;
        if (classicalBest > 1e-10) {
            set ratio = qaoaCost / classicalBest;
        }
        Message($"  Approximation ratio: {ratio}");
        Message("");
        Message("QAOA enables efficient exploration of exponentially large trajectory spaces");
        Message("for multi-leg interplanetary missions beyond classical optimizer reach.");
    }
}
