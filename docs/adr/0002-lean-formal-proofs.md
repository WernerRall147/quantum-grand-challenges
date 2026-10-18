# ADR-0002: Machine-check the mathematics the code relies on with Lean 4 and Mathlib

Date: 2026-10-18
Status: Proposed. Accepted when merged.
Deciders: Werner Rall (repository owner)

## Context

This repository's guards check prose against code and artifacts. `tooling/test_doc_claims.py`
holds test counts to what pytest collects, `tooling/test_citation_claims.py` holds the citation
abstract to `docs/objective-kpis.json`, and the list goes on in
`.github/skills/scientific-claims/SKILL.md`. Nothing checks the mathematics inside the formulas
the code uses. A unit test compares a function with expected values someone wrote down, not with
a specification.

Reading problem 16's baseline for #290 showed what that misses. `repetition_logical_error` in
`problems/16_error_correction/python/classical_baseline.py` uses
`effective_p = 1 - (1 - p) ** rounds`, the probability of at least one flip in `rounds` rounds.
Flips on one bit cancel in pairs, so the probability of a net flip is (1 - (1 - 2p)^r)/2. The two
agree at one round and differ by p² at two. The tests passed because nothing in them said what
the formula was meant to compute.

Gu, Kemeny, Yelin and Lukin (arXiv:2610.22367v1, October 2026) split the work in a way that fits
this repository. An evaluator tests that each circuit does what its task specifies, and Lean 4
proofs establish the mathematical facts the circuits depend on: in
[andigu/uncompute](https://github.com/andigu/uncompute), `lean/divsteps` "proves the step bound
and the branch-recovery rule that the modinv-point-add divstep circuit relies on" and `lean/dqi`
"proves the decoder-error bound that the DQI tasks rely on".

There is no proof assistant in this repository today. CI runs on GitHub-hosted `ubuntu-latest`
runners; `ci-cd.yml` runs on pull requests to `main` and on pushes to `main`. Contributors work
on Windows, and `.github/workflows/copilot-setup-steps.yml` installs what CI installs for the
cloud agent. On the owner's machine, `lean` on PATH is not Lean 4: `pip show lean` reports
version 1.0.225 of "A CLI aimed at making it easier to run QuantConnect's LEAN engine locally and
in the cloud", installed into Python's Scripts folder.

## Decision drivers

- A proof must be checked on every change that can break it, and fail loudly. A proof that
  quietly stops being checked is worse than none (AGENTS.md rule 1).
- A theorem must say exactly what it backs, and a reviewer must be able to read its statement.
- Production stays as it is: no change to the evaluator API image, the Python and Q# toolchain,
  or the cloud agent's default setup.
- Every download is pinned to a version or checked against a published digest.
- Running cost: CI minutes, the repository's 10 GB GitHub Actions cache quota, and contributor
  disk and setup time.
- Upgrades must be deliberate and reviewable.

## Options considered

All CI numbers were measured on GitHub-hosted `ubuntu-latest` runners on 2026-10-18, in
[run 39153868024](https://github.com/WernerRall147/quantum-grand-challenges/actions/runs/39153868024)
on the throwaway branch `spike/lean-ci-measure`. Attempt 1 started with empty caches
("cold"). [Attempt 2](https://github.com/WernerRall147/quantum-grand-challenges/actions/runs/39153868024/attempts/2)
restored the caches attempt 1 saved ("warm"). Each variant checks the same statement where it
can: majority decoding of a distance-3 repetition code fails exactly when at least two of the
three bits flip. The Lean with Mathlib variant is the `formal/` pilot of #294, unchanged. Times
are whole seconds as the runner's clock reported them, and wall time includes runner setup.

| Option | Setup, cold | Download and disk | Check | Job wall time, cold / warm |
|---|---|---|---|---|
| Z3 from Python, `z3-solver==5.1.0.0` | `pip install` 2 s | 51 MB installed | 0 s | 11 s / 13 s |
| Lean 4 v4.35.0, core library only | toolchain 12 s | toolchain 3.0 GB | 0 s | 28 s / 25 s |
| Lean 4 v4.35.0 with Mathlib v4.35.0 | toolchain 13 s; `lake exe cache get` 73 s for 9,031 files | toolchain 3.0 GB; `.lake` 7.3 GB | 5 s cold, 1 s warm | 138 s / 66 s |

The warm Mathlib run restored a 2,711 MB cache entry (736 MB for core). On the owner's Windows
laptop the same pilot needed 3,262 MB of toolchain and 6,908 MB in `.lake`; `lake update`, which
clones Mathlib and fetches its prebuilt files, took 654 s on that connection, and a rebuild of
the pilot takes about 25 s.

1. **Status quo: tests only.** No cost and nothing to maintain. The gap in the context section
   stays open: tests check values someone chose, so a formula that is consistently wrong passes.

2. **Lean 4 with its core library only.** A 3.0 GB toolchain and a check in under a second. It
   proves finite statements by evaluation (the spike's three-bit statement, by `decide`) and
   linear arithmetic (`omega`). It has neither finite sets nor binomial coefficients: `Finset`
   and `Nat.choose` are Mathlib definitions (`Nat.choose` is defined in
   `Mathlib/Data/Nat/Choose/Basic.lean`), and searching the v4.35.0 toolchain's sources finds
   neither. Problem 16's formula, a binomial sum over every odd distance, cannot even be stated
   without rebuilding that library.

3. **Lean 4 with Mathlib, using Mathlib's prebuilt files.** The pilot states and proves problem
   16's formula for every odd distance, over any commutative ring, in a 98-line file, mostly by
   citing Mathlib lemmas such as `Finset.sum_powerset_apply_card`. The cost is size: about 10 GB
   on disk and 138 s per cold CI run, of which `lake exe cache get` is 73 s. It is also the
   ecosystem the prior art uses. The security trade-off is that Lean loads imported `.olean`
   files without re-checking their proofs, so the prebuilt files are trusted to match the pinned
   Mathlib source; rebuilding Mathlib from source would remove that trust at the cost of hours.

4. **Another proof assistant, such as Rocq or Isabelle.** Not measured. Both could state and prove
   the pilot's theorem. Neither is used by the work that prompted this decision and nobody here
   works in them, so adopting one would add a second ecosystem to learn for no gain on the
   statements this repository needs.

5. **SMT from Python with Z3.** By far the cheapest: 51 MB and seconds. It confirmed the
   three-bit statement (`unsat`, so no counterexample exists). But it decides one fixed size at a
   time, so "for every odd distance" is out of reach, and its answer is the solver's verdict
   rather than a proof that something smaller can re-check. It remains a good tool for bounded
   checks of specific circuits, which is a different job.

## Decision

Option 3. Proofs live in `formal/`, a Lake project that pins Lean in `lean-toolchain`
(`leanprover/lean4:v4.35.0`) and Mathlib in `lake-manifest.json` (tag `v4.35.0`, commit
`56a005855ea17e0b0958f73ec801ae140b0a1679`). It is built by its own workflow,
`.github/workflows/lean-proofs.yml`, which:

- runs on pull requests and pushes to `main` that touch `formal/` or the workflow, and on demand;
- installs elan 4.2.4 from its GitHub release after checking the archive's SHA-256 against the
  digest GitHub publishes for it;
- fails if a `.lean` file uses a tactic or declaration that skips the kernel's check;
- builds with `lake build --wfail`, so any warning fails, including the one for an unfinished
  proof;
- builds `QGC/Audit.lean`, where `#guard_msgs` pins the output of `#print axioms` for each
  theorem that backs a claim, so a proof that comes to rest on any axiom beyond `propext`,
  `Classical.choice` and `Quot.sound` fails the build;
- does not use the Actions cache. Caching saves about 70 s per run but would hold 2.7 GB of the
  repository's 10 GB quota for a job that runs only when `formal/` changes. A 20-minute timeout
  makes an outage of Mathlib's file server fail quickly instead of building Mathlib from source.

What a proof certifies here is a mathematical statement about the definitions in its file. It
does not certify that Python or Q# code implements those definitions, and it says nothing about
physical or resource-model assumptions. So every theorem that backs a claim comes with a test
that checks the code against the theorem's definitions; for the pilot that is
`tooling/test_repetition_code_formula.py`, which enumerates every flip pattern.

Tooling never relies on whatever `lean` is on PATH. It calls elan's binaries by path, and
`formal/README.md` tells contributors to check that `lean --version` reports Lean 4.

The cloud agent's default setup does not install Lean. An agent working on `formal/` installs it
as `formal/README.md` describes, so the other sessions do not download about 10 GB.

## Consequences

- A class of claims becomes machine-checked, and "proved" means the kernel checked it with no
  extra axioms rather than that a file compiles.
- Proofs tend to surface definitional gaps: stating problem 16's formula exactly is what exposed
  the `effective_p` question, now with #297.
- Contributors who touch `formal/` need about 10 GB of disk and elan. Everyone else is
  unaffected, because the workflow is filtered to `formal/`.
- The job runs only when `formal/` changes, so a Mathlib change cannot break a proof unnoticed
  between upgrades. That is acceptable because the pins only move when someone moves them.
- Upgrading means bumping `lean-toolchain` and the Mathlib tag together, running `lake update`
  and `lake exe cache get`, and repairing any proof that a renamed lemma breaks. Nothing bumps
  them automatically.
- Reviewing a proof means reading the statement and the definitions; the kernel checks the
  steps. The pull request that adds a theorem must say which claim it backs and what it does not
  cover.
- Follow-up work: the pilot (#294); later theorems, such as the statistical bound the
  verification harness of #295 reports, which needs Mathlib's real analysis; and, if trust in
  the prebuilt files ever matters more than CI time, an occasional run that re-checks them.

## How we will know

- The pull request for #294 links a green `lean-proofs` run, a red run on a deliberately false
  theorem, and a red run on an unfinished proof.
- A pull request that does not touch `formal/` starts no `lean-proofs` run:
  `gh run list --workflow lean-proofs.yml` lists only runs for branches that changed `formal/`.
- A cold `lean-proofs` run stays under 5 minutes; it measured 138 s for the pilot's job here.
- By 2027-04-18, six months from now, either a second claim in this repository is backed by a
  theorem listed in `formal/QGC/Audit.lean`, or a new ADR proposes removing `formal/`.

## Links

- Issues: #290 (intake), #293 (this decision), #294 (pilot), #297 (science review).
- Gu, Kemeny, Yelin, Lukin, "Discovering state-of-the-art quantum circuits with large language
  models", [arXiv:2610.22367v1](https://arxiv.org/abs/2610.22367v1), and
  [andigu/uncompute](https://github.com/andigu/uncompute), whose `lean/` folder is the prior art.
- Measurement runs: [attempt 1, cold](https://github.com/WernerRall147/quantum-grand-challenges/actions/runs/39153868024/attempts/1)
  and [attempt 2, warm](https://github.com/WernerRall147/quantum-grand-challenges/actions/runs/39153868024/attempts/2).
- Lean 4 v4.35.0 release: <https://github.com/leanprover/lean4/releases/tag/v4.35.0>.
  elan 4.2.4: <https://github.com/leanprover/elan/releases/tag/v4.2.4>.
- ADR-0001, the delivery loop this decision was made in.
