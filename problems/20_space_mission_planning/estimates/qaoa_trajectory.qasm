OPENQASM 2.0;
include "qelib1.inc";

// QAOA trajectory: 4-leg mission, depth-1
// gamma=0.1, beta=0.9
qreg q[4];
creg c[4];

h q[0]; h q[1]; h q[2]; h q[3];

// Cost: Z bias for delta-v difference
rz(0.07) q[0]; rz(0.04) q[1]; rz(0.07) q[2]; rz(0.05) q[3];

// Cost: ZZ time-window conflict penalties
cx q[0], q[1]; rz(0.05) q[1]; cx q[0], q[1];
cx q[0], q[2]; rz(0.05) q[2]; cx q[0], q[2];
cx q[0], q[3]; rz(0.05) q[3]; cx q[0], q[3];
cx q[1], q[2]; rz(0.05) q[2]; cx q[1], q[2];
cx q[1], q[3]; rz(0.05) q[3]; cx q[1], q[3];
cx q[2], q[3]; rz(0.05) q[3]; cx q[2], q[3];

// Mixer
rx(1.8) q[0]; rx(1.8) q[1]; rx(1.8) q[2]; rx(1.8) q[3];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
