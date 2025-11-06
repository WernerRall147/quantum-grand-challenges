namespace QuantumGrandChallenges.Hubbard {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function SingletEigenvalue(t : Double, u : Double) : Double {
        let discriminant = Sqrt(u * u + 16.0 * t * t);
        // Negative branch gives the singlet (ground) energy for half filling
        return 0.5 * (u - discriminant);
    }

    function UpperSingletEigenvalue(t : Double, u : Double) : Double {
        let discriminant = Sqrt(u * u + 16.0 * t * t);
        return 0.5 * (u + discriminant);
    }

    function TripletEigenvalue(u : Double) : Double {
        // Two-site Hubbard triplet state has no double occupation penalty
        return 0.0;
    }

    /// # Summary
    /// Demonstrates VQE ansatz circuit for the two-site Hubbard model.
    /// This hardware-efficient ansatz prepares parameterized quantum states
    /// for variational ground state energy optimization.
    ///
    /// # Input
    /// ## theta0, theta1, theta2
    /// Rotation angles for the variational ansatz
    /// ## q0, q1
    /// Qubits representing the two lattice sites
    operation HubbardVQEAnsatz(theta0 : Double, theta1 : Double, theta2 : Double, q0 : Qubit, q1 : Qubit) : Unit is Adj + Ctl {
        // Initialize to |01⟩ state (half-filling: one electron per site)
        X(q0);
        
        // Single-qubit rotations
        Ry(theta0, q0);
        Ry(theta1, q1);
        
        // Entangling layer
        CNOT(q0, q1);
        
        // Additional rotation
        Rz(theta2, q1);
        
        // Second entangling gate
        CNOT(q0, q1);
    }

    @EntryPoint()
    operation RunTwoSiteHubbardAnalysis() : Unit {
        Message("Two-site Hubbard model at half filling (one electron per site)");
        Message("-----------------------------------------------------------");
        Message("");

        let hoppingStrengths = [0.5, 1.0];
        let interactionStrengths = [0.0, 2.0, 4.0, 8.0];

        // Analytical baseline
        Message("ANALYTICAL RESULTS:");
        for t in hoppingStrengths {
            for u in interactionStrengths {
                let gs = SingletEigenvalue(t, u);
                let excited = UpperSingletEigenvalue(t, u);
                let triplet = TripletEigenvalue(u);
                let chargeGap = excited - gs;
                let spinGap = triplet - gs;

                Message($"t = {t}, U = {u}");
                Message($"  Ground state energy (singlet) : {gs}");
                Message($"  Upper singlet energy         : {excited}");
                Message($"  Triplet energy               : {triplet}");
                Message($"  Charge gap Δc                : {chargeGap}");
                Message($"  Spin gap Δs                  : {spinGap}");
            }
        }

        Message("");
        Message("VQE ANSATZ DEMONSTRATION:");
        Message("Preparing variational quantum state with demo parameters");
        
        use q0 = Qubit();
        use q1 = Qubit();
        
        // Demo VQE ansatz with example parameters
        let demoTheta0 = PI() / 4.0;  // pi/4
        let demoTheta1 = PI() / 2.0;  // pi/2
        let demoTheta2 = PI() / 8.0;  // pi/8
        
        HubbardVQEAnsatz(demoTheta0, demoTheta1, demoTheta2, q0, q1);
        Message($"Prepared VQE ansatz with parameters ({demoTheta0}, {demoTheta1}, {demoTheta2})");
        
        Reset(q0);
        Reset(q1);
        
        Message("");
        Message("Next steps for full VQE implementation:");
        Message("  - Measure Hamiltonian expectation values (XX, YY, ZZ Pauli terms)");
        Message("  - Integrate classical optimizer (COBYLA, SPSA) via Python");
        Message("  - Run Azure Quantum Resource Estimator for circuit resource analysis");
        Message("  - Scale to larger lattices with more sophisticated ansatze");
    }
}
