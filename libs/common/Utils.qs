namespace QuantumGrandChallenges.Common {
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Preparation;

    /// # Summary
    /// Common utility operations for quantum grand challenges.
    /// This library provides reusable quantum operations that are frequently
    /// needed across multiple problem implementations.

    /// # Summary
    /// Prepares a uniform superposition over n qubits.
    /// 
    /// # Input
    /// ## qubits
    /// Array of qubits to put in uniform superposition
    operation PrepareUniformSuperposition(qubits : Qubit[]) : Unit is Adj + Ctl {
        ApplyToEach(H, qubits);
    }

    /// # Summary
    /// Implements controlled rotation around Z-axis with angle determined by integer value.
    /// Useful for phase estimation and quantum Fourier transform.
    ///
    /// # Input
    /// ## control
    /// Control qubit
    /// ## target  
    /// Target qubit to rotate
    /// ## power
    /// Power of 2 determining rotation angle: theta = 2*pi / 2^power
    operation ControlledZRotationByPower(control : Qubit, target : Qubit, power : Int) : Unit is Adj + Ctl {
        let angle = 2.0 * PI() / IntAsDouble(2^power);
        Controlled Rz([control], (angle, target));
    }

    /// # Summary
    /// Quantum Fourier Transform on n qubits.
    /// Essential building block for many quantum algorithms.
    ///
    /// # Input
    /// ## qubits
    /// Array of qubits in computational basis to transform
    operation QuantumFourierTransform(qubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        
        for i in 0..n-1 {
            H(qubits[i]);
            for j in i+1..n-1 {
                ControlledZRotationByPower(qubits[j], qubits[i], j-i);
            }
        }
        
        // Reverse qubit order
        for i in 0..n/2-1 {
            SWAP(qubits[i], qubits[n-1-i]);
        }
    }

    /// # Summary
    /// Prepares an arbitrary state from classical amplitudes.
    /// Uses recursive amplitude encoding technique.
    ///
    /// # Input
    /// ## amplitudes
    /// Classical amplitudes (must be normalized)
    /// ## qubits
    /// Qubits to prepare the state on
    operation PrepareArbitraryState(amplitudes : Double[], qubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        if Length(amplitudes) != 2^n {
            fail "Number of amplitudes must equal 2^n where n is number of qubits";
        }
        
        PrepareArbitraryStateRecursive(amplitudes, qubits, 0);
    }

    /// # Summary
    /// Recursive helper for arbitrary state preparation.
    operation PrepareArbitraryStateRecursive(amplitudes : Double[], qubits : Qubit[], level : Int) : Unit is Adj + Ctl {
        let n = Length(qubits);
        if level == n {
            return ();
        }
        
        let blockSize = 2^(n - level - 1);
        mutable evenNorm = 0.0;
        mutable oddNorm = 0.0;
        
        // Calculate norms for even and odd blocks
        for i in 0..2^level - 1 {
            for j in 0..blockSize - 1 {
                let evenIdx = 2 * i * blockSize + j;
                let oddIdx = (2 * i + 1) * blockSize + j;
                set evenNorm += amplitudes[evenIdx] * amplitudes[evenIdx];
                set oddNorm += amplitudes[oddIdx] * amplitudes[oddIdx];
            }
        }
        
        let totalNorm = evenNorm + oddNorm;
        if totalNorm > 1e-10 {
            let theta = 2.0 * ArcTan2(Sqrt(oddNorm), Sqrt(evenNorm));
            Ry(theta, qubits[level]);
        }
        
        // Recursively prepare sub-blocks
        if blockSize > 1 {
            // Prepare even block (control = |0⟩)
            (ControlledOnInt(0, PrepareArbitraryStateRecursive))([qubits[level]], (amplitudes, qubits[level+1..n-1], level + 1));
            
            // Prepare odd block (control = |1⟩)  
            (ControlledOnInt(1, PrepareArbitraryStateRecursive))([qubits[level]], (amplitudes, qubits[level+1..n-1], level + 1));
        }
    }

    /// # Summary
    /// Implements diffusion operator for Grover's algorithm.
    /// Reflects amplitudes around their average value.
    ///
    /// # Input
    /// ## qubits
    /// Array of qubits to apply diffusion operator to
    operation DiffusionOperator(qubits : Qubit[]) : Unit is Adj + Ctl {
        within {
            PrepareUniformSuperposition(qubits);
            ApplyToEach(X, qubits);
        } apply {
            Controlled Z(Most(qubits), Tail(qubits));
        }
    }

    /// # Summary
    /// Generic oracle interface for marking target states.
    /// To be implemented by specific problems.
    ///
    /// # Input
    /// ## qubits
    /// Input qubits encoding the state to check
    /// ## target
    /// Auxiliary qubit that gets flipped if input matches target
    operation MarkingOracle(qubits : Qubit[], target : Qubit) : Unit is Adj + Ctl {
        // Default implementation - marks the all-ones state
        Controlled X(qubits, target);
    }

    /// # Summary
    /// Generic Grover iteration combining oracle and diffusion.
    ///
    /// # Input  
    /// ## oracle
    /// Oracle operation that marks target states
    /// ## qubits
    /// Work qubits for the search space
    /// ## auxiliary
    /// Auxiliary qubit for oracle marking
    operation GroverIteration(oracle : ((Qubit[], Qubit) => Unit is Adj + Ctl), qubits : Qubit[], auxiliary : Qubit) : Unit {
        oracle(qubits, auxiliary);
        DiffusionOperator(qubits);
    }

    /// # Summary
    /// Estimates the amplitude of marked states using quantum amplitude estimation.
    ///
    /// # Input
    /// ## oracle
    /// Oracle that marks target states
    /// ## statePrep
    /// Operation to prepare initial state
    /// ## precision
    /// Number of precision qubits for amplitude estimation
    /// ## qubits
    /// Work qubits for the computation
    /// ## auxiliary
    /// Auxiliary qubit for oracle
    ///
    /// # Output
    /// Estimated amplitude value
    operation AmplitudeEstimation(
        oracle : ((Qubit[], Qubit) => Unit is Adj + Ctl),
        statePrep : (Qubit[] => Unit is Adj + Ctl),
        precision : Int,
        qubits : Qubit[],
        auxiliary : Qubit
    ) : Double {
        // Placeholder implementation - would need full QAE circuit
        // For now, return classical estimate
        return 0.5; // This should be replaced with actual QAE implementation
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
    /// Creates a controlled version of any unitary operation.
    /// Useful for building larger controlled operations.
    ///
    /// # Input
    /// ## op
    /// Operation to make controlled
    /// ## controls
    /// Control qubits
    /// ## targets
    /// Target qubits for the operation
    operation MakeControlled(op : (Qubit[] => Unit is Adj + Ctl), controls : Qubit[], targets : Qubit[]) : Unit is Adj + Ctl {
        Controlled op(controls, targets);
    }
}
