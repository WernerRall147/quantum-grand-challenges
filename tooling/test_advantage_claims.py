"""Advantage claims that were published, found false, and corrected, must stay corrected.

Each entry names the claim, what is actually true, and the source. The scan covers the
surfaces a reader sees: website data, archive notes, Stage D evidence, the agents'
reference index and prompts, the README and the paper.

The knowledge-base index (knowledge/data/algorithm_zoo_index.json) is deliberately not
scanned. It still carries the old QAOA wording, but it mirrors a deployed Azure AI Search
index that tooling/check_algorithm_index_drift.py compares against, so it changes only
together with a re-ingestion.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

SURFACES = (
    "website/data/*.json",
    "website/data/*.ts",
    "problems/reference_index.json",
    "problems/**/ARCHIVED.md",
    "problems/**/STAGE_D_ADVANTAGE_EVIDENCE.md",
    "problems/**/estimates/*.json",
    "agents/orchestrator/prompts/*.md",
    "agents/orchestrator/instructions.py",
    "tooling/generate_stage_d_evidence.py",
    "docs/GROVER_IMPLEMENTATION_SUMMARY.md",
    "docs/paper/methodology-paper.md",
    "README.md",
)

RETRACTED = [
    pytest.param(
        r"NIST (already )?recommends (doubl|AES-256)",
        "NIST expects Grover to give little or no advantage against AES and says AES-128 "
        "will remain secure for decades (csrc.nist.gov PQC FAQ, 'should we double the key "
        "length for AES now?').",
        id="nist-key-length",
    ),
    pytest.param(
        r"doubles (the )?effective key length",
        "Grover halves the effective key length; doubling the key is the response to that.",
        id="grover-key-length-direction",
    ),
    pytest.param(
        r"millions of logical qubits",
        "Grover on AES-128 needs 2,953 logical qubits (Grassl et al., arXiv:1512.04965, "
        "Table 5); no source here supports millions for AES or lattice QCD.",
        id="millions-of-logical-qubits",
    ),
    pytest.param(
        r"at most quadratic",
        "QAOA has no proven speedup at all; 'at most quadratic' asserts a bound nobody proved.",
        id="qaoa-at-most-quadratic",
    ),
    pytest.param(
        r"(constant[- ]depth QAOA|QAOA at constant depth)[^.]{0,40}classically simul",
        "Constant-depth QAOA expectation values are classically computable on bounded-degree "
        "graphs, but sampling its output can be classically hard even at depth one "
        "(Farhi and Harrow, arXiv:1602.07674).",
        id="qaoa-classically-simulable",
    ),
    pytest.param(
        r"QPE provides (the )?exponential speedup",
        "QPE beats exact diagonalization exponentially only given a state that overlaps the "
        "ground state well; no generic exponential advantage for ground-state chemistry is "
        "established (Lee et al., Nat. Commun. 14, 1952, 2023).",
        id="qpe-unconditional-exponential",
    ),
    pytest.param(
        r"1000 classical samples",
        "Monte Carlo at epsilon = 0.001 needs about 1/epsilon^2 = 10^6 samples, not 1000.",
        id="qae-monte-carlo-sample-count",
    ),
]


def _surface_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in SURFACES:
        files.update(p for p in ROOT.glob(pattern) if p.is_file())
    return sorted(files)


def _read(path: Path) -> str:
    raw = path.read_text(encoding="utf-8-sig")
    if path.suffix == ".json":
        # json.dumps escapes non-ASCII by default; compare what the page will show.
        return json.dumps(json.loads(raw), ensure_ascii=False)
    return raw


def test_the_scan_reaches_the_published_surfaces():
    """A glob that matches nothing would pass every check below."""
    found = {p.relative_to(ROOT).as_posix() for p in _surface_files()}
    for required in (
        "website/data/troyerAssessment.json",
        "website/data/stageDEvidence.json",
        "problems/reference_index.json",
        "problems/archived/10_post_quantum_cryptography/ARCHIVED.md",
        "problems/archived/10_post_quantum_cryptography/estimates/advantage_claim_contract.json",
        "docs/paper/methodology-paper.md",
    ):
        assert required in found, f"{required} is no longer scanned"
    assert len(found) > 50


@pytest.mark.parametrize("pattern, truth", RETRACTED)
def test_retracted_claim_is_not_republished(pattern: str, truth: str):
    regex = re.compile(pattern, re.IGNORECASE)
    hits = []
    for path in _surface_files():
        for line_no, line in enumerate(_read(path).splitlines(), start=1):
            match = regex.search(line)
            if match:
                start = max(0, match.start() - 60)
                hits.append(f"{path.relative_to(ROOT).as_posix()}:{line_no}: ...{line[start:match.end() + 60]}...")
    assert not hits, f"Retracted claim published again. What is true: {truth}\n" + "\n".join(hits)


def test_every_qpe_ground_state_entry_states_the_overlap_condition():
    data = json.loads((ROOT / "website" / "data" / "troyerAssessment.json").read_text(encoding="utf-8"))
    qpe = [p for p in data["categories"]["simulation_native"]["problems"] if "QPE" in p["algorithm"]]
    assert len(qpe) == 5
    for entry in qpe:
        assert "overlap" in entry["speedup"], (
            f"{entry['id']} claims '{entry['speedup']}' without the initial-state overlap it depends on"
        )
