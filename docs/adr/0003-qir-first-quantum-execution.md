# ADR-0003: QIR-first quantum execution and evidence

Date: 2026-11-19  
Status: Proposed  
Deciders: Quantum Grand Challenges maintainers

## Context

The repository stores complete active and archived problem programs, but execution paths do not
share one problem resolver or one evidence contract. Readiness historically meant that directories
and estimate-like files existed. Some runners therefore ignored archived programs, while others
resolved them correctly.

Hardware kernels compile to QIR, but the public simulator matrix did not bind results to source and
QIR hashes. Azure job identifiers were kept separately from public evidence, but the successful
local and provider paths did not share a schema. The generated Azure Quantum workspace also
disabled access keys without assigning the Quantum data-plane roles that become mandatory for job
submission and result access on January 11, 2027.

The VQE driver was a separate consistency failure. It invoked a missing C# project, optimized a
classical surrogate, and compared a two-qubit toy measurement with a four-qubit Hubbard
reference. Local execution worked only by bypassing the current QDK/Python project model.

## Decision drivers

- Do not claim quantum advantage from compilation, simulation, emulation, or a toy problem.
- Distinguish local correctness, Base QIR, Adaptive_RI QIR, provider syntax, emulator, and
  physical-device evidence.
- Keep Q# hardware entry circuits fixed and result-producing so Python can aggregate expectations.
- Use managed identity or service-principal object IDs and least-privilege data-plane roles.
- Keep job identifiers and workspace details out of public website data.
- Bind every result to the Q# source, exact input QIR, target profile, SDK, shots, and source
  revision.
- Preserve the pinned QDK baseline while making the next compatibility run explicit.

## Options considered

### 1. Continue with problem-specific Python and Azure scripts

This is the least disruptive option and preserves each problem's current commands. It also keeps
several incompatible definitions of readiness, target discovery, and provenance. Archived path
handling has already diverged under this model, and a future provider or QDK update would require
repeating the same review in every script.

### 2. Add a shared resolver and QIR-first run contract

One resolver handles active and archived folders. Every execution produces one source-bound
record, while private manifests can additionally carry a job identifier. Hardware adapters return
measured `Result[]` values and are compiled with literal parameters under a declared target
profile. Python owns parameter selection, shot accounting, expectation aggregation, and evidence
promotion.

This adds small shared modules and an extra QIR compilation step, but removes path and evidence
drift while retaining local debugging and provider flexibility.

### 3. Use provider SDK submission results as the source of truth

This option minimizes local tooling by treating provider job metadata as the run record. Provider
responses are not portable across IonQ, Quantinuum, and Rigetti, and the approach does not bind a
result to the repository source or enforce local correctness before submission. It also risks
publishing provider-specific identifiers into the website.

## Decision

Adopt option 2.

- `tooling/discover_problems.py` is the canonical active-or-archived resolver.
- Readiness reports independent artifact, local-correctness, target-profile, provider, and hardware
  states. QIR compilation alone is labeled compatibility, not scientific readiness.
- Base is the default compatibility goal when the circuit does not use measurement-dependent
  branching. Adaptive_RI is explicit for the circuits that require it.
- Quantum hardware adapters are fixed measurement programs that return `Result[]`. Variational
  Python loops submit or run one fixed term circuit at a time and aggregate expectations.
- The simulator matrix uses schema version 2.0 and binds records to source and QIR hashes.
- Private Azure manifests and `.azure/` provenance may contain job identifiers. Published website
  records cannot.
- The generated Quantum workspace requires at least one Entra object ID with the Quantum Workspace
  Data Contributor role and accepts separate read-only principals.

## Consequences

### Positive

- Active and archived problems use the same execution and reporting paths.
- Provider syntax checks, emulators, and physical devices can no longer be mistaken for the same
  evidence class.
- A failed or unexpectedly optimized circuit can be reproduced from source and QIR hashes.
- The VQE optimization route uses Q# measurement results and exposes its toy-Hamiltonian limit.
- Generated workspaces fail deployment input validation before a submitting identity can be
  omitted.

### Trade-offs

- Quantum Bicep deployments now require a contributor principal object ID.
- Run setup performs extra hashing and QIR compilation work.
- The provenance layer depends on Git metadata, so non-Git exports must supply an equivalent build
  revision before they submit jobs.
- Phase-sensitive or topology-changing optimization remains blocked until exact state-vector or
  unitary checks cover the candidate.

### Follow-up

- Promote the problem registry and instance contracts into one generated source of truth.
- Extract shared Q# QFT, QPE, HHL, and QAOA primitives after exact equivalence tests.
- Add target-specific noise models and provider normalization without changing the public record
  shape.
- Add a separate QDK-latest compatibility lane after the pinned baseline remains green.

## How we will know

The decision is working when these commands remain green:

```text
python -m pytest tooling/test_quantum_readiness.py -q
python -m pytest tooling/test_hardware_kernels_compile.py -q
python -m pytest tooling/test_vqe_optimizer.py -q
python -m pytest tooling/test_quantum_provenance.py -q
python tooling/azure/assess_problem_readiness.py
python tooling/ci_validate_qsharp.py
python -m pytest agents/tests/test_bicep_generator.py -q
python tooling/reporting/validate_website_data_schema.py
```

## Links

- [Quantum hardware readiness roadmap](../initiatives/quantum-hardware-readiness.md)
- [Azure Quantum workspace data roles](https://learn.microsoft.com/azure/quantum/how-to-create-workspace#assign-data-access-roles-for-users-in-the-workspace)
- [Azure Quantum sessions](https://learn.microsoft.com/azure/quantum/how-to-work-with-sessions)
- [QDK simulator noise models](https://learn.microsoft.com/azure/quantum/qdk-simulator-noise-models)
