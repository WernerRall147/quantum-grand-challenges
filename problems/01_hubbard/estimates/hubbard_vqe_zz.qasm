OPENQASM 2.0;
include "qelib1.inc";

// Hubbard VQE: 2-site half-filling ansatz + ZZ measurement
// Parameters: theta0=pi/4, theta1=pi/2, theta2=pi/8
// Measures ZZ expectation value (interaction term)
qreg q[2];
creg c[2];

// Initialize |01> (half-filling: one electron per site)
x q[0];

// VQE ansatz: Ry rotations + CNOT entangling layers
ry(0.7853981633974483) q[0];
ry(1.5707963267948966) q[1];
cx q[0], q[1];
rz(0.39269908169872414) q[1];
cx q[0], q[1];

// Measure in computational basis (ZZ)
measure q[0] -> c[0];
measure q[1] -> c[1];
