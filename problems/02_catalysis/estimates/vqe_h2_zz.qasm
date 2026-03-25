OPENQASM 2.0;
include "qelib1.inc";

// VQE H2 molecular energy: 2-qubit ansatz with Pauli ZZ measurement
// theta0=pi/4, theta1=pi/2, theta2=0
qreg q[2];
creg c[2];

// Hartree-Fock reference |01>
x q[0];

// Ansatz
ry(0.7853981633974483) q[0];
ry(1.5707963267948966) q[1];
cx q[0], q[1];

// Measure ZZ
measure q[0] -> c[0];
measure q[1] -> c[1];
