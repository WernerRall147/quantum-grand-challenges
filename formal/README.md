# formal/

Lean 4 proofs of mathematical statements that this repository's code and documents rely on.
Why Lean, and what a proof here can and cannot certify, is recorded in
[ADR 0002](../docs/adr/0002-lean-formal-proofs.md).

## What is proved

| Theorem | Statement | Backs |
|---|---|---|
| `QGC.RepetitionCode.fails_iff` | For odd d, majority decoding of a d-bit repetition code fails exactly when at least d / 2 + 1 bits flip, whichever bit was sent. | The threshold in `repetition_logical_error`, `problems/16_error_correction/python/classical_baseline.py` |
| `QGC.RepetitionCode.failureProb_eq` | For odd d, with each bit flipping independently with probability q, the probability that decoding fails is the sum over k from d / 2 + 1 to d of C(d, k) q^k (1 - q)^(d - k). | The value `repetition_logical_error` returns |
| `QGC.RepetitionCode.sum_patternProb` | The flip-pattern probabilities sum to 1. | That `failureProb` is a probability |

A proof is about its own definitions, not about the code. `tooling/test_repetition_code_formula.py`
ties the two together: it checks `repetition_logical_error` against the same definitions by
enumerating every flip pattern, for the distances in `problems/16_error_correction/instances/`,
at `rounds = 1`.

Not covered: for `rounds > 1` the code uses `1 - (1 - p) ** rounds` as the flip probability.
That is a modelling choice, and no theorem here says anything about it (#297).

## How it is checked

- `lake build --wfail` compiles every proof and fails on any warning, including the warning
  Lean gives for an unfinished proof.
- `QGC/Audit.lean` fails the build if a theorem rests on any axiom beyond Lean's three standard
  ones (`propext`, `Classical.choice`, `Quot.sound`). Skipping a proof step adds one.
- `.github/workflows/lean-proofs.yml` runs both on every pull request that touches `formal/`,
  with a search that rejects the tactics and declarations that skip the kernel's check.

When you add a theorem that backs a claim, add a line for it to `QGC/Audit.lean` and to the
table above, and add a test that checks the code against the theorem's definitions.

## Building locally

1. Install elan, Lean's toolchain manager, from its
   [GitHub releases](https://github.com/leanprover/elan/releases). On Windows,
   `elan-init.exe -y --no-modify-path --default-toolchain none` installs it into
   `%USERPROFILE%\.elan` and leaves PATH alone.
2. From `formal/`, run `lake exe cache get` to fetch Mathlib's prebuilt files, then
   `lake build --wfail`. Expect several gigabytes in `.lake/` and in elan's toolchain folder;
   ADR 0002 records the sizes measured at these versions.

The versions are pinned: Lean in `lean-toolchain`, the Mathlib commit in `lake-manifest.json`.

**Check which `lean` you are running.** On PyPI, `lean` is QuantConnect's trading CLI
(`pip show lean` reports "A CLI aimed at making it easier to run QuantConnect's LEAN engine
locally and in the cloud"). If Python's Scripts folder is on PATH, typing `lean` can run that
instead of Lean 4. Call elan's binaries by path, for example
`%USERPROFILE%\.elan\bin\lake.exe build`, or check that `lean --version` prints
`Lean (version 4...`.
