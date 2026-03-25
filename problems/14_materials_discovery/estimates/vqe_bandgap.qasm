OPENQASM 2.0;
include "qelib1.inc";

// VQE band gap: 2-qubit tight-binding model
qreg q[2];
creg c[2];

x q[0];
ry(0.6) q[0];
ry(1.0) q[1];
cx q[0], q[1];
rz(0.3) q[1];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
