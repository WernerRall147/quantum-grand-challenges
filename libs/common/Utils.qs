namespace QuantumGrandChallenges.Common {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

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
        ApplyToEachCA(H, qubits);
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
        // Big-endian QFT with final bit reversal. qubits[0] = MSB.
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
    /// Implements diffusion operator for Grover's algorithm.
    /// Reflects amplitudes around their average value.
    ///
    /// # Input
    /// ## qubits
    /// Array of qubits to apply diffusion operator to
    operation DiffusionOperator(qubits : Qubit[]) : Unit is Adj + Ctl {
        within {
            PrepareUniformSuperposition(qubits);
            ApplyToEachCA(X, qubits);
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

    function ClipProbability(value : Double) : Double {
        if (value < 0.0) {
            return 0.0;
        }
        if (value > 1.0) {
            return 1.0;
        }
        return value;
    }

    operation ApplyAllOnesPhase(qubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        if (n == 0) {
            ()
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
        register : Qubit[],
        marker : Qubit
    ) : Unit is Adj + Ctl {
        within {
            X(marker);
            H(marker);
        } apply {
            oracle(register, marker);
            ReflectAboutState(statePrep, register);
        }
    }

    operation GroverOperatorPower(
        statePrep : Qubit[] => Unit is Adj + Ctl,
        oracle : (Qubit[], Qubit) => Unit is Adj + Ctl,
        power : Int,
        register : Qubit[],
        marker : Qubit
    ) : Unit is Adj + Ctl {
        if (power <= 0) {
            ()
        } else {
            for _ in 1..power {
                GroverOperator(statePrep, oracle, register, marker);
            }
        }
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
        if (precision <= 0) {
            fail "Amplitude estimation requires at least one precision qubit.";
        }

        use precisionRegister = Qubit[precision];

        ApplyToEach(H, precisionRegister);
        statePrep(qubits);

        for idx in 0..precision - 1 {
            let power = 1 <<< idx;
            Controlled GroverOperatorPower([precisionRegister[idx]], (statePrep, oracle, power, qubits, auxiliary));
        }

        Adjoint QuantumFourierTransform(precisionRegister);

        mutable results = [Zero, size = precision];
        for idx in 0..precision - 1 {
            set results w/= idx <- M(precisionRegister[idx]);
        }
        let phaseInt = ResultArrayAsInt(results);

        ResetAll(precisionRegister);
        Reset(auxiliary);
        ResetAll(qubits);

        let phase = IntAsDouble(phaseInt) / IntAsDouble(1 <<< precision);
        let theta = phase * PI();
        let amplitude = Sin(theta) * Sin(theta);
        return ClipProbability(amplitude);
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
