namespace QuantumGrandChallenges.DatabaseSearch {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Measurement;

    /// # Summary
    /// Calculates the optimal number of Grover iterations for a given marked fraction.
    ///
    /// # Input
    /// ## markedFraction
    /// Fraction of marked items in the search space (M/N)
    ///
    /// # Output
    /// Optimal number of Grover iterations
    function CalculateGroverIterations(markedFraction : Double) : Int {
        if markedFraction <= 0.0 or markedFraction >= 1.0 {
            return 0;
        }
        
        let amplitude = Sqrt(markedFraction);
        let theta = ArcSin(amplitude);
        
        // Optimal iterations: floor((π/4θ) - 1/2)
        let optimalRounds = Floor(PI() / (4.0 * theta) - 0.5);
        return MaxI(1, optimalRounds);
    }

    /// # Summary
    /// Predicts the success probability after k Grover iterations.
    ///
    /// # Input
    /// ## markedFraction
    /// Fraction of marked items (M/N)
    /// ## iterations
    /// Number of Grover iterations applied
    ///
    /// # Output
    /// Predicted success probability
    function PredictSuccessProbability(markedFraction : Double, iterations : Int) : Double {
        let amplitude = Sqrt(markedFraction);
        let theta = ArcSin(amplitude);
        let finalAngle = IntAsDouble(2 * iterations + 1) * theta;
        return Sin(finalAngle) * Sin(finalAngle);
    }

    /// # Summary
    /// Oracle that marks specific target indices by flipping the phase.
    /// 
    /// # Description
    /// This oracle marks target states by applying a phase flip when the
    /// input qubits encode one of the target indices.
    ///
    /// # Input
    /// ## targets
    /// Array of target indices to mark (e.g., [3, 7, 12])
    /// ## qubits
    /// Search register qubits
    operation MarkTargetIndices(targets : Int[], qubits : Qubit[]) : Unit {
        for target in targets {
            // Mark |target⟩ with phase flip using controlled-on-bitstring pattern
            within {
                // Flip qubits where target has 0 bits
                for i in 0..Length(qubits) - 1 {
                    if (target &&& (1 <<< i)) == 0 {
                        X(qubits[Length(qubits) - 1 - i]);
                    }
                }
            } apply {
                // Apply phase flip to |11...1⟩ state (marked target)
                Controlled Z(Most(qubits), Tail(qubits));
            }
        }
    }

    /// # Summary
    /// Diffusion operator (also called inversion-about-average).
    ///
    /// # Description
    /// Reflects all amplitudes around their average value. This is the key
    /// amplitude amplification step in Grover's algorithm.
    /// Implements: 2|s⟩⟨s| - I where |s⟩ is the uniform superposition.
    ///
    /// # Input
    /// ## qubits
    /// Array of qubits to apply diffusion to
    operation DiffusionOperator(qubits : Qubit[]) : Unit {
        // Transform to computational basis
        ApplyToEach(H, qubits);
        ApplyToEach(X, qubits);
        
        // Multi-controlled Z on |11...1⟩ state
        Controlled Z(Most(qubits), Tail(qubits));
        
        // Transform back
        ApplyToEach(X, qubits);
        ApplyToEach(H, qubits);
    }

    /// # Summary
    /// Single Grover iteration: Oracle + Diffusion.
    ///
    /// # Description
    /// One complete Grover iteration consists of:
    /// 1. Apply oracle to mark target states
    /// 2. Apply diffusion operator to amplify marked amplitudes
    ///
    /// # Input
    /// ## targets
    /// Target indices to search for
    /// ## qubits
    /// Search register
    operation GroverIteration(targets : Int[], qubits : Qubit[]) : Unit {
        MarkTargetIndices(targets, qubits);
        DiffusionOperator(qubits);
    }

    /// # Summary
    /// Runs Grover's search algorithm for specified targets.
    ///
    /// # Description
    /// Complete implementation of Grover's quantum search algorithm:
    /// 1. Initialize to uniform superposition
    /// 2. Apply optimal number of Grover iterations
    /// 3. Measure to find marked item
    ///
    /// # Input
    /// ## targets
    /// Array of target indices to search for
    /// ## numQubits
    /// Number of qubits (search space size = 2^numQubits)
    /// ## iterations
    /// Number of Grover iterations to apply (use CalculateGroverIterations for optimal)
    ///
    /// # Output
    /// Measured index from the search space
    operation GroverSearch(targets : Int[], numQubits : Int, iterations : Int) : Int {
        use qubits = Qubit[numQubits];
        
        // Step 1: Initialize to uniform superposition
        ApplyToEach(H, qubits);
        
        // Step 2: Apply Grover iterations
        for _ in 1..iterations {
            GroverIteration(targets, qubits);
        }
        
        // Step 3: Measure
        let results = ForEach(M, qubits);
        let measurement = ResultArrayAsInt(results);
        
        // Ensure all qubits are reset
        ResetAll(qubits);
        
        return measurement;
    }

    /// # Summary
    /// Runs multiple Grover search trials and collects statistics.
    ///
    /// # Input
    /// ## targets
    /// Target indices to search for
    /// ## numQubits
    /// Number of search qubits
    /// ## iterations
    /// Number of Grover iterations per trial
    /// ## shots
    /// Number of measurement trials
    ///
    /// # Output
    /// Tuple of (success_count, found_targets, all_measurements)
    operation GroverSearchWithStatistics(
        targets : Int[], 
        numQubits : Int, 
        iterations : Int, 
        shots : Int
    ) : (Int, Int[], Int[]) {
        mutable successCount = 0;
        mutable foundTargets = [false, size = Length(targets)];
        mutable measurements = [0, size = shots];
        
        for shot in 0..shots - 1 {
            let result = GroverSearch(targets, numQubits, iterations);
            set measurements w/= shot <- result;
            
            // Check if we found a target
            mutable isTarget = false;
            for targetIdx in 0..Length(targets) - 1 {
                if result == targets[targetIdx] {
                    set isTarget = true;
                    set foundTargets w/= targetIdx <- true;
                    set successCount += 1;
                }
            }
        }
        
        // Convert boolean array to int array of found target indices
        mutable foundIndices = [];
        for i in 0..Length(targets) - 1 {
            if foundTargets[i] {
                set foundIndices += [targets[i]];
            }
        }
        
        return (successCount, foundIndices, measurements);
    }

    /// # Summary
    /// Utility function to convert measurement results to integer.
    ///
    /// # Input
    /// ## results
    /// Array of measurement results
    ///
    /// # Output
    /// Integer representation of the bit string
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

    /// # Summary
    /// Demonstrates Grover's algorithm on small instances for different scenarios.
    @EntryPoint()
    operation RunGroverDemonstration() : Unit {
        Message("=== Grover's Quantum Database Search Algorithm ===\n");
        
        // Demo 1: Single target in small search space
        Message("Demo 1: Single target search (4 qubits, 16 items)");
        Message("----------------------------------------");
        let numQubits1 = 4;
        let searchSpace1 = 2^numQubits1;
        let targets1 = [7];  // Search for index 7
        let markedFraction1 = IntAsDouble(Length(targets1)) / IntAsDouble(searchSpace1);
        let optimalIterations1 = CalculateGroverIterations(markedFraction1);
        let predictedProb1 = PredictSuccessProbability(markedFraction1, optimalIterations1);
        
        Message($"  Search space: {searchSpace1} items");
        Message($"  Target indices: {targets1}");
        Message($"  Marked fraction: {markedFraction1} ({Length(targets1)}/{searchSpace1})");
        Message($"  Optimal iterations: {optimalIterations1}");
        Message($"  Predicted success probability: {predictedProb1}");
        
        let shots1 = 100;
        let (successCount1, foundTargets1, measurements1) = GroverSearchWithStatistics(
            targets1, 
            numQubits1, 
            optimalIterations1, 
            shots1
        );
        let empiricalProb1 = IntAsDouble(successCount1) / IntAsDouble(shots1);
        
        Message($"  Empirical success rate: {empiricalProb1} ({successCount1}/{shots1})");
        Message($"  Found targets: {foundTargets1}");
        Message("");
        
        // Demo 2: Multiple targets
        Message("Demo 2: Multiple target search (5 qubits, 32 items)");
        Message("----------------------------------------");
        let numQubits2 = 5;
        let searchSpace2 = 2^numQubits2;
        let targets2 = [5, 12, 19, 27];  // Search for 4 targets
        let markedFraction2 = IntAsDouble(Length(targets2)) / IntAsDouble(searchSpace2);
        let optimalIterations2 = CalculateGroverIterations(markedFraction2);
        let predictedProb2 = PredictSuccessProbability(markedFraction2, optimalIterations2);
        
        Message($"  Search space: {searchSpace2} items");
        Message($"  Target indices: {targets2}");
        Message($"  Marked fraction: {markedFraction2} ({Length(targets2)}/{searchSpace2})");
        Message($"  Optimal iterations: {optimalIterations2}");
        Message($"  Predicted success probability: {predictedProb2}");
        
        let shots2 = 100;
        let (successCount2, foundTargets2, measurements2) = GroverSearchWithStatistics(
            targets2,
            numQubits2,
            optimalIterations2,
            shots2
        );
        let empiricalProb2 = IntAsDouble(successCount2) / IntAsDouble(shots2);
        
        Message($"  Empirical success rate: {empiricalProb2} ({successCount2}/{shots2})");
        Message($"  Found targets: {foundTargets2}");
        Message("");
        
        // Demo 3: Larger search space (matching medium instance)
        Message("Demo 3: Large search space (12 qubits, 4096 items)");
        Message("----------------------------------------");
        let numQubits3 = 12;
        let searchSpace3 = 2^numQubits3;
        let targets3 = [42, 137, 999, 2048];  // 4 targets in 4096 space
        let markedFraction3 = IntAsDouble(Length(targets3)) / IntAsDouble(searchSpace3);
        let optimalIterations3 = CalculateGroverIterations(markedFraction3);
        let predictedProb3 = PredictSuccessProbability(markedFraction3, optimalIterations3);
        
        Message($"  Search space: {searchSpace3} items");
        Message($"  Target indices: {targets3}");
        Message($"  Marked fraction: {markedFraction3} ({Length(targets3)}/{searchSpace3})");
        Message($"  Optimal iterations: {optimalIterations3}");
        Message($"  Predicted success probability: {predictedProb3}");
        
        let shots3 = 50;  // Fewer shots for larger space
        let (successCount3, foundTargets3, measurements3) = GroverSearchWithStatistics(
            targets3,
            numQubits3,
            optimalIterations3,
            shots3
        );
        let empiricalProb3 = IntAsDouble(successCount3) / IntAsDouble(shots3);
        
        Message($"  Empirical success rate: {empiricalProb3} ({successCount3}/{shots3})");
        Message($"  Found targets: {foundTargets3}");
        Message("");
        
        // Quadratic speedup demonstration
        Message("=== Quadratic Speedup Analysis ===");
        Message("Classical exhaustive search: O(N) queries");
        Message("Grover's algorithm: O(√N) queries\n");
        
        let classicalQueries1 = searchSpace1 / 2;  // Average for 1 target
        let quantumQueries1 = optimalIterations1;
        let speedup1 = IntAsDouble(classicalQueries1) / IntAsDouble(quantumQueries1);
        Message($"Demo 1 ({searchSpace1} items): Classical={classicalQueries1}, Quantum={quantumQueries1}, Speedup={speedup1}x");
        
        let classicalQueries2 = searchSpace2 / Length(targets2);  // Adjusted for multiple targets
        let quantumQueries2 = optimalIterations2;
        let speedup2 = IntAsDouble(classicalQueries2) / IntAsDouble(quantumQueries2);
        Message($"Demo 2 ({searchSpace2} items): Classical~{classicalQueries2}, Quantum={quantumQueries2}, Speedup~{speedup2}x");
        
        let classicalQueries3 = searchSpace3 / Length(targets3);
        let quantumQueries3 = optimalIterations3;
        let speedup3 = IntAsDouble(classicalQueries3) / IntAsDouble(quantumQueries3);
        Message($"Demo 3 ({searchSpace3} items): Classical~{classicalQueries3}, Quantum={quantumQueries3}, Speedup~{speedup3}x");
        
        Message("\n✅ Grover's algorithm demonstration complete!");
    }
}
