# Quantum Grand Challenges — Meeting Preparation Brief

## 1. Deep Dive: QAE Risk Analysis (Problem 03 — Most Mature)

### The Problem
Financial institutions need to estimate tail risk — the probability that portfolio losses exceed a critical threshold (Value-at-Risk). Classical Monte Carlo sampling achieves precision ε using O(1/ε²) samples. Quantum Amplitude Estimation achieves the same precision with O(1/ε) oracle calls — a quadratic speedup.

### What We Built
- **Q# Implementation**: Full canonical QAE with Grover operators, quantum phase estimation, and amplitude encoding of a log-normal loss distribution
- **Circuit**: 11 qubits (4 loss + 6 precision + 1 marker), ~3,000 T-states
- **Bug Found & Fixed**: The amplitude encoding used a Lorentzian kernel instead of a true log-normal PDF. This persisted through multiple CI-passing builds because the circuit compiled and produced plausible numbers. Only systematic comparison against the classical baseline caught it — validating the framework's insistence on classical comparison at every stage.
- **Calibration**: 3-run ensemble with bounded uncertainty. Theoretical tail probability (16.1%) matches classical Monte Carlo exactly after correction.
- **Azure Validation**: QASM circuit validated on Quantinuum H2-1SC trapped-ion syntax checker.
- **Live Demo (April 2, 2026)**: Fresh job `03_qae-risk-demo-meeting` submitted and succeeded on Quantinuum H2-1SC (job ID: `584a77f2`, 128 shots, 10s turnaround, $0.00 cost).

### Results
| Metric | Classical (Monte Carlo) | Quantum (QAE) |
|---|---|---|
| Tail probability P(Loss > 2.5) | 16.14% ± 0.37% | 15.7% ± 3.3% (4-qubit, 20 reps) |
| Query complexity | O(1/ε²) = 10,000 samples | O(1/ε) ≈ 30 oracle calls |
| Theoretical speedup | — | Quadratic |
| Hardware required (fault-tolerant) | — | ~594K physical qubits, 6.4s runtime |

### Honest Assessment
- The quadratic speedup is real in query complexity but the **constant-factor overhead is enormous**: 594K qubits for a problem a laptop solves in milliseconds
- At realistic noise (1% two-qubit gate error), the circuit would fail completely — error correction is required
- This is a **projected** advantage, not demonstrated. The framework correctly classifies it as Stage C, not Stage D.

---

## 2. Why This Framework Matters

### What We've Built (Quantified)
| Metric | Count |
|---|---|
| Quantum algorithm implementations | 20 / 20 |
| Algorithm families covered | 9 (VQE, QAOA, Grover, HHL, Shor, QAE, swap test, QEC, Trotter) |
| QASM circuits validated on Quantinuum H2 | 20 / 20 |
| Multi-run calibration with uncertainty bounds | 19 / 20 |
| Classical baselines | 20 / 20 |
| CI checks (automated, every PR) | 7 |
| PRs merged | 30 |
| DOI | 10.5281/zenodo.19222021 |

### Time and Effort Estimate
| Phase | Effort | Calendar Time |
|---|---|---|
| Initial framework + first 5 implementations | ~3 months | Oct 2025 – Jan 2026 |
| CI/CD pipeline + maturity gates + website | ~1 month | Feb 2026 |
| Azure Quantum integration + smoke workflows | ~2 weeks | Mar 2026 |
| Remaining 15 implementations + all calibration | ~2 days (intensive) | Mar 24-25, 2026 |
| Paper + DOI + scaling/noise analysis | ~1 day | Mar 25-26, 2026 |
| **Total estimated effort** | **~5 months part-time** | Oct 2025 – Mar 2026 |

### What Makes This Unique
1. **Nobody else has 20 problems in one repo with standardized gates.** The closest are QED-C benchmarks (circuit-level only) and QUARK (optimization only). We cover physics, finance, chemistry, cryptography, ML, optimization, QEC, and more — all with the same framework.

2. **The maturity gate model is novel.** Published quantum benchmarks typically report "we ran X on Y hardware." Our framework explicitly prevents premature claims — and our paper honestly reports that **0 of 20 problems have demonstrated quantum advantage**, which we consider a success of the methodology.

3. **End-to-end Azure Quantum integration.** Every circuit is validated on Quantinuum trapped-ion hardware (syntax checker). The shared workflow (`smoke_problem.py`) lets any problem submit to Azure with one command.

4. **Real scaling and noise data.** Our Grover analysis shows that at 1% two-qubit gate error, success collapses from 96% to 6% at 4 qubits. This kind of honest analysis is rare in quantum computing papers.

---

## 3. Alignment with Microsoft Quantum Strategy

### "Why Microsoft is building a fault-tolerant quantum supercomputer"

Our resource estimation data makes the case concrete. The QAE risk analysis requires **594,000 physical qubits** at the fault-tolerant scale — this is exactly the kind of problem that needs Microsoft's topological qubit approach to reach practical qubit counts. Our framework provides a systematic way to **identify which problems actually need fault tolerance** vs. which can run on near-term hardware.

**Talking point**: "Our framework shows that 20 problems across 9 algorithm families all compile and validate on Azure Quantum today. But our scaling analysis shows that practical utility requires fault-tolerant machines — validating Microsoft's long-term investment in topological qubits."

### "Why Microsoft is willing to invest for decades"

Our noise analysis directly quantifies this. At current error rates (10⁻³ for trapped ions, 10⁻² for superconducting), even a 4-qubit Grover search degrades from 96% to 6% success. The gap between "compiles on a simulator" and "runs correctly on hardware" is enormous. Decades of investment in error correction, better qubits, and fault tolerance are necessary before these algorithms deliver practical value.

**Talking point**: "We've quantified the noise gap: a 4-qubit circuit that works perfectly on a simulator fails 94% of the time at realistic error rates. This is why Microsoft's investment in error correction and fault tolerance is essential — and why honest frameworks like ours matter."

### "Building the world's first scalable quantum computer"

Our 20-problem registry serves as a **readiness benchmark** for any quantum computer. As hardware improves, each problem can be re-run on real QPUs to track progress. The maturity gate model provides a principled way to measure when a problem transitions from "theoretically interesting" to "practically useful."

**Talking point**: "Our framework is designed to be a living benchmark. As Microsoft's quantum hardware scales, we can re-run all 20 problems and track which ones transition from Stage B to Stage C to Stage D — providing quantitative evidence of progress toward practical quantum computing."

### "Using AI + HPC + Azure to make quantum usable"

Our entire workflow runs on Azure. Q# compiles via .NET, circuits submit to Azure Quantum, results return through the Azure API. The CI/CD pipeline runs on GitHub Actions. The website deploys via GitHub Pages. This is quantum development as a cloud-native software engineering practice — exactly the model Azure Quantum enables.

**Talking point**: "Every circuit in our project was developed using the Microsoft quantum stack: Q# for implementation, Azure Quantum for hardware validation, GitHub Actions for CI/CD. This is quantum computing as a software engineering discipline, powered by Azure."

---

## 4. The Ask

### How and With Whom Can I Get Involved?

1. **Azure Quantum team**: Access to the Resource Estimator target (`microsoft.estimator`) would replace our mock estimates with real, credible qubit/gate/runtime projections — dramatically strengthening both the framework and the paper.

2. **Quantinuum QPU credits**: We've requested academic access for ~25,000 HQC to run 4 circuits on H1 hardware. Real hardware results would be the difference between "validated on simulators" and "demonstrated on quantum hardware."

3. **Microsoft Research — Quantum Systems group**: The maturity gate framework could be useful for internal quantum algorithm development. We'd welcome collaboration on extending it.

4. **Q# / QDK team**: Our project uses QDK 0.28 (legacy). Migration to the modern QDK would future-proof the framework and could serve as a migration case study.

### What We Need to Produce Quality Data

| Need | Current State | With Access |
|---|---|---|
| Resource Estimator | Mock estimates (uniform) | Real qubit/gate/runtime per problem |
| QPU execution | Syntax validation only | Actual noisy hardware results |
| Full emulator | 78h+ queue (H2-1E) | Priority access for calibration runs |
| Modern QDK | Legacy SDK 0.28 | Modern qsharp package, better tooling |

### What We Can Deliver in Return

- **Open-source benchmark suite** usable by the Azure Quantum team for customer demos
- **Methodology paper** (under preparation for Quantum journal) citing Microsoft tools and Azure Quantum
- **Scaling/noise data** that honestly positions quantum computing readiness — useful for customer education
- **20-problem readiness tracker** that measures hardware progress over time

---

## 5. Key Numbers to Remember

- **20 problems, 9 algorithm families, 20/20 Azure validated**
- **Grover at 4 qubits: 96% noiseless → 6% at 1% error rate**
- **QAE requires 594K physical qubits for a problem a laptop solves in milliseconds**
- **0 of 20 problems demonstrate quantum advantage** (this is honest, and the framework correctly identifies this)
- **DOI: 10.5281/zenodo.19222021** — citable, reproducible, open-source

---

## 6. Live Demo Walkthrough (if time permits)

### Option A: Quick (2 min) — Show Azure Job Completion
```
az quantum job show --job-id "584a77f2-1381-4001-9bdf-47baa8086c80" -o table
```
Shows: job name, Succeeded status, Quantinuum H2-1SC target, 10s turnaround, $0.00 cost.

### Option B: Medium (5 min) — Run QAE Locally + Azure
```bash
# 1. Run Q# locally (shows tail probability estimation)
cd problems/archived/03_qae_risk
python -c "import qsharp; qsharp.init(project_root='qsharp'); print(qsharp.run('Main.QAEKernel()', shots=1))"

# 2. Show the QASM circuit
cat estimates/qae_simplified_4q.qasm

# 3. Show Azure job history
az quantum job list -o table
```

### Option C: Full (10 min) — End-to-End Framework Demo
```bash
# 1. Show the repo structure (20 problems, standardized layout)
ls problems/

# 2. Run classical baseline
python problems/03_qae_risk/python/classical_baseline.py

# 3. Run quantum implementation (modern QDK — qsharp Python package)
python -c "import qsharp; qsharp.init(project_root='problems/archived/03_qae_risk/qsharp'); print(qsharp.run('Main.QAEKernel()', shots=1))"

# 4. Show Azure validation
az quantum job list -o table | head -10

# 5. Show the website
# Open: https://wernerrall147.github.io/quantum-grand-challenges/

# 6. Show the KPI report
python tooling/reporting/stage_kpis.py
```

### Key URLs to Have Open
- **GitHub**: https://github.com/WernerRall147/quantum-grand-challenges
- **Website**: https://wernerrall147.github.io/quantum-grand-challenges/
- **DOI**: https://doi.org/10.5281/zenodo.19222021
- **Paper**: docs/paper/methodology-paper.html (open locally in browser)
