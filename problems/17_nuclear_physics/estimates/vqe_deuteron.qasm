OPENQASM 2.0;
include "qelib1.inc";

// VQE deuteron: 2-qubit nuclear Hamiltonian
qreg q[2];
creg c[2];

x q[0];
ry(0.7) q[0];
ry(1.4) q[1];
cx q[0], q[1];
rz(0.5) q[1];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
