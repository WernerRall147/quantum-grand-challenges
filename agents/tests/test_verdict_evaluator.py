"""The verdict-quality number must move when quality changes, and the money shot
must be asserted by value.

These tests guard Workstream C's definition of done: verdict_accuracy is a real
metric, `opt-portfolio` declining quantum is a tracked assertion, and citation
grounding is graded on whether a source resolves, not on whether a field is
populated. The last test deliberately injects a regression and confirms the gate
goes red - watching the check fail before trusting it (.github/copilot-instructions.md).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents.evaluations.verdict_evaluator import (  # noqa: E402
    CitationGroundingEvaluator,
    VerdictMatchEvaluator,
)

EVAL_DIR = ROOT / "agents" / "evaluations"
CASES = json.loads((EVAL_DIR / "cases.json").read_text(encoding="utf-8"))["cases"]
CACHE = json.loads((EVAL_DIR / "cases_kb_cache.json").read_text(encoding="utf-8"))["cases"]


def _route(case_id: str) -> str:
    """Route one cached case through the real router and return the platform."""
    from agents.classifier.platform_router import route_platform

    case = next(c for c in CASES if c["id"] == case_id)
    entry = CACHE[case_id]
    return route_platform(case["problem"], entry["matches"], entry["score"])["platform"]


# --- verdict matching -------------------------------------------------------

def test_money_shot_routes_hpc():
    """opt-portfolio declining quantum is demo beat 2. It must route HPC."""
    assert _route("opt-portfolio") == "HPC"
    result = VerdictMatchEvaluator()(actual="HPC", allowed=["HPC"])
    assert result["verdict_match"] == 1.0
    assert result["verdict_pass"] is True


def test_evaluator_scores_zero_on_wrong_verdict():
    """The number moves: a QUANTUM answer where HPC was expected scores 0."""
    result = VerdictMatchEvaluator()(actual="QUANTUM", allowed=["HPC"])
    assert result["verdict_match"] == 0.0
    assert result["verdict_pass"] is False


def test_allow_list_accepts_either_defensible_answer():
    result = VerdictMatchEvaluator()(actual="INCONCLUSIVE", allowed=["HPC", "INCONCLUSIVE"])
    assert result["verdict_pass"] is True


# --- citation grounding -----------------------------------------------------

def test_grounding_needs_two_checkable_sources():
    vague = CitationGroundingEvaluator()(references=["recent literature", "see the paper"])
    assert vague["grounded_count"] == 0
    assert vague["citations_pass"] is False

    real = CitationGroundingEvaluator()(
        references=["arXiv:2409.08910", "doi:10.1103/PhysRevA.1.1"]
    )
    assert real["grounded_count"] == 2
    assert real["citations_pass"] is True


def test_grounding_fails_on_a_proven_missing_citation():
    result = CitationGroundingEvaluator()(
        references=["arXiv:2409.08910", "arXiv:9999.99999"],
        citation_checks=[
            {"status": "resolved", "url": "https://arxiv.org/abs/2409.08910"},
            {"status": "missing", "url": "https://arxiv.org/abs/9999.99999"},
        ],
    )
    assert result["citations_resolve"] == 0.0
    assert "https://arxiv.org/abs/9999.99999" in result["missing"]


# --- the gate, watched failing ---------------------------------------------

def test_runner_gate_passes_on_current_router(monkeypatch, tmp_path):
    import agents.evaluations.run_foundry_eval as runner

    monkeypatch.setattr(runner, "RESULTS_PATH", tmp_path / "results.json")
    monkeypatch.setattr(sys, "argv", ["run_foundry_eval.py", "--offline"])
    assert runner.main() == 0


def test_runner_gate_goes_red_when_money_shot_regresses(monkeypatch, tmp_path):
    """Inject a portfolio->QUANTUM regression and confirm the gate fails."""
    import agents.evaluations.run_foundry_eval as runner
    from agents.classifier import platform_router

    real_route = platform_router.route_platform

    def regressed(problem, matches, score):
        out = real_route(problem, matches, score)
        if "portfolio" in problem.lower():
            return {**out, "platform": "QUANTUM"}
        return out

    monkeypatch.setattr(platform_router, "route_platform", regressed)
    monkeypatch.setattr(runner, "RESULTS_PATH", tmp_path / "results.json")
    monkeypatch.setattr(sys, "argv", ["run_foundry_eval.py", "--offline"])
    assert runner.main() == 1


def _cases_with_an_unrecorded_case(tmp_path: Path) -> Path:
    data = json.loads((EVAL_DIR / "cases.json").read_text(encoding="utf-8"))
    data["cases"].append({
        "id": "unrecorded-case",
        "problem": "Estimate the ground state energy of a transition-metal catalyst",
        "expect_platform": "QUANTUM",
    })
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_router_gate_fails_on_a_case_with_no_recorded_matches(monkeypatch, tmp_path):
    """A skipped case leaves the denominator, so a newly labelled case could never fail."""
    import agents.evaluations.run_eval as run_eval

    monkeypatch.setattr(run_eval, "CASES_PATH", _cases_with_an_unrecorded_case(tmp_path))
    monkeypatch.setattr(sys, "argv", ["run_eval.py", "--offline"])
    assert run_eval.main() == 2


def test_foundry_gate_fails_on_a_case_with_no_recorded_matches(monkeypatch, tmp_path):
    import agents.evaluations.run_foundry_eval as runner

    monkeypatch.setattr(runner, "CASES_PATH", _cases_with_an_unrecorded_case(tmp_path))
    monkeypatch.setattr(runner, "RESULTS_PATH", tmp_path / "results.json")
    monkeypatch.setattr(sys, "argv", ["run_foundry_eval.py", "--offline"])
    with pytest.raises(SystemExit) as exit_info:
        runner.main()
    assert exit_info.value.code == 2
