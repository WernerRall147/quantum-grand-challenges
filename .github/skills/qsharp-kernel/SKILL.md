---
name: qsharp-kernel
description: How to change a Q# kernel or problem program in this repository without breaking the physics - QDK 1.31.0 specifics and pitfalls, exact-simulation tests, hardware-kernel compilation, and which estimates and diagrams to regenerate. Use when editing anything under problems/*/qsharp/ or code that runs Q#.
---

# Change a Q# kernel safely

A kernel that compiles and runs can still compute the wrong thing; several in this repository
did. A kernel change is done when a test compares its output with the exact answer.

## The toolchain

- `qdk` is pinned to 1.31.0. Import it as `from qdk import qsharp`. There is no .NET toolchain.
- Each problem is a project: `problems/<p>/qsharp/qsharp.json` with `src/Main.qs`. The file name
  is the namespace, so operations are called as `Main.<Operation>()`.
- Compile everything: `python tooling/ci_validate_qsharp.py`. Run every entry point:
  `python tooling/run_all_qsharp.py`.
- One project:
  `python -c "from qdk import qsharp; qsharp.init(project_root='problems/<p>/qsharp'); print(qsharp.run('Main.<Op>()', 1))"`.

## Pitfalls that have bitten this repository

- **`qsharp.set_quantum_seed` makes every shot in a run identical.** Never use it for multi-shot
  statistics: a seeded 1,000-shot run is one sample repeated.
- **Qubit order in state dumps:** in a dense state from `DumpMachine`, the first-allocated qubit
  is the most significant bit.
- **`Exp(paulis, theta, qubits)` applies exp(+i·theta·P).** Check the sign against the
  Hamiltonian convention you are implementing.
- **Hardware kernels compile under the Adaptive_RI profile**, which is stricter than the
  simulator. Under qdk 1.31.0 the QIR compiler panics on partially applied callables inside
  controlled operations, and cannot fold `ExpD` at compile time: pass literal values.
- **Amplitude amplification:** `within { U } apply { V }` is the operator U†VU, so the reflection
  about A|0⟩ is `within { Adjoint A } apply { S0 }`. The iterate is Q = -A S0 A† S_chi (Brassard
  et al., 2002), and its -1 phase matters once Q is controlled, as in QPE and QAE. The wrong
  order or sign still produces plausible-looking numbers.

## Testing a kernel

Compare with an exact answer, not with the kernel's own previous output.

- Get the state vector: `qsharp.run(expression, shots=1, save_events=True)[0]["dumps"][0]`, then
  `.as_dense_state()`. `tooling/test_hhl_kernel.py` shows the pattern, including comparing with
  an independent NumPy construction of the same circuit.
- For sampled outputs, compare the empirical distribution with the exact one using a tolerance
  justified by the shot count, as in `tooling/test_qaoa_kernels.py`.
- Existing kernel tests: `tooling/test_qae_kernel.py`, `tooling/test_hhl_kernel.py`,
  `tooling/test_qaoa_kernels.py`, `tooling/test_qpe_kernels.py`, `tooling/test_shor_kernel.py`,
  `tooling/test_hft_kernel.py`, `tooling/test_swap_test_kernel.py`,
  `tooling/test_ising_chain_kernel.py`. Extend the matching one, or add one in the same style.
- A changed `HardwareKernel.qs`: `python -m pytest tooling/test_hardware_kernels_compile.py -q`.
- Watch the new test fail against the old kernel before you trust it.

## After the kernel changes

1. Resource estimates: `python tooling/generate_estimates.py` rewrites each problem's
   `circuits/estimate.json` and `website/data/paretoFrontiers.json`.
2. Circuit diagrams: `python tooling/trace_circuits.py` re-renders `circuits/circuit.txt` from
   each `HardwareKernel.qs`.
3. Maturity contract: `python tooling/reporting/stage_kpis.py --policy tooling/reporting/maturity-policy.json --enforce`.
4. Every README, paper section or website page that quotes a changed number: the
   [scientific-claims](../scientific-claims/SKILL.md) skill.

Review the regenerated files with `git diff --stat` and commit only those your change affected.
Entry points and `HardwareKernel.qs` files are on the danger list: never delete them without an
explicit human OK.
