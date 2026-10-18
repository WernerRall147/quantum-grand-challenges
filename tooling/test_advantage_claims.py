"""Advantage claims that were published, found false, and corrected, must stay corrected.

Each entry names the claim, what is actually true, and the source. The scan covers the
surfaces a reader sees: website data, archive notes, Stage D evidence, the agents'
reference index and prompts, the README, the paper, and the talk notes and proposal that
quote numbers from them.

The knowledge-base index (knowledge/data/algorithm_zoo_index.json) mirrors a deployed
Azure AI Search index that tooling/check_algorithm_index_drift.py compares against, so it
changes only together with a re-ingestion, and it is scanned claim by claim. Its old
RSA-2048 logical-qubit count was corrected on 2026-10-18 (#297) and is scanned for. It
still carries the old QAOA wording, which is exempt until that entry is corrected: its
speedup_class "quadratic_at_most" is router vocabulary, so changing it changes routing.
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
    "docs/architecture.md",
    "docs/paper/methodology-paper.md",
    "README.md",
    "docs/AzureFriday/deck-notes.md",
    "docs/AzureFriday/script.md",
    "docs/QuantumPioneersProgram/SoftwareTrack-Proposal-Skeleton.md",
    "website/pages/**/*.tsx",
    "website/components/*.tsx",
    "problems/**/qsharp/src/*.qs",
    "problems/**/qsharp/HardwareKernel.qs",
    "problems/**/estimates/*.qasm",
)

# Verbatim program output kept as a record of a superseded kernel, not published claims.
# Problem 03's README lists these as produced by the canonical kernel before its correction.
RECORDS = ("problems/archived/03_qae_risk/estimates/quantum_estimate*.json",)

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
    pytest.param(
        r"implying CRQC|CRQC expected",
        "Google's 2029 date is the deadline for its own PQC migration; its post gives no date "
        "for a cryptographically relevant quantum computer (blog.google, 2026-03-25).",
        id="google-2029-is-not-a-crqc-date",
    ),
    pytest.param(
        r"real-world application milestone",
        "Google calls its Quantum Echoes NMR experiment a proof-of-principle step toward "
        "real-world application, not a milestone reached.",
        id="quantum-echoes-overstated",
    ),
    pytest.param(
        r"4,?000 logical qubits",
        "RSA-2048 takes about 1,400 logical qubits in Gidney's 2025 construction "
        "(arXiv:2505.15917v1, Table 5) and 3n + 0.002 n lg n, about 6,200, in Gidney and "
        "Ekerå's (arXiv:1905.09749v3); 4,000 matches neither.",
        id="rsa-2048-logical-qubits",
    ),
    pytest.param(
        r"largest device today",
        "The width shown is the device the cost was priced on (56 qubits for Quantinuum H2); "
        "Rigetti (108) and Pasqal (100) in the same price list are larger.",
        id="priced-device-is-not-the-largest",
    ),
    pytest.param(
        r"<Wilson loop>|Wilson=|ZZ plaquettes|Confinement signature:|Trotter lattice gauge (with|kernel|simulation)",
        "Problem 19's kernel is a transverse-field Ising chain evolved from |0...0>: it has no "
        "gauge fields or plaquettes, it measures the product of Z over all sites, and it cannot "
        "show a confinement signature (tooling/test_ising_chain_kernel.py).",
        id="ising-chain-is-not-a-gauge-theory",
    ),
    pytest.param(
        r"demonstrates quadratic speedup",
        "An 11-qubit simulation demonstrates no speedup. QAE's O(1/epsilon) query count is a "
        "theorem (Brassard et al., quant-ph/0005055) and loading and error-correction costs "
        "outweigh it at practical sizes (Babbush et al., PRX Quantum 2, 010103, 2021).",
        id="qae-simulation-demonstrates-no-speedup",
    ),
    pytest.param(
        r"demonstrates a pathway to quantum advantage",
        "Problem 03 implements amplitude estimation at toy scale and is archived because "
        "loading and error-correction costs outweigh the quadratic saving.",
        id="qae-no-pathway-demonstrated",
    ),
    pytest.param(
        r"18\.98\s*%",
        "Problem 03's circuit encodes the discrete tail probability 16.14% of its 16-level "
        "grid; the continuous log-normal tail is 17.98%. 18.98% matches neither "
        "(tooling/test_qae_kernel.py).",
        id="qae-tail-probability",
    ),
]


def _surface_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in SURFACES:
        files.update(p for p in ROOT.glob(pattern) if p.is_file())
    for pattern in RECORDS:
        files.difference_update(ROOT.glob(pattern))
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
        "docs/AzureFriday/deck-notes.md",
        "docs/QuantumPioneersProgram/SoftwareTrack-Proposal-Skeleton.md",
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


KNOWLEDGE_BASE = ROOT / "knowledge" / "data" / "algorithm_zoo_index.json"

# Retracted claims the knowledge base still carries, and why each is not yet corrected there.
KNOWLEDGE_BASE_PENDING = {
    "qaoa-at-most-quadratic": "QAOA's speedup_class 'quadratic_at_most' is router vocabulary",
    "qaoa-classically-simulable": "the QAOA entry is corrected as a whole, with its speedup_class",
}


def _knowledge_base_hits(claim_ids) -> list[str]:
    text = _read(KNOWLEDGE_BASE)
    hits = []
    for param in RETRACTED:
        if param.id not in claim_ids:
            continue
        pattern, _ = param.values
        for match in re.finditer(pattern, text, re.IGNORECASE):
            hits.append(f"{param.id}: ...{text[max(0, match.start() - 60):match.end() + 60]}...")
    return hits


def test_retracted_claims_are_not_in_the_knowledge_base():
    scanned = {param.id for param in RETRACTED} - set(KNOWLEDGE_BASE_PENDING)
    hits = _knowledge_base_hits(scanned)
    assert not hits, (
        f"{KNOWLEDGE_BASE.relative_to(ROOT).as_posix()} carries a retracted claim. Correct the entry, "
        "then re-seed the deployed index from it:\n" + "\n".join(hits)
    )


@pytest.mark.parametrize("claim_id", sorted(KNOWLEDGE_BASE_PENDING))
def test_each_knowledge_base_exemption_is_still_needed(claim_id: str):
    assert claim_id in {param.id for param in RETRACTED}, f"{claim_id} names no retracted claim"
    assert _knowledge_base_hits({claim_id}), (
        f"The knowledge base no longer carries {claim_id}; remove it from KNOWLEDGE_BASE_PENDING "
        "so the scan covers it."
    )


def test_every_qpe_ground_state_entry_states_the_overlap_condition():
    data = json.loads((ROOT / "website" / "data" / "troyerAssessment.json").read_text(encoding="utf-8"))
    qpe = [p for p in data["categories"]["simulation_native"]["problems"] if "QPE" in p["algorithm"]]
    assert len(qpe) == 5
    for entry in qpe:
        assert "overlap" in entry["speedup"], (
            f"{entry['id']} claims '{entry['speedup']}' without the initial-state overlap it depends on"
        )
