OPENQASM 2.0;
include "qelib1.inc";

// Quantum VaR estimation: amplitude encode market states + oracle marking
// 2 market qubits + 1 marker qubit = 3 qubits
// Market states: |00>=normal, |01>=normal, |10>=loss, |11>=loss
// Amplitude encoding via Ry rotations

qreg mkt[2];
qreg mark[1];
creg c[3];

// Amplitude encode market return distribution
// P(normal) ~ 0.85, P(loss) ~ 0.15
ry(0.7956) mkt[0];
// Sub-register encoding
cx mkt[0], mkt[1];
ry(0.5) mkt[1];
cx mkt[0], mkt[1];

// Oracle: mark loss states |10> and |11> (mkt[0]=|1>)
// When mkt[0]=1, flip marker
cx mkt[0], mark[0];

// Measure all
measure mkt[0] -> c[0];
measure mkt[1] -> c[1];
measure mark[0] -> c[2];
