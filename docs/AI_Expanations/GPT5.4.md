Quantum Grand Challenges Repository — End-to-End Analysis
🌌 What the Project Is Trying to Achieve (For a Non-Specialist)
Imagine you wanted to test whether quantum computers — a fundamentally different kind of computer that harnesses quantum mechanics — could eventually solve problems that stump today's best supercomputers. But quantum computers are still immature, noisy, and tiny. How do you prepare for them now?

This repository, WernerRall147/quantum-grand-challenges, takes a methodical engineering approach: it picks 20 of the world's hardest scientific and engineering problems, sets up a rigorous classical (conventional computer) baseline for each, writes quantum programs in Microsoft's Q# language representing the best-known quantum algorithm for each problem, and tracks how far each quantum approach is from being practically useful. Everything is plumbed into CI/CD pipelines, resource estimators, and a live dashboard at https://wernerrall147.github.io/quantum-grand-challenges/.

The key honest caveat — stated openly in the repository — is that no quantum computer in 2026 can actually outperform classical methods on any of these 20 problems. The repository's value is in the research scaffolding: defining what success would look like, building reproducible classical comparisons, and estimating what hardware would be needed. As [README.md, lines 259–280] summarizes: only three problems (03, 05, 15) are at "Stage C" (hardware-aware validation); the other 17 are at "Stage B" (quantum algorithm compiles and runs, but no comparative advantage evidence yet).

Architecture & Infrastructure
The repository is built around a consistent four-stage maturity gate model, described in [docs/objective-gates.md]:

Stage	Meaning
A	Deterministic classical baseline validated with parameterized instances
B	Q# implementation compiles and runs; resource estimation scaffolded
C	Hardware-aware validation: calibration evidence, uncertainty bounds, Azure Quantum checks
D	Full advantage evidence package: fair classical comparator, explicit claim category (theoretical/projected/demonstrated)
The stack is:

Q# (Microsoft) via modern QDK (qsharp Python package v1.27, no .NET dependency) — [README.md, lines 52–66]
Azure Quantum Resource Estimator for fault-tolerant cost projections
Python for classical baselines and analysis
Next.js for the live dashboard
GitHub Actions CI/CD running all 20 classical, build, and test targets in every push — [README.md, lines 20–27]
Problem-by-Problem Analysis
01 · Hubbard Model (Strongly Correlated Electrons)
Scientific challenge: The Hubbard model is a toy model for electrons on a lattice, capturing how strong on-site repulsion leads to Mott insulator phases and potentially explains high-temperature superconductivity. Even the two-site version contains the key physics. Scaling it to large lattices is computationally intractable classically. [problems/01_hubbard/README.md, lines 1–12]

Quantum approach: Variational Quantum Eigensolver (VQE) with an Ry+CNOT+Rz ansatz and Pauli expectation measurements, plus a full HHL implementation for comparison. Resource estimates: VQE needs 48.5k–110k physical qubits; HHL needs 18.7k qubits. [README.md, lines 262, 402–406]

Real-world impact if successful: Designing room-temperature superconductors, novel magnetic materials, and fundamentally understanding quantum matter.

Current repo status: Stage B. The two-site implementation is deliberately minimal ("intentionally small," per README.md line 79). The Q# code performs analytical parity with classical results — it doesn't add quantum value yet; it validates the wiring.

Classical vs. quantum today (2026): Exact diagonalization handles small systems easily; density-matrix renormalization group (DMRG) and tensor network methods handle 1D/quasi-1D lattices up to ~100 sites efficiently. For 2D strongly correlated systems, classical methods struggle. Quantum simulation is genuinely promising here — this is often cited as a canonical use case for quantum advantage. However, demonstrating advantage even for small 2D Hubbard models requires error-corrected hardware far beyond today's devices (the resource estimates suggest ~50k–110k physical qubits for toy instances).

02 · Catalysis Simulation
Scientific challenge: Predicting reaction rates and energy barriers for heterogeneous catalysts (e.g., Pt, Fe, Cu). Industrial catalysis underlies ~90% of chemical manufacturing. The goal is to replace empirical trial-and-error with quantum-accurate first-principles simulation. [problems/02_catalysis/README.md, lines 1–4]

Quantum approach: VQE for H₂ molecular ground state in STO-3G basis with Pauli Hamiltonian decomposition. Plan: VQE → Phase Estimation for precision refinement. [README.md, line 263]

Real-world impact: Designing more efficient and selective catalysts for green chemistry, ammonia synthesis, CO₂ reduction.

Current repo status: Stage B. The Q# code replicates an Arrhenius rate formula — the same formula as the Python baseline. No genuine quantum chemistry simulation yet. [problems/02_catalysis/README.md, lines 37, 44–46]

Classical vs. quantum today: DFT (VASP, Quantum ESPRESSO) works well for many catalysts and is the industrial standard. For strongly correlated transition-metal active sites (e.g., nitrogenase's iron-molybdenum cofactor), DFT is unreliable and quantum simulation is widely expected to provide advantage. This is an active and promising area — Microsoft and IBM both cite catalysis as a near-term quantum use case, but practical demonstrations on real molecules remain limited to tiny systems (H₂, LiH) that classical methods handle trivially.

03 · Quantum Amplitude Estimation for Financial Risk Analysis (Most Advanced)
Scientific challenge: Estimating tail risk probabilities — e.g., P(portfolio loss > threshold) — with high precision. Classical Monte Carlo requires O(1/ε²) samples for precision ε. This is expensive for high-precision financial risk audits (e.g., ε = 0.001). [problems/03_qae_risk/README.md, lines 1–14]

Quantum approach: Iterative Quantum Amplitude Estimation (IQAE, no QPE register): adaptive Grover amplification rounds with Clopper-Pearson confidence intervals, matching the theoretical quadratic speedup O(1/ε). Classical Monte Carlo baseline: 18.98% ± 0.39% for 10k samples; QAE achieves 19.58% ± 1.82% on 20 ensemble runs. [docs/QAE_PROJECT_COMPLETION.md, lines 27–36]

Real-world impact: Cheaper, faster financial stress testing for banks and regulators; more responsive risk management.

Current repo status: Stage C (most advanced in the repo). Full canonical QAE implementation with Grover operators, QPE, inverse QFT, and statistical averaging. Azure Quantum Resource Estimates: 594k physical qubits, 6.4s runtime, 965k T-states for the optimal architecture. [docs/QAE_PROJECT_COMPLETION.md, lines 47–65]

Classical vs. quantum today: Finance is one of the most-cited quantum advantage applications. The IQAE algorithm is well-established theoretically (Brassard et al., Grinko et al.). The theoretical O(1/ε) advantage is real. However, the catch is that even at O(1/ε) speedup, fault-tolerant quantum hardware capable of running it (594k qubits) is estimated to be 10+ years away by most industry roadmaps. Current NISQ machines with noise degrade the advantage significantly. Goldman Sachs and JPMorgan have published research exploring this, but practical deployment remains distant.

04 · Quantum Linear Solvers (HHL)
Scientific challenge: Solving large sparse linear systems Ax = b — the backbone of PDE solvers (fluid dynamics, climate models, structural analysis). The classical complexity is O(N log N) for sparse systems. HHL claims O(log N) complexity. [problems/04_linear_solvers/README.md, lines 1–3]

Quantum approach: Full HHL implementation: state preparation (Ry encoding), block encoding, 4-qubit QPE, inverse QFT, eigenvalue inversion via controlled Ry rotations, ancilla post-selection. Resource: 18.7k qubits, 52ms runtime for a 2×2 system. Success probability ~26.6% (1/κ²). [problems/04_linear_solvers/README.md, lines 38–62]

Real-world impact: If practical, would revolutionize PDE-based simulations used in aerospace, climate, engineering.

Current repo status: Stage B. The HHL implementation works for a 2×2 system — a toy problem any laptop handles in nanoseconds. The 18.7k physical qubit estimate is for this tiny instance. [problems/04_linear_solvers/README.md, line 60: "62% fewer qubits than VQE, demonstrates near-term feasibility for small-scale quantum advantage exploration."]

Classical vs. quantum today: HHL is highly controversial. Multiple papers (Aaronson 2015, Tang 2019) have shown that the practical conditions for quantum advantage are extremely restrictive: A must be sparse, κ (condition number) must be small, quantum state preparation of b must be efficient, and the output must be a quantum state (reading all N elements destroys the speedup). Classical algorithms already achieve O(κ √N log(1/ε)) for sparse systems. The "quantum advantage" largely disappears in practice. This is considered speculative for most real applications.

05 · QAOA for Max-Cut
Scientific challenge: Max-Cut on a weighted graph: partition nodes into two sets to maximize the total weight of cut edges. NP-hard in general. Used in VLSI layout, network partitioning. [problems/05_qaoa_maxcut/README.md, lines 1–3]

Quantum approach: Quantum Approximate Optimization Algorithm (QAOA) with ZZ cost layer, Rx mixer, coordinate-descent parameter optimizer. Depth sweeps (1–3 layers) and noise sweeps included. Azure Quantum syntax checker validated. [README.md, line 265]

Real-world impact: Better combinatorial optimization for logistics, network design, machine scheduling.

Current repo status: Stage C. Most developed QAOA implementation in the repo. Includes depth sweep evidence artifacts, noise sensitivity analysis, Azure manifest for cloud submission. Classical brute-force baseline for exact cut values. [problems/05_qaoa_maxcut/README.md, lines 11–16]

Classical vs. quantum today: The Goemans-Williamson algorithm gives a provable 0.878-approximation for Max-Cut in polynomial time. QAOA at finite depth has not been shown to beat GW. Recent theoretical results (Bravyi et al. 2020, Hastings 2019) suggest QAOA on unweighted 3-regular graphs doesn't outperform GW at low depth. Despite massive industrial interest (Google, IBM), QAOA's quantum advantage remains unproven and currently speculative for general instances. The repo honestly reflects this: advantage claim is tagged theoretical. [problems/05_qaoa_maxcut/README.md, lines 73–79]

06 · High-Frequency Trading
Scientific challenge: Discovering intraday trading signals from limit-order-book microstructure data within milliseconds; combining prediction accuracy, latency, and transaction cost management. [problems/06_high_frequency_trading/README.md, lines 1–11]

Quantum approach: Described as "Quantum VaR (amplitude encoding + oracle)" in the main README table, but the actual Q# file is a placeholder that does nothing. The Python baseline is a moving-average crossover strategy with Sharpe ratio, drawdown metrics. [problems/06_high_frequency_trading/README.md, lines 24–51]

Real-world impact: If quantum ML delivered faster/better signal discovery, it could shift competitive dynamics in quantitative finance.

Current repo status: Stage B, but essentially closer to Stage A — the Q# placeholder validates project wiring only. No quantum algorithm is implemented.

Classical vs. quantum today: HFT in practice is dominated by ultra-low-latency classical systems (FPGAs, co-location). Machine learning (especially transformer-based models and LSTMs) increasingly drives signal discovery. The latency argument is directly hostile to quantum computing: quantum hardware cannot execute circuits in microseconds with error correction. Quantum ML for HFT is considered highly speculative — even papers from Goldman Sachs acknowledge that quantum latency will never match classical for execution. This is arguably the weakest quantum use case in the repository.

07 · Drug Discovery
Scientific challenge: Identifying ligands with strong binding affinity and favorable pharmacokinetics from vast chemical design spaces. Accurate electronic structure for binding energy requires going beyond empirical force fields. [problems/07_drug_discovery/README.md, lines 1–5]

Quantum approach: VQE binding energy using a Pauli Hamiltonian encoding for small active-site models (H₂, LiH size). Plan: active-space UCCSD VQE → Phase Estimation for chemically accurate energies. [README.md, line 267]

Real-world impact: Compressing the drug discovery pipeline from ~15 years and $2.6B per drug; enabling designs impossible with classical methods.

Current repo status: Stage B. Classical baseline uses Lennard-Jones + Coulomb coarse-grained scoring — not quantum chemistry. Q# is placeholder only. [problems/07_drug_discovery/README.md, lines 36–46]

Classical vs. quantum today: AlphaFold3 (2024) has dramatically advanced protein structure prediction. Classical MD (GROMACS, Amber) and docking (AutoDock Vina, Glide) handle large-scale screening. For precise binding energies of highly correlated systems (heavy metals in active sites), quantum simulation is genuinely expected to outperform DFT. This is an active and promising area — companies like Quantinuum and Microsoft specifically target small molecule / active site problems. Advantage for full drug candidates remains 10–15 years away.

08 · Protein Folding
Scientific challenge: Predicting the 3D structure of a protein from its amino acid sequence — the "protein folding problem." Conformational search is exponentially large classically. [problems/08_protein_folding/README.md, lines 1–5]

Quantum approach: QAOA lattice folding with contact energy optimization; amplitude-encoded Boltzmann sampling. [README.md, line 268]

Real-world impact: Would enable designing novel enzymes, understanding disease mechanisms, and accelerating drug target identification.

Current repo status: Stage B. Classical baseline uses knowledge-based contact potentials on simplified lattice models. Q# is placeholder. [problems/08_protein_folding/README.md, lines 45–50]

Classical vs. quantum today: AlphaFold2 (2021) and AlphaFold3 (2024) have essentially solved structure prediction for most single-chain proteins, with atomic accuracy. This fundamentally changes the landscape. The original "protein folding problem" is largely solved classically. What remains open is understanding dynamics, intrinsically disordered proteins, and multi-component assemblies. Quantum computing's relevance here has shifted from structure prediction to possibly simulating quantum effects in enzyme catalysis (which connects back to problem 02). The framing in this repo may be somewhat outdated in light of AlphaFold3.

09 · Integer Factorization (Shor's Algorithm)
Scientific challenge: Breaking RSA encryption by factoring large semi-prime numbers. The best classical algorithm (GNFS) scales sub-exponentially; Shor's scales polynomially — an exponential advantage. [problems/09_factorization/README.md, lines 1–5]

Quantum approach: Shor's algorithm with QPE and modular exponentiation. The implementation is hardcoded for N=15 with explicit permutation unitaries for each base (a=2,4,7,8,11,13,14). This is standard for small demonstrations. [problems/09_factorization/qsharp/src/Main.qs, lines 31–57]

Real-world impact: Would break most current public-key cryptography, motivating migration to post-quantum schemes (CRYSTALS-Kyber, CRYSTALS-Dilithium) — already standardized by NIST in 2024.

Current repo status: Stage B. Pollard's rho classical baseline; Q# implements Shor's for N=15 only. The repo itself acknowledges: "While practical quantum hardware remains distant" [problems/09_factorization/README.md, line 5].

Classical vs. quantum today: Shor's algorithm is the most famous quantum algorithm. Its advantage is mathematically proven and exponential. However, cryptographically relevant factoring (RSA-2048 = 2048-bit numbers) requires roughly 20 million physical qubits with current error correction assumptions (Webber et al. 2022). The best public quantum hardware in 2026 has ~1,000–10,000 qubits with high error rates. NIST has already standardized PQC algorithms in anticipation. Shor's is proven to be advantageous but practically impractical for decades.

10 · Post-Quantum Cryptography (Security Analysis)
Scientific challenge: Estimating the security margin of NIST-standardized PQC schemes (Kyber, Dilithium, etc.) against both classical lattice attacks (BKZ) and quantum-enhanced attacks (Grover-accelerated sieving). [problems/10_post_quantum_cryptography/README.md, lines 1–5]

Quantum approach: Grover key search in Q# (80–92% success rate reported in README table); classical baseline estimates BKZ attack costs for NIST parameter sets. [README.md, line 270]

Real-world impact: Ensuring deployed PQC is actually secure and helping set safe parameter sizes.

Current repo status: Stage B. The classical baseline models NIST lattice parameters. Q# Grover search is implemented but for the general key search problem (not lattice-specific). No lattice-specific quantum attack primitives. [problems/10_post_quantum_cryptography/README.md, lines 38–45]

Classical vs. quantum today: NIST standardized CRYSTALS-Kyber, CRYSTALS-Dilithium, SPHINCS+, and FALCON in 2024. The security analysis of PQC against quantum attacks (especially Grover's quadratic speedup on symmetric components and quantum BKZ variants) is an active research area. This is actually a valuable and legitimate quantum computing use case — using quantum algorithms to analyze quantum-resistant cryptography. The field is active and well-defined, with groups at NIST, CWI, and elsewhere working on concrete security bounds.

11 · Quantum Machine Learning (Kernel Methods)
Scientific challenge: Whether quantum kernel methods — mapping classical data into high-dimensional Hilbert spaces — can provide better generalization than classical kernel methods for specific datasets. [problems/11_quantum_machine_learning/README.md, lines 1–5]

Quantum approach: Swap test kernel evaluation on a 5-qubit circuit; classical RBF baseline. [README.md, line 271]

Real-world impact: Better ML models for classification, potentially discovering data structures inaccessible to classical kernels.

Current repo status: Stage B. Classical RBF kernel baseline only; Q# placeholder. [problems/11_quantum_machine_learning/README.md, lines 40–50]

Classical vs. quantum today: QML is one of the most hyped but also most critically scrutinized quantum applications. Ewin Tang's dequantization results (2018+) showed that many quantum ML speedups have matching classical analogues when the input data is classically accessible (which it almost always is). Huang et al. (2021, Nature Communications) showed quantum kernels can theoretically have advantages on certain datasets, but finding real-world datasets where this holds is unsettled. The consensus in 2026 is that QML advantages are speculative and application-dependent, with no clear demonstrated advantage. The data-loading bottleneck (loading classical data into quantum states) consumes most theoretical speedup.

12 · Quantum Optimization (Combinatorial Scheduling)
Scientific challenge: Multi-machine job scheduling to minimize weighted tardiness — a core operations research problem. NP-hard in general. [problems/12_quantum_optimization/README.md, lines 1–5]

Quantum approach: QAOA scheduling with job-machine cost Hamiltonian and constraint-respecting mixers. Described as achieving "ratio 1.0 optimal" in the main README. [README.md, line 272]

Real-world impact: Better supply chain management, hospital scheduling, logistics.

Current repo status: Stage B. Greedy weighted tardiness classical baseline only; Q# placeholder. The "ratio 1.0 optimal" claim in the main README is aspirational for future QAOA implementation. [problems/12_quantum_optimization/README.md, lines 45–50]

Classical vs. quantum today: Commercial solvers (Gurobi, CPLEX, IBM CPLEX) routinely solve scheduling instances with thousands of jobs using branch-and-bound with cutting planes. The gap between QAOA and optimized classical solvers is currently enormous — QAOA requires many more shots and gives worse approximation ratios for real-world instances. Quantum optimization remains speculative for practical combinatorial problems. D-Wave's quantum annealers have been tested on scheduling but have not demonstrated reliable advantage over classical solvers at scale.

13 · Climate Modeling
Scientific challenge: Solving the large sparse linear systems arising from discretized PDEs (diffusion equations) in climate models, hoping to accelerate multi-scale climate projections. [problems/13_climate_modeling/README.md, lines 1–5]

Quantum approach: HHL-based diffusion solver with QPE + Trotter time evolution. [README.md, line 273]

Real-world impact: Faster, higher-resolution climate projections critical for policy planning.

Current repo status: Stage B. 1D energy balance diffusion model only; Q# placeholder. [problems/13_climate_modeling/README.md, lines 37–46]

Classical vs. quantum today: High-performance climate models (CESM, ECMWF IFS) run on petaflop-scale supercomputers and are continuously improving. ML-accelerated surrogates (GraphCast, FourCastNet) achieve remarkable forecast skill at low cost. The HHL approach faces the same fundamental critique as problem 04 — the input data-loading bottleneck, condition number assumptions, and quantum state output limitation all erode practical advantage. HHL for climate PDEs is widely considered impractical in the research community; classical sparse solvers (CG, multigrid) are already near-optimal for the well-conditioned diffusion operators in climate models.

14 · Materials Discovery (Battery Cathodes)
Scientific challenge: Identifying battery cathode materials with optimal voltage, stability, and capacity from exponentially large composition spaces. [problems/14_materials_discovery/README.md, lines 1–5]

Quantum approach: VQE band gap estimation using tight-binding Hamiltonian; plan for defect and conduction band evaluation. [README.md, line 274]

Real-world impact: Better batteries for electric vehicles and grid storage — a trillion-dollar market.

Current repo status: Stage B. Surrogate cluster expansion model only; Q# placeholder. [problems/14_materials_discovery/README.md, lines 37–46]

Classical vs. quantum today: The Materials Project database contains DFT-computed properties for ~150,000 materials. Machine learning potentials (CHGNet, MACE, M3GNet) accelerate screening by orders of magnitude. For strongly correlated oxides (NMC, LFP), DFT+U and dynamical mean-field theory (DMFT) partially address correlation effects. Quantum simulation (VQE) for small unit cells of correlated materials is genuinely promising — companies like Microsoft and Quantinuum target this. Advantage is expected before Shor-scale hardware but remains years away.

15 · Database Search (Grover's Algorithm) (Stage C)
Scientific challenge: Unstructured search: given N items in an unsorted database, find a marked item. Classical best: O(N) queries. Grover's: O(√N) queries — a provable quadratic speedup. [problems/15_database_search/README.md, lines 1–5]

Quantum approach: Canonical Grover with oracle + diffusion, for configurable N and marked-item counts. Validated in simulator. [problems/15_database_search/README.md, lines 40–47]

Real-world impact: Quadratic speedup for exhaustive search underlying cryptographic attacks, combinatorial search, and database queries.

Current repo status: Stage C. Full canonical Grover with simulator-validated success rates: 93% for 16-item single-target, 71% for 32-item multi-target, 100% for 4096-item benchmark. Advantage claim tagged projected. [problems/15_database_search/README.md, lines 40–47, 72–79]

Classical vs. quantum today: Grover's quadratic speedup is mathematically proven and is one of the most rigorously established quantum advantages. However, the practical value is limited: a quadratic speedup matters most for very large N, but loading the oracle efficiently is non-trivial, and the constant factors in quantum hardware may offset the speedup for realistic database sizes. For cryptographic key search (AES-256: N=2²⁵⁶), Grover's advantage is real but the required qubit counts remain beyond near-term hardware. The repo's implementation correctly demonstrates the algorithm concept on small N in simulation.

16 · Quantum Error Correction
Scientific challenge: Protecting logical qubits from decoherence by encoding them in larger physical qubit arrays. The threshold theorem guarantees fault-tolerant quantum computing is possible if the physical error rate is below a threshold. [problems/16_error_correction/README.md, lines 1–5]

Quantum approach: 3-qubit repetition code — the simplest QEC code, correcting 100% of single-qubit bit-flip errors. Plan: surface code stabilizers and minimum-weight matching decoders. [README.md, line 276]

Real-world impact: Without error correction, quantum computers cannot run the deep circuits needed for useful algorithms. QEC is the enabling technology for all other problems in this repository.

Current repo status: Stage B. Classical repetition-code logical error rate model; Q# placeholder for stabilizer simulation. [problems/16_error_correction/README.md, lines 37–46]

Classical vs. quantum today: Error correction is uniquely quantum — there is no classical analog to the problem. This is the most critical active R&D area in quantum computing. Google's 2024 Nature paper demonstrated surface code performance below the threshold for the first time (logical error rate decreasing as code distance increases). Microsoft's topological qubit approach aims for high intrinsic fidelity. The field is rapidly advancing and this is arguably the most important enabling technology for all other problems. The repo's treatment is modest (3-qubit code) compared to the frontier (surface codes at distance 7+).

17 · Nuclear Physics (Few-Nucleon Systems)
Scientific challenge: Computing binding energies of light nuclei (deuteron, helion, alpha particle) using effective field theory (EFT) Hamiltonians — a step toward ab initio nuclear structure calculations. [problems/17_nuclear_physics/README.md, lines 1–5]

Quantum approach: VQE for deuteron with pionless EFT Hamiltonian; plan for adiabatic state preparation and phase estimation. [README.md, line 277]

Real-world impact: Understanding nuclear binding and reactions — relevant to nuclear energy, isotope production, and fundamental physics.

Current repo status: Stage B. EFT exact diagonalization baseline; Q# placeholder. [problems/17_nuclear_physics/README.md, lines 35–46]

Classical vs. quantum today: For few-nucleon systems (A ≤ 4–6), classical methods (NCSM, no-core CI) are highly accurate. For medium nuclei (A ~ 10–40), coupled cluster and many-body perturbation theory work reasonably. For heavy nuclei and dense matter, quantum simulation is expected to be genuinely advantageous. The NuQS collaboration and InQubator for Quantum Simulation (IQuS) are active research programs specifically targeting nuclear physics on quantum hardware. This is a legitimate and active quantum computing research area, with small demonstrated experiments (deuteron VQE) published by Dumitrescu et al. (2018) on actual hardware.

18 · Photovoltaics (Solar Energy Efficiency)
Scientific challenge: Understanding exciton transport, quantum coherence effects, and light-harvesting dynamics in photovoltaic materials to exceed the Shockley-Queisser efficiency limit. [problems/18_photovoltaics/README.md, lines 1–5]

Quantum approach: Quantum walk for exciton transport dynamics on a donor-acceptor lattice. [README.md, line 278]

Real-world impact: More efficient solar cells — potentially breaking the ~33% single-junction theoretical limit by engineering quantum coherence.

Current repo status: Stage B. Shockley-Queisser baseline (classical thermodynamic model); Q# placeholder. [problems/18_photovoltaics/README.md, lines 37–46]

Classical vs. quantum today: There is genuine scientific interest in whether quantum coherence plays a functional role in energy transfer in biological light-harvesting complexes (Fleming et al., although the interpretation remains debated). Classical rate equations and TDDFT handle most PV design problems. Engineering controllable quantum coherence in silicon or perovskite solar cells is a materials problem more than a computation problem. Using quantum computers to simulate quantum coherence in light-harvesting is plausible in principle (the Hamiltonian is local and could be efficiently simulated), but this falls in the domain of speculative to promising — the commercial PV industry is not waiting for quantum computers.

19 · Quantum Chromodynamics (Lattice Gauge Theory)
Scientific challenge: Non-perturbative QCD — computing hadron masses, gluon dynamics, and confinement from first principles on a discretized spacetime lattice. One of the hardest problems in theoretical physics. [problems/19_quantum_chromodynamics/README.md, lines 1–5]

Quantum approach: Trotter-based lattice gauge simulation using Kogut-Susskind Hamiltonian with SU(2)/SU(3) gauge groups; Wilson plaquette energy estimation. [README.md, line 279]

Real-world impact: Fundamental physics — computing proton mass from quarks, understanding quark-gluon plasma (formed in heavy-ion collisions), and potentially informing particle physics beyond the Standard Model.

Current repo status: Stage B. Wilson plaquette energy estimator (classical Monte Carlo method); Q# placeholder. [problems/19_quantum_chromodynamics/README.md, lines 37–46]

Classical vs. quantum today: Lattice QCD on classical supercomputers (using Monte Carlo for Euclidean spacetime path integrals) has matured over 40 years and achieves sub-percent precision for many hadron masses. However, it faces the sign problem for finite baryon density (e.g., nuclear matter at high density) — the fundamental limitation that makes these computations exponentially expensive. Quantum simulation in Minkowski spacetime is one of the most compelling cases for quantum advantage because quantum computers naturally avoid the sign problem. Groups at Fermilab, CERN, and university labs actively pursue lattice gauge theory on quantum hardware. This is among the most scientifically justified targets in the repo.

20 · Space Mission Planning (Trajectory Optimization)
Scientific challenge: Designing optimal interplanetary trajectories with gravity assists, minimizing total delta-v (fuel expenditure) subject to launch window constraints. Combinatorially complex for multi-flyby missions. [problems/20_space_mission_planning/README.md, lines 1–5]

Quantum approach: QAOA trajectory optimization with penalty functions for constraints; quantum annealing for delta-v minimization. Described as finding "exact optimal" in the main README. [README.md, line 280]

Real-world impact: Cheaper and faster space missions — enabling more ambitious science payloads and longer exploration.

Current repo status: Stage B. Patched-conic delta-v estimator; Q# placeholder. The "exact optimal found" claim in the main README reflects the classical brute-force result, not a quantum result. [problems/20_space_mission_planning/README.md, lines 37–46]

Classical vs. quantum today: ESA's GMAT, JPL's MONTE, and commercial tools like STK already handle complex trajectory optimization using evolutionary algorithms, dynamic programming, and sequential quadratic programming. For large combinatorial trajectory search (e.g., multi-flyby satellite constellations), the problem can be framed as a QUBO/QAOA instance, but the practical case sizes where quantum would help remain unclear. This is considered speculative — the mission-planning community is not waiting for quantum hardware, and the advantage case is not as rigorous as, say, Shor's or Grover's.

Cross-Cutting Assessment
Quantum Advantage Landscape Across the 20 Problems
Category	Problems	Quantum Promise (2026 view)
Proven mathematical advantage	09 (Shor's), 15 (Grover's)	Advantage is real but requires hardware 10–20+ years away
Theoretically well-grounded, promising	01 (Hubbard), 02 (Catalysis), 03 (Risk/QAE), 14 (Materials), 17 (Nuclear), 19 (QCD)	Active research areas with credible paths to advantage
Active research but contested	05 (QAOA/MaxCut), 04 (HHL/Linear), 07 (Drug Discovery), 16 (QEC enabling tech)	Genuine debate; classical methods are strong
Speculative or debated	08 (Protein Folding — largely solved by AlphaFold), 10 (PQC analysis — legitimate but limited), 11 (QML), 12 (Optimization), 13 (Climate/HHL), 18 (PV)	Advantage unclear; classical approaches competitive
Highly speculative	06 (HFT), 20 (Space missions)	Quantum unlikely to be competitive for core use case
What the Repository Does Well
Honest framing: The maturity gate model is rigorous and self-aware. Claims are explicitly tagged as theoretical (17/20 problems) or projected (15_database_search). No problem currently claims demonstrated advantage. [docs/objective-gates.md]

Infrastructure completeness: The CI/CD pipeline, standardized JSON schema, Azure Quantum resource estimates, and deterministic test coverage (build=20/20, classical=20/20, test=20/20) are genuinely solid engineering.

Anchor problems: Problems 03 (QAE), 05 (QAOA), and 15 (Grover) are worked in real depth — actual quantum algorithms with calibrated outputs, noise sweeps, and Azure submissions.

Honest resource estimates: The resource estimates are sobering and honest: QAE needs 594k physical qubits for a financial risk estimate; HHL needs 18.7k for a 2×2 system. These numbers correctly communicate the gap between algorithmic promise and hardware reality.

What the Repository Overstates or Understates
17 of 20 problems are Stage B — the Q# implementations for most problems are either placeholders (a Program.qs with no real algorithm) or trivially small demonstrations (N=15 for Shor's). The main README table claiming "✅ Shor's algorithm (QPE + modular multiply, N=15)" is technically true but represents a demo-scale toy, not a research contribution. [README.md, line 269; problems/09_factorization/qsharp/src/Main.qs, lines 31–57]

Protein folding (08): The framing predates AlphaFold3's impact. The primary classical challenge the repo frames (ab initio structure prediction) is essentially solved for most proteins.

HFL/HFT latency: Quantum computing cannot physically execute in the millisecond timescales required for HFT. This use case requires fundamental reconsideration.

The "all 20 have real quantum implementations" claim in the milestone notes [README.md, line 20] must be read carefully — "real implementation" ranges from a 2-site Hubbard VQE to a full IQAE with calibrated statistics. The implementations are real Q# code that compiles and runs, but their depth and realism vary enormously across the 20 problems.

Summary for a Non-Specialist
What is this repository? A well-engineered research scaffold that asks: "If we had a fault-tolerant quantum computer, which of humanity's hardest problems could it help solve, and how far are we from that?"

What does it deliver? For each of 20 hard problems, it provides: the best classical baseline algorithm running today, the best-known quantum algorithm written in Q#, an honest estimate of how many qubits that quantum algorithm would need, and a clear maturity label for where the work actually stands.

What's the bottom line? In 2026, quantum computers cannot outperform classical computers on any of these 20 problems. The three most advanced implementations (financial risk estimation, MaxCut optimization, database search) are validated on simulators and have passed syntax checks on real Azure Quantum hardware, but the resources required for genuine advantage are 10–1,000× beyond today's best hardware. For roughly six of the 20 problems (Hubbard model, catalysis, QAE, quantum chromodynamics, nuclear physics, materials discovery), the scientific case for eventual quantum advantage is credible and well-grounded in peer-reviewed theory. For a few others (HFT, protein folding post-AlphaFold, general scheduling), the quantum case is weak or partially obsolete. The repository is most valuable as a structured research roadmap — it makes the journey from classical to quantum computing rigorous, honest, and reproducible.