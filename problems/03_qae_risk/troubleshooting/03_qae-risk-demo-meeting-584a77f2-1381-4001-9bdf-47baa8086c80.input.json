OPENQASM 2.0;
include "qelib1.inc";

// QAE Risk: simplified amplitude estimation with 1 Grover iteration
// 2 loss qubits + 1 precision qubit + 1 marker = 4 qubits
// Encodes a simple 4-state distribution, marks states above threshold

qreg loss[2];
qreg prec[1];
qreg mark[1];
creg c[2];

// State preparation: encode distribution amplitudes
ry(1.2) loss[0];
cx loss[0], loss[1];
ry(0.8) loss[1];
cx loss[0], loss[1];

// Oracle: mark tail states |10> and |11> (loss > threshold)
cx loss[0], mark[0];

// Single Grover iteration
// Reflect about marked state
z mark[0];

// Reflect about initial state
h loss[0]; h loss[1];
x loss[0]; x loss[1];
cz loss[0], loss[1];
x loss[0]; x loss[1];
h loss[0]; h loss[1];

// Phase estimation step
h prec[0];
// Controlled Grover on precision qubit
cx prec[0], loss[0];
cx prec[0], loss[1];
h prec[0];

// Measure precision and marker
measure prec[0] -> c[0];
measure mark[0] -> c[1];
