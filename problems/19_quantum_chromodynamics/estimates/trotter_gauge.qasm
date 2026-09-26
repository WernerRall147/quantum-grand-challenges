OPENQASM 2.0;
include "qelib1.inc";

// Transverse-field Ising chain: 4 sites, 3 first-order Trotter steps from |0000>, with
// beta dt = 0.5 (nearest-neighbour ZZ couplings) and h dt = 0.3 (transverse Rx field) per
// step: the same circuit as qsharp/HardwareKernel.qs. A spin-chain stand-in for lattice
// gauge dynamics, not a gauge theory. The previous export used angles so small that the
// state barely left |0000>, so no check could tell a right circuit from a wrong one.
// tooling/test_ising_chain_kernel.py simulates this file against exact evolution.
qreg q[4];
creg c[4];

// Trotter step 1
cx q[0], q[1]; rz(1.0) q[1]; cx q[0], q[1];
cx q[1], q[2]; rz(1.0) q[2]; cx q[1], q[2];
cx q[2], q[3]; rz(1.0) q[3]; cx q[2], q[3];
rx(0.6) q[0]; rx(0.6) q[1]; rx(0.6) q[2]; rx(0.6) q[3];

// Trotter step 2
cx q[0], q[1]; rz(1.0) q[1]; cx q[0], q[1];
cx q[1], q[2]; rz(1.0) q[2]; cx q[1], q[2];
cx q[2], q[3]; rz(1.0) q[3]; cx q[2], q[3];
rx(0.6) q[0]; rx(0.6) q[1]; rx(0.6) q[2]; rx(0.6) q[3];

// Trotter step 3
cx q[0], q[1]; rz(1.0) q[1]; cx q[0], q[1];
cx q[1], q[2]; rz(1.0) q[2]; cx q[1], q[2];
cx q[2], q[3]; rz(1.0) q[3]; cx q[2], q[3];
rx(0.6) q[0]; rx(0.6) q[1]; rx(0.6) q[2]; rx(0.6) q[3];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
