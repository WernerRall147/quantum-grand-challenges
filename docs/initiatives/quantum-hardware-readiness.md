# Quantum hardware readiness and optimization roadmap

Audit date: 2026-11-18 <!-- historical -->

## Scope

This roadmap separates correctness and portability fixes from optional optimization work. It
reviews the problem programs, Python orchestration, QIR compilation, resource estimation, Azure
Quantum submission, emulation, and durable evidence in the repository.

It does not establish quantum advantage. No problem in this repository demonstrates quantum
advantage on available hardware. Compiling or running a toy kernel is compatibility evidence, not
scientific or commercial advantage.

## Executive conclusion

The repository stores each problem's Q# source, classical code, instances, baseline, hardware
kernel, circuit, and estimate. Optimization is only partially organized:

- Exact and statistical kernel tests, resource estimates, noisy simulation, and a reversible-kernel
  optimizer already exist.
- The normal verification paths do not all discover both active and archived problem directories.
- The readiness reports test the presence of files more often than the behavior of the programs.
- The published hardware evidence is not tied to a portable chain of source hash, QIR hash,
  target, shots, SDK version, job identifier, and result.
- The resource estimate expression and the submitted hardware-kernel expression are intentionally
  different and must remain visibly distinct.
- Q# compilation against a target profile proves that QIR is accepted, but not that a provider
  emulator or physical device produced a useful result.

## Implemented foundation

The implementation associated with this roadmap now provides:

- Quantum data-plane role assignments in the generated Bicep reference, with a required
  contributor principal and optional read-only principals.
- One active-or-archived problem resolver used by readiness, manifests, smoke orchestration,
  simulator discovery, and one-kernel submission.
- Readiness output that separates artifact, Base QIR, Adaptive_RI QIR, local, provider, emulator,
  and hardware states.
- A Base and Adaptive_RI compile matrix guarded in CI.
- A QDK-native VQE driver with fixed Pauli-term QIR programs and explicit toy-Hamiltonian labels.
- Source, input/QIR, target-profile, SDK, and worktree provenance for simulator and private
  submission records.
- [ADR 0003](../adr/0003-qir-first-quantum-execution.md), which fixes the QIR-first architecture
  and evidence promotion rules.

Shared Q# libraries, a generated instance schema, target-specific noise models, and multi-policy QRE
selection remain follow-up implementation work rather than implied completed capabilities.

## P0: correctness and access

### Assign Azure Quantum data-plane roles

Microsoft Learn states that, beginning January 11, 2027, users need **Quantum Workspace Data
Reader** to view job results and **Quantum Workspace Data Contributor** to submit jobs.

The generated workspace template currently creates the workspace and system identity, disables API
keys, and emits no Quantum data-plane role assignments. See
[`bicep_generator.py`](../../agents/code_generator/bicep_generator.py).

Required work:

1. Add explicit role-assignment parameters for the identities that submit and read jobs.
2. Assign Contributor to the submitting identity and Reader to read-only consumers.
3. Add a deployment preflight that resolves the workspace scope and expected role definitions.
4. Document the role requirement in the Quantum deployment runbook.
5. Verify real assignment and access, not only Bicep syntax.

Source: [Create an Azure Quantum
workspace](https://learn.microsoft.com/azure/quantum/how-to-create-workspace#assign-data-access-roles-for-users-in-the-workspace).

### Replace shape-based readiness with behavior-based evidence

[`assess_problem_readiness.py`](../../tooling/azure/assess_problem_readiness.py) currently looks
only under `problems/<id>`. Archived IDs remain in the report, but their directory, evidence, and
readiness fields are false because the assessor never resolves `problems/archived/<id>`. It also
calls a problem ready when its directories and an estimate-like evidence file are present.

Replace the single `shared_workflow_ready` flag with independent states:

| State | Required evidence |
|---|---|
| Local correctness | A simulator result checked against an independent reference |
| Base QIR | Successful Base-profile QIR compilation, where supported |
| Adaptive QIR | Successful Adaptive_RI compilation, where required |
| Syntax target | Provider syntax checker accepts the exact submitted QIR |
| Emulator | Provider emulator result is captured and compared with the local reference |
| Hardware | Physical-device job metadata and raw result are captured |

Each state must be earned separately. A syntax checker, local simulator, provider emulator, and
physical device are not interchangeable evidence.

### Fix problem discovery in one place

[`discover_problems.py`](../../tooling/discover_problems.py) already resolves active and archived
problems. Runners that still implement their own `problems/<id>` search should consume that helper
or a shared resolver:

- [`run_simulator_matrix.py`](../../tooling/run_simulator_matrix.py)
- [`prepare_problem_manifest.py`](../../tooling/azure/prepare_problem_manifest.py)
- [`assess_problem_readiness.py`](../../tooling/azure/assess_problem_readiness.py)
- [`submit_hardware_kernels.py`](../../tooling/submit_hardware_kernels.py)
- Legacy collection and smoke-report paths

This is a correctness fix, because current reports can understate the repository's runnable
inventory.

## P1: one portable problem and execution contract

Four surfaces currently repeat related problem information: the reference index, Azure registry,
estimator configuration, and estimator entry-point table. Instance files also use multiple
structures. The result is duplicated metadata and divergent path resolution.

Add one schema-validated problem contract with these fields:

- Stable problem ID, title, status, and canonical directory.
- Instance files and instance schema.
- Classical baseline entry point and output contract.
- Q# project and Main entry expression.
- Hardware-kernel project and entry expression.
- Supported target profiles and required provider features.
- Result measurements, expected-value rules, and post-selection handling.
- Resource-estimation expression and physical models.
- Evidence and artifact paths.

Generate the reference index, website inventory, Azure manifest inputs, and estimator entry-point
registry from this contract. Hand-maintained mirrors should either become generated artifacts or
be removed after their consumers migrate.

Add a second, repository-wide execution manifest for a single run. It should capture:

- Problem and instance IDs.
- Source revision and source-file hashes.
- QDK and dependency versions.
- Python entry point and Q# entry point.
- Target profile, target ID, input format, and execution mode.
- Noise or emulator model.
- Shot count and random seeds.
- QIR hash and compilation options.
- Job identifier in private or gitignored provenance.
- Sanitized public result and public evidence classification.

The existing [QAOA manifest schema](../../tooling/schema/qaoa_azure_job_manifest.json) is a useful
seed but must no longer be problem-family specific.

## P1: QIR and target-profile architecture

Hardware entry points should return measured `Result[]` values. A reusable quantum core can retain
typed quantum state internally, while its hardware adapter allocates, measures, and returns bits.
This pattern keeps the algorithm testable and the submitted program interoperable with provider
formats.

The audit observed that every registered hardware kernel compiled under Adaptive_RI and that all
but the adaptive error-correction kernel also compiled under Base. Those are historical
observations from 2026-11-18 <!-- historical -->, not a permanent target guarantee.

Recommended profile rules:

- **Base** for non-adaptive circuits when the provider target supports the Base profile.
- **Adaptive_RI** only when mid-circuit measurement, Result-based branching, or resets are
  required.
- Separate Base and Adaptive versions for diagnostics, correction, and workflows that can trade
  dynamic control for a static circuit.
- Compile the exact submitted QIR before every provider run.
- Treat a profile declaration as a minimum capability, not a performance promise.

The HardwareKernel files currently sit outside the normal Q# `src` project directory and are
evaluated explicitly by Python. Q# projects normally include `.qs` files below `src`, so a
hardware-specific subproject should become the normal project entry point. Moving the protected
HardwareKernel files requires explicit human approval and an update to every consumer.

Sources:

- [Submit QIR, OpenQASM, and Pulser circuits to Azure
  Quantum](https://learn.microsoft.com/azure/quantum/quickstart-microsoft-provider-format)
- [Run integrated hybrid quantum jobs with
  Adaptive RI](https://learn.microsoft.com/azure/quantum/hybrid-computing-integrated)

## P1: shared Q# primitives with correctness-preserving tests

[`libs/common/src/Utils.qs`](../../libs/common/src/Utils.qs) already contains reusable QFT, Grover,
reflection, and amplitude-amplification helpers, but problem projects do not import it. Promote
that directory into an explicit Q# library dependency and extract code in this order:

1. Common QFT and controlled-QFT kernels.
2. Phase-estimation and Trotter helper patterns.
3. HHL-style rotations and eigenphase blocks.
4. Amplitude-amplification and reflection helpers.
5. Repeated QAOA cost and mixer layers.

For every extraction, preserve the source-specific operation and add an exact or independently
constructed reference test. The [qsharp-kernel skill](../../.github/skills/qsharp-kernel/SKILL.md)
describes the repository's required failure and verification process.

The reversible optimization evaluator in
[`tooling/kernel_opt/evaluate.py`](../../tooling/kernel_opt/evaluate.py) is a good bounded
foundation. Keep it bounded to transformations that its certificate can prove. Do not allow
optimizer candidates to modify phase-sensitive QPE, VQE, QAOA, or HHL kernels without a
state-vector or unitary equivalence check. A truthful optimization certificate is more important
than a lower gate count.

## P1: Python modernization and algorithm orchestration

### Replace the stale VQE driver

[`problems/01_hubbard/python/vqe_optimizer.py`](../../problems/01_hubbard/python/vqe_optimizer.py)
references a missing C# project, invokes .NET, optimizes a classical surrogate, and evaluates Q#
only after optimization. This conflicts with the repository's Python/QDK toolchain.

Replace it with:

1. A pure Hamiltonian-term representation.
2. A Q# ansatz parameterized by measurement circuits for each required observable.
3. A shot-budgeted expectation estimator in Python.
4. A classical optimizer that consumes real local or remote expectation values.
5. A separate benchmark for the classical surrogate, never as a hidden replacement for quantum
   evaluation.
6. Azure sessions for repeated objective calls where sessions are available.

### Standardize variational workflows

QAOA and VQE should keep classical parameter selection in Python. The Q# program should compile a
concrete parameterized circuit or problem instance per objective evaluation. Share the Python
plumbing for submission, result normalization, confidence intervals, shot allocation, retries, and
reporting.

Azure Quantum sessions are appropriate for repeated VQE and QAOA submissions. Add explicit session
lifecycle handling and never use sessions as a reason to omit per-job provenance.

Source: [Manage Azure Quantum sessions and avoid
timeouts](https://learn.microsoft.com/azure/quantum/how-to-work-with-sessions).

## P1: emulator and noisy-simulation evidence

[`run_noisy_simulation.py`](../../tooling/run_noisy_simulation.py) currently reinitializes the Q#
global interpreter and applies one generic depolarizing sweep to every problem. It has no provider
topology, statistical interval, or target-specific model.

Recommended ladder:

1. Exact state-vector or independently checked unit test.
2. Ideal sparse simulation with deterministic unit inputs.
3. Model-specific noise simulation.
4. Provider emulator with the provider's semantics documented.
5. Physical-device result with cost, calibration, and failure metadata.

Use QDK Python noise APIs for target-like one- and two-qubit models. Add confidence intervals for
sampled outcomes, source and result hashes, shot counts, and a documented normalization policy.
Quantinuum syntax-check targets can validate the provider compiler but intentionally return all-zero
results, so they must never populate physics-performance charts. IonQ simulator output and native
provider quota and shot accounting must be normalized at the adapter boundary.

Sources:

- [Build and configure QDK simulator noise
  models](https://learn.microsoft.com/azure/quantum/qdk-simulator-noise-models)
- [Test and debug quantum programs with QDK
  tools](https://learn.microsoft.com/azure/quantum/testing-debugging)

## P1: resource estimation policy

[`generate_estimates.py`](../../tooling/generate_estimates.py) is the canonical estimate generator
and already uses the QDK QRE APIs. Preserve its `entryExpr` and `hardwareKernelEntryPoint` distinction:
they estimate different programs.

Improvements:

- Estimate the Main program and the exact hardware-kernel program separately.
- Keep the full Pareto frontier as first-class data.
- Support explicit selection policies: minimum physical qubits, minimum runtime, deadline, qubit
  budget, or target error budget.
- Label which point is published and why.
- Retire or redirect old estimator and Makefile paths instead of maintaining mock defaults.
- Use the same problem contract for circuits, estimates, and hardware runs.

Source: [Create application models from quantum frameworks for resource
estimation](https://learn.microsoft.com/azure/quantum/qre-supported-applications).

## P2: algorithm-specific optimization backlog

### QPE and Trotterized chemistry

- Move repeated QPE, phase rotation, and Trotter helpers into the shared Q# library.
- Add exact unitary tests at the smallest nontrivial Hamiltonians.
- Add iterative phase estimation variants where the trade of classical control for fewer
  concurrent estimation qubits is useful.
- Track logical T count, qubits, depth, and post-measurement interpretation separately.
- Never infer chemistry or materials utility from the toy kernel alone.

### HHL and linear systems

- Deduplicate the linear-solver and climate HHL circuits.
- Preserve the conditioned success rate and post-selection probability.
- Add Base-compatible variants and larger matrix families only when a classical reference is
  available.
- Measure oracle preparation and state-extraction costs, not only the internal HHL block.

### QAE

- Add iterative QAE as a hardware-oriented alternative where it reduces qubits or depth.
- Track confidence intervals and decision thresholds with the reported shot count.
- Avoid describing a sampled risk estimate as exact.

### QAOA and QML

- Cache and reuse classical graph encodings and compiled circuit structure where QDK supports it.
- Allocate shots using uncertainty and optimizer progress.
- Add target-topology and gate-native cost data only after exact circuit equivalence is proven.
- Keep the classical optimizer, data encoding, and measurement aggregation outside Q#.

### Reversible arithmetic, Grover, and factorization

- Continue using exhaustive basis-state verification for small registers.
- Keep seed-drawn guarantees explicitly limited to the stated reversible-permutation class.
- Add phase-sensitive certificates before extending transformations to other kernels.
- Optimize and report oracle cost, not just the surrounding Grover or Shor wrapper.
- Keep all current small-number examples classified as demonstrations, not scalable evidence.

### Error correction and adaptive control

- Preserve error-correction kernels as Adaptive_RI-only when Result-based branching is required.
- Add an independent Base-profile diagnostic circuit for syndrome generation and measurement.
- Report raw syndromes, correction branches, and post-processing separately.

## P2: future provider and QDK compatibility

Add a compatibility lane that is explicitly separate from the pinned production toolchain:

- Keep QDK 1.31.0 as the release baseline until the repository intentionally upgrades it.
- Run a scheduled QDK-latest compatibility job without automatically changing project files.
- Recompile every hardware kernel under each declared profile when the QDK or target catalog changes.
- Store the target catalog's profile, input format, quota model, and result normalization rules in a
  versioned file.
- Keep analog pulse targets, such as neutral-atom Pulser inputs, separate from gate-model QIR
  workflows. Accepting them requires new per-problem programs, not a target-name substitution.
- Promote an algorithm through local, syntax, emulator, and hardware stages independently.

## Recommended implementation sequence

1. Add Quantum data-plane role assignments and an access preflight.
2. Fix active and archived problem discovery in readiness and simulator paths.
3. Introduce behavior-based readiness states. The archived-path regression must assert the resolved
   directory, evidence, and readiness values, not only the presence of each problem ID in the
   report.
4. Add the problem and execution contracts and derive the duplicated registries.
5. Replace the stale VQE driver with a QDK-native, shot-budgeted objective.
6. Wire `libs/common` into a pilot Q# project and move one duplicated primitive after exact tests.
7. Add target-specific noise and normalized emulator evidence.
8. Expand QRE selection from minimum-qubit-only to explicit policies.
9. Add provider-emulator promotion and an intentionally separate physical-device lane.
10. Add a latest-QDK compatibility workflow after the pinned baseline remains green.

## Definition of done

The roadmap is complete when:

- Every registered problem resolves through the same active-or-archived resolver.
- Readiness distinguishes compilation, correctness, emulator, and hardware evidence.
- Exact QIR for the hardware entry point is compiled and hashed for every submitted run.
- Source, target, profile, shots, SDK, noise model, and result provenance can be reconstructed.
- The generated infrastructure assigns the required Quantum data-plane roles.
- Q# project imports and tests cover every shared primitive.
- Python orchestration has no .NET dependency and no surrogate-only VQE path.
- Published claims identify simulator, emulator, or physical hardware evidence.
- No claim of quantum advantage appears without repository evidence that meets the scientific
  claims policy.
