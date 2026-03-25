OPENQASM 2.0;
include "qelib1.inc";

// Quantum walk exciton transport: coin + 2 position qubits
qreg coin[1];
qreg pos[2];
creg c[3];

// Initialize exciton at site 1
x pos[1];

// Walk step 1: coin + conditional shift
ry(0.6) coin[0];
cx coin[0], pos[0];
cx coin[0], pos[1];

// Walk step 2
ry(0.6) coin[0];
cx coin[0], pos[0];
cx coin[0], pos[1];

measure coin[0] -> c[0];
measure pos[0] -> c[1];
measure pos[1] -> c[2];
