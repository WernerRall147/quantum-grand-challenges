"""The index every verdict rests on is hand-edited. These are the ways that can go wrong.

The rules under test were derived from the committed 47 rather than invented - see
tooling/validate_algorithm_index.py for the one candidate rule that did not hold and is
deliberately absent.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tooling.validate_algorithm_index import (  # noqa: E402
    INDEX_PATH, scaffold, validate,
)


def entry(**overrides):
    base = {
        "name": "Test Algorithm",
        "category": "Number Theory",
        "speedup_class": "superpolynomial",
        "troyer_verdict": "QUANTUM_ADVANTAGE",
        "io_bottleneck": False,
        "naturally_quantum": True,
        "notes": "n/a",
    }
    base.update(overrides)
    return base


def only(problems, fragment):
    return [p for p in problems if fragment in p]


class TestTheSilentFailure:
    """A speedup class the router does not know matches none of its tests and says nothing."""

    def test_an_unknown_speedup_class_is_caught(self):
        problems = validate([entry(speedup_class="super-polynomial")])
        assert only(problems, "means nothing to the router")

    def test_the_deliberate_qualified_classes_are_accepted(self):
        problems = validate([entry(
            name="HHL-like", speedup_class="exponential_core",
            troyer_verdict="HPC_PREFERRED", io_bottleneck=True, naturally_quantum=False,
        )])
        assert problems == []

    def test_exponential_core_without_the_bottleneck_is_incoherent(self):
        """Without io_bottleneck the label is just a misspelling that hides an advantage."""
        problems = validate([entry(
            name="HHL-like", speedup_class="exponential_core",
            troyer_verdict="HPC_PREFERRED", io_bottleneck=False, naturally_quantum=False,
        )])
        assert only(problems, "requires io_bottleneck=True")


class TestOverClaiming:
    def test_quantum_advantage_needs_a_strong_speedup(self):
        problems = validate([entry(speedup_class="quadratic")])
        assert only(problems, "survive error correction")

    def test_quantum_advantage_cannot_have_an_io_bottleneck(self):
        problems = validate([entry(io_bottleneck=True)])
        assert only(problems, "io_bottleneck=True")

    def test_a_string_boolean_is_rejected(self):
        """"false" is truthy, so this inverts the filter rather than failing loudly."""
        problems = validate([entry(io_bottleneck="false")])
        assert only(problems, "must be a real boolean")


class TestLosingTheReason:
    def test_relabelling_an_io_bound_entry_to_a_bare_strong_class_is_caught(self):
        """The HHL case. Nothing else catches it, which is why this rule exists.

        Dropping 'exponential_core' for plain 'exponential' keeps every other field
        valid while discarding the record of *why* classical wins.
        """
        problems = validate([entry(
            name="HHL Algorithm", speedup_class="exponential",
            troyer_verdict="HPC_PREFERRED", io_bottleneck=True, naturally_quantum=False,
        )])
        assert only(problems, "Use 'exponential_core'")

    def test_strong_and_io_bound_but_unresolved_is_allowed(self):
        """Three real entries are superpolynomial and I/O-bound; INCONCLUSIVE is honest."""
        problems = validate([entry(
            name="Quantum Topological Data Analysis", speedup_class="superpolynomial",
            troyer_verdict="INCONCLUSIVE", io_bottleneck=True, naturally_quantum=False,
        )])
        assert problems == []


class TestUnderClaiming:
    def test_passing_every_filter_but_not_marked_advantage_is_flagged(self):
        problems = validate([entry(troyer_verdict="INCONCLUSIVE")])
        assert only(problems, "troyer_verdict is 'INCONCLUSIVE'")


class TestStructuralSpeedupsSurvive:
    """The rule that was NOT enforced, pinned so nobody adds it later."""

    def test_shor_is_quantum_advantage_without_being_naturally_quantum(self):
        problems = validate([entry(name="Shor's Algorithm", naturally_quantum=False)])
        assert problems == [], (
            "structural speedups over classical hardness assumptions are QUANTUM_ADVANTAGE "
            "without simulating a quantum system; enforcing otherwise breaks the "
            "distinction the evaluator exists to draw"
        )


class TestBookkeeping:
    def test_a_stale_total_is_caught(self):
        problems = validate([entry()], declared_total=47)
        assert only(problems, "total_algorithms says 47")

    def test_duplicate_names_are_caught(self):
        problems = validate([entry(), entry()])
        assert only(problems, "duplicate name")

    def test_a_missing_required_field_is_caught(self):
        broken = entry()
        del broken["category"]
        assert only(validate([broken]), "missing required field 'category'")


class TestScaffolding:
    def test_it_fills_the_speedup_from_the_zoo(self):
        built = scaffold("Group Isomorphism")
        assert built is not None
        assert built["speedup_class"] == "superpolynomial"

    def test_an_unfilled_scaffold_cannot_pass_validation(self):
        """The judgement fields are strings until a human replaces them, and strings fail."""
        built = scaffold("Group Isomorphism")
        problems = validate([built])
        assert only(problems, "must be a real boolean")

    def test_an_unknown_name_returns_nothing(self):
        assert scaffold("Not A Real Algorithm") is None


class TestTheCommittedIndex:
    def test_the_real_file_is_coherent(self):
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        entries = index["algorithms"] if isinstance(index, dict) else index
        declared = index.get("total_algorithms") if isinstance(index, dict) else None
        problems = validate(entries, declared)
        assert problems == [], "\n".join(problems)
