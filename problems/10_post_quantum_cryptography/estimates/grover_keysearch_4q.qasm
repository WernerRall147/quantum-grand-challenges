OPENQASM 2.0;
include "qelib1.inc";

// Grover key search: 4-qubit keyspace, target=|1011> (index 11)
// 2 Grover iterations (optimal for N=16, M=1)
qreg q[4];
creg c[4];

// Uniform superposition
h q[0];
h q[1];
h q[2];
h q[3];

// === Iteration 1 ===
// Oracle: mark |1011> (flip q[2] since it's 0 in target)
x q[2];
h q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[1], q[3];
t q[3];
cx q[2], q[3];
tdg q[3];
cx q[0], q[3];
t q[0]; t q[1]; t q[2]; t q[3];
h q[3];
cx q[0], q[1]; t q[0]; tdg q[1]; cx q[0], q[1];
x q[2];

// Diffusion
h q[0]; h q[1]; h q[2]; h q[3];
x q[0]; x q[1]; x q[2]; x q[3];
h q[3];
cx q[2], q[3]; tdg q[3]; cx q[1], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[0], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[1], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[0], q[3];
t q[0]; t q[1]; t q[2]; t q[3];
h q[3];
cx q[0], q[1]; t q[0]; tdg q[1]; cx q[0], q[1];
x q[0]; x q[1]; x q[2]; x q[3];
h q[0]; h q[1]; h q[2]; h q[3];

// === Iteration 2 ===
x q[2];
h q[3];
cx q[2], q[3]; tdg q[3]; cx q[1], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[0], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[1], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[0], q[3];
t q[0]; t q[1]; t q[2]; t q[3];
h q[3];
cx q[0], q[1]; t q[0]; tdg q[1]; cx q[0], q[1];
x q[2];

h q[0]; h q[1]; h q[2]; h q[3];
x q[0]; x q[1]; x q[2]; x q[3];
h q[3];
cx q[2], q[3]; tdg q[3]; cx q[1], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[0], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[1], q[3]; t q[3];
cx q[2], q[3]; tdg q[3]; cx q[0], q[3];
t q[0]; t q[1]; t q[2]; t q[3];
h q[3];
cx q[0], q[1]; t q[0]; tdg q[1]; cx q[0], q[1];
x q[0]; x q[1]; x q[2]; x q[3];
h q[0]; h q[1]; h q[2]; h q[3];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
