OPENQASM 2.0;
include "qelib1.inc";

// QAOA lattice protein folding: 4-residue conformation search
// Contact energy weights: w[0][1]=-1.2, w[1][2]=-0.8, w[2][3]=-1.0, w[0][2]=-0.3, w[1][3]=-0.5
// gamma=0.7, beta=0.5, depth=1
qreg q[4];
creg c[4];

// Uniform superposition
h q[0]; h q[1]; h q[2]; h q[3];

// Cost layer: ZZ interactions for contact energies
// w[0][1]=-1.2: 2*gamma*w = 2*0.7*(-1.2) = -1.68
cx q[0], q[1]; rz(-1.68) q[1]; cx q[0], q[1];
// w[1][2]=-0.8: 2*0.7*(-0.8) = -1.12
cx q[1], q[2]; rz(-1.12) q[2]; cx q[1], q[2];
// w[2][3]=-1.0: 2*0.7*(-1.0) = -1.4
cx q[2], q[3]; rz(-1.4) q[3]; cx q[2], q[3];
// w[0][2]=-0.3: 2*0.7*(-0.3) = -0.42
cx q[0], q[2]; rz(-0.42) q[2]; cx q[0], q[2];
// w[1][3]=-0.5: 2*0.7*(-0.5) = -0.7
cx q[1], q[3]; rz(-0.7) q[3]; cx q[1], q[3];

// Mixer layer: Rx(2*beta=1.0)
rx(1.0) q[0]; rx(1.0) q[1]; rx(1.0) q[2]; rx(1.0) q[3];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
