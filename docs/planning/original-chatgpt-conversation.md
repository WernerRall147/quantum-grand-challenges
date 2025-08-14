# Original ChatGPT Conversation: Quantum Grand Challenges Project Planning

*Date: August 14, 2025*  
*Source: Initial project conception and planning discussion*

## Context
This document contains the original conversation with ChatGPT that outlined the vision and structure for tackling 20 major scientific problems using Q# and quantum computing. This serves as the foundational blueprint for the project.

---

Get me a list of the top 20 most difficult math, science and technological problems that scientists and mathematicians are trying to solve. I would like to use AI to start working on them. 

The focus will be using Microsoft Q# Quantum Development kit to try and solve problems. 
ChatGPT said:
Thought for 1m 25s

Awesome ambition, Werner. Here's a crisp, Q#-first hit list of 20 genuinely hard problems where quantum algorithms (and AI to steer/automate them) could move the needle. For each item I note the Q#/algorithm angle and a concrete "first experiment" you can run.

## Top 20 problems with a Q# plan

1. **Strongly-correlated electrons & high-Tc superconductivity (Hubbard model)**
   - Q# angle: Hamiltonian simulation + Phase Estimation / qubitization; VQE as NISQ-style baseline.
   - Start: Use the QDK chemistry stack (Broombridge format + simulation primitives) to build toy Hubbard instances and estimate resources for fault-tolerant runs. 

2. **Industrial catalysis design (e.g., nitrogen fixation / FeMo-cofactor)**
   - Q# angle: Electronic structure with VQE → PEA refinement.
   - Start: Encode small active spaces from .yaml Broombridge files; sweep ansätze and use the Resource Estimator to compare logical qubit counts vs. error budgets. 

3. **Electrocatalysts for green hydrogen (OER/HER mechanisms)**
   - Q# angle: Reaction path energetics via chemistry library; amplitude estimation for rare-event probabilities.
   - Start: Prototype minimal cluster models and benchmark phase-estimation depth with the Resource Estimator. 

4. **Solid-state battery materials (ion transport & stability)**
   - Q# angle: Band-gap and defect energetics using Hamiltonian simulation; phase estimation on simplified lattices.
   - Start: Build tight-binding toy Hamiltonians and compare Trotter vs. qubitization costs. 

5. **Room-temperature superconductors**
   - Q# angle: Same toolchain as (1), but emphasize multi-orbital models and adiabatic state prep.
   - Start: Resource-estimate adiabatic paths vs. phase-estimation shots for small 2D lattices. 

6. **Accurate drug binding energies (ab initio)**
   - Q# angle: Active-space chemistry + VQE/PEA; use AI to prune conformers/poses.
   - Start: Small ligands (≤12e/12o) in Broombridge; compare ansatz families and logical qubits via the Resource Estimator. 

7. **Biomolecular quantum dynamics (photoactive proteins / exciton transport)**
   - Q# angle: Open-system Hamiltonians (toy models) + phase estimation; amplitude estimation for transfer yields.
   - Start: Dimer/trimer exciton models; study scaling with precision ε in the estimator. 

8. **Quantum simulation for nuclear physics (few-nucleon, lattice gauge toy models)**
   - Q# angle: Trotter/qubitization; adiabatic prep into low-lying spectra.
   - Start: Encode a 1D lattice gauge toy model; estimate T gate counts under different code distances. 

9. **Climate & catastrophe risk (tail probabilities)**
   - Q# angle: Quantum Amplitude Estimation (QAE) → quadratic speedup over Monte Carlo.
   - Start: Implement QAE in Q# on a synthetic loss distribution; benchmark sample vs. query complexity. 

10. **Fusion plasma control & scheduling**
    - Q# angle: QAOA/quantum search for discrete control sequences; AI tunes schedules and cost functions.
    - Start: QAOA for constrained sequence selection; use the Katas patterns to stand up mixers/costs. 

11. **Global logistics / portfolio & risk-parity optimization**
    - Q# angle: QAOA / Grover-style search (feasible-set oracles).
    - Start: Prototype a Max-Cut/knapsack instance; try Grover or QAOA and measure depth/width needs. 

12. **Large sparse linear systems & PDE solves**
    - Q# angle: HHL-family algorithms (and modern refinements).
    - Start: Implement a toy HHL on a sparse matrix oracle and resource-estimate vs. condition number κ. 

13. **Inverse problems (tomography, deblurring) via linear solvers**
    - Q# angle: Map to Ax=b primitives (HHL-style) + amplitude estimation for observables.
    - Start: Build an oracle for banded A and compare precision/ε scaling. 

14. **Quantum kernel methods (QSVM) for small, structured data**
    - Q# angle: Feature-map circuits + kernel estimation; AI selects feature maps.
    - Start: Implement kernel estimation circuits from Katas patterns; study noise vs. margin tradeoffs. 

15. **Cryptanalysis of RSA/ECC (transition planning)**
    - Q# angle: Shor's algorithm; do resource estimation for RSA-2048 / P-256 to inform crypto agility.
    - Start: Use Q# resource estimator targets to quantify logical qubits, T-depth, and physical qubits under a surface-code model. 

16. **Quantum attacks on symmetric crypto (key search, collisions)**
    - Q# angle: Grover gives quadratic speedups; quantify the real overhead with Q#.
    - Start: Build a Grover oracle for a toy block cipher; compare iterations vs. target security level. 

17. **Assessment of post-quantum schemes (lattices, codes, multivariate)**
    - Q# angle: Prototype/estimate quantum subroutines used in the best-known attacks (e.g., quantum sieving components) to stress-test parameters.
    - Start: Stub the oracles and use the estimator to bound plausible speedups. 

18. **Fault-tolerant quantum computing itself (decoders, layouts, compilers)**
    - Q# angle: Use the Resource Estimator to co-design algorithms with code distances, error rates, and T-factories; AI searches schedules/teleportation layouts.
    - Start: Vary code parameters in the estimator's target profile and plot cost curves. 

19. **Approximation of hard combinatorial problems (Max-Cut, SAT variants)**
    - Q# angle: QAOA / Grover hybrids; AI tunes mixers, initial states, and schedules.
    - Start: Run QAOA depth-1..p on graph families; study performance vs. instance structure using Katas scaffolds. 

20. **Fast unstructured search / pattern-matching in massive spaces**
    - Q# angle: Grover with problem-specific oracles (the hard part); AI helps synthesize/verify oracles.
    - Start: Implement and benchmark a Q# oracle for a constrained pattern search and measure success amplitude growth. 

## Your starter toolbox (Q# + AI)

- QDK Chemistry & Broombridge for electronic structure inputs and samples
- Quantum Katas for production-ready Q# patterns (Grover, phase estimation, QAOA scaffolding)
- Azure Quantum Resource Estimator to turn every idea above into qubits/T-gates/physical-qubits under your chosen code & error rates
- Linear-algebra workhorses like HHL (and descendants) as building blocks
- Grover/search concepts for various applications

## How to attack one problem end-to-end (repeatable playbook)

1. Scope a toy instance small enough to simulate/classically validate
2. Write the Q# kernel (oracle / cost / time-evolution) using Katas patterns
3. Run the Resource Estimator for multiple precision targets and error models; record logical vs. physical costs
4. Use AI (Copilot/Copilot Chat) to: generate oracles, auto-search ansätze/schedules, and build parameter sweeps & plots; keep prompts reproducible in your repo
5. Decide "research viable or not yet" from cost curves; iterate problem size/model

---

## Project Structure Discussion

The conversation then evolved to discuss how to structure a project that would systematically tackle these problems using AI tools and quantum computing.

### Key Architectural Decisions

**Monorepo vs Multi-repo:**
- Decision: Single monorepo `quantum-grand-challenges/` with standardized scaffold per problem type
- Rationale: Keeps shared Q# libraries, common CI, and single results website together
- Future: Can split if a track grows too large

**Recommended Structure:**
```
quantum-grand-challenges/
├─ libs/                         # Reusable Q# + C# helpers (oracles, AE, PEA, QAOA, HHL)
├─ problems/
│  ├─ 01_hubbard/                # Strongly-correlated electrons
│  │  ├─ qsharp/                 # Q# project (alg kernels)
│  │  ├─ python/                 # harness/plots (optional)
│  │  ├─ instances/              # YAML/JSON inputs (e.g., Broombridge for chemistry)
│  │  ├─ estimates/              # Resource Estimator JSON outputs
│  │  └─ README.md               # What, why, how, status
│  ├─ 02_catalysis/
│  ├─ 03_qae_risk/               # Monte Carlo → QAE
│  ├─ 04_linear_solvers/         # HHL family
│  ├─ 05_qaoa_maxcut/            # Combinatorial optim
│  ├─ 06_shor_resources/         # Crypto resource studies
│  └─ ...
├─ tooling/
│  ├─ estimator/                 # CLI scripts to run Azure Quantum Resource Estimator
│  ├─ azq/                       # az quantum job helpers (targets, submit, fetch)
│  └─ schema/                    # JSON schema for results
├─ .devcontainer/                # Codespaces dev image (QDK, az, Python, Node)
├─ .github/workflows/            # CI: build, test, estimate, publish site
├─ website/                      # Next.js (or Docusaurus) + charts from JSON artifacts
└─ docs/                         # High-level docs; Problem book; How-to run
```

### Development Environment Strategy

**Codespaces + DevContainer with:**
- Azure Quantum Development Kit (QDK) + VS Code extension
- Azure CLI with quantum extension (`az extension add -n quantum`)
- Resource Estimator (open-source, runs locally)
- Optional chemistry input support (Broombridge YAML)

### Standard Results Contract (JSON)

Uniform outputs for automation and website integration:

```json
{
  "problem_id": "03_qae_risk",
  "algorithm": "QAE",
  "instance": {"seed": 42, "dist": "lognormal", "epsilon": 0.01},
  "estimator_target": "surface_code_generic_v1",
  "metrics": {
    "logical_qubits": 127,
    "physical_qubits": 1_800_000,
    "t_count": 2.3e11,
    "runtime_days": 4.2
  },
  "build": {"commit": "abc123", "qdk_version": "v1.x"},
  "date_utc": "2025-08-14T20:00:00Z",
  "notes": "ε=0.01; compared to classical MC 1e6 samples"
}
```

### AI/Agent Strategy

**Phase A — Single orchestrator**
- Planner that reads papers/issues → emits task lists + acceptance criteria
- Drafts Q# oracles/cost functions from specs
- Writes estimator configs and analysis notebooks

**Phase B — Light multi-agent (hub-and-spoke)**
- Literature Miner → DOI/arXiv to structured design brief
- Kernel Engineer → Q# interfaces and tests
- Experiment Runner → estimator sweeps and JSON persistence
- Analyst/Publisher → JSON to charts + markdown summaries

### Immediate Implementation Targets

1. **QAE for tail risk** (`problems/03_qae_risk/`)
2. **Shor resource study** (`problems/06_shor_resources/`)
3. **HHL toy linear solver** (`problems/04_linear_solvers/`)
4. **Chemistry/Broombridge demo** (`problems/02_catalysis/`)

---

*This document serves as the foundational reference for all future development decisions and AI agent interactions.*
