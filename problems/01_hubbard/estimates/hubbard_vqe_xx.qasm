OPENQASM 2.0;
include "qelib1.inc";

// Hubbard VQE: 2-site half-filling ansatz + XX measurement
// Measures XX expectation value (hopping term)
qreg q[2];
creg c[2];

// Initialize |01> (half-filling)
x q[0];

// VQE ansatz
ry(0.7853981633974483) q[0];
ry(1.5707963267948966) q[1];
cx q[0], q[1];
rz(0.39269908169872414) q[1];
cx q[0], q[1];

// Rotate to XX basis
h q[0];
h q[1];

// Measure
measure q[0] -> c[0];
measure q[1] -> c[1];
