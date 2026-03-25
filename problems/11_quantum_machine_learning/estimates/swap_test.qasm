OPENQASM 2.0;
include "qelib1.inc";

// Swap test kernel estimation: ancilla + 2x2 feature registers
qreg anc[1];
qreg a[2];
qreg b[2];
creg c[1];

// Prepare feature states (simple rotations)
ry(0.6) a[0];
ry(1.2) a[1];
ry(0.8) b[0];
ry(1.0) b[1];

// Swap test
h anc[0];
cswap anc[0], a[0], b[0];
cswap anc[0], a[1], b[1];
h anc[0];

measure anc[0] -> c[0];
