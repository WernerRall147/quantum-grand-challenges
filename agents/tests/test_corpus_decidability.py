"""What the corpus can and cannot carry, and the guard that watches it.

eval_paper_classifier.py asks whether the classifier is any good. These tests cover the
other question, which turned out to be the binding one: whether there is anything in the
corpus for it to find.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agents.classifier.paper_classifier import (  # noqa: E402
    INDETERMINATE, STRONG, WEAK, classify_paper,
)


def _import_measure():
    """Import the tool without its Azure dependencies at collection time."""
    try:
        from tooling.measure_corpus_decidability import sweep_is_pure_dilution
    except ImportError as exc:  # pragma: no cover - only when azure SDK is absent
        pytest.skip(f"measure_corpus_decidability unavailable: {exc}")
    return sweep_is_pure_dilution


class TestTheDilutionGuard:
    """The floor exists to catch the sweep going to noise, not to police normal drift."""

    def test_measured_sweep_rate_passes(self):
        # 2026-08-24: 42 decided of 1,788 = 2.3%, against a 1% floor.
        assert _import_measure()(42, 1788, 0.01) is False

    def test_a_sweep_below_the_floor_is_caught(self):
        assert _import_measure()(5, 1788, 0.01) is True

    def test_an_empty_sweep_is_not_dilution(self):
        """A fresh index or a failed ingest must not read as a quality regression.

        Without this, 0/0 would either divide by zero or report the worst possible
        score for a corpus that simply has not been written yet.
        """
        assert _import_measure()(0, 0, 0.01) is False

    def test_exactly_at_the_floor_passes(self):
        assert _import_measure()(10, 1000, 0.01) is False


class TestWhatRetrievalActuallyReturns:
    """The 0/25 result was real, and these are the shapes that produce it."""

    def test_an_application_paper_states_no_scaling_claim(self):
        """The dominant shape in the daily sweep: implementation work, no complexity claim.

        This is why the sweep sits at 2.3% while curated references sit at 13.5%.
        """
        result = classify_paper(
            "Quantum-Informed Portfolio Selection: An End-to-End Pipeline",
            "We present an end-to-end pipeline applying variational quantum circuits to "
            "portfolio selection on NISQ hardware, and report results on a 12-qubit device.",
        )
        assert result.speedup_class == INDETERMINATE
        assert result.evidence == []

    def test_a_cited_reference_usually_does_state_one(self):
        result = classify_paper(
            "Polynomial-Time Algorithms for Prime Factorization",
            "We give algorithms achieving an exponential speedup over the best known "
            "classical methods for factoring and discrete logarithms.",
        )
        assert result.speedup_class == STRONG

    def test_length_alone_does_not_make_a_paper_decidable(self):
        """Curated references are shorter (966 chars) yet six times more decidable.

        Guards against anyone concluding the fix is to index more text per paper.
        """
        long_but_silent = "We investigate " + ("hardware noise characteristics " * 60)
        assert classify_paper("A study", long_but_silent).speedup_class == INDETERMINATE

    def test_counter_evidence_still_counts_as_decided(self):
        """A paper arguing against advantage is signal, not noise."""
        result = classify_paper(
            "Classical simulation of quantum advantage experiments",
            "We show the proposed circuits are classically simulable and offer "
            "no quantum speedup.",
        )
        assert result.speedup_class == WEAK
        assert result.is_decided
