"""The paper classifier must prefer silence to a confident wrong answer.

Measured against the 358 Zoo-labelled papers on 2026-08-24: abstains on 87%, is right on
90% of what it does decide, and reads 2 of 119 WEAK papers as STRONG. Always answering
STRONG would score 67% accuracy on the same set while being wrong about every paper whose
speedup does not survive error correction, which is why accuracy is not the target.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agents.classifier.paper_classifier import (  # noqa: E402
    INDETERMINATE,
    STRONG,
    WEAK,
    classify_paper,
)


class TestAbstainsByDefault:
    def test_silence_is_indeterminate_not_strong(self):
        result = classify_paper("A quantum algorithm for something", "We present a method.")
        assert result.speedup_class == INDETERMINATE
        assert result.evidence == []

    def test_empty_input_does_not_claim_anything(self):
        assert classify_paper("", "").speedup_class == INDETERMINATE


class TestReadsBothDirections:
    def test_exponential_claim_reads_strong(self):
        result = classify_paper("Exponential speedup for simulating quantum systems")
        assert result.speedup_class == STRONG
        assert "exponential speedup" in result.evidence

    def test_quadratic_claim_reads_weak(self):
        result = classify_paper("A quadratic speedup for unstructured search")
        assert result.speedup_class == WEAK

    def test_refutation_reads_weak(self):
        """A dequantization result is evidence against, and must not read as neutral."""
        result = classify_paper(
            "Quantum-inspired classical algorithms for recommendation systems",
            "We dequantize the quantum recommendation algorithm.")
        assert result.speedup_class == WEAK


class TestConflictAbstains:
    def test_both_signals_present_abstains_rather_than_picking(self):
        """Papers contrasting regimes mention both. Guessing which is the over-claim path."""
        result = classify_paper(
            "On quantum speedups",
            "We show an exponential speedup in one regime and only a quadratic speedup "
            "in another.")
        assert result.speedup_class == INDETERMINATE
        assert result.conflict is True
        assert len(result.evidence) >= 2

    def test_conflict_is_not_silently_reported_as_silence(self):
        silent = classify_paper("A paper about nothing in particular")
        conflicted = classify_paper(
            "x", "exponential speedup here, quadratic speedup there")
        assert silent.speedup_class == conflicted.speedup_class == INDETERMINATE
        assert silent.conflict is False and conflicted.conflict is True


class TestDecidedFlag:
    def test_only_strong_and_weak_count_as_decided(self):
        assert classify_paper("exponential speedup").is_decided
        assert classify_paper("quadratic speedup").is_decided
        assert not classify_paper("no signal here").is_decided
