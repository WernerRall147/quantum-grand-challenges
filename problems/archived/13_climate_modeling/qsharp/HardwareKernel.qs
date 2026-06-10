// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum
// Problem: 13_climate_modeling
// Target profile: Adaptive_RI

import Std.Math.*;
import Std.Measurement.*;
import Std.Convert.IntAsDouble;

@EntryPoint()
operation ClimateHHLKernel() : Result[] {
    use prec = Qubit[3];
    use sys = Qubit();
    use anc = Qubit();
    // Encode RHS
    Ry(1.2, sys);
    // Phase estimation
    for q in prec { H(q); }
    for k in 0..2 {
        let power = 1 <<< k;
        for _ in 1..power {
            Controlled Rz([prec[k]], (1.0, sys));
            Controlled Rx([prec[k]], (0.5, sys));
        }
    }
    // Simplified inverse QFT
    SWAP(prec[0], prec[2]);
    for j in 0..2 {
        for k in 0..j-1 {
            Controlled R1([prec[k]], (-PI() / IntAsDouble(1 <<< (j-k)), prec[j]));
        }
        H(prec[j]);
    }
    // Eigenvalue inversion
    for k in 0..2 {
        Controlled Ry([prec[k]], (0.3 / IntAsDouble(k + 1), anc));
    }
    let r = MResetEachZ(prec) + [M(anc)];
    Reset(sys); Reset(anc);
    return r;
}
