---
name: scientific-claims
description: Rules and procedure for writing or checking a scientific or numerical claim in this repository - the paper, docs, READMEs, website data, the evaluator's reference data and prompts. Covers what counts as evidence, the guard tests, citations, dates and regenerating the paper's HTML and PDF. Use whenever a change adds, edits or depends on a number, citation, maturity stage, speedup or comparison.
---

# Scientific claims

This project's argument is that it does not over-claim, so one wrong number costs more here than
elsewhere. Write every claim as if a referee will check it, because one will.

## The standard

- **No problem demonstrates quantum advantage on available hardware.** "Advantage",
  "exponential speedup", "outperforms", "solves" and "first" need evidence that meets that bar,
  and here it does not exist. Say what was estimated, for which instance and under which
  assumptions.
- **Every number traces to evidence.** Strongest first: re-running the computation, an artifact
  in this repository (a problem's `estimates/` and `circuits/estimate.json`,
  `docs/objective-kpis.json`), or a primary source you have read. Memory and secondary sources
  are leads, not evidence.
- **One file owns each fact.** The ownership table is in
  `.github/instructions/documentation.instructions.md`; elsewhere, link to the owner instead of
  repeating the number.
- **State the conditions:** instance size, error model, shot count, intervals, simulator versus
  hardware.
- **Qualifiers travel with the number.** A fidelity without its post-selection rate, or a gate
  count without its cost model, is a different and stronger claim. Coverage of arXiv:2512.13908
  turned "a state fidelity of 0.9999(1) (retaining 8% of attempts)", for a prepared T state, into
  "99.99% logical fidelity". When you quote a number, carry every qualifier the source attaches
  to it.

## Guards that already exist

| Guard | What it holds in place |
|---|---|
| `tooling/test_citation_claims.py` | The `CITATION.cff` abstract against `docs/objective-kpis.json` |
| `tooling/test_doc_claims.py` | Test counts and maturity-stage counts in every live document |
| `tooling/test_advantage_claims.py` | Advantage claims that were published, found false and corrected stay corrected |
| `tooling/test_architecture_claims.py` | The file tree in `docs/architecture.md` names real files |
| `tooling/test_website_claims.py` | Rendering and data claims in the website source |
| `tooling/test_script_claims.py` | The recording script's headline numbers against the code |
| `tooling/test_frontier_results.py` | The frontier-results register: every claim has conditions, one kind of evidence and its limits; arXiv identifiers are versioned; named problems and zoo entries exist |

When you correct a claim that could recur, extend the matching guard and watch it fail on the old
wording before you change the text. Past counts written as history end their line with
`<!-- historical -->`.

## Citations

- Cite by DOI or arXiv identifier and read the source: the arXiv tools or a fetch of the abstract
  page, not recall. Note the version.
- Quote or paraphrase what the source says, for the same setting: problem size, error model,
  assumptions. A number that is not in the source is not a citation.

## Results from the literature

A published result that bears on this repository's numbers or verdicts goes in
`knowledge/data/frontier_results.json`, which owns such facts. A person adds each entry after
reading the source; nothing is ingested into it automatically. Each claim names its location in
the source, its conditions, what it does not establish, and one kind of evidence. If a result is
supported in two ways, write two claims.

| Evidence | Meaning |
|---|---|
| `hardware-measured` | Measured on a physical device. Give the device, post-selection and the stated uncertainty. |
| `numerical-simulation` | A classical simulation of a model, such as Monte Carlo, state vector or stabilizer. Give the noise model. |
| `analytical-estimate` | A resource or performance estimate from formulas or a cost model, not run. |
| `logical-count-certified-by-code` | Exact logical gate and qubit counts from released code that a reader can re-run. |
| `sampled-verification` | Correctness from random tests with a stated statistical guarantee, which holds for the test distribution only. |
| `formally-proved` | A mathematical statement checked by a proof assistant. It does not show that code implements the statement. |
| `zero-knowledge-proof` | Validated by a zero-knowledge proof, with the construction withheld. |

Library docstrings are not sources. qdk 1.31.0's `GSJ24Factory` docstring cites arXiv:2409.17595
under a title the arXiv record does not have.

## Dates

Read today's date from the system: `date -u +%F` in bash, `Get-Date -Format yyyy-MM-dd` in
PowerShell. Never infer it from file contents or memory.

## The paper

1. Edit `docs/paper/methodology-paper.md`, the source.
2. Regenerate the HTML: `python tooling/reporting/regenerate_paper_html.py` (needs
   `pip install markdown`).
3. Regenerate the PDF by printing that HTML with headless Chromium or Edge, which honours its A4
   print styles. On Windows:
   `msedge --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="<repo>\docs\paper\Quantum Grand Challenges - Methodology Paper.pdf" file:///<repo>/docs/paper/methodology-paper.html`.
   If no browser is available, as in the cloud agent, say so in the pull request so a human
   regenerates it.
4. Add a dated revision note to the paper. Archived releases are immutable; correct the live
   version and say what changed.
