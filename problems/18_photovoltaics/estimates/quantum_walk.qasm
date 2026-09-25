OPENQASM 2.0;
include "qelib1.inc";

// Quantum walk exciton transport on a 4-site ring: coin + 2 position qubits.
// The site is 2 * pos[0] + pos[1]; coin |1> steps right, coin |0> steps left.
// Same circuit as qsharp/HardwareKernel.qs. The previous version applied CNOTs from
// the coin to both position bits, which is not a step in either direction.
qreg coin[1];
qreg pos[2];
creg c[3];

// Initialize exciton at site 1
x pos[1];

// Walk step 1: coin, then coin-controlled increment and decrement of the site
ry(1.0) coin[0];
ccx coin[0], pos[1], pos[0];
cx coin[0], pos[1];
x coin[0];
cx coin[0], pos[1];
ccx coin[0], pos[1], pos[0];
x coin[0];

// Walk step 2
ry(1.0) coin[0];
ccx coin[0], pos[1], pos[0];
cx coin[0], pos[1];
x coin[0];
cx coin[0], pos[1];
ccx coin[0], pos[1], pos[0];
x coin[0];

// Walk step 3
ry(1.0) coin[0];
ccx coin[0], pos[1], pos[0];
cx coin[0], pos[1];
x coin[0];
cx coin[0], pos[1];
ccx coin[0], pos[1], pos[0];
x coin[0];

measure coin[0] -> c[0];
measure pos[0] -> c[1];
measure pos[1] -> c[2];
