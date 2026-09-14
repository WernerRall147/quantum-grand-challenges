"""Verdict-quality evaluators for Foundry-hosted and offline evaluation.

Assert behaviour, not shape (.github/copilot-instructions.md). A verdict is graded
on whether the routed platform equals the expected platform, and a citation on
whether it has a resolvable target - never on whether a field is merely populated.
An evaluator that passed because `verdict` was a non-empty string would be the
3,182-character Q# failure again: every field present, every answer wrong.

Both evaluators are plain callables returning a metrics dict, so the same object
runs offline in run_foundry_eval.py and drops straight into
`azure.ai.evaluation.evaluate(evaluators={...})` when the SDK and a project are
present. Neither imports azure, so they are hermetically testable.
"""

from __future__ import annotations

from typing import Any, Sequence

from agents.orchestrator.citations import citation_target


class VerdictMatchEvaluator:
    """Does the routed platform match the expected label?

    `expect_platform_in` cases carry more than one defensible answer, so the
    evaluator accepts an allow-list. The score is 1.0 only when the actual
    platform is in it - the number that moves when routing quality changes.
    """

    def __call__(
        self,
        *,
        expected: str | None = None,
        actual: str | None = None,
        allowed: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        allow = list(allowed) if allowed else ([expected] if expected else [])
        matched = actual in allow
        return {
            "verdict_match": 1.0 if matched else 0.0,
            "verdict_pass": matched,
            "expected": "|".join(allow) if allow else "",
            "actual": actual or "",
        }


class CitationGroundingEvaluator:
    """Do the references carry checkable sources, and does anything fail to resolve?

    Two distinct facts, because they fail for different reasons:
      grounded_count  how many references resolve to a real arXiv id, DOI or URL.
                      "Recent literature" has no target and does not count.
      resolved_ok     False only when a citation is *proven* missing (a recorded
                      404/410). A network flake or a publisher 403 is not a
                      fabrication and is left alone, matching citations.py.

    `min_grounded` defaults to 2, the count score_narrative.py already demands, so
    a QUANTUM_ADVANTAGE verdict cannot pass on a single citable source.
    """

    def __init__(self, min_grounded: int = 2):
        self.min_grounded = min_grounded

    def __call__(
        self,
        *,
        references: Sequence[Any] | None = None,
        citation_checks: Sequence[dict] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        refs = list(references or [])
        grounded = sum(1 for r in refs if isinstance(r, str) and citation_target(r) is not None)

        # A recorded "missing" is the only fabrication signal. Absent checks means
        # nothing was resolved live, which is unknown, not a failure.
        missing = [c for c in (citation_checks or []) if c.get("status") == "missing"]
        resolved_ok = not missing

        passed = grounded >= self.min_grounded and resolved_ok
        return {
            "grounded_count": grounded,
            "citations_resolve": 1.0 if passed else 0.0,
            "citations_pass": passed,
            "missing": [c.get("url") or c.get("ref") for c in missing],
        }
