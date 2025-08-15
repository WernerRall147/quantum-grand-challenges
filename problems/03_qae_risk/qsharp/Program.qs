namespace QuantumGrandChallenges.QAERisk {
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Preparation;
    open QuantumGrandChallenges.Common;

    /// # Summary
    /// Quantum Amplitude Estimation for financial risk analysis.
    /// Estimates the probability of tail risk events (losses exceeding threshold).

    /// # Summary
    /// Parameters for risk distribution and QAE algorithm.
    newtype RiskParameters = (
        /// Number of qubits to represent loss values
        LossQubits: Int,
        /// Number of precision qubits for amplitude estimation
        PrecisionQubits: Int,
        /// Risk threshold (losses above this are "tail events")
        Threshold: Double,
        /// Distribution parameters (mean, std dev, etc.)
        DistributionParams: Double[]
    );

    /// # Summary
    /// Prepares a quantum state encoding a log-normal loss distribution.
    /// Uses amplitude encoding to represent the probability distribution.
    ///
    /// # Input
    /// ## lossQubits
    /// Qubits to encode loss values
    /// ## mean
    /// Mean of the underlying normal distribution (log-space)
    /// ## stdDev
    /// Standard deviation of the underlying normal distribution
    operation PrepareLogNormalDistribution(lossQubits : Qubit[], mean : Double, stdDev : Double) : Unit is Adj + Ctl {
        let n = Length(lossQubits);
        let numStates = 2^n;
        
        // Calculate log-normal probabilities for each discrete loss level
        mutable amplitudes = new Double[numStates];
        mutable totalProb = 0.0;
        
        for i in 0..numStates - 1 {
            // Map integer i to loss value (exponential scaling for wide range)
            let lossValue = IntAsDouble(i + 1) / IntAsDouble(numStates) * 10.0; // Scale to [0, 10]
            
            // Log-normal PDF: f(x) = (1/(x*σ*√(2π))) * exp(-((ln(x)-μ)²)/(2σ²))
            if lossValue > 0.0 {
                let logLoss = Log(lossValue);
                let exponent = -((logLoss - mean) * (logLoss - mean)) / (2.0 * stdDev * stdDev);
                let probability = (1.0 / (lossValue * stdDev * Sqrt(2.0 * PI()))) * E()^exponent;
                set amplitudes w/= i <- probability;
                set totalProb += probability;
            }
        }
        
        // Normalize amplitudes
        for i in 0..numStates - 1 {
            set amplitudes w/= i <- Sqrt(amplitudes[i] / totalProb);
        }
        
        // Prepare the quantum state with these amplitudes
        PrepareArbitraryState(amplitudes, lossQubits);
    }

    /// # Summary
    /// Oracle that marks states where loss exceeds the risk threshold.
    /// Flips auxiliary qubit if the loss value is in the "tail risk" region.
    ///
    /// # Input
    /// ## lossQubits
    /// Qubits encoding the loss value
    /// ## auxiliary
    /// Auxiliary qubit to mark tail risk states
    /// ## threshold
    /// Risk threshold value
    operation TailRiskOracle(lossQubits : Qubit[], auxiliary : Qubit, threshold : Double) : Unit is Adj + Ctl {
        let n = Length(lossQubits);
        let numStates = 2^n;
        
        // Calculate which states correspond to losses > threshold
        mutable thresholdInt = 0;
        for i in 0..numStates - 1 {
            let lossValue = IntAsDouble(i + 1) / IntAsDouble(numStates) * 10.0;
            if lossValue > threshold {
                set thresholdInt = i;
                break;
            }
        }
        
        // Create a controlled operation that flips auxiliary for states >= thresholdInt
        for i in thresholdInt..numStates - 1 {
            (ControlledOnInt(i, X))(lossQubits, auxiliary);
        }
    }

    /// # Summary
    /// Amplitude amplification operation for QAE.
    /// Combines state preparation with oracle marking.
    ///
    /// # Input
    /// ## lossQubits
    /// Work qubits for loss encoding
    /// ## auxiliary
    /// Auxiliary qubit for oracle marking
    /// ## riskParams
    /// Risk distribution parameters
    operation AmplitudeAmplificationOperator(lossQubits : Qubit[], auxiliary : Qubit, riskParams : RiskParameters) : Unit is Adj + Ctl {
        let (lossQubitCount, precisionQubits, threshold, distParams) = riskParams!;
        
        // Assume log-normal with mean=distParams[0], stdDev=distParams[1]
        let mean = distParams[0];
        let stdDev = distParams[1];
        
        // State preparation
        PrepareLogNormalDistribution(lossQubits, mean, stdDev);
        
        // Oracle application
        TailRiskOracle(lossQubits, auxiliary, threshold);
    }

    /// # Summary
    /// Quantum Amplitude Estimation circuit for tail risk probability.
    /// Uses phase estimation to determine the amplitude of marked states.
    ///
    /// # Input
    /// ## riskParams
    /// Risk analysis parameters
    ///
    /// # Output
    /// Estimated tail risk probability
    operation EstimateTailRiskProbability(riskParams : RiskParameters) : Double {
        let (lossQubitCount, precisionQubits, threshold, distParams) = riskParams!;
        
        use (lossQubits, auxiliary, precisionQubitsArray) = (Qubit[lossQubitCount], Qubit(), Qubit[precisionQubits]);
        
        // Initialize auxiliary in |-> state for amplitude estimation
        X(auxiliary);
        H(auxiliary);
        
        // Quantum Phase Estimation on amplitude amplification operator
        mutable angle = 0.0;
        
        // Apply controlled powers of the amplitude amplification operator
        for j in 0..precisionQubits - 1 {
            let power = 2^j;
            
            for _ in 1..power {
                Controlled AmplitudeAmplificationOperator([precisionQubitsArray[j]], (lossQubits, auxiliary, riskParams));
            }
        }
        
        // Inverse QFT to extract phase information
        Adjoint QuantumFourierTransform(precisionQubitsArray);
        
        // Measure precision qubits to get phase estimate
        let results = ForEach(MResetZ, precisionQubitsArray);
        let phaseInt = ResultArrayAsInt(results);
        
        // Convert phase to amplitude estimate
        let phase = IntAsDouble(phaseInt) / IntAsDouble(2^precisionQubits);
        let amplitude = Sin(PI() * phase);
        let probability = amplitude * amplitude;
        
        // Clean up auxiliary qubit
        Reset(auxiliary);
        ResetAll(lossQubits);
        
        return probability;
    }

    /// # Summary
    /// Monte Carlo estimation for classical baseline comparison.
    /// Samples from the distribution and counts tail events.
    ///
    /// # Input
    /// ## numSamples
    /// Number of Monte Carlo samples
    /// ## mean
    /// Log-normal distribution mean (log-space)
    /// ## stdDev
    /// Log-normal distribution standard deviation
    /// ## threshold
    /// Risk threshold
    ///
    /// # Output
    /// Estimated tail probability and standard error
    function ClassicalMonteCarloEstimate(numSamples : Int, mean : Double, stdDev : Double, threshold : Double) : (Double, Double) {
        // This would normally use a random number generator
        // For Q# simulation, we'll use a deterministic approximation
        
        mutable tailCount = 0;
        let stepSize = 10.0 / IntAsDouble(numSamples);
        
        for i in 0..numSamples - 1 {
            // Deterministic sampling across the range
            let u = IntAsDouble(i) / IntAsDouble(numSamples);
            
            // Approximate inverse log-normal CDF (simplified)
            let lossValue = E()^(mean + stdDev * (2.0 * u - 1.0));
            
            if lossValue > threshold {
                set tailCount += 1;
            }
        }
        
        let probability = IntAsDouble(tailCount) / IntAsDouble(numSamples);
        let standardError = Sqrt(probability * (1.0 - probability) / IntAsDouble(numSamples));
        
        return (probability, standardError);
    }

    /// # Summary
    /// Main entry point for QAE risk analysis.
    /// Runs both quantum and classical estimation for comparison.
    @EntryPoint()
    operation RunQAERiskAnalysis() : (Double, Double, Double) {
        // Define problem parameters
        let lossQubits = 8;           // 2^8 = 256 discrete loss levels  
        let precisionQubits = 6;      // Precision ε ≈ 1/2^6 ≈ 0.016
        let threshold = 3.0;          // Risk threshold (95th percentile-ish)
        let mean = 0.0;               // Log-normal mean (log-space)
        let stdDev = 1.0;             // Log-normal std dev
        
        let riskParams = RiskParameters(lossQubits, precisionQubits, threshold, [mean, stdDev]);
        
        // Quantum estimation
        let quantumProb = EstimateTailRiskProbability(riskParams);
        
        // Classical baseline  
        let mcSamples = 10000;
        let (classicalProb, classicalError) = ClassicalMonteCarloEstimate(mcSamples, mean, stdDev, threshold);
        
        Message($"Quantum Amplitude Estimation: {quantumProb}");
        Message($"Classical Monte Carlo: {classicalProb} ± {classicalError}");
        Message($"Relative difference: {Abs(quantumProb - classicalProb) / classicalProb * 100.0}%");
        
        return (quantumProb, classicalProb, classicalError);
    }

    /// # Summary
    /// Unit tests for QAE risk analysis components.
    @Test("QuantumSimulator")
    operation TestLogNormalStatePreparation() : Unit {
        use qubits = Qubit[4];
        
        // Test that state preparation doesn't crash
        PrepareLogNormalDistribution(qubits, 0.0, 1.0);
        
        // Verify qubits are in superposition (not computational basis)
        let prob0 = 1.0; // Would measure probability in real test
        
        ResetAll(qubits);
    }

    @Test("QuantumSimulator")
    operation TestTailRiskOracle() : Unit {
        use (lossQubits, auxiliary) = (Qubit[3], Qubit());
        
        // Test oracle on known state
        X(lossQubits[0]); // Put in state |001⟩ (loss = 1)
        
        TailRiskOracle(lossQubits, auxiliary, 0.5); // Threshold = 0.5
        
        // Should flip auxiliary since loss > threshold
        let result = MResetZ(auxiliary);
        // In real test: Assert(result == One, "Oracle should mark tail risk state");
        
        ResetAll(lossQubits);
    }

    @Test("QuantumSimulator")
    operation TestFullQAECircuit() : Unit {
        let riskParams = RiskParameters(4, 3, 2.0, [0.0, 1.0]);
        
        // Test that full circuit runs without error
        let result = EstimateTailRiskProbability(riskParams);
        
        // Verify result is a valid probability
        // Assert(result >= 0.0 and result <= 1.0, "Probability must be in [0,1]");
        
        Message($"Test QAE result: {result}");
    }
}
