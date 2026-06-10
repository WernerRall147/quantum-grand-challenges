# Stage D Advantage Evidence Package - 10_post_quantum_cryptography

## Scope And Claim Boundary

- Problem: Symmetric key search using Grover's algorithm (finding k such that E(k, plaintext) = ciphertext).
- Current claim category: `projected`.
- Claim boundary: Asymptotic query scaling (Grover O(√N) vs classical brute-force O(N)).
- Non-claim boundary: No demonstrated backend wall-clock advantage is claimed. Quadratic speedup only halves effective key length.

## Baseline Fairness Review

- Classical comparator is explicit in `python/classical_baseline.py` and persisted in `estimates/classical_baseline.json`.
- Brute-force is optimal for unstructured key search (no exploitable structure in properly designed ciphers).
- Fairness status: pass for query-complexity objective; Grover quadratic speedup is already factored into NIST post-quantum key length recommendations.

## Uncertainty Methodology

- Cross-platform emulator validation: H2-1E 80%, Rigetti QVM 83% success rate (100 shots each).
- 20-run calibration ensemble with bounded confidence intervals.
- Noise resilience: 84.1% fidelity at p=0.05 depolarizing noise (3-qubit circuit, 1 Grover iteration).

## Sensitivity And Risk Analysis

- Oracle-synthesis sensitivity:
  - Real AES/SHA oracle implementation may require millions of T-gates, dramatically increasing resource requirements.
- Key length scaling:
  - Quadratic speedup doubles effective key length; NIST already recommends AES-256 (vs AES-128) to counter Grover.
- Backend sensitivity:
  - Current evidence is emulator-centric; hardware noise and transpilation effects not yet quantified for production key sizes.

## Backend And Deployment Assumptions

- Azure execution validated on Quantinuum H2-1E and Rigetti QVM emulators.
- Resource estimate: 32,536 physical qubits for 3-qubit toy instance.
- Practical AES-128 key search would require O(thousands of logical qubits) and ~2^64 Grover iterations.

## Residual Limitations

- Quadratic speedup only  does not break modern cryptography, only doubles effective key length.
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
