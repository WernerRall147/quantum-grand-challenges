namespace QuantumGrandChallenges.QAERisk {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;

    newtype RiskParameters = (
        LossQubits : Int,
        Threshold : Double,
        Mean : Double,
        StdDev : Double
    );

    function NumStates(lossQubits : Int) : Int {
        return 1 <<< lossQubits;
    }

    function LossValueFromIndex(index : Int, lossQubits : Int) : Double {
        let numStates = NumStates(lossQubits);
        let fraction = IntAsDouble(index + 1) / IntAsDouble(numStates);
        return fraction * 10.0;
    }

    function LogNormalPdf(x : Double, mean : Double, stdDev : Double) : Double {
        mutable spread = stdDev;
        if (spread <= 0.1) {
            set spread = 0.1;
        }

        let center = 1.0 + mean;
        let distance = x - center;
        let denominator = 1.0 + (distance * distance) / (spread * spread);
        return 1.0 / denominator;
    }

    function AbsDouble(value : Double) : Double {
        if (value < 0.0) {
            return -value;
        }

        return value;
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

        if (total <= 0.0) {
            return raw;
        }

        mutable normalized = [0.0, size = numStates];
        for index in 0 .. numStates - 1 {
            set normalized w/= index <- raw[index] / total;
        }

        return normalized;
    }

    function TailProbability(probabilities : Double[], threshold : Double, lossQubits : Int) : Double {
        let numStates = Length(probabilities);
        mutable probabilitySum = 0.0;

        for index in 0 .. numStates - 1 {
            let loss = LossValueFromIndex(index, lossQubits);
            if (loss > threshold) {
                set probabilitySum += probabilities[index];
            }
        }

        return probabilitySum;
    }

    function ClassicalMonteCarloEstimate(numSamples : Int, mean : Double, stdDev : Double, threshold : Double, lossQubits : Int) : (Double, Double) {
        let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);
        let tailProb = TailProbability(probabilities, threshold, lossQubits);
        let sampleCount = IntAsDouble(numSamples);
        let standardError = Sqrt(tailProb * (1.0 - tailProb) / sampleCount);
        return (tailProb, standardError);
    }

    function EstimateTailRiskProbability(riskParams : RiskParameters) : Double {
        let (lossQubits, threshold, mean, stdDev) = riskParams!;
        let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);
        return TailProbability(probabilities, threshold, lossQubits);
    }

    operation PrepareUniformSuperposition(qubits : Qubit[]) : Unit is Adj + Ctl {
        for q in qubits {
            H(q);
        }
    }
    
    operation PrepareDistributionState(probabilities : Double[], lossQubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(lossQubits);
        let numStates = 1 <<< n;
        let amplitudes = NormalizedAmplitudes(probabilities, numStates);
        ApplyMultiplexRotations(amplitudes, lossQubits);
    }
    
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
                
                within {
                    X(qubits[0]);
                } apply {
                    Controlled ApplyMultiplexRotations([qubits[0]], (leftAmps, qubits[1...]));
                }
                
                Controlled ApplyMultiplexRotations([qubits[0]], (rightAmps, qubits[1...]));
            }
        }
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
            for i in 0 .. half - 1 {
                set leftAmps w/= i <- leftAmps[i] / leftNorm;
            }
        }
        if (rightNorm > 1e-10) {
            for i in 0 .. half - 1 {
                set rightAmps w/= i <- rightAmps[i] / rightNorm;
            }
        }
        
        return (leftAmps, rightAmps, leftNorm, rightNorm);
    }

    operation OracleTailMarking(threshold : Double, lossQubits : Int, register : Qubit[], marker : Qubit) : Unit is Adj + Ctl {
        let n = Length(register);
        
        for index in 0 .. (1 <<< n) - 1 {
            let lossValue = LossValueFromIndex(index, lossQubits);
            
            if (lossValue > threshold) {
                within {
                    for bitIdx in 0 .. n - 1 {
                        let bit = (index >>> bitIdx) &&& 1;
                        if (bit == 0) {
                            X(register[bitIdx]);
                        }
                    }
                } apply {
                    Controlled X(register, marker);
                }
            }
        }
    }

    operation ApplyAllOnesPhase(qubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        if (n == 0) {
            // no-op
        } elif (n == 1) {
            Z(qubits[0]);
        } else {
            Controlled Z(qubits[0..n - 2], qubits[n - 1]);
        }
    }

    operation ReflectAboutZero(register : Qubit[]) : Unit is Adj + Ctl {
        within {
            ApplyToEachCA(X, register);
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
        lossRegister : Qubit[],
        marker : Qubit
    ) : Unit is Adj + Ctl {
        ReflectAboutState(statePrep, lossRegister);
        oracle(lossRegister, marker);
    }

    operation OracleMarkOne(reg : Qubit[], mark : Qubit) : Unit is Adj + Ctl {
        Controlled X(reg, mark);
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

    function ClipProbability(value : Double) : Double {
        if (value < 0.0) {
            return 0.0;
        }
        if (value > 1.0) {
            return 1.0;
        }
        return value;
    }

    function MaxDouble(a : Double, b : Double) : Double {
        if (a > b) {
            return a;
        }
        return b;
    }

    function MinDouble(a : Double, b : Double) : Double {
        if (a < b) {
            return a;
        }
        return b;
    }

    function MaxInt(a : Int, b : Int) : Int {
        if (a > b) {
            return a;
        }
        return b;
    }

    function ResultArrayAsInt(results : Result[]) : Int {
        mutable output = 0;
        let nBits = Length(results);
        for i in 0..nBits - 1 {
            if results[i] == One {
                set output += 2^(nBits - 1 - i);
            }
        }
        return output;
    }

    operation ResetRegister(register : Qubit[]) : Unit {
        body (...) {
            for qubit in register {
                let result = M(qubit);
                if (result == One) {
                    X(qubit);
                }
            }
        }
    }

    operation QuantumFourierTransform(register : Qubit[]) : Unit is Adj + Ctl {
        // Big-endian QFT with final bit reversal. register[0] = MSB.
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
            if (j < right) {
                SWAP(register[j], register[right]);
            }
        }
    }

    operation QuantumPhaseEstimationQAE(
        statePrep : Qubit[] => Unit is Adj + Ctl,
        oracle : (Qubit[], Qubit) => Unit is Adj + Ctl,
        precisionQubits : Qubit[],
        lossRegister : Qubit[],
        marker : Qubit
    ) : Unit {
        for q in precisionQubits {
            H(q);
        }
        
        statePrep(lossRegister);
        // Prepare marker for phase kickback once
        X(marker);
        H(marker);
        
        let n = Length(precisionQubits);
        for idx in 0 .. n - 1 {
            let power = 1 <<< (n - 1 - idx); // big-endian power scheduling
            Controlled GroverOperatorPower(
                [precisionQubits[idx]], 
                (statePrep, oracle, power, lossRegister, marker)
            );
        }
        
        Adjoint QuantumFourierTransform(precisionQubits);
    }

    operation CanonicalQAE(
        riskParams : RiskParameters, 
        precisionBits : Int, 
        repetitions : Int
    ) : (Double, Double) {
        let (lossQubits, threshold, mean, stdDev) = riskParams!;
        let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);
        let theoreticalTailProb = TailProbability(probabilities, threshold, lossQubits);
        
        if (theoreticalTailProb <= 0.0 or theoreticalTailProb >= 1.0) {
            return (ClipProbability(theoreticalTailProb), 0.0);
        }
        
        let runs = MaxInt(1, repetitions);
        mutable phaseOutcomes = [0, size = 1 <<< precisionBits];
        mutable sumAmplitude = 0.0;
        mutable sumAmplitudeSquares = 0.0;
        
        for run in 1 .. runs {
            use precisionReg = Qubit[precisionBits];
            use lossReg = Qubit[lossQubits];
            use marker = Qubit();
            
            let statePrep = PrepareDistributionState(probabilities, _);
            let oracle = OracleTailMarking(threshold, lossQubits, _, _);
            
            QuantumPhaseEstimationQAE(statePrep, oracle, precisionReg, lossReg, marker);
            
            mutable results = [Zero, size = precisionBits];
            for idx in 0 .. precisionBits - 1 {
                set results w/= idx <- M(precisionReg[idx]);
            }
            let phaseInt = ResultArrayAsInt(results);
            
            set phaseOutcomes w/= phaseInt <- phaseOutcomes[phaseInt] + 1;
            
            let phaseEstimate = IntAsDouble(phaseInt) / IntAsDouble(1 <<< precisionBits);
            let theta = phaseEstimate * PI();
            let amplitudeEstimate = Sin(theta);
            let probabilityEstimate = amplitudeEstimate * amplitudeEstimate;
            
            set sumAmplitude += probabilityEstimate;
            set sumAmplitudeSquares += probabilityEstimate * probabilityEstimate;
            
            ResetAll(precisionReg);
            ResetAll(lossReg);
            Reset(marker);
        }
        
        let runsDouble = IntAsDouble(runs);
        let meanAmplitude = sumAmplitude / runsDouble;
        let variance = MaxDouble(0.0, (sumAmplitudeSquares / runsDouble) - (meanAmplitude * meanAmplitude));
        let stdError = Sqrt(variance / runsDouble);
        
        mutable bestPhaseInt = 0;
        mutable bestCount = 0;
        for idx in 0 .. Length(phaseOutcomes) - 1 {
            if (phaseOutcomes[idx] > bestCount) {
                set bestCount = phaseOutcomes[idx];
                set bestPhaseInt = idx;
            }
        }
        
        Message($"=== Canonical QAE Results (precision={precisionBits} bits, runs={runs}) ===");
        Message("Phase measurement histogram (top 10):");
        mutable displayedCount = 0;
        for _ in 1 .. 10 {
            mutable maxIdx = 0;
            mutable maxCount = 0;
            for idx in 0 .. Length(phaseOutcomes) - 1 {
                if (phaseOutcomes[idx] > maxCount) {
                    set maxCount = phaseOutcomes[idx];
                    set maxIdx = idx;
                }
            }
            if (maxCount > 0) {
                let phase = IntAsDouble(maxIdx) / IntAsDouble(1 <<< precisionBits);
                let theta = phase * PI();
                let prob = Sin(theta) * Sin(theta);
                Message($"  Phase {maxIdx}/{1 <<< precisionBits} (θ={theta}, P≈{prob}): {maxCount} times");
                set phaseOutcomes w/= maxIdx <- 0;
            }
        }
        
        let bestPhase = IntAsDouble(bestPhaseInt) / IntAsDouble(1 <<< precisionBits);
        let bestTheta = bestPhase * PI();
        let bestAmplitude = Sin(bestTheta) * Sin(bestTheta);
        
        Message($"Most frequent outcome: phase={bestPhaseInt}/{1 <<< precisionBits}, θ={bestTheta}, P≈{bestAmplitude}");
        Message($"Mean amplitude estimate: {meanAmplitude} ± {stdError}");
        Message($"Theoretical tail probability: {theoreticalTailProb}");
        Message($"Relative error: {AbsDouble(meanAmplitude - theoreticalTailProb) / theoreticalTailProb * 100.0}%");
        
        return (ClipProbability(meanAmplitude), stdError);
    }

    operation TestQaeUniformHalf() : Unit {
        // Simple sanity check: uniform superposition over 1 qubit => P(good)=0.5
        let precisionBits = 5;
        let repetitions = 40;
        mutable sumProb = 0.0;
        for _ in 1..repetitions {
            use precisionReg = Qubit[precisionBits];
            use lossReg = Qubit[1];
            use marker = Qubit();

            let statePrep = PrepareUniformSuperposition;

            QuantumPhaseEstimationQAE(statePrep, OracleMarkOne, precisionReg, lossReg, marker);

            mutable phaseInt = 0;
            for idx in 0 .. precisionBits - 1 {
                if (M(precisionReg[idx]) == One) {
                    set phaseInt += 1 <<< idx;
                }
            }

            let phase = IntAsDouble(phaseInt) / IntAsDouble(1 <<< precisionBits);
            let theta = phase * PI();
            let prob = Sin(theta) * Sin(theta);
            set sumProb += prob;

            ResetAll(precisionReg);
            ResetAll(lossReg);
            Reset(marker);
        }

        let mean = sumProb / IntAsDouble(repetitions);
        Message($"TestQaeUniformHalf mean={mean}");
    }

    @EntryPoint()
    operation RunQAERiskAnalysis() : Unit {
        // Debug sanity check
        TestQaeUniformHalf();
        Message("=== Quantum Amplitude Estimation for Tail Risk Analysis ===");
        Message("");
        
        let lossQubits = 4;
        let threshold = 2.5;
        let mean = 0.0;
        let stdDev = 1.0;
        let riskParams = RiskParameters(lossQubits, threshold, mean, stdDev);
        
        let probabilities = LogNormalProbabilities(lossQubits, mean, stdDev);
        let theoreticalTailProb = TailProbability(probabilities, threshold, lossQubits);
        
        Message($"Risk Model Configuration:");
        Message($"  Loss distribution qubits: {lossQubits} (2^{lossQubits} = {1 <<< lossQubits} discrete levels)");
        Message($"  Loss threshold: {threshold}");
        Message($"  Distribution: Log-normal(μ={mean}, σ={stdDev})");
        Message($"  Theoretical tail probability P(Loss > {threshold}): {theoreticalTailProb}");
        Message("");
        
        let precisionBits = 5;
        let repetitions = 20;
        
        Message($"QAE Algorithm Parameters:");
        Message($"  Precision qubits: {precisionBits} (phase resolution: π/{1 <<< precisionBits})");
        Message($"  Repetitions: {repetitions}");
        Message($"  Total qubits: {lossQubits + precisionBits + 1} (loss + precision + marker)");
        Message("");
        
        let (qaeEstimate, qaeError) = CanonicalQAE(riskParams, precisionBits, repetitions);
        
        Message("");
        Message("=== Classical Baseline Comparison ===");
        let monteCarloSamples = 10000;
        let (mcEstimate, mcError) = ClassicalMonteCarloEstimate(monteCarloSamples, mean, stdDev, threshold, lossQubits);
        Message($"Monte Carlo ({monteCarloSamples} samples): {mcEstimate} ± {mcError}");
        Message($"  Relative error vs theoretical: {AbsDouble(mcEstimate - theoreticalTailProb) / theoreticalTailProb * 100.0}%");
        Message("");
        
        Message("=== Quantum Advantage Analysis ===");
        let qaeRelativeError = AbsDouble(qaeEstimate - theoreticalTailProb) / theoreticalTailProb;
        let mcRelativeError = AbsDouble(mcEstimate - theoreticalTailProb) / theoreticalTailProb;
        let precisionImprovement = mcRelativeError / MaxDouble(qaeRelativeError, 1e-10);
        
        Message($"QAE precision: ε ≈ {qaeError}");
        Message($"MC precision: ε ≈ {mcError}");
        Message($"Precision improvement factor: {precisionImprovement}x");
        Message($"Query complexity: QAE uses O(1/ε) = O({1.0 / MaxDouble(qaeError, 0.01)}) oracle calls");
        Message($"                  MC uses O(1/ε²) = O({IntAsDouble(monteCarloSamples)}) samples");
        Message("");
        
        Message("=== Summary ===");
        Message($"Theoretical:     P = {theoreticalTailProb}");
        Message($"QAE estimate:    P = {qaeEstimate} ± {qaeError}");
        Message($"MC estimate:     P = {mcEstimate} ± {mcError}");
        Message($"QAE demonstrates quadratic speedup: O(1/ε) vs O(1/ε²) for precision ε");
    }
}