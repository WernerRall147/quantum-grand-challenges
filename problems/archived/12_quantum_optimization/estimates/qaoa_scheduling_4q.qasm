OPENQASM 2.0;
include "qelib1.inc";

// QAOA Scheduling: 4-job 2-machine assignment
// Pairwise ZZ penalties + Rx mixer, depth=1
// gamma=0.9, beta=0.9 (optimized parameters)
qreg q[4];
creg c[4];

// Uniform superposition
h q[0]; h q[1]; h q[2]; h q[3];

// Cost layer: ZZ interactions for job conflict penalties
// w[0][1]=1.0
cx q[0], q[1]; rz(1.8) q[1]; cx q[0], q[1];
// w[0][2]=0.5
cx q[0], q[2]; rz(0.9) q[2]; cx q[0], q[2];
// w[0][3]=0.2
cx q[0], q[3]; rz(0.36) q[3]; cx q[0], q[3];
// w[1][2]=1.2
cx q[1], q[2]; rz(2.16) q[2]; cx q[1], q[2];
// w[1][3]=0.8
cx q[1], q[3]; rz(1.44) q[3]; cx q[1], q[3];
// w[2][3]=0.6
cx q[2], q[3]; rz(1.08) q[3]; cx q[2], q[3];

// Mixer layer: Rx(2*beta=1.8)
rx(1.8) q[0]; rx(1.8) q[1]; rx(1.8) q[2]; rx(1.8) q[3];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
