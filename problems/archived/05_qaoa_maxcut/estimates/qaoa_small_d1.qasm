OPENQASM 2.0;
include "qelib1.inc";

// QAOA MaxCut depth-1: 3-node weighted triangle (A-B:1.0, B-C:1.2, A-C:0.8)
// Optimized parameters from coordinate search: gamma=0.5, beta=0.5
qreg q[3];
creg c[3];

// Initialize uniform superposition
h q[0];
h q[1];
h q[2];

// Cost layer: exp(-i * gamma * w_ij * ZZ) for each edge
// Edge A-B (weight 1.0): exp(-i * 0.5 * 1.0 * Z0 Z1)
cx q[0], q[1];
rz(1.0) q[1];
cx q[0], q[1];

// Edge B-C (weight 1.2): exp(-i * 0.5 * 1.2 * Z1 Z2)
cx q[1], q[2];
rz(1.2) q[2];
cx q[1], q[2];

// Edge A-C (weight 0.8): exp(-i * 0.5 * 0.8 * Z0 Z2)
cx q[0], q[2];
rz(0.8) q[2];
cx q[0], q[2];

// Mixer layer: exp(-i * beta * X) for each qubit
// Rx(2*beta) = Rx(1.0) for each qubit
rx(1.0) q[0];
rx(1.0) q[1];
rx(1.0) q[2];

// Measure
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
