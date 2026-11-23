import Std.Measurement.MResetZ;

operation HubbardToyAnsatz(
    theta0 : Double,
    theta1 : Double,
    theta2 : Double,
    q0 : Qubit,
    q1 : Qubit
) : Unit {
    X(q0);
    Ry(theta0, q0);
    Ry(theta1, q1);
    CNOT(q0, q1);
    Rz(theta2, q1);
    CNOT(q0, q1);
}

operation MeasureProductZ(register : Qubit[]) : Result {
    CNOT(register[0], register[1]);
    let parity = MResetZ(register[1]);
    let cleanup = MResetZ(register[0]);
    return parity;
}

/// One fixed-term measurement for the two-qubit VQE toy Hamiltonian.
operation MeasureHubbardToyTerm(
    theta0 : Double,
    theta1 : Double,
    theta2 : Double,
    term : Int
) : Result[] {
    use register = Qubit[2];
    HubbardToyAnsatz(theta0, theta1, theta2, register[0], register[1]);

    mutable measurement = Zero;
    if term == 0 {
        H(register[0]);
        H(register[1]);
        set measurement = MeasureProductZ(register);
    } elif term == 1 {
        Adjoint S(register[0]);
        Adjoint S(register[1]);
        H(register[0]);
        H(register[1]);
        set measurement = MeasureProductZ(register);
    } elif term == 2 {
        set measurement = MResetZ(register[0]);
        let cleanup = MResetZ(register[1]);
    } elif term == 3 {
        let cleanup = MResetZ(register[0]);
        set measurement = MResetZ(register[1]);
    } else {
        fail $"Unsupported Hamiltonian term {term}";
    }

    return [measurement];
}
