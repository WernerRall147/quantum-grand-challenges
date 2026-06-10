#!/usr/bin/env python3
"""Create standalone HardwareKernel.qs files for all problems.

Each kernel contains only the core quantum operation (ansatz/oracle/circuit)
that can compile to Adaptive_RI QIR for Azure Quantum submission.
No measurement-dependent classical post-processing.
"""

from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# For each problem: a self-contained Q# file with @EntryPoint that compiles to QIR
# The kernel uses the same quantum operations but strips all classical statistics/loops
KERNELS = {
"01_hubbard": '''
import Std.Convert.IntAsDouble;
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation HubbardVQEKernel() : Result[] {
    use qs = Qubit[2];
    // VQE ansatz with fixed parameters (θ₀=1.0, θ₁=0.5, θ₂=0.3)
    X(qs[0]);
    Ry(1.0, qs[0]);
    Ry(0.5, qs[1]);
    CNOT(qs[0], qs[1]);
    Rz(0.3, qs[1]);
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
''',

"02_catalysis": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation ChemistryVQEKernel() : Result[] {
    use qs = Qubit[2];
    X(qs[0]);
    Ry(1.0, qs[0]);
    Ry(0.5, qs[1]);
    CNOT(qs[0], qs[1]);
    Rz(0.3, qs[1]);
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
''',

"05_qaoa_maxcut": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation QaoaMaxCutKernel() : Result[] {
    use qs = Qubit[3];
    // Init: uniform superposition
    for q in qs { H(q); }
    // Cost layer (triangle graph, γ=0.5)
    // Edge 0-1
    CNOT(qs[0], qs[1]); Rz(1.0, qs[1]); CNOT(qs[0], qs[1]);
    // Edge 0-2
    CNOT(qs[0], qs[2]); Rz(1.0, qs[2]); CNOT(qs[0], qs[2]);
    // Edge 1-2
    CNOT(qs[1], qs[2]); Rz(1.0, qs[2]); CNOT(qs[1], qs[2]);
    // Mixer layer (β=0.5)
    for q in qs { Rx(1.0, q); }
    return MResetEachZ(qs);
}
''',

"06_high_frequency_trading": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation HFTKernel() : Result[] {
    use qs = Qubit[2];
    use marker = Qubit();
    // Encode simple market state
    Ry(0.8, qs[0]);
    CNOT(qs[0], qs[1]);
    Ry(0.4, qs[1]);
    CNOT(qs[0], qs[1]);
    // Mark loss state |00⟩
    X(qs[0]); X(qs[1]);
    Controlled X(qs, marker);
    X(qs[0]); X(qs[1]);
    let r = [M(marker)];
    ResetAll(qs); Reset(marker);
    return r;
}
''',

"07_drug_discovery": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation DrugBindingKernel() : Result[] {
    use qs = Qubit[2];
    X(qs[0]);
    Ry(1.0, qs[0]);
    Ry(0.5, qs[1]);
    CNOT(qs[0], qs[1]);
    Rz(0.3, qs[1]);
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
''',

"08_protein_folding": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation FoldingQaoaKernel() : Result[] {
    use qs = Qubit[3];
    for q in qs { H(q); }
    // ZZ cost interactions
    CNOT(qs[0], qs[1]); Rz(0.6, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[1], qs[2]); Rz(0.8, qs[2]); CNOT(qs[1], qs[2]);
    // Mixer
    for q in qs { Rx(1.0, q); }
    return MResetEachZ(qs);
}
''',

"09_factorization": '''
import Std.Math.*;
import Std.Canon.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation ShorKernel() : Result[] {
    // Simplified period finding for N=15, a=7
    // 4 counting qubits + 4 work qubits
    use counting = Qubit[4];
    use work = Qubit[4];
    X(work[3]); // Init |1⟩
    for q in counting { H(q); }
    // Controlled modular multiplication (simplified for a=7, N=15)
    // U|x⟩ = |7x mod 15⟩ permutation: 1→7→4→13→1, etc.
    Controlled SWAP([counting[3]], (work[0], work[2]));
    Controlled SWAP([counting[3]], (work[1], work[3]));
    Controlled X([counting[3]], work[0]);
    Controlled X([counting[3]], work[1]);
    // Inverse QFT on counting register
    SWAP(counting[0], counting[3]);
    SWAP(counting[1], counting[2]);
    for j in 0..3 {
        for k in 0..j-1 {
            Controlled R1([counting[k]], (-PI() / IntAsDouble(1 <<< (j - k)), counting[j]));
        }
        H(counting[j]);
    }
    let result = MResetEachZ(counting);
    ResetAll(work);
    return result;
}
''',

"10_post_quantum_cryptography": '''
import Std.Math.*;
import Std.Canon.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation GroverKeyKernel() : Result[] {
    use qs = Qubit[3];
    // Grover search for target=5 (|101⟩) in 3-qubit space
    for q in qs { H(q); }
    // 1 Grover iteration (optimal for N=8, M=1: ~2 iterations, use 1 for small circuit)
    // Oracle: flip phase of |101⟩
    X(qs[1]);
    Controlled Z(qs[0..1], qs[2]);
    X(qs[1]);
    // Diffusion
    for q in qs { H(q); X(q); }
    Controlled Z(qs[0..1], qs[2]);
    for q in qs { X(q); H(q); }
    return MResetEachZ(qs);
}
''',

"11_quantum_machine_learning": '''
import Std.Math.*;
import Std.Measurement.*;

@EntryPoint()
operation SwapTestKernel() : Result[] {
    use ancilla = Qubit();
    use regA = Qubit[2];
    use regB = Qubit[2];
    // Encode feature vectors
    Ry(1.2, regA[0]); Ry(0.6, regA[1]);
    Ry(0.9, regB[0]); Ry(0.4, regB[1]);
    // Swap test
    H(ancilla);
    Controlled SWAP([ancilla], (regA[0], regB[0]));
    Controlled SWAP([ancilla], (regA[1], regB[1]));
    H(ancilla);
    let r = [M(ancilla)];
    ResetAll(regA); ResetAll(regB); Reset(ancilla);
    return r;
}
''',

"12_quantum_optimization": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation SchedulingQaoaKernel() : Result[] {
    use qs = Qubit[4];
    for q in qs { H(q); }
    // ZZ cost (job conflicts)
    CNOT(qs[0], qs[1]); Rz(0.8, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[1], qs[2]); Rz(0.6, qs[2]); CNOT(qs[1], qs[2]);
    CNOT(qs[2], qs[3]); Rz(0.4, qs[3]); CNOT(qs[2], qs[3]);
    // Mixer
    for q in qs { Rx(1.0, q); }
    return MResetEachZ(qs);
}
''',

"13_climate_modeling": '''
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
''',

"14_materials_discovery": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation MaterialsVQEKernel() : Result[] {
    use qs = Qubit[2];
    X(qs[0]);
    Ry(1.0, qs[0]);
    Ry(0.5, qs[1]);
    CNOT(qs[0], qs[1]);
    Rz(0.3, qs[1]);
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
''',

"15_database_search": '''
import Std.Math.*;
import Std.Canon.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation GroverSearchKernel() : Result[] {
    use qs = Qubit[4];
    for q in qs { H(q); }
    // 3 Grover iterations for N=16, M=1 (optimal ~ π/4·√16 ≈ 3)
    for _ in 1..3 {
        // Oracle: mark |0111⟩ = 7
        X(qs[0]);
        Controlled Z(qs[0..2], qs[3]);
        X(qs[0]);
        // Diffusion
        for q in qs { H(q); X(q); }
        Controlled Z(qs[0..2], qs[3]);
        for q in qs { X(q); H(q); }
    }
    return MResetEachZ(qs);
}
''',

"16_error_correction": '''
import Std.Measurement.*;

@EntryPoint()
operation QECKernel() : Result[] {
    use data = Qubit();
    use anc1 = Qubit();
    use anc2 = Qubit();
    // Prepare superposition state to protect
    H(data);
    // Encode: 3-bit repetition code
    CNOT(data, anc1);
    CNOT(data, anc2);
    // Introduce error on qubit 1 (simulated)
    X(anc1);
    // Syndrome extraction
    use syn = Qubit[2];
    CNOT(data, syn[0]); CNOT(anc1, syn[0]);
    CNOT(anc1, syn[1]); CNOT(anc2, syn[1]);
    // Measure syndrome and correct
    let s0 = M(syn[0]);
    let s1 = M(syn[1]);
    // Correction based on syndrome
    if s0 == One and s1 == One { X(anc1); }
    elif s0 == One { X(data); }
    elif s1 == One { X(anc2); }
    // Decode and measure
    CNOT(data, anc2); CNOT(data, anc1);
    let r = [MResetZ(data)];
    Reset(anc1); Reset(anc2); ResetAll(syn);
    return r;
}
''',

"17_nuclear_physics": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation NuclearVQEKernel() : Result[] {
    use qs = Qubit[2];
    X(qs[0]);
    Ry(1.0, qs[0]);
    Ry(0.5, qs[1]);
    CNOT(qs[0], qs[1]);
    Rz(0.3, qs[1]);
    CNOT(qs[0], qs[1]);
    return MResetEachZ(qs);
}
''',

"18_photovoltaics": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation QuantumWalkKernel() : Result[] {
    use coin = Qubit();
    use pos = Qubit[2];
    // 3 steps of quantum walk
    for _ in 1..3 {
        Ry(1.0, coin); // Coin flip
        // Conditional shift right
        Controlled SWAP([coin], (pos[0], pos[1]));
        // Conditional shift left
        X(coin);
        Controlled SWAP([coin], (pos[0], pos[1]));
        X(coin);
    }
    return MResetEachZ([coin] + pos);
}
''',

"19_quantum_chromodynamics": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation LatticeGaugeKernel() : Result[] {
    use qs = Qubit[4];
    // 3 Trotter steps (β=0.5, h=0.3)
    for _ in 1..3 {
        // ZZ plaquettes
        for i in 0..2 {
            CNOT(qs[i], qs[i+1]);
            Rz(1.0, qs[i+1]);
            CNOT(qs[i], qs[i+1]);
        }
        // Transverse field
        for q in qs { Rx(0.6, q); }
    }
    return MResetEachZ(qs);
}
''',

"20_space_mission_planning": '''
import Std.Math.*;
import Std.Measurement.MResetEachZ;

@EntryPoint()
operation MissionQaoaKernel() : Result[] {
    use qs = Qubit[3];
    for q in qs { H(q); }
    // Cost: single-qubit Z bias + pairwise ZZ
    Rz(0.4, qs[0]); Rz(0.6, qs[1]); Rz(0.3, qs[2]);
    CNOT(qs[0], qs[1]); Rz(0.8, qs[1]); CNOT(qs[0], qs[1]);
    CNOT(qs[1], qs[2]); Rz(0.5, qs[2]); CNOT(qs[1], qs[2]);
    // Mixer
    for q in qs { Rx(1.0, q); }
    return MResetEachZ(qs);
}
''',
}


def main():
    written = 0
    for name, kernel in sorted(KERNELS.items()):
        qsharp_dir = PROBLEMS_DIR / name / "qsharp"
        out_file = qsharp_dir / "HardwareKernel.qs"
        header = f"// HardwareKernel.qs  Minimal QIR-compatible kernel for Azure Quantum\n// Problem: {name}\n// Target profile: Adaptive_RI\n\n"
        out_file.write_text(header + kernel.strip() + "\n", encoding="utf-8")
        print(f"OK {name}")
        written += 1
    print(f"\nWrote {written} hardware kernels")


if __name__ == "__main__":
    main()
