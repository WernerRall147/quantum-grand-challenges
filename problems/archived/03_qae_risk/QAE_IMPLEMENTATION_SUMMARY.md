# Quantum Amplitude Estimation (QAE) Implementation Summary

## Overview

This problem estimates the tail probability P(Loss > threshold) of a discretized log-normal loss distribution with two amplitude-estimation algorithms: canonical QAE (Brassard, Høyer, Mosca and Tapp 2002), which runs phase estimation on the Grover iterate, and iterative QAE (Grinko, Gacon, Zoufal and Woerner 2021), which needs no phase register. Both reach additive error ε with O(1/ε) applications of the state-preparation circuit, where Monte Carlo needs O(1/ε²) samples. That speedup is quadratic, and no quantum algorithm needs fewer queries (Nayak and Wu 1999); it does not include the cost of loading the distribution or of error correction, and the problem is archived because those costs outweigh it.

A correction on 2026-09-27 fixed the canonical kernel's Grover iterate and replaced the IQAE driver; see the problem README. Results reported before that date came from the faulty kernel.

## Test Case

- **Loss distribution**: log-normal(μ = 0, σ = 1), evaluated at the 16 points (i + 1)·10/16 and normalized (`Main.LogNormalProbabilities`).
- **Threshold**: 2.5. The circuit encodes the discrete tail probability **a = 0.1614** of that grid; the continuous log-normal tail it approximates is 0.1798.
- **Canonical QAE**: 4 loss qubits, 6 phase qubits, 1 marker (11 qubits); 120 repetitions in the demo.
- **IQAE**: 4 loss qubits and 1 marker (5 qubits).

## Circuit

1. **State preparation** `PrepareDistributionState`: a tree of multiplexed Ry rotations prepares A|0⟩ = Σᵢ √pᵢ |i⟩ (circuit size O(2ⁿ) for n loss qubits).
2. **Oracle** `OracleTailMarking`: flips the marker for every basis state above the threshold. With the marker in |−⟩ this is the phase flip S_χ on the loss register.
3. **Reflection** `ReflectAboutState`: A S_0 A†, with S_0 = I − 2|0⟩⟨0|, applying A† first and A last.
4. **Grover iterate** `GroverOperator`: Q = −A S_0 A† S_χ. On the span of A|0⟩ its eigenvalues are e^{±2iθ} with sin²θ = a. The −1 is a global phase for Q alone and a relative phase once Q is controlled, so it matters for phase estimation.
5. **Phase estimation** `QuantumPhaseEstimationQAE`: phase qubit j controls Q^(2^(m−1−j)), then an inverse QFT. Outcome y estimates a as sin²(πy/2^m).

## Verified Behaviour (`tooling/test_qae_kernel.py`)

- The phase register's distribution equals Theorem 11 of Brassard et al., applied to the eigenphases ±θ/π, to 10⁻⁹ (from the simulator's state vector), for two configurations. With 6 phase bits it peaks at 8 and 56 of 64 with probability 0.27 each; outcome 8 decodes to 0.1464, within the 0.0385 bound of their Theorem 12.
- `Main.QAEKernel()`, the estimator and calibration entry point, reads the register most significant bit first.
- The 2-bit hardware kernel samples Theorem 11's distribution. At that resolution it cannot estimate a: its likeliest outcomes decode to 0.5 for a = 0.232.
- `IQAERound` measures sin²((2k+1)θ) for k = 1 and 3.
- The IQAE driver's intervals contain a in at least 95% of repeated runs, and its query count grows as 1/ε.

The only earlier test prepared a uniform superposition with H at a = 1/2. H is its own inverse and the eigenphases for a = 1/2 are symmetric under the sign error, so that test could not see either fault in the old kernel, whose register peaked at 0 and 32.

## IQAE Driver (`python/iqae_driver.py`)

Algorithm 1 of Grinko et al.: FindNextK chooses the largest Grover power whose scaled interval stays within one half-circle, the measured frequency is bounded with a Clopper-Pearson interval at level α/T (T bounds the number of rounds), and rounds that reuse a power are pooled. The driver compares IQAE against plain Monte Carlo on the same 16-level distribution at equal interval half-width, counting applications of A or its inverse on both sides. A run on 2026-09-27 (ε = 0.05, α = 0.05) returned [0.152, 0.191] from 600 queries, where Monte Carlo needs 1,373 samples for the same half-width; with an exact sampler, IQAE needs 42,715 queries at half-width 0.0004 where Monte Carlo needs 3.2 million samples. These are noiseless query counts, not run times.

## Resources

The current resource estimate is in the problem README and `circuits/estimate.json`. Its cost is driven by rotations, because arbitrary-angle rotations are synthesized from T states. The older figures below came from the retired `qsharp.estimate` API and describe an earlier configuration; they are kept for the record only.

| Architecture (legacy) | Physical qubits | Runtime | T states |
|---|---:|---:|---:|
| gate_ns_e3 | 594k | 6.4 s | 965k |
| gate_ns_e4 | 561k | 6.7 s | 965k |
| maj_ns_e4 (Majorana profile) | 400k | 28.5 s | 965k |

## Limitations

- State preparation costs O(2ⁿ) gates for n loss qubits, and loading real portfolio distributions is the main obstacle to any advantage.
- The loss model is synthetic and the tail probability is discretization-dependent (0.1614 on 16 levels against 0.1798 for the continuous model).
- `python/analyze.py` still calls the retired `dotnet` toolchain, so the ensembles it produced cannot be regenerated until it is ported; they predate the correction.
- Babbush et al. (PRX Quantum 2, 010103, 2021) conclude that quadratic speedups will not give an advantage on early fault-tolerant machines without a significant improvement in error correction.

## References

1. G. Brassard, P. Høyer, M. Mosca, A. Tapp, "Quantum Amplitude Amplification and Estimation", Contemporary Mathematics 305 (2002), [arXiv:quant-ph/0005055](https://arxiv.org/abs/quant-ph/0005055).
2. D. Grinko, J. Gacon, C. Zoufal, S. Woerner, "Iterative quantum amplitude estimation", npj Quantum Information 7, 52 (2021), [arXiv:1912.05559](https://arxiv.org/abs/1912.05559).
3. S. Woerner, D. J. Egger, "Quantum risk analysis", npj Quantum Information 5, 15 (2019), [arXiv:1806.06893](https://arxiv.org/abs/1806.06893).
4. N. Stamatopoulos et al., "Option Pricing using Quantum Computers", Quantum 4, 291 (2020), [arXiv:1905.02666](https://arxiv.org/abs/1905.02666).
5. A. Nayak, F. Wu, "The quantum query complexity of approximating the median and related statistics", STOC 1999, [arXiv:quant-ph/9804066](https://arxiv.org/abs/quant-ph/9804066).
6. R. Babbush et al., "Focus beyond quadratic speedups for error-corrected quantum advantage", PRX Quantum 2, 010103 (2021), [arXiv:2011.04149](https://arxiv.org/abs/2011.04149).
