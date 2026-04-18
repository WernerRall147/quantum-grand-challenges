Now I have a complete picture of all 20 problems. Let me synthesize a comprehensive breakdown for you.

---

# 🌌 Quantum Grand Challenges — Full Breakdown & Real-World Context

This repository is a **systematic scientific workbench** — not a toy project. It takes 20 of the hardest unsolved or computationally intractable problems in science and industry, builds classical baselines, and progressively replaces those with Q# quantum implementations to rigorously test where quantum computing can actually move the needle. Here's what each problem means, what it's doing, and how it stacks up against the best we know today.

---

## 🏗️ How the Repo Works (Before Diving In)

Each problem follows a **maturity gate system**:
- **Stage A** — Problem defined
- **Stage B** — Classical baseline + Q# scaffold compiles
- **Stage C** — Real quantum circuit, uncertainty-bounded comparisons, hardware-aware validation
- **Stage D** — Demonstrated quantum advantage evidence

All 20 are **Stage B or better** as of March 2026. Problems 3, 5, and 15 have reached **Stage C**.

---

## The 20 Problems

### 🔬 PHYSICS & CHEMISTRY

---

### 01 · Hubbard Model *(Stage B)*
**What it is:** The Hubbard model is physics' minimal model of electron-electron interactions in a crystal lattice. It explains phenomena like high-temperature superconductivity, magnetism, and metal-insulator transitions.

**What your repo does:** Solves the 2-site half-filled Hubbard model analytically in both Python and Q#, tracking the energy gap between singlet and triplet states (the "spin gap" and "charge gap") across interaction strength.

**Real-world impact:** Understanding the Hubbard model at scale = understanding **high-temperature superconductors** like cuprates. Room-temperature superconductivity would eliminate resistive losses in power grids (~$20B/year saved in the US alone), enable lossless MRI machines, and power quantum computers themselves.

**Current best classical knowledge:** Classical computers can exactly solve Hubbard models up to ~20–30 sites using exact diagonalization. Beyond that, approximations (DMRG, quantum Monte Carlo) struggle — especially for 2D lattices at finite doping. This is a known "sign problem" wall.

**Quantum advantage potential:** VQE and QPE on quantum hardware are expected to scale to hundreds of sites with polynomial resources — something no classical algorithm can match. IBM and Google have simulated small Hubbard lattices on NISQ hardware (2022–2024), but noise still dominates.

**Your repo's gap:** Still analytical parity (no actual VQE/QPE circuit yet). The next step is the real Q# quantum kernel.

---

### 02 · Quantum Catalysis *(Stage B)*
**What it is:** Chemical catalysts lower the activation energy of reactions. The repo models catalytic reaction rates (Arrhenius model) for Pt, Fe, and Cu catalysts.

**What your repo does:** Classical Arrhenius rate baseline, matched by a Q# analytical stub. Targets: computing accurate electronic-structure energy barriers using quantum simulation.

**Real-world impact:** Industrial catalysis uses **~90% of all manufactured chemicals** as intermediates. Ammonia synthesis (Haber-Bosch, for fertilizer) alone uses 1–2% of global energy. A 10% efficiency improvement in catalysis = hundreds of millions of tons of CO₂ saved annually. Quantum-designed catalysts could also unlock **CO₂ reduction**, nitrogen fixation at room temperature, and next-generation fuel cells.

**Current best classical knowledge:** Density Functional Theory (DFT) is the workhorse — but it approximates electron exchange-correlation and fails for strongly correlated systems. Coupled cluster methods (CCSD(T)) are more accurate but scale as O(N⁷) — impractical for most realistic active sites.

**Quantum advantage potential:** Quantum phase estimation can compute molecular ground states with chemical accuracy (~1 kcal/mol) using polynomial resources. Microsoft's estimates suggest a fault-tolerant quantum computer could simulate FeMo-cofactor (the active site in nitrogen fixation) in hours vs. years classically.

---

### 17 · Quantum Nuclear Physics *(Stage B)*
**What it is:** Simulating few-nucleon systems (proton-proton, deuteron, helium-4) using effective field theory (EFT) Hamiltonians derived from QCD.

**What your repo does:** Classical EFT Hamiltonian builder + diagonalization baseline, Q# stub for quantum simulation via adiabatic state preparation and phase estimation.

**Real-world impact:** Understanding nuclear binding energies with precision underpins:
- **Nuclear energy** — more accurate reaction cross-sections for reactor design and safety
- **Astrophysics** — nucleosynthesis in stars, neutron star equation of state
- **Weapons non-proliferation** — verification physics

**Current best classical knowledge:** Nuclear lattice EFT and *ab initio* methods (NCSM, coupled cluster) handle nuclei up to ~A=12–16 on classical supercomputers. Beyond that, scaling becomes intractable.

**Quantum advantage:** First-principles simulation of medium-to-heavy nuclei (A > 40) is a natural quantum computing target. Research from groups at the University of Washington and Lawrence Berkeley shows quantum simulation could unlock this regime.

---

### 19 · Quantum Chromodynamics (QCD) *(Stage B)*
**What it is:** QCD is the theory of the strong nuclear force — what holds protons and neutrons together via quarks and gluons. It's notoriously intractable in the non-perturbative (low-energy) regime.

**What your repo does:** Classical Wilson plaquette energy estimator (lattice gauge theory) + Q# stub targeting Kogut-Susskind Hamiltonian encoding with SU(3)/SU(2) gauge constraints.

**Real-world impact:** Solving nonperturbative QCD from first principles would:
- Explain **confinement** (why quarks are never free)
- Predict hadron masses from scratch (proton radius puzzle)
- Enable **precision particle physics** tests at CERN/LHC
- Eventually model quark-gluon plasmas as seen in neutron star mergers

**Current best classical knowledge:** Lattice QCD runs on the world's largest supercomputers. It works, but scales as O(V⁵) in lattice volume and faces a sign problem at finite density. Monte Carlo methods hit a fermion sign problem wall.

**Quantum advantage:** Quantum simulation of gauge theories is a flagship application, first proposed by Feynman (1982). Google, IBM, and Quantinuum have demonstrated toy SU(2) and U(1) lattice gauge models on NISQ hardware (2023–2024). Full SU(3) at relevant scales requires fault-tolerant hardware many years out.

---

### 18 · Photovoltaics *(Stage B)*
**What it is:** Maximizing solar cell efficiency by modeling light absorption, carrier transport, and recombination using quantum coherence effects.

**What your repo does:** Shockley-Queisser classical efficiency estimator baseline; Q# stub targeting excitonic network encoding and open quantum dynamics (Lindblad channels).

**Real-world impact:** The theoretical Shockley-Queisser limit for single-junction solar cells is ~33%. Multi-junction and quantum coherence effects (e.g., in photosynthesis) could push beyond this. A 5% absolute efficiency gain across global solar capacity = ~100 GW of additional clean energy equivalent.

**Current best classical knowledge:** DFT and time-dependent DFT (TD-DFT) model excited states but struggle with strongly correlated electron-hole pairs and multi-exciton dynamics. ORCA and Gaussian are state of the art but hit walls for large chromophore assemblies.

**Quantum advantage:** Quantum simulation of excitonic energy transfer (like in photosynthesis) is theorized to provide exponential speedup for open quantum dynamics. A 2023 paper from Harvard demonstrated quantum simulation of a 2D light-harvesting analog.

---

## 💊 BIOLOGY & MEDICINE

---

### 07 · Drug Discovery *(Stage B)*
**What it is:** Finding molecules that bind to disease-causing protein targets with high affinity.

**What your repo does:** Classical docking/scoring baseline across molecule libraries; Q# stub targeting VQE with UCCSD ansatz for electronic structure of small drug fragments (H₂, LiH, minimal basis sets).

**Real-world impact:** Average cost to bring a drug to market: **$2.6 billion**, 12+ years. Quantum-accurate binding energy calculations could:
- Screen billions of candidate molecules in silico
- Reduce false positives in early discovery
- Cut timelines by years for diseases like Alzheimer's, cancer, antibiotic-resistant bacteria

**Current best classical knowledge:** AlphaFold2/3 (DeepMind, 2021–2024) revolutionized structure prediction. However, structure ≠ binding energy — quantum mechanics governs the binding. Classical docking (AutoDock, Glide) uses empirical force fields that miss quantum correlation effects crucial for tight binders.

**Quantum advantage:** Quantum computers promise *exact* or near-exact electronic structure calculations for binding pockets. Pfizer, Roche, and Boehringer Ingelheim are all partnering with quantum hardware companies for this. Timeline: fault-tolerant hardware needed — likely 5–10 years.

---

### 08 · Protein Folding *(Stage B)*
**What it is:** Predicting the 3D structure of proteins from their amino acid sequence, and modeling the folding energy landscape.

**What your repo does:** Classical knowledge-based contact-map scoring baseline; Q# stub for quantum Boltzmann sampling over lattice conformations.

**Real-world impact:** Misfolded proteins cause Parkinson's, Alzheimer's, ALS, and many cancers. Understanding the folding landscape = understanding disease mechanisms + rational drug design.

**Current best classical knowledge:** **AlphaFold3** (2024) achieves near-experimental accuracy for single protein structure prediction. It's arguably the decade's biggest AI breakthrough in biology. However, it predicts *one* low-energy structure — not the *full energy landscape* or *dynamics* (folding pathways, transient misfolded states).

**Quantum advantage:** Quantum computers could sample the full Boltzmann distribution over conformational space — something classical computers cannot do efficiently for large proteins. This is a longer-term (10+ year) target. For now, your problem wisely focuses on the quantum-accessible piece: quantum-enhanced energy estimation, not structure prediction (where classical AI already wins).

---

## 💰 FINANCE & COMPUTING

---

### 03 · Quantum Amplitude Estimation for Risk Analysis *(Stage C — Most Advanced)*
**What it is:** Using QAE to estimate tail risk (the probability of extreme financial losses) with quadratic speedup over classical Monte Carlo.

**What your repo does:** Full IQAE implementation, Grover + QPE circuits, Azure Quantum resource estimation (594k physical qubits, 6.4 seconds runtime), calibrated classical vs. quantum comparison.
- **Classical Monte Carlo (10k samples):** 18.98% ± 0.39%
- **QAE (20 ensemble runs):** 19.58% ± 1.82%
- **Theoretical:** 18.98%

**Real-world impact:** Banks and financial institutions run millions of Monte Carlo simulations daily for **Value-at-Risk (VaR)** and stress testing (Basel III/IV requirements). A quadratic speedup (O(1/ε) vs O(1/ε²)) means:
- A calculation needing 10,000 samples needs only ~100 quantum oracle calls for ε=0.01
- Real-time risk recalculation during market crises
- More accurate tail-risk modeling for systemic risk (think: 2008-style events)

**Current best classical knowledge:** GPU-accelerated Monte Carlo (NVIDIA cuQuantum, standard in all major banks). For 99.9% VaR confidence, classical needs millions of samples. Quasi-Monte Carlo (QMC) methods provide some improvement but not quadratic.

**Quantum advantage:** The quadratic speedup is **provable** — one of the few proven quantum advantages for a financial application. Goldman Sachs, JPMorgan, and HSBC have published papers demonstrating this pathway. The bottleneck: fault-tolerant hardware with ~600k physical qubits — still years away.

---

### 04 · Quantum Linear Solvers (HHL) *(Stage B–C transition)*
**What it is:** HHL algorithm for solving linear systems Ax=b exponentially faster than classical methods (under assumptions).

**What your repo does:** Full HHL implementation with QPE, inverse QFT, eigenvalue inversion, and post-selection. **Azure Resource Estimate: 18,680 physical qubits, 52ms runtime** — the most resource-efficient problem in the repo.

**Real-world impact:** Linear systems underpin **everything computational** — fluid dynamics, structural engineering (finite element analysis), machine learning, power grid optimization, and climate modeling. HHL's theoretical exponential speedup means:
- Solving a million-variable fluid simulation in milliseconds
- Real-time optimization of electrical grids
- Weather modeling at finer spatial resolution

**Current best classical knowledge:** Conjugate gradient, GMRES, multigrid methods for sparse systems. Sparse systems up to ~10⁸ variables are tractable on classical supercomputers. The challenge: HHL's speedup is conditional on the matrix being sparse, well-conditioned, and the solution readable — these assumptions often don't hold in practice.

**Important nuance:** Scott Aaronson's "HHL fine print" — the quantum speedup often disappears when you account for state preparation (loading classical data into the quantum state) and readout (extracting the full solution vector). Your repo acknowledges this honestly. Real-world advantage is more nuanced than the asymptotic claim suggests.

---

### 05 · QAOA for Max-Cut *(Stage C)*
**What it is:** Quantum Approximate Optimization Algorithm applied to the Max-Cut graph partitioning problem — a canonical NP-hard combinatorial optimization problem.

**What your repo does:** Full depth-configurable QAOA with noise sweeps, depth sweeps (d=1,2,3), uncertainty-bounded multi-trial reporting, Azure job manifests, and calibrated comparisons.
- Small instance, depth 3: refined mean cut = **2.2** (vs classical optimum) 
- Degrades gracefully: 2.2 → 1.95 as noise goes from p=0 → p=10%

**Real-world impact:** Max-Cut generalizes to:
- **Chip design** (VLSI partitioning)
- **Network design** (clustering, community detection)
- **Portfolio optimization** (asset correlation partitioning)
- **Scheduling** (conflict-free resource allocation)

**Current best classical knowledge:** The Goemans-Williamson algorithm (1995) gives a 0.878 approximation guarantee in polynomial time using semidefinite programming. For exact Max-Cut, it's NP-hard. Classical heuristics (simulated annealing, tabu search) work well in practice.

**Quantum advantage status:** QAOA at low depth (p=1,2,3) does NOT beat Goemans-Williamson classically. Research (Bravyi et al., 2020; IBM, 2022) shows shallow QAOA is beaten by classical algorithms on average. The hope is deep QAOA or better ansätze on fault-tolerant hardware might eventually win. **This remains an open research question** — and your repo is building exactly the right evidence base to answer it honestly.

---

### 06 · High-Frequency Trading *(Stage B)*
**What it is:** Using quantum-enhanced machine learning (variational classifiers, quantum kernels) to predict short-term price movements in electronic markets.

**What your repo does:** Classical moving-average crossover strategy baseline on synthetic limit order books; Q# stub for amplitude-encoded feature maps and variational classifiers.

**Real-world impact:** HFT firms collectively move ~$50B/day in equity markets. A statistically significant quantum prediction edge — even fractional basis points — across millions of trades = enormous profit. But more importantly, **better HFT risk models** reduce flash crashes and systemic market instability.

**Current best classical knowledge:** Deep learning (LSTMs, transformers) on tick data. Reinforcement learning for order execution. Classical ML is highly competitive; most "alpha" is arbitraged away quickly. Latency (nanoseconds) is as important as prediction accuracy.

**Quantum advantage:** Highly speculative at present. Quantum kernel methods *might* find patterns in market data that classical kernels miss — but the loading problem (getting market data into qubits fast enough) is a fundamental bottleneck. Most researchers consider this a longer-term aspiration.

---

### 09 · Integer Factorization (Shor's Algorithm) *(Stage B)*
**What it is:** Breaking RSA encryption by factoring large integers using Shor's quantum algorithm — the most famous quantum computing result.

**What your repo does:** Classical Pollard Rho factoring baseline; Q# stub for modular exponentiation circuits, QFT-based phase estimation, and order finding for small semi-primes (15, 21, 35).

**Real-world impact:** RSA-2048 secures the majority of internet traffic (HTTPS, banking, email). Shor's algorithm would **break all RSA encryption** — a civilization-level security event. This is why NIST finalized post-quantum cryptography standards in 2024 (CRYSTALS-Kyber, CRYSTALS-Dilithium, SPHINCS+).

**Current best classical knowledge:** Best known classical algorithm (General Number Field Sieve, GNFS) factors RSA-2048 in ~10²⁰ operations — infeasible even for all classical computers on Earth. The largest RSA number ever factored classically: **RSA-250** (829 bits, factored in 2020).

**Quantum status:** Factoring RSA-2048 would require ~4,000 *logical* qubits, but millions of *physical* qubits with error correction. Current best: ~1,000–2,000 physical qubits (IBM, Google, Quantinuum). **No quantum computer has broken RSA.** Realistic timeline for cryptographically relevant Shor: 10–20+ years with current hardware trajectories. Your repo's honest framing — "practical hardware remains distant" — is exactly right.

---

### 10 · Post-Quantum Cryptography *(Stage B)*
**What it is:** The flip side of Problem 09 — analyzing the security of quantum-resistant cryptographic schemes (lattice-based, hash-based) against quantum attacks.

**What your repo does:** Classical cost estimation for classical and quantum lattice attacks (BKZ reduction, Grover-amplified sieving); Q# stub for amplitude amplification kernels for nearest-vector search.

**Real-world impact:** NIST finalized PQC standards in 2024. But "quantum-resistant" doesn't mean immune to quantum attacks — Grover's algorithm still gives a quadratic speedup over brute-force attacks on symmetric/hash schemes, halving effective key lengths. Ongoing analysis of lattice parameters (dimension, modulus) is critical to ensure 20–50 year security.

**Current best classical knowledge:** **NIST PQC standards (2024)**: CRYSTALS-Kyber (key exchange), CRYSTALS-Dilithium (signatures), SPHINCS+ (hash-based). Lattice-based schemes have survived 6+ years of public cryptanalysis. Google, Apple, and Signal have already begun migration.

**Quantum angle in your repo:** Modeling how Grover + BKZ hybrid attacks scale — crucial for parameter selection. This is active academic research (Albrecht, Bai, Ducas et al.).

---

## 🧠 ALGORITHMS & COMPUTING

---

### 11 · Quantum Machine Learning *(Stage B)*
**What it is:** Using quantum kernel methods (swap-test based Gram matrices) to classify data in higher-dimensional Hilbert spaces than classical kernels can efficiently access.

**What your repo does:** Classical RBF kernel ridge regression baseline; Q# stub for parameterized feature maps and quantum kernel evaluation.

**Real-world impact:** If quantum kernels outperform classical ones on structured data (e.g., molecular fingerprints, time-series), it would accelerate:
- Drug discovery (molecular property prediction)
- Fraud detection (financial pattern recognition)
- Materials informatics (crystal property prediction)

**Current best classical knowledge:** Classical ML (transformers, gradient boosting) dominates most benchmarks. The QML hype was partially deflated by theoretical results showing that quantum kernel models face "exponential concentration" — their kernels may become exponentially hard to estimate. Research by Huang et al. (2021, Nature Comms) showed quantum kernels can have provable advantages on *specifically constructed* datasets, but natural datasets remain an open challenge.

**Your repo's honest framing:** Classical RBF baseline first, quantum improvement to be demonstrated. This is the right scientific approach.

---

### 12 · Quantum Combinatorial Optimization (Scheduling) *(Stage B)*
**What it is:** Using QAOA for scheduling and resource allocation — minimizing weighted job tardiness across machines.

**What your repo does:** Classical greedy weighted tardiness scheduler baseline; Q# stub for cost Hamiltonian encoding with machine-constraint mixers.

**Real-world impact:** Industrial scheduling (semiconductor fab, hospital operating rooms, airline crew rostering) is a multi-billion dollar problem. A 1–2% improvement in utilization = $50–100M/year for a mid-size manufacturer.

**Current best classical knowledge:** Commercial solvers (Gurobi, CPLEX) handle problems with thousands of variables near-optimally. Meta-heuristics (genetic algorithms, simulated annealing) scale further. QAOA at current depth doesn't beat these — it's a longer-term play.

---

### 15 · Quantum Database Search (Grover) *(Stage C)*
**What it is:** Grover's algorithm for unstructured search — finds a marked item in N unsorted items in O(√N) steps vs. O(N) classically.

**What your repo does:** Full canonical Grover implementation in Q# with validated simulator results:
- 93% success rate for 16-item single-target search
- 71% for 32-item multi-target search
- 100% for 4,096-item benchmark case

**Real-world impact:** 
- **Cryptography:** Grover halves the effective key length of symmetric encryption (AES-128 → effectively AES-64 against quantum). This is why AES-256 is recommended for post-quantum security.
- **Database search:** √N speedup for truly unstructured data
- **Optimization subroutine:** Grover is a building block in many other quantum algorithms (amplitude amplification)

**Current best classical knowledge:** Classical hash tables, B-trees achieve O(1) or O(log N) for *structured* data. Grover only wins for genuinely *unstructured* search — rare in practice. But as a subroutine within larger algorithms, the speedup compounds.

**Your repo:** One of the most technically complete implementations — actual Grover circuits running on simulators with empirical success rates. Well positioned for Stage D hardware validation.

---

### 16 · Quantum Error Correction *(Stage B)*
**What it is:** Designing and simulating error correction codes (repetition codes, surface codes) that suppress qubit decoherence faster than it accumulates.

**What your repo does:** Classical analytical repetition-code logical error model; Q# stub for stabilizer syndrome extraction and decoder integration.

**Real-world impact:** QEC is the **gating technology for all other problems in this repo**. Without fault tolerance:
- Hubbard VQE is too noisy
- Shor's algorithm is unusable
- QAE errors dominate signal

Every other problem in this repo becomes viable only when QEC works at scale.

**Current best state of the art (2025–2026):**
- **Google:** Demonstrated below-threshold surface code in 2023 (Nature). Achieved logical qubit error rate of 10⁻⁶ with ~1,000 physical qubits per logical qubit.
- **Microsoft:** Topological qubits (Majorana-based) announced significant milestones in 2025, claiming dramatically better physical error rates.
- **IBM:** Heron processors hitting ~0.1% 2-qubit gate errors.
- **Threshold for fault tolerance:** ~1% physical error rate → logical error suppression kicks in. Most hardware is now at or below this threshold.

This is the most enabling problem in your repo. Progress here unlocks all others.

---

## 🌍 ENVIRONMENT & SPACE

---

### 13 · Climate Modeling *(Stage B)*
**What it is:** Using HHL (quantum linear solver) to solve the large sparse linear systems that arise from discretized climate partial differential equations (diffusion equations, energy balance models).

**What your repo does:** Classical 1D energy balance diffusion solver; Q# stub targeting HHL-based linear system solving for radiative forcing profiles.

**Real-world impact:** Climate models (CMIP6) run on exascale supercomputers. Finer spatial resolution = better regional projections = better infrastructure planning. A 10× speed improvement in climate models could mean:
- Sub-km hurricane track prediction
- County-level flood risk assessment
- Near-real-time wildfire spread modeling

**Current best classical knowledge:** NCAR CESM, E3SM, and UK Met Office models run at 10–25 km resolution. GPUs have accelerated these 10–100×. Neural emulators (FourCastNet, GraphCast by Google/DeepMind) achieve remarkable speed at coarser resolution.

**Quantum angle:** If HHL's assumptions hold (sparse, well-conditioned climate operators — which they roughly do for some PDE discretizations), quantum linear solvers could provide polynomial-to-exponential speedup. But the data loading bottleneck again applies.

---

### 14 · Materials Discovery (Batteries) *(Stage B)*
**What it is:** Discovering next-generation battery cathode materials by exploring composition/crystal structure space, targeting stability, voltage, and energy density.

**What your repo does:** Surrogate energy/stability scoring for battery candidate compositions; Q# stub targeting VQE with Hubbard-like operators for electronic structure of candidate lattices.

**Real-world impact:** Lithium-ion batteries power EVs, grid storage, and consumer electronics — a **$150B+ market**. Quantum-designed solid-state electrolytes or high-voltage cathodes (>4.5V) could double energy density, cut charging times, and eliminate fire risk.

**Current best classical knowledge:** DFT (VASP, Quantum ESPRESSO) + high-throughput screening (Materials Project has DFT data for 150,000+ compounds). Google DeepMind's GNoME (2023) discovered 2.2 million new stable crystal structures using AI. But DFT misses strongly correlated electron materials — precisely where next-gen battery cathodes often live.

**Quantum advantage:** Same story as catalysis and drug discovery — quantum simulation for strongly correlated materials is where classical DFT fails and quantum computers excel. Microsoft's Azure Quantum has highlighted battery materials as a priority application.

---

### 20 · Space Mission Planning *(Stage B)*
**What it is:** Optimizing interplanetary trajectories (launch windows, delta-v budgets, gravity assist sequences) using quantum optimization.

**What your repo does:** Classical patched-conic delta-v estimator and window feasibility scoring; Q# stub targeting qubit-register trajectory encoding with QAOA/annealing hybrids.

**Real-world impact:** Trajectory optimization for complex missions (multi-flyby, L2 orbit insertion, asteroid sample return) is solved with tools like GMAT and GPOPS-II. A quantum optimizer could:
- Find more fuel-efficient trajectories (saving millions in launch costs)
- Optimize large constellations (Starlink-scale) routing in real-time
- Enable more ambitious science missions within fixed ΔV budgets

**Current best classical knowledge:** SPICE/GMAT (NASA), Copernicus (ESA). Evolutionary algorithms (PACO, pygmo) handle multi-objective trajectory optimization well. JPL's Europa Clipper trajectory was optimized with 23 flybys classically — impressive but computationally intensive.

**Quantum angle:** QAOA applied to the discrete assignment problem of selecting flyby sequences. Similar to the scheduling/combinatorial optimization landscape — quantum advantage not yet demonstrated, but the encoding is tractable.

---

## 📊 Summary Table

| # | Problem | Domain | Maturity | Quantum Algorithm | Real-World Stakes | Quantum Advantage Status |
|---|---------|--------|----------|------------------|-------------------|--------------------------|
| 01 | Hubbard Model | Physics | Stage B | VQE / QPE | Superconductivity, energy | Theoretically strong |
| 02 | Catalysis | Chemistry | Stage B | QPE / VQE | Fertilizer, fuel cells, CO₂ | Strong, 5–10yr timeline |
| 03 | Risk Analysis | Finance | **Stage C** | **IQAE (full impl.)** | Bank stress testing, VaR | **Proven quadratic speedup** |
| 04 | Linear Solvers | Computing | Stage B–C | HHL | CFD, ML, climate | Conditional (data loading caveat) |
| 05 | Max-Cut (QAOA) | Optimization | **Stage C** | **QAOA (full impl.)** | Chip design, logistics | Open question — active research |
| 06 | HFT | Finance | Stage B | QML / variational | Market stability | Highly speculative |
| 07 | Drug Discovery | Medicine | Stage B | VQE / UCCSD | $2.6B/drug cost, cancer | Strong, 5–10yr timeline |
| 08 | Protein Folding | Biology | Stage B | Quantum Boltzmann | Alzheimer's, Parkinson's | Complementary to AlphaFold |
| 09 | Factorization | Cryptography | Stage B | Shor's | Internet security (RSA) | **Proven** — 20yr hardware timeline |
| 10 | Post-Quantum Crypto | Security | Stage B | Grover + BKZ | NIST PQC validation | Active — Grover halves key strength |
| 11 | QML Kernels | AI/ML | Stage B | Swap-test kernels | Drug/materials discovery | Unresolved — concentration problem |
| 12 | Scheduling | Optimization | Stage B | QAOA | Manufacturing, logistics | Classical still wins |
| 13 | Climate Modeling | Environment | Stage B | HHL | Flood/fire prediction | Conditional on HHL assumptions |
| 14 | Materials (Batteries) | Energy | Stage B | VQE | EV batteries, grid storage | Strong, 5–10yr timeline |
| 15 | Database Search | Computing | **Stage C** | **Grover (full impl.)** | Cryptography, search | **Proven √N speedup** |
| 16 | Error Correction | Enabling Tech | Stage B | QEC / Surface Code | **Enables all other problems** | Hardware crossing threshold NOW |
| 17 | Nuclear Physics | Physics | Stage B | QPE / Adiabatic | Reactor design, astrophysics | Strong, long-term |
| 18 | Photovoltaics | Energy | Stage B | Quantum dynamics | Solar efficiency | Speculative near-term |
| 19 | QCD | Particle Physics | Stage B | Hamiltonian simulation | Fundamental physics | Long-term (10–20yr) |
| 20 | Space Planning | Aerospace | Stage B | QAOA / annealing | Mission cost, science ROI | Moderate — similar to scheduling |

---

## 🎯 The Big Picture

Your repo is doing something genuinely important: **it doesn't oversell**. Each problem has an honest "Advantage Claim Contract" — calling out what's theoretical, what's projected, and what's demonstrated. This is rare in the quantum space, where hype runs ahead of reality.

The **three most impactful near-term targets** with the clearest quantum advantage pathways are:
1. **Problem 03 (Risk/QAE)** — Proven quadratic speedup, your most advanced implementation
2. **Problem 02/07/14 (Chemistry: Catalysis, Drug Discovery, Materials)** — Fault-tolerant quantum chemistry is the field's most credible first killer app
3. **Problem 16 (Error Correction)** — The gating technology: solve this and all others become viable

The **most civilization-altering** if it succeeds: **Problem 09 (Shor's/RSA)** — but it's also the furthest from realization.