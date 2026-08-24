"""The ingestion filter has to keep both sides of the advantage question.

Lives under agents/tests because pytest.ini's testpaths are test_baselines.py, problems
and agents; a file under knowledge/ would never run.

Until 2026-08-24 the filter kept only papers matching quantum keywords, which selects
for quantum framing rather than for relevance. Measured on a five-paper sample from
abs:"tensor network simulation", it dropped "Fast classical simulation of ..." and kept
"QuantumPhaseNet: A Gauge-Covariant Geometric and Quantum-Spectral Theory of Semantic
Concepts", a natural-language paper borrowing quantum vocabulary. That is half the
reason retrieval over this corpus could only ever argue for quantum.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "knowledge" / "ingest"))

from arxiv_ingester import (  # noqa: E402
    COUNTEREVIDENCE_KEYWORDS,
    QUANTUM_KEYWORDS,
    SOURCES,
    filter_advantage_relevance,
)


def paper(title, abstract=""):
    return {"title": title, "abstract": abstract}


class TestFilterKeepsBothSides:
    def test_keeps_a_quantum_advantage_paper(self):
        p = paper("Quantum phase estimation for the FeMoco cofactor")
        assert filter_advantage_relevance([p]) == [p]

    def test_keeps_the_classical_simulation_paper_it_used_to_drop(self):
        p = paper(
            "Fast classical simulation of 'Fast, accurate, high-resolution simulation "
            "of large-scale quantum circuits'"
        )
        assert filter_advantage_relevance([p]) == [p], (
            "a classical simulation refuting a quantum result is exactly the "
            "counter-evidence this corpus lacks"
        )

    def test_keeps_a_limits_result(self):
        p = paper("Quantum Speedups Require Structure or Depth")
        assert filter_advantage_relevance([p]) == [p]

    def test_still_drops_something_unrelated(self):
        p = paper("A survey of medieval bookbinding techniques")
        assert filter_advantage_relevance([p]) == []


class TestSourcesCoverBothSides:
    def test_at_least_one_counter_evidence_source_is_configured(self):
        labels = " ".join(label for label, _ in SOURCES).lower()
        assert "no quantum speedup" in labels or "classically simulable" in labels, (
            "every source argues for quantum; the corpus cannot answer 'do not use it'"
        )

    def test_dequantization_is_not_a_source(self):
        """It is a homonym. As a source it returns neural-network quantization papers.

        Measured 2026-08-24: abs:"dequantization" gives 295 results led by CellFill,
        FluxBin LLM inference and quantization-aware training. Safe as a keyword,
        because a paper only reaches the filter if another source already returned it.
        """
        queries = " ".join(q for _, q in SOURCES).lower()
        assert "dequantiz" not in queries
        assert any("dequantiz" in kw for kw in COUNTEREVIDENCE_KEYWORDS)

    def test_keyword_lists_stay_separate(self):
        overlap = set(QUANTUM_KEYWORDS) & set(COUNTEREVIDENCE_KEYWORDS)
        assert not overlap, f"a term cannot mean both sides: {overlap}"


class TestZooReferenceParsing:
    """The Zoo's own markup is irregular, and guessing around it loses entries."""

    @staticmethod
    def _mod():
        sys.path.insert(0, str(ROOT / "tooling"))
        import ingest_zoo_references
        return ingest_zoo_references

    def test_known_speedup_classes_pass_through(self):
        normalise = self._mod().normalise_speedup
        assert normalise("Superpolynomial") == ("Superpolynomial", "Superpolynomial")
        assert normalise("  Polynomial.  ") == ("Polynomial", "Polynomial")

    def test_prose_is_left_unclassified_rather_than_guessed(self):
        """Adiabatic Algorithms carries a sentence where a class word should be.

        Taking it literally labelled 40 citations with a truncated sentence. Inventing
        a class the source does not state would be worse.
        """
        normalise = self._mod().normalise_speedup
        cls, raw = normalise("A plausible example of superpolynomial speedup appears in [")
        assert cls == "unclassified"
        assert raw.startswith("A plausible example")

    def test_compound_speedup_is_not_forced_into_one_class(self):
        normalise = self._mod().normalise_speedup
        cls, _ = normalise("Polynomial Directly, Superpolynomial Recursively")
        assert cls == "unclassified"

    def test_marker_matches_every_entry_variant(self):
        """60 of the 74 use the bare form; matching only that silently loses fourteen."""
        marker = self._mod().ALGORITHM_MARKER
        for variant in ("<b>Algorithm:</b>", '<b id="abelian_HSP">Algorithm:</b>',
                        "<b>Algorithm: </b>"):
            assert marker.search(variant), variant
