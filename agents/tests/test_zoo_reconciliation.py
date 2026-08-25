"""Every Zoo algorithm must be accounted for, and the accounting must be able to fail.

The live reconciliation runs here rather than only in a workflow, so a Zoo entry that
nobody dispositioned fails the same gate as everything else.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tooling.reconcile_algorithm_zoo import (  # noqa: E402
    INDEX_PATH, LEDGER_PATH, ZOO_PATH, normalise, reconcile,
)

OURS = ["Shor's Algorithm", "HHL Algorithm", "Grover's Search"]
LEDGER = {
    "aliases": {"_comment": "ignored", "factoring": "Shor's Algorithm"},
    "excluded": {"_comment": "ignored", "ordered search": "Constant factor; fails F3."},
    "candidates": {"_comment": "ignored", "zeta functions": "Superpolynomial."},
}


def zoo(*pairs):
    return [{"name": n, "speedup": s} for n, s in pairs]


class TestDispositions:
    def test_an_exact_name_needs_no_ledger_entry(self):
        result = reconcile(zoo(("Grover's Search", "Polynomial")), OURS, LEDGER)
        assert result["matched"] == [("Grover's Search", "Grover's Search")]
        assert result["unreconciled"] == []

    def test_an_alias_resolves_a_name_no_string_match_could(self):
        """The case that started this: the Zoo names the problem, we name the author."""
        result = reconcile(zoo(("Factoring", "Superpolynomial")), OURS, LEDGER)
        assert result["matched"] == [("Factoring", "Shor's Algorithm")]

    def test_an_exclusion_is_recorded_not_ignored(self):
        result = reconcile(zoo(("Ordered Search", "Constant factor")), OURS, LEDGER)
        assert result["excluded"] == [("Ordered Search", "constant factor")]
        assert result["unreconciled"] == []

    def test_a_candidate_counts_as_a_gap_not_a_failure(self):
        result = reconcile(zoo(("Zeta Functions", "Superpolynomial")), OURS, LEDGER)
        assert result["candidates"] == [("Zeta Functions", "superpolynomial")]
        assert result["unreconciled"] == []


class TestTheGuardsFire:
    """A guard nobody has watched fail is not a guard."""

    def test_an_undispositioned_algorithm_is_caught(self):
        result = reconcile(zoo(("Gauss Sums", "Superpolynomial")), OURS, LEDGER)
        assert result["unreconciled"] == [("Gauss Sums", "superpolynomial")]

    def test_a_renamed_index_entry_breaks_its_alias(self):
        """Renaming "Shor's Algorithm" would otherwise turn a match back into a silent gap."""
        renamed = ["Shor Factoring Algorithm", "HHL Algorithm", "Grover's Search"]
        result = reconcile(zoo(("Factoring", "Superpolynomial")), renamed, LEDGER)
        assert result["dangling_aliases"] == [("factoring", "Shor's Algorithm")]

    def test_only_strong_claims_are_flagged_as_structural_gaps(self):
        """A polynomial gap cannot produce a QUANTUM verdict anyway, so it is not urgent."""
        ledger = {"aliases": {}, "excluded": {},
                  "candidates": {"zeta functions": "x", "matrix rank": "y"}}
        result = reconcile(
            zoo(("Zeta Functions", "Superpolynomial"), ("Matrix Rank", "Polynomial")),
            OURS, ledger,
        )
        assert len(result["candidates"]) == 2
        assert result["strong_candidates"] == [("Zeta Functions", "superpolynomial")]


class TestNormalisation:
    def test_punctuation_and_case_do_not_matter(self):
        assert normalise("Discrete-log") == "discrete log"
        assert normalise("Pell's Equation") == normalise("PELL S EQUATION")


class TestTheRealFilesReconcile:
    """The committed Zoo, index and ledger must agree right now, not just in principle."""

    def test_nothing_is_unaccounted_for(self):
        zoo_data = json.loads(ZOO_PATH.read_text(encoding="utf-8"))
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        entries = index["algorithms"] if isinstance(index, dict) else index

        result = reconcile(zoo_data["algorithms"], [e["name"] for e in entries], ledger)

        assert result["dangling_aliases"] == [], (
            "an alias points at an index entry that no longer exists"
        )
        assert result["unreconciled"] == [], (
            "these Zoo algorithms have no disposition; add them to "
            f"{LEDGER_PATH.name}: {result['unreconciled']}"
        )

    def test_every_algorithm_is_dispositioned_exactly_once(self):
        zoo_data = json.loads(ZOO_PATH.read_text(encoding="utf-8"))
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        entries = index["algorithms"] if isinstance(index, dict) else index

        result = reconcile(zoo_data["algorithms"], [e["name"] for e in entries], ledger)
        counted = (len(result["matched"]) + len(result["excluded"])
                   + len(result["candidates"]) + len(result["unreconciled"]))
        assert counted == len(zoo_data["algorithms"])
