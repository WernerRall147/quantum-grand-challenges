#!/usr/bin/env python3
"""Generate hand-crafted ASCII circuit diagrams for all 20 problems.

These diagrams show the core quantum kernel/ansatz for each problem,
not the full analysis loop. They are designed to be human-readable
and show the essential quantum structure.
"""

from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

CIRCUITS = {
"01_hubbard": """\
===================================================================
  Problem 01: Hubbard Model — VQE Ansatz (2-qubit)
  Algorithm: Variational Quantum Eigensolver
  Qubits: 2 | Params: θ₀, θ₁, θ₂ | Pauli terms: XX, YY, ZI, IZ
===================================================================

q0 ─── X ─── Ry(θ₀) ───── ● ──────────── ● ─── ⟨Pauli⟩
                           │              │
q1 ──────── Ry(θ₁) ────── X ── Rz(θ₂) ── X ─── ⟨Pauli⟩

  Step 1: X initializes q0 to |1⟩  (Hartree-Fock reference)
  Step 2: Ry rotations create parameterized superposition
  Step 3: CNOT-Rz-CNOT entangles and adds ZZ correlation
  Step 4: Measure ⟨XX⟩, ⟨YY⟩, ⟨ZI⟩, ⟨IZ⟩ Pauli expectations
  Step 5: Classical optimizer updates θ₀, θ₁, θ₂

  Energy = -t(⟨XX⟩ + ⟨YY⟩) + U/2(⟨ZI⟩ + ⟨IZ⟩)
""",

"02_catalysis": """\
===================================================================
  Problem 02: Catalysis — VQE for H₂ Ground State (2-qubit)
  Algorithm: Variational Quantum Eigensolver (STO-3G basis)
  Qubits: 2 | Params: θ₀, θ₁, θ₂
===================================================================

q0 ─── X ─── Ry(θ₀) ───── ● ──────────── ● ─── ⟨Pauli⟩
                           │              │
q1 ──────── Ry(θ₁) ────── X ── Rz(θ₂) ── X ─── ⟨Pauli⟩

  Same hardware-efficient ansatz as Hubbard (shared 2-qubit structure)
  
  H₂ Hamiltonian (STO-3G, R=0.74 Å):
    H = c₀·I + c₁·Z₀ + c₂·Z₁ + c₃·Z₀Z₁ + c₄·X₀X₁
  
  Measures: ⟨Z₀⟩, ⟨Z₁⟩, ⟨Z₀Z₁⟩, ⟨X₀X₁⟩
  Arrhenius activation energy derived from ground state
""",

"03_qae_risk": """\
===================================================================
  Problem 03: QAE Risk — IQAE Kernel (5-qubit)
  Algorithm: Iterative Quantum Amplitude Estimation
  Qubits: 4 loss + 1 marker = 5 (no precision register)
===================================================================

            ┌──────────────────────┐   ┌─────────────────┐
loss[0] ──┤                        ├──┤                   ├──┤ Q^k ├── ...
loss[1] ──┤  PrepareDistribution   ├──┤  OracleTailMark  ├──┤     ├── ...
loss[2] ──┤  (Ry + Controlled Ry   ├──┤  (multi-CNOT on  ├──┤     ├── ...
loss[3] ──┤   multiplexed rots)    ├──┤   threshold)     ├──┤     ├── ...
           └──────────────────────┘   └────────┬──────────┘  └──┬──┘
marker ────────────── |0⟩ ─────────────────── X ──────────────── M

  IQAE Round (k Grover iterations):
    1. A = Oracle ∘ StatePrep  →  √(1-a)|bad⟩|0⟩ + √a|good⟩|1⟩
    2. Q^k = (A · S₀ · A† · Sχ)^k  amplifies marked amplitude
    3. Measure marker: P(1) = sin²((2k+1)θ), sin²(θ) = a

  Classical driver picks k adaptively to narrow confidence interval
  No QFT or precision register needed — 44% fewer qubits than QPE
""",

"04_linear_solvers": """\
===================================================================
  Problem 04: Linear Solvers — HHL Algorithm (5-qubit)
  Algorithm: Harrow-Hassidim-Lloyd
  Qubits: 1 system + 3 precision + 1 ancilla = 5
===================================================================

            ┌────────┐  ┌──────────────┐  ┌────────┐  ┌────────┐
prec[0] ─── H ───────┤              ├──┤                ├──┤      ├── M
prec[1] ─── H ───────┤  Controlled   ├──┤  Inverse QFT   ├──┤      ├── M
prec[2] ─── H ───────┤  e^{iAt·2^k}  ├──┤  (H + CR1 +    ├──┤      ├── M
              │       │  (Trotter)    ├──┤   SWAP)        ├──┤      ├──
system ── Ry(b) ─────┤              ├──┤                ├──┤ C-Ry ├──
               └─────┘  └──────────────┘  └────────┘  └───┬────┘
ancilla ──── |0⟩ ──────────────────────────────────────── Ry ─── M

  1. Encode RHS vector |b⟩ via Ry rotation on system qubit
  2. Phase estimation: H on precision, controlled Hamiltonian sim
  3. Inverse QFT extracts eigenvalues into precision register
  4. Controlled rotation: Ry(C/λ) on ancilla conditioned on eigenvalue
  5. Measure ancilla — post-select on |1⟩ to get |x⟩ ∝ A⁻¹|b⟩
""",

"05_qaoa_maxcut": """\
===================================================================
  Problem 05: QAOA MaxCut (3-qubit triangle graph)
  Algorithm: Quantum Approximate Optimization Algorithm
  Qubits: 3 (one per vertex) | Depth: p layers
===================================================================

                    ┌── Cost Layer (γ) ──┐  ┌── Mixer Layer (β) ──┐
q0 ─── H ──────── ZZ(γ·w₀₁) ── ZZ(γ·w₀₂) ── Rx(2β) ─── ... ─── M
                     ╳                        
q1 ─── H ──────── ZZ(γ·w₀₁) ── ZZ(γ·w₁₂) ── Rx(2β) ─── ... ─── M
                                   ╳
q2 ─── H ──────── ZZ(γ·w₀₂) ── ZZ(γ·w₁₂) ── Rx(2β) ─── ... ─── M

  ZZ interaction (per edge):
    q_i ─── ● ──────────── ● ───
             │              │
    q_j ─── X ── Rz(2γw) ── X ───  =  exp(-iγw · Z⊗Z)

  1. Initialize uniform superposition |+⟩^n
  2. Cost layer: ZZ rotations for each edge (encodes cut value)
  3. Mixer layer: Rx rotations (drives exploration)
  4. Repeat p times, measure, evaluate cut value
  5. Classical optimizer tunes (γ, β)
""",

"06_high_frequency_trading": """\
===================================================================
  Problem 06: HFT — Amplitude Estimation for VaR (3-qubit)
  Algorithm: Quantum Amplitude Estimation
  Qubits: 2 register + 1 marker = 3
===================================================================

reg[0] ─── Ry(θ₀) ─── X ─── Controlled Ry ─── Controlled Ry ───── ...
                              │                │
reg[1] ──────────────────── Ry(θ₁) ─────── Ry(θ₂) ─── ● ──── ...
                                                        │
marker ─── |0⟩ ──────────────────────────────────────── X ──── M

  State prep encodes P&L distribution into amplitudes
  Oracle marks loss states (P&L < threshold)
  Grover amplification + measurement estimates VaR tail probability
""",

"07_drug_discovery": """\
===================================================================
  Problem 07: Drug Discovery — VQE Binding Energy (2-qubit)
  Algorithm: Variational Quantum Eigensolver
  Qubits: 2 | Model: ligand-receptor binding Hamiltonian
===================================================================

q0 ─── X ─── Ry(θ₀) ───── ● ──────────── ● ─── ⟨Pauli⟩
                           │              │
q1 ──────── Ry(θ₁) ────── X ── Rz(θ₂) ── X ─── ⟨Pauli⟩

  Same 2-qubit VQE ansatz applied to binding-energy Hamiltonian
  Measures ⟨Z₀⟩, ⟨Z₁⟩, ⟨Z₀Z₁⟩, ⟨X₀X₁⟩ for energy estimation
  Binding affinity ∝ ground state energy ↔ drug efficacy
""",

"08_protein_folding": """\
===================================================================
  Problem 08: Protein Folding — QAOA on Contact Map (4-qubit)
  Algorithm: QAOA for lattice protein folding
  Qubits: 4 (residue positions)
===================================================================

           ┌──── Cost (γ) ────┐  ┌── Mixer (β) ──┐
q0 ── H ── ● ──────────────── ● ── Rx(2β) ────── ...  ── M
            │   ZZ(2γw₀₁)     │
q1 ── H ── X ── Rz ── X ── ● ── Rx(2β) ────── ...  ── M
                             │   ZZ(2γw₁₂)
q2 ── H ──────────────── X ── Rz ── X ── ● ── Rx(2β) ── M
                                          │
q3 ── H ──────────────────────────── X ── Rz ── X ── Rx(2β) ── M

  Contact energy Hamiltonian: Σ wᵢⱼ ZᵢZⱼ (pairwise residue interactions)
  Minimizes folding energy = maximizes native contacts
""",

"09_factorization": """\
===================================================================
  Problem 09: Factorization — Shor's Algorithm, N=15 (8-qubit)
  Algorithm: Quantum Phase Estimation for period finding
  Qubits: 4 counting + 4 work = 8
===================================================================

count[0] ─── H ─── Ctrl-U^8 ─────────────────── ┐
count[1] ─── H ──────── Ctrl-U^4 ────────────── ┤ Inverse
count[2] ─── H ──────────── Ctrl-U^2 ────────── ┤  QFT    ─── M
count[3] ─── H ──────────────── Ctrl-U^1 ────── ┘          ─── M
                                │ │ │ │
work[0] ──── |0⟩ ──────────── ┤ ├ ┤ ├ ────────────────────
work[1] ──── |0⟩ ──────────── ┤ U^k(a,N) ├ ────────────────
work[2] ──── |0⟩ ──────────── ┤ = a^k mod N├ ──────────────
work[3] ──── |1⟩ ──────────── ┤ (SWAP+CNOT)├ ──────────────

  U|x⟩ = |a·x mod N⟩ for a=7, N=15
  U^k implemented via controlled SWAP/CNOT permutations  
  After inverse QFT, count register encodes s/r (period fraction)
  Classical post-processing: continued fractions → r → factors
""",

"10_post_quantum_cryptography": """\
===================================================================
  Problem 10: Post-Quantum Crypto — Grover Key Search (n-qubit)
  Algorithm: Grover's search (brute-force key exhaustion)
  Qubits: n (keyspace = 2ⁿ) | Tested: n = 3, 4, 5
===================================================================

         ┌─ H^n ─┐  ┌── Oracle ──┐  ┌── Diffusion ──┐
q[0] ─── H ──────── X?── Ctrl-Z ── X? ── H ── X ── Ctrl-Z ── X ── H ─── ×⌊π/4·√N⌋
q[1] ─── H ──────── X?──   │    ── X? ── H ── X ──   │    ── X ── H ──
 ...      ...          ...  │     ...        ...       │         ...
q[n-1] ── H ──────── X?── Z ──── X? ── H ── X ── Z ──── X ── H ───

  Oracle: flips phase of |target⟩ via X-gates + multi-controlled Z
  Diffusion: 2|s⟩⟨s|-I = H·(2|0⟩⟨0|-I)·H
  Optimal iterations: ⌊π/4 · √(2ⁿ)⌋

  Security implication: reduces n-bit key to √n effective strength
    AES-128: classical 2^127 → quantum ~2^64 queries
    AES-256: classical 2^255 → quantum ~2^128 queries
""",

"11_quantum_machine_learning": """\
===================================================================
  Problem 11: Quantum ML — Swap Test Kernel (5-qubit)
  Algorithm: Quantum Kernel Estimation via Swap Test
  Qubits: 2 (regA) + 2 (regB) + 1 (ancilla) = 5
===================================================================

ancilla ─── H ──────── ● ──────── ● ──── H ─── M
                       │          │
regA[0] ── Ry(x₀) ── SWAP ────── │ ──────────── 
regA[1] ── Ry(x₁) ──  │  ─────── │ ────────────
                       │          │
regB[0] ── Ry(y₀) ────┘    ──── SWAP ──────────
regB[1] ── Ry(y₁) ──────── ─────  │  ──────────

  1. Encode feature vectors x, y into amplitudes via Ry
  2. Controlled-SWAP between registers (conditioned on ancilla)
  3. Measure ancilla: P(0) = (1 + |⟨x|y⟩|²) / 2
  4. Kernel value K(x,y) = |⟨x|y⟩|² for SVM/classifier
""",

"12_quantum_optimization": """\
===================================================================
  Problem 12: Quantum Optimization — QAOA Job Scheduling (4-qubit)
  Algorithm: QAOA for weighted scheduling
  Qubits: 4 (one per job)
===================================================================

           ┌ Cost(γ): ZZ for conflicts ┐  ┌ Mixer(β) ┐
q0 ── H ── ● ──────────────── ● ──────── Rx(2β) ── × p layers ── M
            │                  │
q1 ── H ── X ── Rz(2γw) ── X ── ● ────── Rx(2β) ─────────────── M
                                  │
q2 ── H ──────────────── X ── Rz ── X ── Rx(2β) ─────────────── M
q3 ── H ──────────────────────────────── Rx(2β) ─────────────── M

  Encodes job conflict graph as ZZ interactions
  Minimizes weighted makespan / maximizes throughput
""",

"13_climate_modeling": """\
===================================================================
  Problem 13: Climate Modeling — HHL for Diffusion PDE (5-qubit)
  Algorithm: HHL quantum linear solver
  Qubits: 3 precision + 1 system + 1 ancilla = 5
===================================================================

prec[0] ── H ──── Ctrl-e^{iHt} ─────────────────────── ┐
prec[1] ── H ───────── Ctrl-e^{iH·2t} ──────────────── ┤ Inv QFT
prec[2] ── H ───────────── Ctrl-e^{iH·4t} ──────────── ┘
                              │                    ┌─────────────┐
system ── Ry(b) ──────────── Trotter ──────────── │ C-Ry(C/λ)  │
                                                   └──────┬──────┘
ancilla ── |0⟩ ────────────────────────────────────────── Ry ── M

  Trotter step: Rz(2t)·Rx(t) (discretized diffusion operator)
  Solves Ax=b where A encodes spatial diffusion operator
  Solution encodes temperature/concentration field
""",

"14_materials_discovery": """\
===================================================================
  Problem 14: Materials Discovery — VQE Band Gap (2-qubit)
  Algorithm: Variational Quantum Eigensolver
  Qubits: 2 | Model: tight-binding Hamiltonian
===================================================================

q0 ─── X ─── Ry(θ₀) ───── ● ──────────── ● ─── ⟨Pauli⟩
                           │              │
q1 ──────── Ry(θ₁) ────── X ── Rz(θ₂) ── X ─── ⟨Pauli⟩

  Estimates ground/excited state energies of tight-binding model
  Band gap = E_excited - E_ground (key material property)
  Critical for photovoltaics, semiconductors, superconductors
""",

"15_database_search": """\
===================================================================
  Problem 15: Database Search — Grover's Algorithm (n-qubit)
  Algorithm: Grover's quantum search
  Qubits: n (search space = 2ⁿ) | Tested: n = 4, 5, 12
===================================================================

     ┌─ Init ─┐  ┌───── Oracle ──────┐  ┌───── Diffusion ──────┐
q[0] ── H ────── X?──── Ctrl-Z ──── X? ── H ── X ── Ctrl-Z ── X ── H ──
q[1] ── H ────── X?────   |    ──── X? ── H ── X ──   |    ── X ── H ──
q[2] ── H ────── X?────   |    ──── X? ── H ── X ──   |    ── X ── H ──
q[3] ── H ────── X?──── Z ──────── X? ── H ── X ── Z ────── X ── H ──
                 └─ flip unmarked ──┘    └─ reflect about |s⟩ ─┘
                 
     ↑ Repeat ⌊π/4 · √(N/M)⌋ times for M targets in N items ↑

  Multi-target oracle: marks each target state with phase flip
  Diffusion: reflects about uniform superposition |s⟩
  Success probability: >90% at optimal iteration count
""",

"16_error_correction": """\
===================================================================
  Problem 16: Error Correction — 3-Bit Repetition Code (5-qubit)
  Algorithm: Quantum error correction (bit-flip code)
  Qubits: 3 code + 2 syndrome = 5
===================================================================

          ┌─ Encode ──┐  ┌─ Error ─┐  ┌── Syndrome ──┐  ┌ Correct ┐
data ──── ● ──── ● ─── X(p)? ───── ● ──────── ● ────── X? ──── M
          │      │                  │           │
anc1 ──── X ──── │ ──── X(p)? ──── X ── ● ──── │ ────── X? ──── M
                 │                       │      │
anc2 ──── ────── X ──── X(p)? ────────── X ──── X ────── X? ──── M
                                         │      │
syn0 ──── ─────────────────────────────── M ──── │ ────────────── 
                                                 │
syn1 ──── ──────────────────────────────────── M ──────────────

  Encode: CNOT copies logical qubit across 3 physical qubits
  Error: random bit-flip X with probability p
  Syndrome: parity checks detect which qubit flipped
    syn0 = q0 ⊕ q1, syn1 = q1 ⊕ q2
  Correct: apply X to the identified erroneous qubit
""",

"17_nuclear_physics": """\
===================================================================
  Problem 17: Nuclear Physics — VQE Deuteron (2-qubit)
  Algorithm: Variational Quantum Eigensolver
  Qubits: 2 | Model: deuteron EFT Hamiltonian
===================================================================

q0 ─── X ─── Ry(θ₀) ───── ● ──────────── ● ─── ⟨Pauli⟩
                           │              │
q1 ──────── Ry(θ₁) ────── X ── Rz(θ₂) ── X ─── ⟨Pauli⟩

  Deuteron Hamiltonian (2-body EFT):
    H = c₀·I + c₁·Z₀ + c₂·Z₁ + c₃·Z₀Z₁ + c₄·X₀X₁ + c₅·Y₀Y₁
  
  Ground state energy → deuteron binding energy (2.22 MeV)
""",

"18_photovoltaics": """\
===================================================================
  Problem 18: Photovoltaics — Quantum Walk (3-qubit)
  Algorithm: Discrete-time quantum walk (exciton transport)
  Qubits: 1 coin + 2 position = 3
===================================================================

            ┌── Coin ──┐  ┌──── Shift ────┐
coin ──── Ry(2g) ──── X ──── ● ──────────── ● ────── × T steps
                             │              │
pos[0] ──────────────────── SWAP ────────── │ ──────
                              │             │ 
pos[1] ──────────────────────┘──────────── SWAP ────

  1. Coin rotation: Ry(2g) controls L/R probability (coupling strength)
  2. Conditional shift: SWAP position register based on coin state
  3. Simulates exciton hopping along a 1D chain
  4. Quantum walk spreads ballistically: σ ∝ t (vs √t classical)
  5. Models photon-harvesting efficiency in organic photovoltaics
""",

"19_quantum_chromodynamics": """\
===================================================================
  Problem 19: QCD — Trotterized Lattice Gauge (4-qubit)
  Algorithm: Hamiltonian simulation (1st order Trotter)
  Qubits: 4 (lattice sites)
===================================================================

           ┌──── ZZ plaquettes ────────┐  ┌── Transverse field ──┐
q[0] ──── ● ──────────────── ──────── ──── Rx(2h) ────────────── × T steps
           │                               
q[1] ──── X ── Rz(2β) ── X ── ● ──── ──── Rx(2h) ──────────────
                                │
q[2] ──── ────────────── X ── Rz(2β) ── X ── ● ── Rx(2h) ──────
                                               │
q[3] ──── ──────────────────────────── X ── Rz(2β) ── X ── Rx(2h)

  H = -β Σᵢ ZᵢZᵢ₊₁ - h Σᵢ Xᵢ   (simplified Z₂ lattice gauge)
  
  ZZ interaction: CNOT-Rz-CNOT decomposes exp(-iβ ZZ)
  Transverse field: Rx(2h) = exp(-ih X)
  Trotter error: O(Δt²) per step
""",

"20_space_mission_planning": """\
===================================================================
  Problem 20: Space Mission — QAOA Trajectory (4-qubit)
  Algorithm: QAOA for trajectory optimization
  Qubits: 4 (mission leg assignments)
===================================================================

           ┌── Cost(γ): Δv bias + window conflicts ──┐  ┌ Mixer ┐
q0 ── H ── Rz(2γ·Δv₀) ── ● ──────────────── ● ────── Rx(2β) ── M
                           │  ZZ(conflict)    │
q1 ── H ── Rz(2γ·Δv₁) ── X ── Rz(2γw) ── X ── ● ── Rx(2β) ── M
                                                  │
q2 ── H ── Rz(2γ·Δv₂) ──────────────── X ── Rz ── X ── Rx(2β) ── M
q3 ── H ── Rz(2γ·Δv₃) ──────────────────────────── Rx(2β) ── M

  Cost encodes: single-qubit Δv budget + pairwise time window conflicts
  Finds optimal trajectory assignment minimizing total Δv
"""
}


def main():
    written = 0
    for problem_name, diagram in CIRCUITS.items():
        circuits_dir = PROBLEMS_DIR / problem_name / "circuits"
        circuits_dir.mkdir(exist_ok=True)
        out_path = circuits_dir / "circuit.txt"
        out_path.write_text(diagram, encoding="utf-8")
        lines = len(diagram.strip().splitlines())
        print(f"OK {problem_name}: {lines} lines")
        written += 1
    print(f"\nWrote {written} circuit diagrams")


if __name__ == "__main__":
    main()
