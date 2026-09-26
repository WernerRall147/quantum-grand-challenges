OPENQASM 2.0;
include "qelib1.inc";

// QAOA MaxCut depth-1: unweighted 3-node triangle
// Optimized repository-convention parameters: gamma=2.827433388230814, beta=0.3141592653589793
// For textbook MaxCut exp(-i gamma_standard C), gamma_standard = -2 gamma up to global phase.
qreg q[3];
creg c[3];

h q[0]; h q[1]; h q[2];

cx q[0], q[1]; rz(5.654866776461628) q[1]; cx q[0], q[1];
cx q[0], q[2]; rz(5.654866776461628) q[2]; cx q[0], q[2];
cx q[1], q[2]; rz(5.654866776461628) q[2]; cx q[1], q[2];

rx(0.6283185307179586) q[0];
rx(0.6283185307179586) q[1];
rx(0.6283185307179586) q[2];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
