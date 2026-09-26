OPENQASM 2.0;
include "qelib1.inc";

// Toy four-job two-machine same-side penalty QUBO.
// Optimized p=1 parameters: gamma=0.3141592653589793, beta=1.2566370614359172.
qreg q[4];
creg c[4];

h q[0]; h q[1]; h q[2]; h q[3];

cx q[0], q[1]; rz(0.6283185307179586) q[1]; cx q[0], q[1];
cx q[0], q[2]; rz(0.3141592653589793) q[2]; cx q[0], q[2];
cx q[0], q[3]; rz(0.12566370614359174) q[3]; cx q[0], q[3];
cx q[1], q[2]; rz(0.7539822368615503) q[2]; cx q[1], q[2];
cx q[1], q[3]; rz(0.5026548245743669) q[3]; cx q[1], q[3];
cx q[2], q[3]; rz(0.37699111843077515) q[3]; cx q[2], q[3];

rx(2.5132741228718345) q[0];
rx(2.5132741228718345) q[1];
rx(2.5132741228718345) q[2];
rx(2.5132741228718345) q[3];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
