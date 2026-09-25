# ARCHIVED  Post-Quantum Cryptography

**Status**: Archived (April 2026)

## Archival Reason

Quadratic O(√N) Grover speedup is provably optimal but only halves effective key length. The AES oracle needs millions of T gates per Grover iteration, about 2^86 T gates in total for AES-128 (Grassl et al., arXiv:1512.04965), dominating total cost. NIST expects Grover to give little or no advantage against AES, because its iterations must run in series, and considers AES-128 secure for decades to come (NIST PQC FAQ).

> Code in this directory remains for **pedagogical reference**.

## Reference

Analysis follows Dr. Matthias Troyer’s “Building the Modern Quantum Architecture” framework (2025–2026).
