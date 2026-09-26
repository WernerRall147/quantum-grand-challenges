OPENQASM 2.0;
include "qelib1.inc";

// Toy four-variable Ising/QUBO same-side energy, not a protein-folding model.
// Optimized p=1 parameters: gamma=0.47123889803846897, beta=1.119192382841364.
qreg q[4];
creg c[4];

h q[0]; h q[1]; h q[2]; h q[3];

cx q[0], q[1]; rz(-1.1309733552923256) q[1]; cx q[0], q[1];
cx q[0], q[2]; rz(-0.2827433388230814) q[2]; cx q[0], q[2];
cx q[1], q[2]; rz(-0.7539822368615504) q[2]; cx q[1], q[2];
cx q[1], q[3]; rz(-0.47123889803846897) q[3]; cx q[1], q[3];
cx q[2], q[3]; rz(-0.9424777960769379) q[3]; cx q[2], q[3];

rx(2.238384765682728) q[0];
rx(2.238384765682728) q[1];
rx(2.238384765682728) q[2];
rx(2.238384765682728) q[3];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
