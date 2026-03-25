OPENQASM 2.0;
include "qelib1.inc";

// Trotter lattice gauge: 4-site 1D chain, 3 Trotter steps
// ZZ plaquettes + transverse Rx field
qreg q[4];
creg c[4];

// Trotter step 1 (dt=0.1)
cx q[0], q[1]; rz(0.2) q[1]; cx q[0], q[1];
cx q[1], q[2]; rz(0.2) q[2]; cx q[1], q[2];
cx q[2], q[3]; rz(0.2) q[3]; cx q[2], q[3];
rx(0.06) q[0]; rx(0.06) q[1]; rx(0.06) q[2]; rx(0.06) q[3];

// Trotter step 2
cx q[0], q[1]; rz(0.2) q[1]; cx q[0], q[1];
cx q[1], q[2]; rz(0.2) q[2]; cx q[1], q[2];
cx q[2], q[3]; rz(0.2) q[3]; cx q[2], q[3];
rx(0.06) q[0]; rx(0.06) q[1]; rx(0.06) q[2]; rx(0.06) q[3];

// Trotter step 3
cx q[0], q[1]; rz(0.2) q[1]; cx q[0], q[1];
cx q[1], q[2]; rz(0.2) q[2]; cx q[1], q[2];
cx q[2], q[3]; rz(0.2) q[3]; cx q[2], q[3];
rx(0.06) q[0]; rx(0.06) q[1]; rx(0.06) q[2]; rx(0.06) q[3];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
