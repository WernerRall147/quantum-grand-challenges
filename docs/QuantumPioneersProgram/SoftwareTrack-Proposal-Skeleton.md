# 2026 Microsoft Quantum Pioneers Program - Software Track
## Proposal Skeleton (DRAFT)

> **This is a working skeleton, not a finished submission.** Content drawn from the
> `quantum-grand-challenges` project is pre-filled as supporting evidence. Sections
> marked **[TO COMPLETE]** must be written by the eligible faculty Principal
> Investigator. Do not submit until the eligibility and format checks below pass.

---

## 0. Pre-submission checklist (read first)

| Item | Requirement | Status |
|---|---|---|
| **Deadline** | Phase 1 closes **17 July 2026, 11:59 pm PT** | [ ] on track |
| **Eligibility - faculty** | PI/co-PI must be faculty (assistant/associate/full or equivalent research-track) at a university or degree-granting research institution | **[CONFIRM]** |
| **Eligibility - not MS** | Microsoft employees/directors and immediate family are **ineligible** | **[CONFIRM]** |
| **PI count** | Max **2 PIs** per proposal; each person on max **1** proposal/year | [ ] |
| **Page budget** | **5 pages** for the proposal body | [ ] |
| **CV** | **1-2 pages per PI**, appended (not counted against clarity of the 5 pages) | [ ] |
| **Submission** | Email to **QPP@microsoft.com**, subject exactly `2026 Quantum Pioneers Program – Software Track` | [ ] |
| **Phase 2** | If selected (14 finalists): <=30-min presentation at Proposers' Day, **14 Aug 2026** | [ ] |

**Judging weights:** 33% Faculty Merit / 33% Research Merit / 33% Proposal Quality.
Write section 6 (CV) and the framing to score on all three.

**Target theme(s):** primary = **Quantum architecture**; secondary = **Quantum
applications for chemistry and materials**. Both are explicitly solicited themes.

**One-sentence thesis (edit to taste):**
> An open, automated resource-estimation and validation framework that produces
> honest, reproducible, end-to-end *logical*-resource analyses for scientifically
> meaningful chemistry and materials workloads on **measurement-based / topological**
> fault-tolerant architectures.

---

## 1. Research Description  *(feeds 33% Research Merit)*

*Target length: ~2 of the 5 pages.*

### 1.1 Motivation
The credibility of quantum advantage claims depends on honest, end-to-end resource
accounting - not asymptotic hand-waving. Constant-factor costs of error correction,
data loading (I/O), and magic-state distillation routinely erase claimed speedups.
Microsoft's own utility-scale framing (Troyer's filters) makes this concrete. Tooling
that *enforces* this honesty, and that targets measurement-based / topological
execution specifically, is a software foundation the field currently lacks.

### 1.2 Prior work by the team (foundation this builds on)
This proposal extends an existing, open-source framework (DOI: 10.5281/zenodo.19222021):
- A **four-stage maturity-gate model (A->D)** that blocks premature advantage claims,
  with **CI/CD that rejects merges** when a maturity claim is not backed by evidence
  artifacts.
- A **structured "advantage claim contract"** (claim category, fair classical
  comparator, resource-scaling claim, I/O assumptions, noise model, uncertainty
  method, residual risks).
- **20 problem domains** implemented in Microsoft Q# (modern QDK) with classical
  baselines, parameterized instances, and resource-estimation artifacts; **9 remain
  active** and **11 were honestly downgraded** (I/O bottleneck, quadratic-only, QEC
  overhead) - a demonstrated commitment to honest negative results.
- A **DiVincenzo hardware-readiness overlay** and a live evaluator backed by a
  peer-reviewed knowledge base.

### 1.3 Proposed research aims
**Aim 1 - Logical-resource estimation for measurement-based / topological execution.**
Extend the maturity-gate framework (currently gate-model, and partly mock-estimated)
to emit *honest* logical-resource budgets targeted at measurement-based operation:
magic-state distillation counts, lattice-surgery / measurement schedules, code-cycle
budgets, and their uncertainty bounds. Integrate with the Azure Quantum Resource
Estimator as the ground-truth backend, replacing placeholder estimates.

**Aim 2 - Application to a scientifically meaningful chemistry/materials workload.**
Apply the hardened pipeline end-to-end to a high-value target (e.g., FeMoco / nitrogen
fixation catalysis, or band-gap estimation for strongly-correlated materials where DFT
fails) to produce reproducible early-fault-tolerant resource analyses with explicit
fair classical comparators and residual-risk accounting.

**Aim 3 - Open, CI-enforced benchmark + reproducibility harness.**
Release the resource-estimate benchmarks and the policy-enforcement harness as an
open resource the community can extend, so that measurement-based resource claims are
comparable and auditable across groups.

### 1.4 What is genuinely new here
- Resource-estimation tooling specialized for **measurement-based / topological**
  layers, not generic gate-model.
- **Policy-as-code** that ties advantage claims to evidence artifacts (novel in the
  quantum-software-engineering space).
- Honest, uncertainty-bounded, end-to-end estimates for a real chemistry/materials
  target, reproducible by third parties.

### 1.5 Concrete starting point and the resource-estimate gap

**Current framework output (illustrative - and deliberately flagged as placeholder).**
The pipeline already emits standardized resource-estimate JSON per problem and target
profile. Today many of these are *mock* placeholder values: a toy H2 VQE (catalysis)
and Shor factoring of N=15 currently report *identical* figures, which is physically
meaningless and is exactly the false-confidence failure mode the maturity gates exist
to catch.

| Problem (mock profile) | Logical qubits | Physical qubits | T-count | T-depth | Runtime |
|---|---|---|---|---|---|
| 02_catalysis - VQE H2 (`qubit_gate_ns_e3`) | 16 | 35,200 | 65,536 | 4,096 | 480 s |
| 02_catalysis - VQE H2 (`surface_code_generic_v1`) | 16 | 19,200 | 65,536 | 4,096 | 480 s |
| 09_factorization - Shor N=15 (`qubit_gate_ns_e3`) | 16 | 35,200 | 65,536 | 4,096 | 480 s |

*Source: `problems/*/estimates/latest*.json` (`qdk_version: mock`). The identical rows
are the point - replacing them with real Azure Quantum Resource Estimator runs and
measurement-based logical budgets is **Aim 1**.*

**Scientifically-grounded targets (documented, literature-based).** The utility
thresholds the hardened pipeline would estimate honestly (from
`problems/reference_index.json`):

| Domain | Documented utility threshold |
|---|---|
| Catalysis / chemistry (FeMoco) | QPE for chemistry - Troyer's primary utility example |
| Drug discovery | > 50 orbitals to exceed classical FCI |
| Materials discovery | correlated band-gap regime where DFT fails |
| Nuclear physics | A > 20 nucleons |
| Factorization (Shor) | RSA-2048 ~ 4,000 logical qubits |

The contrast - trivially-simulable toy instances now vs. the logical-qubit scale real
utility demands - is precisely the estimation gap Aims 1-2 close, specialized for
measurement-based / topological execution.

**[TO COMPLETE]** Sharpen one aim into the headline result the PI is confident can be
delivered in the funding period; cite 3-5 key references (Troyer utility-scale
analyses; magic-state distillation; measurement-based/lattice-surgery; the FeMoco
resource-estimation literature).

---

## 2. Statement of Need  *(required element)*

*Target length: ~0.5 page.*

The specific outstanding challenge: **end-to-end, honest, reproducible logical-resource
estimation for early-fault-tolerant, measurement-based workloads is fragmented,
frequently over-optimistic, and rarely auditable.**

Award funding will be used for **[TO COMPLETE: e.g., one PhD student / postdoc for 12
months, Azure Quantum compute, and dissemination]**. Be explicit and concrete - the
rules require stating what the funding is for.

---

## 3. Collaboration Requested from Microsoft  *(required element)*

*Target length: ~0.5 page.*

- Access to and guidance on the **Azure Quantum Resource Estimator** and measurement-
  based / topological tooling in the **QDK / Q#** stack.
- **Azure Quantum credits / compute** for large resource-estimation sweeps.
- Technical feedback from the Microsoft Quantum team on measurement-based cost models
  and how logical/physical interfaces should be represented.
- **[TO COMPLETE: any data, pre-release tooling, or co-authorship the PI wants to ask
  for.]**

*Why this is a low-friction ask:* the existing project already runs on Q# (modern QDK)
and Azure Quantum (Quantinuum, Rigetti providers) with CI-based validation, so the
collaboration slots directly into a working pipeline.

---

## 4. Desired Outcome and Expected Impact  *(required element)*

*Target length: ~0.5 page.*

- **Outcome:** an open, CI-enforced resource-estimation framework + a reproducible
  early-FT resource-analysis benchmark for a real chemistry/materials target, specialized
  for measurement-based execution.
- **Impact:** raises the evidentiary bar for advantage claims across the community;
  gives Microsoft an auditable, honest tooling layer aligned with its utility-scale and
  topological priorities; trains **[TO COMPLETE: N]** students in fault-tolerant
  resource analysis.
- **Metrics of success:** **[TO COMPLETE: e.g., published benchmark, X problems taken
  to Stage D with real (non-mock) estimates, adoption/citations.]**

---

## 5. Facilities, Materials, Equipment, Software  *(required element)*

*Target length: ~0.5 page. This section is strong because most of it already exists.*

**Already available (this team):**
- Open-source framework and 20-domain implementation base (DOI: 10.5281/zenodo.19222021),
  AGPL-3.0, with methodology paper.
- Microsoft **Q# / modern QDK** toolchain (Python-hosted, no .NET dependency).
- **Azure Quantum** workspace with Quantinuum and Rigetti providers; **GitHub Actions**
  CI with automated validation checks; Next.js KPI dashboard.
- Standardized per-problem structure: classical baselines, parameterized instances,
  `estimates/` artifacts, reproducible Makefiles.

**Needed (via the award / Microsoft collaboration):**
- Azure Quantum Resource Estimator access at scale and compute credits.
- **[TO COMPLETE: personnel (student/postdoc), any institutional HPC, licenses.]**

**Honesty note (keep this - it is on-brand for the program):** some current
`estimates/*.json` are placeholder/mock values pending real Resource Estimator runs;
hardening these into validated logical-resource estimates is precisely Aim 1.

---

## 6. Principal Investigator CV(s)  *(required; 1-2 pages per PI, appended)*

**[TO COMPLETE - FACULTY PI]** This section carries the 33% "Faculty Merit" score.
Include: appointment and institution, research accomplishments, relevant publications,
community engagement, prior funded work, and role on this proposal.

- **PI 1 (faculty, eligible):** [name, title, institution]
- **PI 2 (optional, max 2 total):** [name, title, institution] - e.g., the framework
  author as technical co-PI **only if independently eligible**; otherwise list as
  senior personnel/collaborator, not a PI.

---

## Appendix A - Evidence index (cite from these in the body)

| Claim in proposal | Evidence in repo |
|---|---|
| Maturity-gate model A->D with CI enforcement | `docs/paper/methodology-paper.md` sec 3.2; CI in `.github/workflows/` |
| Advantage claim contract | `docs/paper/methodology-paper.md` sec 3.3; per-problem `README.md` |
| 9 active / 11 honestly-archived problems | `problems/reference_index.json` |
| Chemistry/materials targets (FeMoco, correlated materials) | `problems/02_catalysis`, `07_drug_discovery`, `14_materials_discovery` |
| Resource-estimation artifacts (and mock caveat) | `problems/02_catalysis/estimates/latest.json`, `*surface_code*`, `*qubit_gate_ns_e3*` |
| DiVincenzo readiness overlay | `docs/paper/methodology-paper.md` sec 3.4 |
| Toolchain (Q#, Azure Quantum, CI) | `docs/paper/methodology-paper.md` sec 4.1 |
| Published artifact | Zenodo DOI 10.5281/zenodo.19222021 |

## Appendix B - How each section maps to the judging criteria

| Judging criterion (33% each) | Where it is earned |
|---|---|
| Faculty Merit | Section 6 (PI CV) - **the eligible faculty PI is essential** |
| Research Merit | Section 1 (aims, novelty, alignment with measurement-based/topological) |
| Proposal Quality | Whole document: clarity, the demonstrated ability to execute (Appendix A track record) |

## Appendix C - Submission mechanics

- Email **QPP@microsoft.com**, subject line exactly:
  `2026 Quantum Pioneers Program – Software Track`
- Attach: 5-page proposal (Sections 1-5) + CV(s) (Section 6).
- Send well before **17 July 2026, 11:59 pm PT**.
- Winners list requestable within 30 days of 14 Aug 2026 via the same address.
