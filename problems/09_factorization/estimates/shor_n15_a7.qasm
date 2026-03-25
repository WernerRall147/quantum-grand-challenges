OPENQASM 2.0;
include "qelib1.inc";

// Shor's algorithm: period finding for a=7 mod 15
// 4 counting qubits (QPE) + 4 work qubits
// Controlled multiply by 7 mod 15: permutation 1->7->4->13->1 (period=4)
// Controlled multiply by 7^2=4 mod 15: swap pairs
// Controlled multiply by 7^4=1 mod 15: identity (no-op)

qreg count[4];
qreg work[4];
creg c[4];

// Initialize work register to |0001> (value 1)
x work[3];

// Hadamard on counting register
h count[0]; h count[1]; h count[2]; h count[3];

// Controlled-U^1 (multiply by 7 mod 15): controlled on count[3]
// 7 mod 15 permutation: shift + flip
cswap count[3], work[0], work[1];
cswap count[3], work[1], work[2];
cswap count[3], work[2], work[3];
cx count[3], work[0];
cx count[3], work[1];
cx count[3], work[2];
cx count[3], work[3];

// Controlled-U^2 (multiply by 4 mod 15): controlled on count[2]
// 4 = 7^2 mod 15 permutation: swap(0,2) swap(1,3)
cswap count[2], work[0], work[2];
cswap count[2], work[1], work[3];

// Controlled-U^4 = identity (7^4 mod 15 = 1): no gates on count[1]
// Controlled-U^8 = identity: no gates on count[0]

// Inverse QFT on counting register
// Swap bit order
swap count[0], count[3];
swap count[1], count[2];

// QFT^-1 layers
h count[0];
cp(-1.5707963267948966) count[1], count[0];
h count[1];
cp(-0.7853981633974483) count[2], count[0];
cp(-1.5707963267948966) count[2], count[1];
h count[2];
cp(-0.39269908169872414) count[3], count[0];
cp(-0.7853981633974483) count[3], count[1];
cp(-1.5707963267948966) count[3], count[2];
h count[3];

// Measure counting register
measure count[0] -> c[0];
measure count[1] -> c[1];
measure count[2] -> c[2];
measure count[3] -> c[3];
