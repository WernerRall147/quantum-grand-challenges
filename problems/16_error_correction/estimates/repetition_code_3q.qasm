OPENQASM 2.0;
include "qelib1.inc";

// 3-qubit bit-flip repetition code with syndrome extraction
// Encodes |1>_L = |111>, injects X error on qubit 1, corrects
qreg code[3];
qreg syn[2];
creg sc[2];
creg out[1];

// Prepare logical |1>: start with |1> on data qubit
x code[0];

// Encode: |1> -> |111>
cx code[0], code[1];
cx code[0], code[2];

// Inject bit-flip error on qubit 1
x code[1];

// Syndrome extraction
cx code[0], syn[0];
cx code[1], syn[0];
cx code[1], syn[1];
cx code[2], syn[1];

// Measure syndromes
measure syn[0] -> sc[0];
measure syn[1] -> sc[1];

// Correction would be applied classically based on syndrome
// For this circuit: syndrome 11 -> error on qubit 1 -> apply X

// Decode
cx code[0], code[2];
cx code[0], code[1];

// Measure logical qubit
measure code[0] -> out[0];
