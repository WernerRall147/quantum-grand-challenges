namespace QuantumGrandChallenges.DatabaseSearch.Estimation {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.ResourceEstimation;
    
    /// # Summary
    /// Marks target indices using phase flip (for resource estimation).
    operation MarkTargetIndicesForEstimation(targets : Int[], qubits : Qubit[]) : Unit {
        for target in targets {
            within {
                for i in 0..Length(qubits) - 1 {
                    if (target &&& (1 <<< i)) == 0 {
                        X(qubits[Length(qubits) - 1 - i]);
                    }
                }
            } apply {
                Controlled Z(Most(qubits), Tail(qubits));
            }
        }
    }
    
    /// # Summary
    /// Diffusion operator for resource estimation.
    operation DiffusionOperatorForEstimation(qubits : Qubit[]) : Unit {
        ApplyToEach(H, qubits);
        ApplyToEach(X, qubits);
        Controlled Z(Most(qubits), Tail(qubits));
        ApplyToEach(X, qubits);
        ApplyToEach(H, qubits);
    }
    
    /// # Summary
    /// Single Grover iteration for resource estimation.
    operation GroverIterationForEstimation(targets : Int[], qubits : Qubit[]) : Unit {
        MarkTargetIndicesForEstimation(targets, qubits);
        DiffusionOperatorForEstimation(qubits);
    }
    
    /// # Summary
    /// Entry point for resource estimation of Grover's algorithm.
    /// Estimates resources for searching a database of 2^numQubits items
    /// for a specified number of target items.
    @EntryPoint()
    operation EstimateGroverResources() : Unit {
        // Scenario 1: Small search (4 qubits, 1 target)
        let numQubits1 = 12;
        let targets1 = [42];
        let markedFraction1 = IntAsDouble(Length(targets1)) / IntAsDouble(2^numQubits1);
        let amplitude1 = Sqrt(markedFraction1);
        let theta1 = ArcSin(amplitude1);
        let iterations1 = Floor(PI() / (4.0 * theta1) - 0.5);
        
        use qubits = Qubit[numQubits1];
        
        // Initialize to uniform superposition
        ApplyToEach(H, qubits);
        
        // Apply optimal number of Grover iterations
        for _ in 1..iterations1 {
            GroverIterationForEstimation(targets1, qubits);
        }
        
        // Measurement (accounted for in estimation)
        let results = ForEach(M, qubits);
        
        ResetAll(qubits);
    }
}
