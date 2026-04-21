OPENQASM 2.0;
include "qelib1.inc";

// Grover search: 4-qubit database (16 items), target=|1011> (index 11)
// Optimal iterations: floor(pi/4 * sqrt(16/1)) = 3
qreg q[4];
creg c[4];

// Initialize uniform superposition
h q[0];
h q[1];
h q[2];
h q[3];

// === Grover iteration 1 ===
// Oracle: mark |1011> with phase flip
// Flip q[2] (the 0-bit in target 1011)
x q[2];
// Multi-controlled Z = H on last + MCX + H on last
h q[3];
ccx q[0], q[1], q[3];
// Need 4-qubit controlled-Z; use decomposition
// CCZ on q[0],q[1],q[2],q[3] via ancilla-free decomposition
x q[2];
// Simplified: use phase oracle on target bitstring 1011
// Reset oracle flips
// Direct phase marking via controlled operations:
// Oracle for |1011>: flip q[2], then apply C3Z, then flip q[2] back
x q[2];
h q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[0];
t q[1];
t q[2];
t q[3];
h q[3];
cx q[0], q[1];
t q[0];
tdg q[1];
cx q[0], q[1];
x q[2];

// Diffusion operator
h q[0];
h q[1];
h q[2];
h q[3];
x q[0];
x q[1];
x q[2];
x q[3];
h q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[0];
t q[1];
t q[2];
t q[3];
h q[3];
cx q[0], q[1];
t q[0];
tdg q[1];
cx q[0], q[1];
x q[0];
x q[1];
x q[2];
x q[3];
h q[0];
h q[1];
h q[2];
h q[3];

// === Grover iteration 2 ===
// Oracle
x q[2];
h q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[0];
t q[1];
t q[2];
t q[3];
h q[3];
cx q[0], q[1];
t q[0];
tdg q[1];
cx q[0], q[1];
x q[2];

// Diffusion
h q[0];
h q[1];
h q[2];
h q[3];
x q[0];
x q[1];
x q[2];
x q[3];
h q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[0];
t q[1];
t q[2];
t q[3];
h q[3];
cx q[0], q[1];
t q[0];
tdg q[1];
cx q[0], q[1];
x q[0];
x q[1];
x q[2];
x q[3];
h q[0];
h q[1];
h q[2];
h q[3];

// === Grover iteration 3 ===
// Oracle
x q[2];
h q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[0];
t q[1];
t q[2];
t q[3];
h q[3];
cx q[0], q[1];
t q[0];
tdg q[1];
cx q[0], q[1];
x q[2];

// Diffusion
h q[0];
h q[1];
h q[2];
h q[3];
x q[0];
x q[1];
x q[2];
x q[3];
h q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[0];
t q[1];
t q[2];
t q[3];
h q[3];
cx q[0], q[1];
t q[0];
tdg q[1];
cx q[0], q[1];
x q[0];
x q[1];
x q[2];
x q[3];
h q[0];
h q[1];
h q[2];
h q[3];

// Measure
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
