# Grover on Quantinuum H2, 2 September 2026

A real Azure Quantum run of this problem's search kernel, kept end to end: what was
submitted, what came back, and what the numbers mean.

| | |
|---|---|
| Job | `qgc-15_database_search-grover` |
| Job id | `ad36284c-a707-11f1-8583-f068e3583cd5` |
| Target | `quantinuum.sim.h2-1e` (Quantinuum H2 emulator - a **noise model**, not a syntax check) |
| Shots | 100 |
| Profile | `Adaptive_RI` |
| Queue | 400 s |
| Execution | 5.2 s |
| Cost | 40.18 eHQC, $0.00 (included credits) |
| Workspace | `qgc-af-demo` - see [why not the original](#why-a-second-workspace) |

## The input

The circuit is [`../../qsharp/HardwareKernel.qs`](../../qsharp/HardwareKernel.qs), unchanged.
Four qubits, so the search space is 2^4 = **16 items**, and exactly one is marked: `|0111>`,
which is 7.

```qsharp
use qs = Qubit[4];
for q in qs { H(q); }        // equal superposition over all 16
for _ in 1..3 {              // 3 Grover iterations
    X(qs[0]);                // oracle: mark |0111>
    Controlled Z(qs[0..2], qs[3]);
    X(qs[0]);
    for q in qs { H(q); X(q); }        // diffusion
    Controlled Z(qs[0..2], qs[3]);
    for q in qs { X(q); H(q); }
}
return MResetEachZ(qs);
```

**Why three iterations.** Grover needs about `(pi/4) * sqrt(N/M)` of them. Here
`sqrt(16/1) = 4`, so `(pi/4) * 4 ≈ 3.14`, and 3 is the nearest whole number. That is not a
rounding nicety - the success probability is `sin²((2k+1) · arcsin(sqrt(M/N)))`, and it
turns over sharply:

| Iterations `k` | Ideal success |
|---|---|
| 1 | 47.3% |
| 2 | 90.8% |
| **3** | **96.1%** |
| 4 | 58.2% |
| 5 | 12.5% |

That is the part people find surprising: in Grover, running the algorithm *longer* makes it
worse. The amplitude rotates onto the marked state and then straight past it.

`Adaptive_RI` is the QIR profile Quantinuum requires. [`input.qir.ll`](input.qir.ll) is the
10,354 bytes of QIR that this compiled to and that Azure actually executed - not a
re-render, the exact submitted payload.

## The output

[`output.json`](output.json) is the exact payload Azure returned: a histogram plus all 100
individual shots.

| Outcome | Count | Share |
|---|---|---|
| **`[0, 1, 1, 1]`** - the marked item | **80** | **80%** |
| `[1, 1, 1, 0]` | 3 | 3% |
| `[0, 1, 1, 0]` | 3 | 3% |
| `[0, 1, 0, 1]`, `[0, 0, 0, 1]`, `[0, 1, 0, 0]`, `[0, 0, 1, 0]` | 2 each | 2% |
| `[1, 0, 0, 1]`, `[0, 0, 1, 1]`, `[1, 1, 0, 1]`, `[1, 0, 1, 1]`, `[1, 1, 0, 0]`, `[1, 0, 0, 0]` | 1 each | 1% |

## What the result means

**It found the right answer.** `[0, 1, 1, 1]` is the marked state, and it dominates. Random
guessing over 16 items would land there about 6 times in 100; Grover landed there 80 times.

**The 20% is noise, not disagreement.** It is spread thinly across twelve different outcomes
at 1-3% each. A competing *answer* would show up as a second tall bar. There isn't one - the
run is one clear peak sitting on a low, flat floor of noise.

**The gap to the ideal is the interesting number.** With no noise at all, this circuit
succeeds **96.1%** of the time - that is analytic, from the formula above, not a
measurement. A noiseless local simulator agrees, though it is sampling, so 200 shots lands
anywhere in roughly 92-97%:

```powershell
python -c "from qdk import qsharp; qsharp.init(target_profile=qsharp.TargetProfile.Adaptive_RI); qsharp.eval(open('problems/archived/15_database_search/qsharp/HardwareKernel.qs').read()); print(qsharp.run('GroverSearchKernel()', shots=200))"
```

| Run | Marked state | What it tells you |
|---|---|---|
| Analytic, noiseless | **96.1%** | the ceiling for this circuit |
| Ideal simulator, 200 shots | 92-97% across runs | the algorithm is correct |
| **Quantinuum H2 emulator, 100 shots** | **80 of 100** | what a realistic noise model costs |

**Roughly 96% down to 80% on a 4-qubit, 3-iteration circuit.** This is about as small as a
useful quantum circuit gets, and it already loses about a sixth of its accuracy. That is the
honest argument for why fault tolerance is not optional, and it is why
[`../../circuits/estimate.json`](../../circuits/estimate.json) puts a fault-tolerant version
of this search at **61,122 physical qubits** for 18 logical ones.

> Quote the emulator result as **"80 of 100 shots"**, which is exact, against a **~96%**
> ideal. Do not quote a single sampled simulator run as though it were a constant - an
> earlier note in this repo said "97%" because one 200-shot run happened to land there.

**None of this makes unstructured search worth doing on a quantum computer.** Grover is a
*quadratic* speedup - `sqrt(N)` instead of `N`. Applying the same
`(pi/4) * sqrt(N)` from above to 10 million records gives roughly **2,500 iterations**
instead of 10 million lookups, which sounds excellent until you price the error correction
above. This problem is archived as `HPC_PREFERRED` for exactly that reason. The algorithm
working is not the same as the algorithm being worth it.

## Reproducing it

```powershell
# submit (quota permitting - see below)
python tooling/submit_one_kernel.py 15_database_search quantinuum.sim.h2-1e `
  --shots 100 --expect "0, 1, 1, 1"

# download a finished job into a folder like this one
python tooling/fetch_azure_job.py <job-id> --dest <folder> --expect "[0, 1, 1, 1]"
```

**Quota.** `h2-1e` is metered in eHQC and shared across the subscription. This 100-shot run
consumed **40.18**. A 200-shot attempt minutes earlier wanted 75.36 against 42.66 remaining
and was rejected with `NotEnoughQuota`. If that happens, lower `--shots`; retrying will not
help.

**Do not quote `h2-1sc`.** That target is a *syntax checker*. It validates that the circuit
compiles and returns all zeros regardless of what the circuit computes. Two older files in
this problem - `estimates/azure_result_grover_4q.json` (128 shots of `"0000"`) and
`estimates/azure_syntax_check_20260407.json` (`[0,0,0,0]` at 1.0) - are h2-1sc output. They
prove the kernel compiles for hardware. They say nothing about whether Grover works, and
`0000` is not the marked state.

## Why a second workspace

This ran in `qgc-af-demo`, not the original `Quantum-Grand-Challenges` workspace, which
cannot accept new jobs. Tenant policy locks the storage account it stages payloads in, and
that account sits in a Microsoft-managed resource group behind a deny assignment - so it
cannot be opened by anyone in this tenant, including a subscription Owner. Older jobs there
can still be *listed*, but not opened.

Full diagnosis, and the ten things ruled out getting to it, in
[`docs/AzureFriday/deck-notes.md`](../../../../../docs/AzureFriday/deck-notes.md) section C7.
