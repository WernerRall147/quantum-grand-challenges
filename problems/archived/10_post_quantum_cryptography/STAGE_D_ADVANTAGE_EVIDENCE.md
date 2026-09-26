# Stage D Advantage Evidence Package - 10_post_quantum_cryptography

## Scope And Claim Boundary

- Problem: Symmetric key search using Grover's algorithm (finding k such that E(k, plaintext) = ciphertext).
- Current claim category: `projected`.
- Claim boundary: Asymptotic query scaling (Grover O(√N) vs classical brute-force O(N)).
- Non-claim boundary: No demonstrated backend wall-clock advantage is claimed. Quadratic speedup only halves effective key length.

## Baseline Fairness Review

- Classical comparator is explicit in `python/classical_baseline.py` and persisted in `estimates/classical_baseline.json`.
- Brute-force is optimal for unstructured key search (no exploitable structure in properly designed ciphers).
- Fairness status: pass for query-complexity objective; Grover's quadratic speedup is already accounted for in NIST's post-quantum security categories, which are defined by the cost of AES key search.

## Uncertainty Methodology

- Cross-platform emulator validation: H2-1E 80%, Rigetti QVM 83% success rate (100 shots each).
- 20-run calibration ensemble with bounded confidence intervals.
- Noise resilience: 84.1% fidelity at p=0.05 depolarizing noise (3-qubit circuit, 1 Grover iteration).

## Sensitivity And Risk Analysis

- Oracle-synthesis sensitivity:
  - Real AES/SHA oracle implementation may require millions of T-gates, dramatically increasing resource requirements.
- Key length scaling:
  - Grover halves the effective key length, but NIST expects it to give little or no advantage against AES, because its iterations must run in series, and considers AES-128 secure for decades to come (NIST PQC FAQ).
- Backend sensitivity:
  - Current evidence is emulator-centric; hardware noise and transpilation effects not yet quantified for production key sizes.

## Backend And Deployment Assumptions

- Azure execution validated on Quantinuum H2-1E and Rigetti QVM emulators.
- Resource estimate: 32,536 physical qubits for 3-qubit toy instance.
- Practical AES-128 key search would require 2,953 logical qubits and about 2^86 T gates over ~2^64 Grover iterations (Grassl et al., arXiv:1512.04965).

## Residual Limitations

- Quadratic speedup only: it halves the effective key length and does not break modern cryptography.
- Oracle implementation cost for real ciphers is prohibitive with current technology.
- The practical threat to cryptography comes from Shor's algorithm (factoring), not Grover (search).

## Current Generated Stage D Artifacts

- `estimates/advantage_claim_contract.json`
- `estimates/scaling_analysis_stage_d.json`
- `estimates/stage_d_evidence_summary.json`
- `estimates/resource_estimate.json`
- `estimates/calibration_ensemble.json`

## Promotion Checklist To `demonstrated`

- [x] File advantage claim contract with explicit category and residual risks.
- [x] Generate scaling analysis with honest crossover estimates.
- [x] Cross-platform emulator validation (H2-1E + Rigetti QVM).
- [x] 20-run calibration ensemble with bounded uncertainty.
- [ ] Demonstrate on real quantum hardware (H1 QPU) with shot-based confidence intervals.
- [ ] Integrate realistic AES oracle cost into end-to-end resource analysis.
- [ ] Compare against quantum-resistant alternatives (lattice-based, hash-based cryptography).
