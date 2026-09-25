OPENQASM 3.0;
include "stdgates.inc";

// Order finding for a = 7 mod 15 (order 4): the same circuit as qsharp/HardwareKernel.qs.
// Both registers are little-endian (index 0 is the lowest bit). count[k] controls U^(2^k)
// for U = multiplication by 7 mod 15; 7^2 = 4 and 7^4 = 1, so only count[0] and count[1]
// control anything, and c reads s * 16 / 4: c[0] and c[1] are 0, c[2] and c[3] uniform.
// The previous export controlled U with count[3] and applied x13 in place of x7, so it did
// not find the period, and its OpenQASM 2 gates (swap, cswap, cp) are not in the QDK's
// qelib1.inc. tooling/test_shor_kernel.py simulates this file.
qubit[4] count;
qubit[4] work;
bit[4] c;

x work[0];
h count[0];
h count[1];
h count[2];
h count[3];

// Controlled U: multiply by 7 = multiply by 8 (rotate one place toward the low end), then
// flip every bit, because 7x = 15 - 8x mod 15.
cswap count[0], work[0], work[1];
cswap count[0], work[1], work[2];
cswap count[0], work[2], work[3];
cx count[0], work[0];
cx count[0], work[1];
cx count[0], work[2];
cx count[0], work[3];

// Controlled U^2: multiply by 4 (rotate two places).
cswap count[1], work[0], work[2];
cswap count[1], work[1], work[3];

// Inverse QFT on the little-endian counting register.
swap count[0], count[3];
swap count[1], count[2];
h count[0];
cp(-pi / 2) count[0], count[1];
h count[1];
cp(-pi / 4) count[0], count[2];
cp(-pi / 2) count[1], count[2];
h count[2];
cp(-pi / 8) count[0], count[3];
cp(-pi / 4) count[1], count[3];
cp(-pi / 2) count[2], count[3];
h count[3];

c = measure count;
