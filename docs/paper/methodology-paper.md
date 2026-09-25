# A Software Engineering Framework for Reproducible Quantum Algorithm Development: Maturity Gates, Automated Validation, and Honest Limitations Across 20 Problem Domains

*This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). You are free to share and adapt for non-commercial purposes with attribution.*

> **Erratum, 2026-08-24, revised 2026-08-27 and 2026-09-25.** Section 4.1 of this
> repository copy reports the current toolchain pin, qsharp 1.31.0. The archived v2.0.0
> record (DOI 10.5281/zenodo.19660251, released 2026-04-20) reports 1.27, which was
> accurate at that date; the repository pin moved to 1.31.0 on 2026-08-03 (#151) and the
> paper text was not updated at the time. The current archive, v3.1.0
> (DOI 10.5281/zenodo.22126595), reports 1.31.0. The Azure Quantum runs in Section 6
> were made in April 2026 and therefore used qsharp 1.27, as Section 6.1 now states.

> **Erratum, 2026-08-28.** Sections 7.1 and 9 and the conclusion of the archived v1.0.1
> and v2.0.0 records state that all 20 problems had reached Stage C and that four had <!-- historical -->
> reached Stage D. That was not accurate at either date: when v2.0.0 was archived on
> 2026-04-20, `docs/objective-kpis.json` recorded 3 problems at Stage C, 17 at Stage B <!-- historical -->
> and none at Stage D. The first Stage D promotion landed on 2026-05-06 (#89), after both
> archives. This repository copy now states the figures that file records - 9 at Stage C,
> 8 at Stage B, 3 at Stage D - and `tooling/test_doc_claims.py` fails the build when the
> two disagree. A paper arguing that maturity gates prevent premature claims should not
> have overstated its own.

> **Revision, 2026-09-25.** Every number, citation and description in this copy was
> checked against the repository's committed data and code. The following did not hold
> and are corrected in the text: the cross-platform agreement in Section 7.2 (the
> committed histograms give the same unique most frequent outcome for 14 of 19 problems,
> not 17); the reading of the noise table in Section 7.3.1 (its columns are single-qubit
> error rates, with two-qubit rates ten times higher, and its first noisy column now
> matches the committed model output); the AES-128 Grover cost in Section 7.3 (about
> 10^19 is the iteration count, not the gate count); Section 7.4, which now states that
> the Goemans-Williamson column is a computed bound and that GW was not run; the
> utility-scale classification in Section 8, which contradicted both the framework it
> cites and the project's own screening; the description of CI enforcement in Sections
> 1.1 and 5 (the checks fail the build but do not block merges, and verify a declared
> stage and two README sections, not the evidence each stage requires; the
> documentation-claim guards were not run by CI at all until a step was added in this
> revision); the toolchain, kernels and four qubit counts
> behind the Section 6.1 syntax checks; the kernel behind the largest resource estimate and the stale range in
> Lesson 3 of Section 7.5; the stages in Appendix A; and several related-work
> descriptions and citations. Section 8 adds a limitation found during this check, that
> stage labels rested on evidence nothing verified, and following it up found defects in
> the kernels themselves. The five QPE kernels applied only diagonal rotations, so they
> returned the diagonal energy of their input basis state rather than a ground-state
> energy, and the quantum-walk kernel's position never depended on its coin. Those six
> kernels were rewritten and tested against exact simulation (Section 4.2), the resource
> estimates of the QPE problems now target the QPE routines (Section 4.4), every
> calibration ensemble was regenerated, and CI now fails when the ensemble behind a
> Stage C or D label does not match the sources it claims to describe (Section 5.2).

## Authors

Werner Rall

## Abstract

We present a software engineering framework for organizing quantum algorithm development across multiple problem domains. The framework provides standardized project structure, automated CI/CD validation, and a four-stage maturity gate model designed to prevent premature quantum advantage claims. We apply the framework to 20 problem domains using Microsoft Q#, implementing ten algorithm families at toy scale (2-14 qubits) where classical simulation is trivial. **We do not claim quantum advantage for any problem.** All implementations use small, highly structured instances specifically chosen for correctness validation, not for demonstrating quantum utility. Simulator and emulator results confirm algorithmic correctness at small scale but reveal nothing about practical scalability. The primary contribution is the methodology itself  particularly the maturity gate model that forces honest assessment of what has and has not been demonstrated  not the individual quantum implementations. Screening the same 20 problems against utility-scale filters archived eleven of them, including all three that had completed the Stage D evidence package, which shows that documenting a claim fully and the claim being favorable are independent. We include a scaling analysis for Grover search showing the expected O(√N) query complexity alongside the corresponding growth in gate count and the effect of gate noise under an explicit analytic model. The framework and all implementations are open-source (DOI: 10.5281/zenodo.19222020).

**Keywords:** quantum software engineering, development methodology, maturity gates, reproducibility, Q#, CI/CD

## 1. Introduction

The quantum computing community faces a credibility challenge. Claims of quantum advantage have repeatedly been weakened or overturned: sampling and utility-scale experiments have been reproduced by improved classical simulation [8, 9], a claimed exponential speedup for recommendation systems was matched by a quantum-inspired classical algorithm [10], and accounting for the constant-factor cost of quantum error correction erodes quadratic speedups [6]. A contributing factor is the absence of standardized development practices that enforce honest assessment at each stage of quantum algorithm development.

This paper addresses not the algorithms themselves  which are well-established in the literature  but the **software engineering process** of developing, validating, and honestly assessing quantum implementations. We propose a framework that applies the same rigor to quantum development that software engineering applies to classical systems: standardized structure, automated testing, evidence-based quality gates, and reproducible benchmarks.

**Scope and limitations.** Our 20 implementations are toy-scale (2-14 qubits) where classical simulation is trivial. We use standard textbook algorithms applied to small structured instances. We do not advance quantum algorithm theory, discover new speedups, or demonstrate quantum utility. The contribution is purely methodological: a framework designed to prevent the common failure mode of claiming more than the evidence supports.

### 1.1 Contributions

1. **Maturity Gate Model**: A four-stage procedural framework (A→D) with explicit evidence requirements at each stage, designed to prevent premature quantum advantage claims. This is a process contribution, not a complexity-theoretic one.
2. **Standardized Problem Structure**: A reproducible template ensuring every problem includes classical baselines, parameterized instances, quantum implementations, and honest limitations documentation.
3. **Automated Policy Checks**: CI jobs that fail when a problem's declared maturity stage falls below its policy minimum or required README sections are missing. Section 5 states what these checks do and do not verify.
4. **Scaling Analysis**: For one representative problem (Grover search), we show how gate count and noise sensitivity grow with problem size under an explicit analytic model, illustrating the gap between toy validation instances and practically relevant scales.
5. **Lessons Learned**: Practical insights from building 20 quantum implementations, including how compiled-but-incorrect code, encoding bugs, mock estimates and presence-only checks can create false confidence.

## 2. Related Work

Prior benchmarking efforts include the QED-C application-oriented benchmark suite [1], which measures how faithfully hardware executes many well-known algorithms as circuit width and depth grow, and the QUARK framework [2], which defines application-level benchmarks, initially for industrial optimization problems. Software development kits such as Qiskit [3] provide the circuit construction and compilation layer that such benchmarks exercise. Our work differs in emphasis rather than breadth: instead of measuring hardware or software performance, it defines process gates that govern what may be claimed about an implementation, and it emphasizes reproducibility infrastructure. The utility-scale screening in Section 8 operationalizes the argument of Hoefler, Häner and Troyer [11] that quadratic speedups and data-intensive problems are unlikely to yield practical advantage.

## 3. Framework Design

### 3.1 Problem Structure

Each of the 20 problems follows an identical directory layout; the eleven archived problems (Section 8) keep the same layout under `problems/archived/`:

```
problems/XX_name/
├── qsharp/          # Q# quantum implementation (src/Main.qs, HardwareKernel.qs)
├── circuits/        # Resource estimate (estimate.json) and circuit diagrams
├── python/          # Classical baseline and analysis
├── instances/       # Parameterized YAML configurations (small/medium/large)
├── estimates/       # Resource estimation artifacts
├── plots/           # Generated visualizations
├── Makefile         # Reproducible build commands
└── README.md        # Documentation with advantage claim contract
```

This uniformity enables automated tooling to operate across all 20 problems without problem-specific logic.

### 3.2 Maturity Gate Model

We define four progressive stages, each with explicit evidence requirements:

**Stage A (Classical Baseline Validated):**
- Deterministic classical baseline implementation
- Instance coverage (small, medium at minimum)
- Reproducible command path documented
- Metrics persisted in standardized JSON schema

**Stage B (Quantum Implementation Ready):**
- Q# quantum algorithm implemented with real gate operations
- Build and run validation passing in CI
- Resource estimation path documented
- Algorithm assumptions and known limits stated

**Stage C (Hardware-Aware Validation):**
- Multi-run calibration with uncertainty bounds
- Quantum/classical comparison with confidence intervals
- Hardware mapping and transpilation assumptions documented
- DiVincenzo readiness criteria assessed

**Stage D (Advantage Evidence Package):**
- Advantage claim template completed with explicit category (theoretical/projected/demonstrated)
- Fair classical comparator identified and justified
- Residual risks and assumption sensitivities documented
- Reproducible end-to-end evidence chain

Stage D certifies that a claim is completely documented, whatever its category; a Stage D problem may, and in this project does, carry a claim that no practical advantage has been shown.

**How stages are recorded.** Each problem's README declares its current stage on a "Current gate" line. The policy check (Section 5.2) verifies that the declared stage meets a per-problem minimum and that every README contains the advantage-contract and DiVincenzo-readiness sections; for one problem (05) it also requires the estimator-summary and backend-assumption files. It does not inspect the calibration ensembles or evidence packages that Stages C and D require, and it does not re-derive the stage from the evidence, so a declaration is accepted whether or not that evidence exists or describes the current kernel. Section 8 (limitation 8) describes where this mattered.

### 3.3 Advantage Claim Contract

Each problem includes a structured advantage claim with fields for: claim category, problem class and regime, baseline algorithm and fairness rationale, quantum resource scaling claim, data-loading and I/O assumptions, noise/error model assumptions, confidence/uncertainty method, and residual risks. This prevents implicit or unsupported advantage claims.

### 3.4 DiVincenzo Readiness Overlay

For Stage C/D problems, we assess the five DiVincenzo criteria for quantum computation [12]: scalable qubit system, initialization capability, coherence relative to gate times, universal gate set, and qubit-specific measurement. The criteria describe a physical platform rather than an algorithm, so the assessment records how well the hardware assumed by each problem's resource estimate meets them. Each criterion is tagged as met, partial, not-yet, or not-applicable with evidence notes.

## 4. Implementation

### 4.1 Toolchain

- **Quantum:** Microsoft Q# with modern QDK (currently pinned to qsharp 1.31.0, Python-hosted, no .NET dependency; the April 2026 Azure runs in Section 6 used qsharp 1.27)
- **Classical:** Python 3.11 with NumPy, SciPy, Matplotlib
- **Cloud:** Azure Quantum with Quantinuum and Rigetti providers
- **CI/CD:** Seven GitHub Actions workflows, three of which run on pull requests (Section 5.1)
- **Website:** Statically generated Next.js dashboard

### 4.2 Algorithm Families

Table 1 summarizes the ten algorithm families implemented across the 20 problems. Qubit counts cover the hardware kernels, the demonstration instances in each `Main.qs`, and the instances passed to the resource estimator.

| Algorithm Family | Problems | Qubits | Key Operations |
|---|---|---|---|
| VQE, then QPE* | 01, 02, 07, 14, 17 | 2-14 | Ry, CNOT, Rz, Pauli measurement (VQE); Trotterized Pauli exponentials, phase estimation (QPE) |
| QAOA | 05, 08, 12, 20 | 2-4 | H, ZZ cost (CNOT+Rz), Rx mixer |
| Grover | 10, 15 | 3-12 | Oracle marking, diffusion operator |
| HHL/QPE | 04, 13 | 5-6 | QPE, QFT, eigenvalue inversion |
| Amplitude estimation | 03, 06 | 3-14 | State prep, oracle, Grover^k; canonical QAE adds a QPE precision register, IQAE does not |
| Shor | 09 | 8 | QPE, controlled modular multiply |
| Swap Test | 11 | 5 | Controlled-SWAP, Hadamard test |
| QEC | 16 | 5 | Syndrome extraction, correction |
| Quantum Walk | 18 | 3 | Coin rotation, conditional shift |
| Trotter | 19 | 2-4 | ZZ plaquettes, transverse field |

\* The VQE routines (2-3 qubits) remain in each `Main.qs`. On 2026-04-18 (#66) the hardware kernels of these five problems were replaced by quantum phase estimation (QPE) kernels, but every controlled evolution in them was built from Rz and CNOT-conjugated Rz gates, a diagonal unitary: from a computational basis state the phase register returned that state's diagonal energy, never the ground-state energy. On 2026-09-25 they were rewritten as Trotterized QPE on a 4-qubit Jordan-Wigner two-site Hubbard model (01), the parity-reduced 2-qubit STO-3G H₂ Hamiltonian (02), the 2-qubit deuteron model of Dumitrescu et al. [20] (17), and 2-qubit models labelled as toys (07, 14), and `tooling/test_qpe_kernels.py` now compares each against exact diagonalization of the same Hamiltonian. The hardware kernels use 2 phase bits (4-6 qubits) and the resource estimates 10 (12-14 qubits). The emulator histograms and the noise study in Section 7.2 were produced by the VQE kernels and predate both changes; the calibration ensembles and resource estimates were regenerated from the rewritten QPE routines. The same revision found that the quantum-walk kernel (18) swapped its position qubits whichever way the coin pointed, and rewrote its shift as a coin-controlled step (`tooling/test_exciton_walk.py`).

### 4.3 Classical Baselines

Every problem includes a deterministic classical baseline that serves as the comparison target. Baseline algorithms are chosen to be the standard classical approach for each domain (e.g., exact diagonalization for Hubbard, Monte Carlo for risk analysis, brute-force for MaxCut at small scale). All baselines produce JSON output conforming to a shared schema.

### 4.4 Resource Estimation Pipeline

We employ a centralized estimation manager (`tooling/generate_estimates.py`) that runs the Quantum Resource Estimator v3 (`qdk.qre`) [19] on each problem's estimation entry point. All 20 problems have real profiles targeting a gate-based superconducting architecture (50 ns gates, 10⁻³ error rate) with a surface code, round-based magic-state factories and a total error budget of 10⁻³. QRE v3 returns a Pareto frontier trading physical qubits against runtime; we report the point with the fewest physical qubits, which is also the slowest. The estimated programs are the toy instances themselves, compiled for fault-tolerant execution, not utility-scale versions of the problems; for the five QPE problems of Table 1 they are the QPE routines with a 10-bit phase register. Physical qubit counts range from 1,746 (3-qubit QEC repetition code) to 754,715 (QPE on the materials-discovery model). The pipeline also supports batch calibration via `tooling/generate_calibration_ensemble.py`, which runs each kernel 20 times to produce ensemble statistics with 95% confidence intervals (for the QPE problems each run is the most frequent of 8 estimates at 8 phase bits). All 20 committed ensembles now carry valid statistics and record hashes of the Q# sources they ran; before this revision 10 of the 20 did (Section 8, limitation 8).

The QRE v3 migration superseded an earlier range of 1,764 to 401,400 produced by the now-deprecated `qsharp.estimate` API. For the programs estimated at the time, under matched assumptions, QRE v3 reported 1.0× to 3.9× fewer physical qubits at 1.5× to 2× the runtime, consistent with selecting the low-qubit corner of the frontier rather than any change in the underlying circuits.

Current target architectures:
- `qubit_gate_ns_e3`: Gate-based model, 50 ns gate time, 10⁻³ error rate
- `qubit_gate_ns_e4`: Gate-based model, 50 ns gate time, 10⁻⁴ error rate
- `qubit_gate_us_e3`: Gate-based model, 100 μs gate time, 10⁻³ error rate
- `qubit_gate_us_e4`: Gate-based model, 100 μs gate time, 10⁻⁴ error rate

The ns profiles are typical of superconducting qubits and the μs profiles of trapped ions, but the four profiles differ only in gate time, measurement time and physical error rate (`tooling/estimator_config.py`).

Majorana profiles and the floquet code were retired at the QRE v3 migration: QRE v3 ships no floquet code, and the Majorana architecture yielded an empty Pareto frontier for every code and factory combination tested.

## 5. Automated Validation

### 5.1 CI Pipeline

Three workflows run on pull requests; the dependency-graph check runs only when code, workflow or build files change:

1. **CI/CD**: its build-and-test job validates workflow syntax, compiles and runs all 20 Q# projects, runs the classical baseline tests and the evaluator test suite, validates JSON schemas, enforces the maturity policy (Section 5.2), and runs the tests under `tooling/` and `viz/`, which include the documentation-claim, evidence-provenance and kernel-correctness checks. That last step was added on 2026-09-25; until then CI did not run those guards, so the stage-count check cited in the errata above failed only when someone ran it locally
2. **Dependency Graph Drift Check**: fails when the committed dependency and reachability map is stale
3. **Azure Secret Hygiene**: prevents accidental credential commits

Four further workflows deploy the website and the evaluator API, run a nightly resource-estimation sweep, KPI refresh and runnable-correctness audit, and schedule an uptime probe of the deployed API (its cron asks for every 30 minutes; GitHub's throttling of scheduled workflows has produced roughly one run every four hours). Earlier versions of this paper listed seven pull-request checks, including dedicated Stage D readiness, runnable-correctness and reporting-integrity gates; these were consolidated or removed between April and June 2026 (#67, #124), and the correctness audit now runs nightly rather than per pull request. None of the checks is configured as a required status check on the main branch, so a failing check reports a problem but does not block a merge.

### 5.2 KPI Dashboard

An automated reporting script (`stage_kpis.py`) scans all 20 problem directories and produces a maturity status report with four flags per problem: advantage contract present, estimator profile summary generated, backend assumptions documented, and DiVincenzo readiness assessed. The build-and-test job fails when a declared stage is below its per-problem minimum, when a README lacks the advantage-contract or DiVincenzo-readiness section, or, for 05 only, when the estimator-summary or backend-assumption file is missing. These are presence checks (a heading in the README, or an artifact file with non-placeholder content): they establish that some evidence was filed, not that it is current, correct, or the evidence the declared stage requires. Two checks added on 2026-09-25 go further. At Stage C and above the calibration ensemble must have at least 20 runs and complete statistics, and the hashes it records of the Q# sources it ran must match the current sources, so rewriting a kernel invalidates its ensemble. At Stage D the claim category in the README must match the machine-readable contract.

Current coverage: 20/20 problems have advantage contracts, estimator summaries, backend assumptions and DiVincenzo readiness sections.

## 6. Azure Quantum Integration

### 6.1 Circuit Validation

On 12-13 April 2026, the hardware kernels of all 20 problems were compiled from Q# to QIR with the modern QDK (qsharp 1.27, the version pinned at the time) and accepted by the Quantinuum H2-1SC syntax checker via Azure Quantum. A syntax checker verifies that a program is well formed for the target; it does not simulate it. Table 2 lists the kernels as recorded then, with approximate gate counts: 20 kernels from 19 problems (two for 01). The 04_linear_solvers kernel also passed and is not listed. The VQE kernels in the table (six rows covering five problems) were replaced by QPE kernels five days later (Section 4.2); those replacements were submitted to the H2-1E emulator on 10 June 2026, but their results were never retrieved into the committed run history, and they were themselves rewritten on 2026-09-25 because their evolution was diagonal. The quantum-walk kernel listed here is also the version before its 2026-09-25 correction. Neither rewritten set has been submitted to Azure Quantum.

| Circuit | Algorithm | Qubits | Gates | Status |
|---|---|---|---|---|
| Hubbard VQE (ZZ basis) | VQE | 2 | ~8 | Succeeded |
| Hubbard VQE (XX basis) | VQE | 2 | ~10 | Succeeded |
| MaxCut QAOA depth-1 | QAOA | 3 | ~12 | Succeeded |
| Database Grover 4-qubit | Grover | 4 | ~200 | Succeeded |
| Key Search Grover | Grover | 3 | ~150 | Succeeded |
| Scheduling QAOA | QAOA | 4 | ~24 | Succeeded |
| QEC Repetition Code | QEC | 5 | ~10 | Succeeded |
| Shor N=15 (a=7) | Shor | 8 | ~50 | Succeeded |
| HHL Diffusion PDE | HHL | 5 | ~30 | Succeeded |
| QAE Simplified | QAE | 5 | ~20 | Succeeded |
| Quantum VaR | QAE | 3 | ~10 | Succeeded |
| QAOA Protein Folding | QAOA | 3 | ~30 | Succeeded |
| VQE Catalysis | VQE | 2 | ~6 | Succeeded |
| VQE Drug Binding | VQE | 2 | ~8 | Succeeded |
| Swap Test Kernel | Swap | 5 | ~10 | Succeeded |
| VQE Band Gap | VQE | 2 | ~6 | Succeeded |
| VQE Deuteron | VQE | 2 | ~8 | Succeeded |
| Quantum Walk Exciton | Walk | 3 | ~8 | Succeeded |
| Trotter Gauge | Trotter | 4 | ~40 | Succeeded |
| QAOA Trajectory | QAOA | 3 | ~30 | Succeeded |

### 6.2 Shared Azure Workflow

A problem-agnostic Azure submission pipeline (`tooling/azure/smoke_problem.py`) enables any problem to submit circuits to Azure Quantum through a single interface, with env-gated authentication, manifest tracking, and audit reporting.

## 7. Results and Discussion

### 7.1 What the Framework Demonstrates (and What It Does Not)

Of the 20 problems, 9 have reached Stage C (declared on the basis of calibration ensembles and real Azure Quantum Resource Estimator profiles; limitation 8 in Section 8 records what that evidence does and does not establish), 8 remain at Stage B, and **3 have reached Stage D** (advantage evidence packages with explicit claim contracts). The 3 Stage D problems (QAE risk analysis, QAOA MaxCut, Grover database search) filed claim contracts in the categories "theoretical" (QAOA MaxCut and QAE risk analysis) and "projected" (Grover database search); until this revision the QAE README gave "projected", and CI now fails when a README and its contract disagree. None claims a demonstrated advantage. The QAOA MaxCut contract states that there is "no proven quantum advantage for MaxCut QAOA at any constant depth" and identifies the Goemans-Williamson 0.878-approximation [7] as the polynomial-time classical competitor. The Grover contract rests on the provably optimal O(√N) query speedup and lists oracle synthesis overhead as its main residual risk. It does not establish a problem size at which the speedup becomes practical, and for unstructured data the cost of loading the database into an oracle or QRAM is itself O(N).

Maturity and merit are independent. When the utility-scale filters of Section 8 were applied to all 20 problems in April 2026 (five filters then; the sixth, F6, was added in August 2026), eleven were archived. They include all three Stage D problems: QAE risk analysis for a quadratic speedup offset by data-loading cost, QAOA MaxCut for having no proven speedup, and Grover database search for a quadratic speedup offset by QRAM cost. The nine active problems are all at Stage C. A complete evidence package documents a claim; it does not make the claim favorable.

**What our results demonstrate:**
- Algorithmic correctness at small scale (Grover finds marked items, Shor factors 15 with a circuit compiled for that modulus, QEC corrects single bit-flips, and the QPE kernels and the quantum walk sample the distributions that exact simulation of the same circuits predicts)
- The framework's ability to organize and validate quantum development across multiple problem domains
- Practical lessons about failure modes in quantum software development

**What our results do NOT demonstrate:**
- Quantum advantage over classical methods for any problem
- Noise resilience or hardware viability
- Scalability to practically relevant problem sizes
- Superiority over state-of-the-art classical algorithms

### 7.2 Simulator and Emulator Results Are Sanity Checks, Not Experiments

No problem was run on quantum hardware. Validation used noiseless local simulation, the Quantinuum H2-1SC syntax checker, the Quantinuum H2-1E emulator (which applies a noise model of the H2 hardware) and the Rigetti QVM simulator. Zero-variance results (e.g., 100% QEC correction rate, exact QAOA optimality) confirm correct circuit construction but reveal nothing about performance under realistic noise, which limits the size of circuit that near-term devices can execute reliably [5]. A circuit that achieves perfect results on a simulator may fail completely on hardware with 10⁻³ two-qubit gate error rates once it is deep enough.

The H2-1SC syntax checker validates that circuits are well-formed QIR but does not simulate quantum behavior. In April 2026, H2-1E emulator results were collected for all 20 problems (100 shots each), and 19 were also run on the Rigetti QVM. For 14 of those 19, the most frequent outcome is the same unique outcome on both platforms; for two more (05, 08) the QVM histogram has a tie that includes the H2-1E mode; for three (03, 12, 20) the modes differ. The total variation distance between the paired 100-shot histograms ranges from 0.00 to 0.44 (median 0.06). With 100 shots, sampling error alone is up to ±0.05 in each outcome probability (one standard deviation), so these comparisons show that both platforms compiled and executed the same programs; they are not evidence about hardware behavior. They ran the kernels of April 2026: for 01, 02, 07, 14 and 17 the VQE kernels, and for 18 a walk whose position never moved (Section 4.2).

A separate local simulation with the QDK's depolarizing noise model at strengths p = 0.001, 0.01 and 0.05 (100 shots each, April 2026) measured the classical fidelity between each kernel's noisy and ideal output histograms. At p = 0.05 the 2-qubit VQE kernels retained 0.83-0.96, while three kernels fell below 0.40 (Grover database search with three iterations 0.15, quantum walk 0.30 for the kernel before its correction, 8-qubit Shor 0.38). These estimates are shot-noise limited: several rise between p = 0.001 and p = 0.01, which added noise cannot cause. A September 2026 run of the Grover database-search kernel (four qubits, three iterations) on H2-1E returned the marked item in 80 of 100 shots, against an ideal 96.1% and about 6 in 100 for random guessing (`problems/archived/15_database_search/azure_runs/`).

Selected correctness validation results:
- **Grover (10_pqc)**: 80-94% success in noiseless simulation of the 3-, 4- and 5-qubit instances, consistent with the ideal 78%, 91% and 90% for the iteration counts the implementation uses (1, 2 and 3, one fewer than the optimal counts used in Section 7.3)
- **Shor (09_factorization)**: Correctly factors 15 = 3 × 5. The controlled modular multipliers are fixed permutations compiled for N = 15, so the circuit demonstrates the structure of period finding, not scalable modular arithmetic; compiled demonstrations of this kind say little about factoring in general [16]. It is a textbook demonstration, not a research contribution
- **QEC (16_error_correction)**: 512/512 = 100% correction on simulator (meaningless without noise  the entire point of QEC is noise resilience)

### 7.3 Scaling Analysis: Grover Search (Computed)

To illustrate the gap between toy validation and practical utility, we computed Grover search resource requirements at increasing qubit counts with an analytic gate-count model (`tooling/run_paper_analyses.py`). Each iteration applies two multi-controlled Z gates (oracle and diffusion), each counted as n-2 Toffoli gates, and each Toffoli is decomposed into 6 CX and 7 T gates [4]; n is the search-register size and the iteration count is the standard ⌊(π/4)√N⌋. The model omits ancilla qubits and their uncomputation (a textbook V-chain construction of an n-qubit multi-controlled Z uses 2n-5 Toffolis and n-3 ancillas), so its counts are order-of-magnitude illustrations, not compiled circuits.

| Qubits (n) | Keyspace (N) | Iterations | CX Gates | T Gates | Total Gates | Success (noiseless) |
|---|---|---|---|---|---|---|
| 3 | 8 | 2 | 24 | 28 | 84 | 94.5% |
| 4 | 16 | 3 | 72 | 84 | 222 | 96.1% |
| 5 | 32 | 4 | 144 | 168 | 424 | 99.9% |
| 6 | 64 | 6 | 288 | 336 | 828 | 99.7% |
| 8 | 256 | 12 | 864 | 1,008 | 2,424 | 100% |
| 10 | 1,024 | 25 | 2,400 | 2,800 | 6,650 | 100% |
| 12 | 4,096 | 50 | 6,000 | 7,000 | 16,500 | 100% |
| 16 | 65,536 | 201 | 33,768 | 39,396 | 92,058 | 100% |
| 20 | 1,048,576 | 804 | 173,664 | 202,608 | 471,144 | 100% |

The quadratic speedup (O(√N) queries) is real in query complexity, but total gate count grows as O(√N × n) where n is the number of qubits. For n=20 (N ≈ 10⁶), the model gives ~471K gates. For a 128-bit keyspace it gives about 1.4 × 10¹⁹ Grover iterations and 6 × 10²² gates with a trivial marking oracle; with a reversible AES-128 circuit as the oracle, published estimates reach about 2⁸⁶ ≈ 8 × 10²⁵ T gates on 2,953 logical qubits [13], far beyond any foreseeable hardware. **No amount of CI/CD rigor changes these scaling realities.**

### 7.3.1 Noise Impact on Grover Scaling

Using the same gate counts and a simple survival model, in which the circuit returns the noiseless output distribution if no counted gate fails and a uniformly random output otherwise, we computed the impact on Grover success probability. Each of the 6n-2 H and X gates per iteration fails with probability p₁ and each CX with p₂ = 10p₁; the T gates inside the Toffolis are not counted as failure points, which makes the model optimistic:

| Qubits | 2Q Gates | Noiseless | p₁=0.1%, p₂=1% | p₁=1%, p₂=10% | p₁=5%, p₂=50% |
|---|---|---|---|---|---|
| 3 | 24 | 94.5% | 74.9% | 17.2% | 12.5% |
| 4 | 72 | 96.1% | 47.1% | 6.3% | 6.2% |
| 5 | 144 | 99.9% | 23.5% | 3.1% | 3.1% |
| 6 | 288 | 99.7% | 6.0% | 1.6% | 1.6% |
| 8 | 864 | 100% | 0.4% | 0.4% | 0.4% |

At a two-qubit error rate of 1%, success at 4 qubits falls from 96% (noiseless) to 47%, at 6 qubits from 99.7% to 6.0% (random guessing: 1.6%), and at 8 qubits it is indistinguishable from random guessing. At a 10% two-qubit error rate it is at the random-guess level from 4 qubits; the last column, a 50% two-qubit error rate, is outside any realistic regime and shows only saturation. Real devices also suffer coherent and correlated errors that this model ignores. This demonstrates that noiseless simulator results (Section 7.2) reveal nothing about practical viability. Error correction would be required for any non-trivial Grover instance, adding orders of magnitude in qubit overhead.

### 7.4 Classical Baseline Honesty: Goemans-Williamson vs QAOA

To illustrate why our classical baselines are insufficient for advantage claims, we set QAOA MaxCut against the Goemans-Williamson (GW) approximation guarantee [7] on three small weighted graphs:

| Graph | Nodes | Edges | Optimal Cut (brute force) | GW Guarantee (≥0.878×OPT) | Cuts Enumerated (2ⁿ) |
|---|---|---|---|---|---|
| Triangle | 3 | 3 | 2.2 | ≥1.93 | 8 |
| Square+diag | 4 | 5 | 4.0 | ≥3.51 | 16 |
| Pentagon+diags | 5 | 7 | 5.4 | ≥4.74 | 32 |

GW was not run: the guarantee column is 0.878 × OPT, computed from the brute-force optimum, and bounds the expected cut of GW's randomized rounding for non-negative weights. At these sizes (n ≤ 5) exhaustive enumeration evaluates at most 32 cuts, so it finds the optimum instantly and neither GW nor QAOA can be compared meaningfully against it. The GW guarantee, and any comparison with it, only matters at sizes where exact methods become impractical, far beyond these instances. For reference, depth-1 QAOA on 3-regular graphs is guaranteed an approximation ratio of only 0.6924 [14], below GW's 0.878. **Claiming QAOA advantage against brute-force at n=3 is meaningless**  this is precisely the kind of inflated claim that our maturity gate framework is designed to prevent.

### 7.5 Lessons Learned

1. **Compiled code ≠ correct quantum code**: Analytical Q# code that runs classical math with a token qubit allocation compiles, passes CI, and produces plausible output  but performs no quantum computation. Fifteen of our twenty implementations were initially such placeholders. Gate-count auditing is essential, and it is not enough: the five QPE kernels had the gates QPE needs but only diagonal ones, and the quantum-walk shift ignored its coin. Both ran and passed CI for months, and both failed at once when their sampled outputs were compared with exact simulation of the circuits they claimed to be.

2. **Encoding bugs persist through validation**: A Lorentzian PDF masquerading as a log-normal distribution in the QAE implementation survived multiple development cycles because the circuit compiled and produced numbers in a plausible range. Only systematic comparison against the classical baseline revealed the error.

3. **Mock estimates previously created false confidence**: Uniform mock resource estimates across all problems suggested comparable resource requirements. Real Quantum Resource Estimator profiles now reveal a range of about 430×: from 1,746 physical qubits (QEC repetition code) to 754,715 (QPE on the materials-discovery model). Explicit T-gate counts are small (QAE: 15, HHL: 12, Shor: 6), but that does not mean the other kernels avoid magic-state distillation. Every arbitrary-angle rotation must be synthesized from T states, so the rotation-only QAOA kernels devote 63-80% of their physical qubits to T factories, the rotation-dominated QPE estimates 90-94%, and the QAE kernel's cost is driven by its 3,713 rotations rather than its 15 T gates.

4. **Process discipline has value even without quantum advantage**: The standardized structure, automated checks, and maturity gates caught real bugs and prevented inflated claims  which is the framework's actual contribution.

5. **Presence checks let evidence go stale**: The policy check confirmed that a declared stage met its minimum and that two README sections existed; it never looked at the evidence Stage C requires. Five problems kept Stage C labels after their kernels were rewritten, and three held them without valid calibration statistics (Section 8, limitation 8), and nothing failed. Binding each ensemble to hashes of the sources it ran turned staleness into a failing check, and regenerating the ensembles exposed the walk defect: its zero spread had been read as a parsing problem.

## 8. Limitations (Critical)

These limitations are fundamental to interpreting this work, not merely areas for improvement:

1. **No quantum advantage is claimed or demonstrated.** All problems are solved trivially by classical computers. The quantum implementations exist to validate the framework methodology, not to demonstrate quantum utility.

2. **No result comes from quantum hardware.** Results come from noiseless simulation, the H2-1E noise-model emulator, the Rigetti QVM and a syntax checker. Zero-variance results (100% QEC correction, exact QAOA optimality) are artifacts of simulation, not evidence of hardware viability. Real quantum hardware with 10⁻³ to 10⁻² error rates would degrade results increasingly with circuit depth; the H2-1E noise model alone reduces the 4-qubit Grover kernel from an ideal 96% success to 80 of 100 shots (Section 7.2).

3. **Classical baselines are deliberately weak.** We use textbook algorithms (brute-force, naive Monte Carlo) for cross-domain standardization. Any comparative statement must acknowledge that state-of-the-art classical methods would perform far better. Quantum advantage claims have repeatedly weakened or vanished when stronger classical methods were applied [8, 9, 10].

4. **Resource estimates use the Quantum Resource Estimator v3.** All 20 problems have been profiled via `qdk.qre` against a gate-based superconducting architecture with a surface code, reporting the fewest-qubit point of the returned Pareto frontier. Physical qubit counts range from 1,746 (QEC) to 754,715 (QPE on the materials-discovery model). These are estimates under stated assumptions (a 10⁻³ error budget, a surface code and round-based factories), not lower or upper bounds: better compilation, codes or factories could reduce them. They describe the toy instances themselves and should not be extrapolated to production problem sizes without careful scaling analysis. Multi-model estimation across 4 hardware configurations (ns and μs gate times, each at 10⁻³ and 10⁻⁴ error rates) shows physical qubit requirements varying by up to 44× for the same problem (26,092 versus 589 for Grover key search). All of that variation comes from the physical error rate: at a fixed error rate the ns and μs profiles give identical qubit counts and differ only in runtime, which is about 1,700× longer at 100 μs. Resource estimates are meaningless without the target error rate and gate time.

5. **Utility-scale screening.** Following Hoefler, Häner and Troyer [11] and Troyer's lecture series on utility-scale quantum computing [15], the project's evaluator applies six filters: a proven speedup (F1), a speedup that survives data input and output (F2), a speedup that survives error-correction overhead (F3), a naturally quantum problem (F4), a feasible crossover problem size (F5) and, for electronic structure, a preparable guiding state (F6) [17]. Eleven of the 20 problems fail at least one filter and are archived (the archival was made in April 2026 with the first five filters; F6 was added in August 2026): four with quadratic speedups (QAE ×2, Grover ×2), three whose speedup depends on loading classical data (HHL ×2, the swap-test classifier), and four QAOA problems with no proven speedup. The nine that remain are quantum simulation problems (the five QPE problems of Table 1, a quantum walk and a Trotter simulation), Shor factoring, and the QEC repetition code, which is retained as infrastructure rather than as an application. The filters were applied to each problem class, not to its toy instance, and for the quantum walk the difference matters: the kernel follows a single exciton, whose exact classical simulation already takes time polynomial in the number of sites, so its pass rests on many-body or strongly coupled open-system transport that the instance does not model. Passing the filters is a screen, not evidence of advantage: even for ground-state quantum chemistry, a generic exponential quantum advantage has not been established [18], in part because preparing a state with sufficient overlap with the ground state may itself be hard, which is the condition F6 tests.

6. **Toy instances reveal nothing about asymptotic behavior.** A 2-qubit VQE or 4-qubit QAOA demonstrates circuit correctness but says nothing about how the algorithm behaves at 50, 100, or 1000 qubits. The scaling analysis in Section 7.3 illustrates how rapidly resource requirements grow.

7. **The maturity gate model is procedural, not complexity-theoretic.** It enforces process discipline but cannot compensate for unfavorable asymptotic scaling. A problem that passes all four maturity gates may still offer no practical quantum advantage if the constant factors or scaling exponents are prohibitive; the three Stage D problems, all archived by the screening above, are examples.

8. **Stage labels are declared, and only partly verified.** Each README states its own stage. Until this revision CI checked only that the declaration met a per-problem minimum and that two README sections existed (Section 5.2), and never inspected the calibration ensembles or evidence packages that Stages C and D require. Nothing therefore flagged that the calibration ensembles cited for the Stage C labels of 01, 02, 07, 14 and 17 (generated 2026-04-10 to 2026-04-12) predated the replacement of those problems' VQE hardware kernels by QPE kernels (2026-04-18), that their resource estimates still targeted the VQE routines, or that three Stage C problems lacked valid ensemble statistics: 16 had three runs, and 14 and 18 reported means, deviations and intervals of zero because their tuple- and list-valued outputs were never parsed. Following that up found worse: the QPE kernels evolved under a diagonal unitary, and the quantum-walk kernel's position never depended on its coin, so once parsed its ensemble showed every run on the same site. All six kernels were rewritten and tested against exact simulation, every ensemble was regenerated, and CI now fails when the ensemble behind a Stage C or D label is missing, incomplete, or was computed from sources other than the current ones. The rest of what each stage requires, such as fairness reviews and scaling analyses, is still checked for presence only, and the emulator and noise studies have not been repeated for the rewritten kernels.

## 9. Future Work

- ~~Obtain real Azure Quantum Resource Estimator profiles~~ (completed April 2026: all 20 problems profiled)
- ~~Promote Stage D candidates~~ (completed 2026-05-06, #89: QAE, QAOA MaxCut, Grover database search with scaling analysis + fairness reviews. Grover PQC was a candidate but remains at Stage B.)
- ~~Multi-model resource estimation~~ (completed April 2026: 4 qubit models × surface code = 80 estimates across all 20 problems. The Majorana profiles and floquet_code were retired because QRE v3 does not realise them for these traces.)
- ~~Evaluator agent for honest quantum/HPC/AI platform recommendation~~ (completed April 2026. Since August 2026 a deterministic router applies the six filters F1-F6 and owns the verdict, and a language model served through the Azure AI Foundry model-router writes only the explanation; model disagreement is recorded, not applied. Since 2026-09-25 the router also owns any exponential or superpolynomial advantage class it publishes)
- ~~Code generation for recommended platform~~ (completed April 2026: Q# generator for quantum problems, Bicep workspace generator for HPC/AI Foundry/Quantum infrastructure)
- Execute small kernels on quantum hardware, not only emulators, and compare the results with the H2-1E noise model
- ~~Re-run the calibration studies for the QPE kernels and point their resource estimates at the QPE routines~~ (completed 2026-09-25, after rewriting the kernels; Section 4.2)
- Re-run the emulator and noise studies for the rewritten QPE and quantum-walk kernels (Section 8, limitation 8)
- Bind the other evidence artifacts to hashes of the kernels they describe, as the calibration ensembles now are, and make the CI checks required for merging, so that stale evidence blocks a merge rather than only failing a build
- Replace at least one classical baseline with a state-of-the-art competitor (Goemans-Williamson for MaxCut, importance sampling for QAE)
- Extend scaling analysis to QAOA and VQE with noise models at different error rates
- Investigate whether the maturity gate model can be extended with complexity-theoretic checks (scaling slope verification, classical hardness evidence requirements)
- Integrate Troyer Part 6 cost model when published  adds quantum vs HPC vs AI cost-advantage analysis to evaluator output

## 10. Conclusion

We have presented a software engineering framework for quantum algorithm development that prioritizes honest assessment over optimistic claims. The framework's primary value is not in the quantum implementations  which are toy-scale and classically trivial  but in the methodology: standardized structure, automated validation, and maturity gates designed to prevent claiming more than the evidence supports.

Of 20 implemented problems, 9 are declared at Stage C, 8 remain at Stage B, and 3 have reached Stage D (advantage evidence with filed claim contracts); for several of the Stage C problems the supporting calibration evidence was stale or incomplete until this revision, which regenerated it and made CI fail when it goes stale again (Section 8). No problem claims demonstrated practical quantum advantage  the Stage D contracts are explicitly tagged as "theoretical" or "projected" with documented residual risks. Screening the same problems against utility-scale filters archived eleven of them. Those eleven include all three Stage D problems, because maturity certifies that a claim is documented, not that it is favorable. The maturity gate model correctly identifies that emulator results on small instances, even with cross-platform validation, do not constitute evidence of quantum utility.

The practical lessons  that placeholders masquerade as implementations, that encoding bugs survive validation, that mock estimates create false confidence, that presence checks let evidence go stale  are transferable to any quantum development effort. We hope the framework's insistence on honest self-assessment contributes to healthier practices in the quantum computing community.

All code, data, and tooling are available at https://github.com/WernerRall147/quantum-grand-challenges (DOI: 10.5281/zenodo.19222020).

## References

[1] T. Lubinski et al., "Application-Oriented Performance Benchmarks for Quantum Computing," IEEE Transactions on Quantum Engineering, 2023.

[2] J. Finžgar et al., "QUARK: A Framework for Quantum Computing Application Benchmarking," IEEE International Conference on Quantum Computing and Engineering, 2022.

[3] A. Javadi-Abhari et al., "Quantum Computing with Qiskit," arXiv:2405.08810, 2024.

[4] M. A. Nielsen and I. L. Chuang, "Quantum Computation and Quantum Information," Cambridge University Press, 2010.

[5] J. Preskill, "Quantum Computing in the NISQ era and beyond," Quantum, 2018.

[6] R. Babbush et al., "Focus beyond quadratic speedups for error-corrected quantum advantage," PRX Quantum, 2021.

[7] M. Goemans and D. Williamson, "Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming," JACM, 1995.

[8] F. Pan, K. Chen, and P. Zhang, "Solving the sampling problem of the Sycamore quantum circuits," Physical Review Letters 129, 090502, 2022 (arXiv:2111.03011).

[9] J. Tindall, M. Fishman, E. M. Stoudenmire, and D. Sels, "Efficient tensor network simulation of IBM's Eagle kicked Ising experiment," PRX Quantum 5, 010308, 2024 (arXiv:2306.14887).

[10] E. Tang, "A quantum-inspired classical algorithm for recommendation systems," Proceedings of the 51st ACM Symposium on Theory of Computing (STOC), 2019 (arXiv:1807.04271).

[11] T. Hoefler, T. Häner, and M. Troyer, "Disentangling hype from practicality: on realistically achieving quantum advantage," Communications of the ACM 66(5), 82-87, 2023 (arXiv:2307.00523).

[12] D. P. DiVincenzo, "The physical implementation of quantum computation," Fortschritte der Physik 48, 771-783, 2000 (arXiv:quant-ph/0002077).

[13] M. Grassl, B. Langenberg, M. Roetteler, and R. Steinwandt, "Applying Grover's algorithm to AES: quantum resource estimates," Post-Quantum Cryptography (PQCrypto 2016), LNCS 9606, 29-43, 2016 (arXiv:1512.04965).

[14] E. Farhi, J. Goldstone, and S. Gutmann, "A quantum approximate optimization algorithm," arXiv:1411.4028, 2014.

[15] M. Troyer, quantum architecture lecture series, Microsoft Quantum, 2025-2026, https://quantum.microsoft.com/en-us/insights/industry-insights/quantum-architecture-series.

[16] J. A. Smolin, G. Smith, and A. Vargo, "Oversimplifying quantum factoring," Nature 499, 163-165, 2013 (arXiv:1301.7007).

[17] M. Mörchen, G. H. Low, T. Weymuth, H. Liu, M. Troyer, and M. Reiher, "Classification of electronic structures and state preparation for quantum computation of reaction chemistry," arXiv:2409.08910, 2024.

[18] S. Lee et al., "Evaluating the evidence for exponential quantum advantage in ground-state quantum chemistry," Nature Communications 14, 1952, 2023 (arXiv:2208.02199).

[19] M. E. Beverland et al., "Assessing requirements to scale to practical quantum advantage," arXiv:2211.07629, 2022.

[20] E. F. Dumitrescu et al., "Cloud quantum computing of an atomic nucleus," Physical Review Letters 120, 210501, 2018 (arXiv:1801.03897).

## Appendix A: Problem Registry

Stages are those recorded in `docs/objective-kpis.json`; status is the outcome of the utility-scale screening in Section 8. Qubit ranges are counted as in Table 1.

| # | Domain | Algorithm | Qubits | Stage | Status |
|---|---|---|---|---|---|
| 01 | Hubbard Model | VQE, then QPE | 2-14 | C | Active |
| 02 | Catalysis | VQE, then QPE | 2-12 | C | Active |
| 03 | Risk Analysis | QAE and IQAE | 5-14 | D | Archived |
| 04 | Linear Solvers | HHL | 5-6 | B | Archived |
| 05 | MaxCut | QAOA | 3 | D | Archived |
| 06 | Trading | QAE | 3 | B | Archived |
| 07 | Drug Discovery | VQE, then QPE | 2-12 | C | Active |
| 08 | Protein Folding | QAOA | 2-4 | B | Archived |
| 09 | Factorization | Shor | 8 | C | Active |
| 10 | Cryptography | Grover | 3-5 | B | Archived |
| 11 | Machine Learning | Swap Test | 5 | B | Archived |
| 12 | Optimization | QAOA | 3-4 | B | Archived |
| 13 | Climate | HHL | 5 | B | Archived |
| 14 | Materials | VQE, then QPE | 2-12 | C | Active |
| 15 | Database Search | Grover | 4-12 | D | Archived |
| 16 | Error Correction | QEC | 5 | C | Active |
| 17 | Nuclear Physics | VQE, then QPE | 2-12 | C | Active |
| 18 | Photovoltaics | Quantum Walk | 3 | C | Active |
| 19 | QCD | Trotter | 2-4 | C | Active |
| 20 | Space Planning | QAOA | 3-4 | B | Archived |
