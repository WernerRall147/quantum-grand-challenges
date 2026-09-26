# ARCHIVED  Quantum Machine Learning

**Status**: Archived (April 2026)

## Archival Reason

No speedup exists for this kernel: loading d classical features into quantum states costs O(d) gates, the same order as computing the kernel classically, and each kernel entry needs O(1/ε²) shots. Proven advantages exist only for contrived problem structures (Liu, Arunachalam and Temme, Nat. Phys. 17, 1013, 2021).

> Code in this directory remains for **pedagogical reference**.

## Reference

Analysis follows Dr. Matthias Troyer’s “Building the Modern Quantum Architecture” framework (2025–2026).
