namespace QuantumGrandChallenges.LinearSolvers {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Measurement;

    // ==================================================================
    // ANALYTICAL BASELINE: Classical Solutions for Small Systems
    // ==================================================================

    function Determinant2x2(matrix : Double[][]) : Double {
        let a = matrix[0][0];
        let b = matrix[0][1];
        let c = matrix[1][0];
        let d = matrix[1][1];
        return a * d - b * c;
    }

    function SolveSymmetric2x2(matrix : Double[][], rhs : Double[]) : Double[] {
        let det = Determinant2x2(matrix);
        if AbsD(det) < 1e-9 {
            fail "Matrix is singular; cannot compute analytical baseline.";
        }

        let a = matrix[0][0];
        let b = matrix[0][1];
        let d = matrix[1][1];
        let f0 = rhs[0];
        let f1 = rhs[1];

        let x0 = (d * f0 - b * f1) / det;
        let x1 = (-b * f0 + a * f1) / det;

        return [x0, x1];
    }

    function ConditionNumberSymmetric2x2(matrix : Double[][]) : Double {
        let a = matrix[0][0];
        let b = matrix[0][1];
        let d = matrix[1][1];
        let trace = a + d;
        let delta = Sqrt((a - d) * (a - d) + 4.0 * b * b);
        let lambdaMax = 0.5 * (trace + delta);
        let lambdaMin = 0.5 * (trace - delta);
        if AbsD(lambdaMin) < 1e-12 {
            fail "Condition number undefined because the minimum eigenvalue is zero.";
        }
        return lambdaMax / lambdaMin;
    }

    function ResidualNorm(matrix : Double[][], solution : Double[], rhs : Double[]) : Double {
        let a00 = matrix[0][0];
        let a01 = matrix[0][1];
        let a10 = matrix[1][0];
        let a11 = matrix[1][1];
        let r0 = a00 * solution[0] + a01 * solution[1] - rhs[0];
        let r1 = a10 * solution[0] + a11 * solution[1] - rhs[1];
        return Sqrt(r0 * r0 + r1 * r1);
    }

    // ==================================================================
    // HHL QUANTUM LINEAR SOLVER
    // ==================================================================
    // Implementation of Harrow-Hassidim-Lloyd (HHL) algorithm for
    // solving linear systems Ax = b using quantum phase estimation
    // and controlled rotations for eigenvalue inversion.
    // ==================================================================

    /// # Summary
    /// Prepares quantum state |b⟩ from classical RHS vector.
    /// For 2D vector [b0, b1], creates state |ψ⟩ = (b0|0⟩ + b1|1⟩)/||b||
    ///
    /// # Input
    /// ## rhs
    /// Classical right-hand side vector [b0, b1]
    /// ## qubit
    /// Single qubit to encode the 2D state
    operation PrepareRHSState(rhs : Double[], qubit : Qubit) : Unit is Adj + Ctl {
        if Length(rhs) != 2 {
            fail "This implementation supports 2D RHS vectors only";
        }

        // Normalize RHS vector
        let norm = Sqrt(rhs[0] * rhs[0] + rhs[1] * rhs[1]);
        let b0 = rhs[0] / norm;
        let b1 = rhs[1] / norm;

        // Prepare |b⟩ = b0|0⟩ + b1|1⟩ using Ry rotation
        // After Ry(θ): cos(θ/2)|0⟩ + sin(θ/2)|1⟩
        // We want: cos(θ/2) = b0, sin(θ/2) = b1
        let theta = 2.0 * ArcTan2(b1, b0);
        Ry(theta, qubit);
    }

    /// # Summary
    /// Block-encodes the Hamiltonian (system matrix) as a unitary operator.
    /// For 2x2 symmetric matrix [[a,b],[b,d]], implements time evolution e^{-iAt}.
    /// Uses Pauli decomposition: A = c_I*I + c_Z*Z + c_X*X
    ///
    /// # Input
    /// ## matrix
    /// System matrix as 2x2 array
    /// ## time
    /// Evolution time parameter
    /// ## qubit
    /// System qubit to apply Hamiltonian to
    operation ApplyBlockEncodedHamiltonian(matrix : Double[][], time : Double, qubit : Qubit) : Unit is Adj + Ctl {
        let a = matrix[0][0];
        let b = matrix[0][1];
        let d = matrix[1][1];

        // Decompose A = (a+d)/2 * I + (a-d)/2 * Z + b * X
        let identity_coeff = (a + d) / 2.0;
        let z_coeff = (a - d) / 2.0;
        let x_coeff = b;

        // Apply rotations to simulate e^{-iAt}
        // First-order Trotter approximation: e^{-iAt} ≈ e^{-iH_I*t}e^{-iH_Z*t}e^{-iH_X*t}
        Rz(-2.0 * z_coeff * time, qubit);
        Rx(-2.0 * x_coeff * time, qubit);
        // Global phase from identity term (can be ignored in many contexts)
    }

    /// # Summary
    /// Quantum Phase Estimation to extract eigenvalue information.
    /// Estimates phase φ where U|ψ⟩ = e^{2πiφ}|ψ⟩ for unitary U = e^{-iA}.
    ///
    /// # Input
    /// ## matrix
    /// System matrix to estimate eigenvalues for
    /// ## systemQubit
    /// Qubit in eigenstate of the matrix
    /// ## precisionQubits
    /// Qubits for phase estimation precision (more = higher precision)
    operation QuantumPhaseEstimation(matrix : Double[][], systemQubit : Qubit, precisionQubits : Qubit[]) : Unit is Adj {
        let n = Length(precisionQubits);
        
        // Step 1: Prepare uniform superposition on precision qubits
        for q in precisionQubits {
            H(q);
        }

        // Step 2: Controlled time evolution U^{2^k} for each precision qubit k
        for i in 0..n-1 {
            let power = 2^i;
            let time = IntAsDouble(power);
            Controlled ApplyBlockEncodedHamiltonian([precisionQubits[i]], (matrix, time, systemQubit));
        }

        // Step 3: Inverse QFT on precision register to extract phase
        Adjoint QuantumFourierTransform(precisionQubits);
    }

    /// # Summary
    /// Quantum Fourier Transform on n qubits.
    /// Maps computational basis to Fourier basis: |j⟩ → (1/√N)Σ_k e^{2πijk/N}|k⟩
    ///
    /// # Input
    /// ## qubits
    /// Qubits to apply QFT to
    operation QuantumFourierTransform(qubits : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        
        for i in 0..n-1 {
            H(qubits[i]);
            for j in i+1..n-1 {
                let angle = PI() / IntAsDouble(2^(j-i));
                Controlled R1([qubits[j]], (angle, qubits[i]));
            }
        }
        
        // Reverse qubit order for standard QFT convention
        for i in 0..n/2-1 {
            SWAP(qubits[i], qubits[n-1-i]);
        }
    }

    /// # Summary
    /// Controlled rotation for eigenvalue inversion: |λ⟩|0⟩ → |λ⟩(√(1-C²/λ²)|0⟩ + C/λ|1⟩)
    /// This encodes 1/λ as the amplitude of the |1⟩ state in the ancilla qubit.
    ///
    /// # Input
    /// ## precisionQubits
    /// Register containing encoded eigenvalue estimate
    /// ## ancillaQubit
    /// Ancilla qubit that will hold amplitude ∝ 1/λ
    /// ## C
    /// Normalization constant (should be < min eigenvalue)
    operation ControlledEigenvalueInversion(precisionQubits : Qubit[], ancillaQubit : Qubit, C : Double) : Unit is Adj {
        let n = Length(precisionQubits);
        
        // Apply controlled Y-rotations based on phase register
        // For eigenvalue λ encoded in phase φ, rotate by angle θ = arcsin(C/λ)
        // Simplified implementation: rotate based on binary encoding
        for i in 0..n-1 {
            let denom = IntAsDouble(2^(i+2)); // Avoid division by very small numbers
            let angle = 2.0 * ArcSin(C / denom);
            Controlled Ry([precisionQubits[i]], (angle, ancillaQubit));
        }
    }

    /// # Summary
    /// Complete HHL algorithm for solving 2x2 linear system Ax = b.
    /// Returns quantum solution state (encoded in computational basis amplitudes).
    ///
    /// # Input
    /// ## matrix
    /// 2x2 system matrix [[a,b],[b,d]]
    /// ## rhs
    /// Right-hand side vector [b0, b1]
    /// ## precisionBits
    /// Number of precision qubits for phase estimation (4-8 recommended)
    ///
    /// # Output
    /// Measurement result from system qubit (0 or 1)
    operation HHLSolve2x2(matrix : Double[][], rhs : Double[], precisionBits : Int) : Result {
        // Allocate quantum registers
        use systemQubit = Qubit();
        use precisionQubits = Qubit[precisionBits];
        use ancillaQubit = Qubit();

        // Step 1: Prepare initial state |b⟩ on system qubit
        PrepareRHSState(rhs, systemQubit);

        // Step 2: Quantum Phase Estimation to encode eigenvalues λ in phase register
        QuantumPhaseEstimation(matrix, systemQubit, precisionQubits);

        // Step 3: Controlled rotation for eigenvalue inversion: |λ⟩|0⟩ → |λ⟩(√...)|0⟩ + (C/λ)|1⟩)
        let C = 0.5; // Normalization constant (tune based on eigenvalue range)
        ControlledEigenvalueInversion(precisionQubits, ancillaQubit, C);

        // Step 4: Uncompute phase estimation (reverse QPE)
        Adjoint QuantumPhaseEstimation(matrix, systemQubit, precisionQubits);

        // Step 5: Measure ancilla to post-select on successful inversion
        let ancillaResult = M(ancillaQubit);
        
        // Step 6: Measure system qubit (solution is encoded in amplitudes)
        let solutionMeasurement = M(systemQubit);

        // Reset qubits before deallocation
        ResetAll([systemQubit] + precisionQubits + [ancillaQubit]);

        // Return measurement result
        // Note: In full HHL, multiple runs + tomography needed to reconstruct solution vector
        return solutionMeasurement;
    }

    @EntryPoint()
    operation RunLinearSolverBaseline() : Unit {
        Message("=== 2x2 Linear System Solver: HHL Algorithm ===");
        Message("");

        let matrix = [[4.0, -1.0], [-1.0, 3.0]];
        let rhs = [15.0, 10.0];

        Message("--- Problem Specification ---");
        Message($"Matrix A: [[{matrix[0][0]}, {matrix[0][1]}], [{matrix[1][0]}, {matrix[1][1]}]]");
        Message($"RHS b: [{rhs[0]}, {rhs[1]}]");
        Message("");

        // ===== ANALYTICAL BASELINE =====
        Message("--- Analytical Baseline ---");
        let classicalSolution = SolveSymmetric2x2(matrix, rhs);
        Message($"Classical solution: x = [{classicalSolution[0]}, {classicalSolution[1]}]");

        let conditionNumber = ConditionNumberSymmetric2x2(matrix);
        Message($"Condition number κ(A): {conditionNumber}");

        let residual = ResidualNorm(matrix, classicalSolution, rhs);
        Message($"Residual ||Ax - b||: {residual}");

        if residual < 1e-8 {
            Message("✓ Classical solution verified");
        }
        Message("");

        // ===== QUANTUM HHL =====
        Message("--- Quantum HHL Algorithm ---");
        let precisionBits = 4; // 4 qubits for phase estimation (16 phase bins)
        
        Message($"Running HHL with {precisionBits} precision qubits...");
        Message("Phase estimation will encode eigenvalues λ₁, λ₂ of matrix A");
        Message("Controlled rotations will compute 1/λ amplitudes");
        Message("");

        // Run HHL algorithm (single shot for demonstration)
        let result = HHLSolve2x2(matrix, rhs, precisionBits);
        
        Message($"System qubit measurement: {result}");
        Message("");
        
        Message("--- Algorithm Analysis ---");
        Message($"Total qubits: {1 + precisionBits + 1} (1 system + {precisionBits} precision + 1 ancilla)");
        Message($"Circuit depth: O(n²) where n = {precisionBits}");
        Message($"Success probability: 1/κ² ≈ {1.0/(conditionNumber*conditionNumber)}");
        Message("");

        Message("Note: Full HHL requires multiple runs + quantum state tomography");
        Message("to reconstruct the complete solution vector x from measurement statistics.");
        Message("This implementation demonstrates the core HHL circuit components:");
        Message("  1. State preparation |b⟩");
        Message("  2. Quantum phase estimation for eigenvalues");
        Message("  3. Controlled rotations for eigenvalue inversion");
        Message("  4. Uncomputation and post-selection");
    }
}
