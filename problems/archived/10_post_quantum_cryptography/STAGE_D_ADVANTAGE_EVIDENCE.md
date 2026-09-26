# Stage D Advantage Evidence Package - 10_post_quantum_cryptography

## Scope And Claim Boundary

- Problem: Symmetric key search using Grover's algorithm (finding k such that E(k, plaintext) = ciphertext).
- Current claim category: `projected`.
- Claim boundary: Asymptotic query scaling (Grover O(√N) vs classical brute-force O(N)).
- Non-claim boundary: No demonstrated backend wall-clock advantage is claimed. Quadratic speedup only halves effective key length.

## Baseline Fairness Review

- The Grover kernel's comparator is classical exhaustive key search. For one marked key among N = 8, it needs (N + 1)/2 = 4.5 oracle queries on average and 8 in the worst case; one Grover iteration finds the key with probability 0.78125 (checked against exact simulation).
- Brute force is optimal for unstructured key search (no exploitable structure in properly designed ciphers).
- `python/classical_baseline.py` answers a different question: a toy cost formula for BKZ lattice attacks on lattice-based schemes (its quadratic cost in the block size and its Grover adjustment are illustrative, not the core-SVP estimates of the lattice estimator). It is not the comparator for the key-search kernel.
- Fairness status: pass for the query-complexity objective; Grover's quadratic speedup is already accounted for in NIST's post-quantum security categories, which are defined by the cost of AES key search.

## Uncertainty Methodology

- Cross-platform emulator validation: H2-1E 80%, Rigetti QVM 83% success rate (100 shots each).
- 20-run calibration ensemble with bounded confidence intervals.
- Noise resilience: classical fidelity 0.71 between noisy and ideal 100-shot histograms at p = 0.05 depolarizing noise (3-qubit circuit, 1 Grover iteration; local simulation regenerated 2026-09-26, shot-noise limited).

## Sensitivity And Risk Analysis

- Oracle-synthesis sensitivity:
  - Real AES/SHA oracle implementation may require millions of T-gates, dramatically increasing resource requirements.
- Key length scaling:
  - Grover halves the effective key length, but NIST expects it to give little or no advantage against AES, because its iterations must run in series, and considers AES-128 secure for decades to come (NIST PQC FAQ).
- Backend sensitivity:
  - Current evidence is emulator-centric; hardware noise and transpilation effects not yet quantified for production key sizes.

## Backend And Deployment Assumptions

- Azure execution validated on Quantinuum H2-1E and Rigetti QVM emulators.
- Resource estimate: 26,092 physical qubits and 12 logical qubits for the 3-qubit toy instance (`circuits/estimate.json`, `Main.GroverKeySearch(3, 5, 1)`).
- Practical AES-128 key search would require 2,953 logical qubits and about 2^86 T gates over ~2^64 Grover iterations (Grassl et al., arXiv:1512.04965).

## Residual Limitations

- Quadratic speedup only: it halves the effective key length and does not break modern cryptography.
- Oracle implementation cost for real ciphers is prohibitive with current technology.
- The practical threat to cryptography comes from Shor's algorithm (factoring), not Grover (search).

## Current Generated Stage D Artifacts

- `estimates/advantage_claim_contract.json`
- `estimates/scaling_analysis_stage_d.json`
- `estimates/stage_d_evidence_summary.json`
- `circuits/estimate.json`
- `estimates/quantum_calibration_ensemble.json`

## Promotion Checklist To `demonstrated`

- [x] File advantage claim contract with explicit category and residual risks.
- [x] Generate scaling analysis with honest crossover estimates.
- [x] Cross-platform emulator validation (H2-1E + Rigetti QVM).
- [x] 20-run calibration ensemble with bounded uncertainty.
- [ ] Demonstrate on real quantum hardware (H1 QPU) with shot-based confidence intervals.
- [ ] Integrate realistic AES oracle cost into end-to-end resource analysis.
- [ ] Compare against quantum-resistant alternatives (lattice-based, hash-based cryptography).
