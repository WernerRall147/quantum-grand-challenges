OPENQASM 2.0;
include "qelib1.inc";

// HHL for 2x2 thermal diffusion: A|x> = |b>
// 3 precision qubits + 1 system qubit + 1 ancilla = 5 qubits
// RHS |b> encoded via Ry rotation
// Hamiltonian simulation via Trotter (Rz+Rx)
// QPE extracts eigenvalues, controlled-Ry inverts

qreg prec[3];
qreg sys[1];
qreg anc[1];
creg c[2];

// Prepare |b> (temperature forcing)
ry(1.2) sys[0];

// QPE: Hadamard on precision register
h prec[0]; h prec[1]; h prec[2];

// Controlled Hamiltonian evolution: U^(2^k)
// Controlled-U^1 on prec[2]
cx prec[2], sys[0];
crz(1.0) prec[2], sys[0];
cx prec[2], sys[0];

// Controlled-U^2 on prec[1]
cx prec[1], sys[0];
crz(2.0) prec[1], sys[0];
cx prec[1], sys[0];

// Controlled-U^4 on prec[0]
cx prec[0], sys[0];
crz(4.0) prec[0], sys[0];
cx prec[0], sys[0];

// Inverse QFT on precision register
swap prec[0], prec[2];
h prec[0];
cp(-1.5707963267948966) prec[1], prec[0];
h prec[1];
cp(-0.7853981633974483) prec[2], prec[0];
cp(-1.5707963267948966) prec[2], prec[1];
h prec[2];

// Controlled rotation for eigenvalue inversion
cry(0.6) prec[0], anc[0];
cry(0.3) prec[1], anc[0];
cry(0.15) prec[2], anc[0];

// Measure ancilla (success indicator) and system
measure anc[0] -> c[0];
measure sys[0] -> c[1];
