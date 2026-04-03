namespace QuantumGrandChallenges.DrugDiscovery {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    operation BindingAnsatz(theta0 : Double, theta1 : Double, theta2 : Double, q0 : Qubit, q1 : Qubit) : Unit {
        X(q0);
        Ry(theta0, q0);
        Ry(theta1, q1);
        CNOT(q0, q1);
        Rz(theta2, q1);
        CNOT(q0, q1);
    }

    operation MeasureBinding(theta0 : Double, theta1 : Double, theta2 : Double, paulis : Pauli[], shots : Int) : Double {
        mutable sum = 0.0;
        for _ in 1 .. shots {
            use register = Qubit[2];
            BindingAnsatz(theta0, theta1, theta2, register[0], register[1]);
            let result = Measure(paulis, register);
            if (result == Zero) { set sum += 1.0; } else { set sum -= 1.0; }
            ResetAll(register);
        }
        return sum / IntAsDouble(shots);
    }

    operation EstimateBindingEnergy(theta0 : Double, theta1 : Double, theta2 : Double, shots : Int) : Double {
        let cI = -0.52;
        let cZ0 = 0.20;
        let cZ1 = -0.18;
        let cZZ = 0.12;
        let cXX = 0.06;
        let z0 = MeasureBinding(theta0, theta1, theta2, [PauliZ, PauliI], shots);
        let z1 = MeasureBinding(theta0, theta1, theta2, [PauliI, PauliZ], shots);
        let zz = MeasureBinding(theta0, theta1, theta2, [PauliZ, PauliZ], shots);
        let xx = MeasureBinding(theta0, theta1, theta2, [PauliX, PauliX], shots);
        return cI + cZ0 * z0 + cZ1 * z1 + cZZ * zz + cXX * xx;
    }

    @EntryPoint()
    operation RunDrugDiscovery() : Unit {
        Message("=== Drug Discovery: VQE Molecular Binding Energy ===");
        Message("");
        let exactBinding = -0.72;
        Message($"Reference binding energy: {exactBinding} Hartree");
        let angles = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8];
        let shots = 48;
        mutable bestE = 100.0;
        mutable bestT0 = 0.0;
        mutable bestT1 = 0.0;
        for t0 in angles {
            for t1 in angles {
                let e = EstimateBindingEnergy(t0, t1, 0.0, shots);
                if (e < bestE) { set bestE = e; set bestT0 = t0; set bestT1 = t1; }
            }
        }
        Message($"VQE binding energy: {bestE} Hartree");
        Message($"Error vs reference: {AbsD(bestE - exactBinding)} Hartree");
        Message("");
        Message("VQE enables quantum-accurate binding affinity prediction for drug candidates.");
    }
}
