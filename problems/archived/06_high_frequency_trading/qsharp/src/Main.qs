// Main.qs  Migrated to modern QDK (qsharp.json project format)

import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// Encode four non-negative weights as amplitudes of two qubits (|i⟩ gets probability
/// w_i² / Σ w²). Only the one- and two-qubit cases are implemented; with two qubits the
/// weights array must have four entries, or the second qubit is left in |0⟩.
operation PrepareMarketState(returns : Double[], qubits : Qubit[]) : Unit {
    let n = Length(qubits);
    if (n == 1 and Length(returns) >= 2) {
        let angle = 2.0 * ArcTan2(AbsD(returns[1]), AbsD(returns[0]));
        Ry(angle, qubits[0]);
    } elif (n >= 2) {
        mutable topSq = 0.0;
        mutable botSq = 0.0;
        let half = Length(returns) / 2;
        for i in 0 .. half - 1 { set topSq += returns[i] * returns[i]; }
        for i in half .. Length(returns) - 1 { set botSq += returns[i] * returns[i]; }
        let angle = 2.0 * ArcTan2(Sqrt(botSq), Sqrt(topSq));
        Ry(angle, qubits[0]);
        if (half >= 2 and topSq > 1e-12) {
            within { X(qubits[0]); }
            apply { Controlled Ry([qubits[0]], (2.0 * ArcTan2(AbsD(returns[1]), AbsD(returns[0])), qubits[1])); }
        }
        if (half >= 2 and botSq > 1e-12) {
            Controlled Ry([qubits[0]], (2.0 * ArcTan2(AbsD(returns[3]), AbsD(returns[2])), qubits[1]));
        }
    }
}

/// Oracle: mark portfolio states where index < threshold (loss states).
operation MarkLossStates(threshold : Int, qubits : Qubit[], marker : Qubit) : Unit is Adj + Ctl {
    let n = Length(qubits);
    for idx in 0 .. threshold - 1 {
        within {
            for bit in 0 .. n - 1 {
                if ((idx >>> (n - 1 - bit)) &&& 1) == 0 {
                    X(qubits[bit]);
                }
            }
        } apply {
            Controlled X(qubits, marker);
        }
    }
}

/// Estimate P(index < threshold) by preparing the state and measuring the marker once per
/// shot. This is direct sampling, not amplitude estimation: its error falls as 1/√shots, like
/// classical Monte Carlo, and it has no quantum speedup.
operation EstimateLossProbability(returns : Double[], thresholdIdx : Int, shots : Int) : Double {
    let n = 2;
    mutable totalProb = 0.0;
    for _ in 1 .. shots {
        use register = Qubit[n];
        use marker = Qubit();
        PrepareMarketState(returns, register);
        MarkLossStates(thresholdIdx, register, marker);
        if (M(marker) == One) { set totalProb += 1.0; }
        ResetAll(register);
        Reset(marker);
    }
    return totalProb / IntAsDouble(shots);
}

@EntryPoint()
operation RunHFTAnalysis() : Unit {
    Message("=== High-frequency trading toy: sampling a loss probability from a 2-qubit state ===");
    Message("");
    let returns = [0.5, 0.35, 0.1, 0.05];
    let thresholdIdx = 2;
    let shots = 256;
    mutable lossWeight = 0.0;
    mutable totalSq = 0.0;
    for i in 0 .. 3 { set totalSq += returns[i] * returns[i]; }
    for i in 0 .. thresholdIdx - 1 { set lossWeight += returns[i] * returns[i]; }
    let exactLoss = lossWeight / totalSq;
    Message($"Exact P(index < {thresholdIdx}): {exactLoss}");
    let sampled = EstimateLossProbability(returns, thresholdIdx, shots);
    Message($"Sampled estimate ({shots} shots): {sampled}");
    Message($"Standard error at this shot count: {Sqrt(exactLoss * (1.0 - exactLoss) / IntAsDouble(shots))}");
    Message("");
    Message("This samples the marked states directly. It is not amplitude estimation and has no speedup;");
    Message("amplitude estimation on this oracle would give a quadratic one (see problem 03).");
}
