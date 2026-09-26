// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 08_protein_folding
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation FoldingQaoaKernel() : Result[] {
    use qs = Qubit[4];
    for q in qs { H(q); }
    // Toy four-variable Ising/QUBO energy, not a protein-folding model.
    // Same weights as Main.RunProteinFolding, with optimized p=1 angles
    // gamma = 0.47123889803846897 and beta = 1.119192382841364.
    CNOT(qs[0], qs[1]); Rz(-1.1309733552923256, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[0], qs[2]); Rz(-0.2827433388230814, qs[2]); CNOT(qs[0], qs[2]);
    CNOT(qs[1], qs[2]); Rz(-0.7539822368615504, qs[2]); CNOT(qs[1], qs[2]);
    CNOT(qs[1], qs[3]); Rz(-0.47123889803846897, qs[3]); CNOT(qs[1], qs[3]);
    CNOT(qs[2], qs[3]); Rz(-0.9424777960769379, qs[3]); CNOT(qs[2], qs[3]);
    for q in qs { Rx(2.238384765682728, q); }
    return MResetEachZ(qs);
}
