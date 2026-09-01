"""The verdict must be decided before the model is called.

This is the load-bearing claim of the whole system. `docs/AzureFriday/script.md`
puts it on a slide: `route_platform()` runs at step 1b, the model at step 4, so
the answer cannot be something the model talked us into. Until the pipeline was
traced, the only evidence was reading `evaluate()` and believing the comments.

These tests assert it from the recorded trace instead. They use a stubbed
knowledge base and a stubbed model client, so they run offline in CI and still
exercise the real `QuantumEvaluator.evaluate()` control flow - the ordering
being checked is the ordering the production path actually takes.

`tooling/show_trace.py` makes the same assertion against the live API.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents.observability.trace import (  # noqa: E402
    exporter_status,
    render,
    span,
    start_trace,
    trace_payload,
)

ROUTER_SPAN = "route_platform"
MODEL_SPAN = "model call"


# ---------------------------------------------------------------------------
# Stubs: a knowledge base and a chat client that behave like the real ones
# ---------------------------------------------------------------------------

class _StubKB:
    """Mimics QuantumKnowledgeBase for the three calls evaluate() makes."""

    def classify_problem(self, problem):
        return {
            "verdict": "QUANTUM_ADVANTAGE",
            "best_algorithm": "Probabilistic Sampling",
            "speedup_class": "exponential",
            "filters": {},
            # A deliberately irrelevant top hit with a low score: this is the
            # real failure the relevance gate exists to catch.
            "matches": [{
                "name": "Probabilistic Sampling (Quantum Supremacy)",
                "score": 0.0167,
                "speedup_class": "exponential",
                "troyer_verdict": "QUANTUM_ADVANTAGE",
            }],
        }

    def find_similar_problems(self, problem):
        return [{"problem_id": "01_hubbard"}]

    def search_papers(self, problem):
        return []


class _StubMessage:
    def __init__(self, content):
        self.content = content


class _StubChoice:
    def __init__(self, content):
        self.message = _StubMessage(content)
        self.finish_reason = "stop"


class _StubUsage:
    total_tokens = 1234


class _StubResponse:
    def __init__(self, content):
        self.choices = [_StubChoice(content)]
        self.model = "stub-model"
        self.usage = _StubUsage()


class _StubCompletions:
    def __init__(self, payload, delay):
        self._payload = payload
        self._delay = delay

    def create(self, **kwargs):
        # A measurable delay, so "the router finished first" cannot pass by
        # accident on a clock with millisecond resolution.
        time.sleep(self._delay)
        return _StubResponse(self._payload)


class _StubChatClient:
    def __init__(self, payload, delay=0.05):
        self.chat = type("_Chat", (), {"completions": _StubCompletions(payload, delay)})()


@pytest.fixture()
def traced_evaluation(monkeypatch):
    """Run the real evaluate() against stubs and return (result, trace)."""
    from agents.orchestrator import evaluate as evaluate_module

    model_json = (
        '{"verdict": "QUANTUM_ADVANTAGE", "recommended_platform": "QUANTUM", '
        '"advantage_class": "exponential", "recommended_algorithm": "QPE", '
        '"explanation": "stub", "red_flags": [], "hpc_alternative": "", '
        '"references": []}'
    )

    evaluator = evaluate_module.QuantumEvaluator.__new__(evaluate_module.QuantumEvaluator)
    evaluator.kb = _StubKB()
    evaluator.last_diagnostics = {}

    monkeypatch.setattr(evaluator, "_get_chat_client",
                        lambda: _StubChatClient(model_json), raising=False)
    monkeypatch.setattr(evaluator, "_get_deployment", lambda: "stub-deployment", raising=False)
    monkeypatch.setattr(evaluate_module, "USE_AGENT", False, raising=False)
    monkeypatch.setattr(evaluate_module, "VERIFY_CITATIONS", False, raising=False)

    with start_trace("test") as _tr:
        result = evaluator.evaluate("Optimize a portfolio of 500 assets")
        payload = trace_payload()

    return result, payload


def _find(spans, needle):
    for entry in spans:
        if needle in entry["name"]:
            return entry
    return None


def _find_all(spans, needle):
    """Every span matching, not just the first.

    Using "the first match" here is how the first version of this test passed
    while the pipeline was deliberately sabotaged: a second `route_platform`
    span was inserted *after* the model call, and the assertion happily compared
    the original one. The claim is about every routing decision, so the check
    has to see all of them.
    """
    return [entry for entry in spans if needle in entry["name"]]


def _end_ms(entry):
    return entry["start_ms"] + entry["duration_ms"]


def test_trace_records_every_pipeline_step(traced_evaluation):
    _result, trace = traced_evaluation
    names = [s["name"] for s in trace["spans"]]

    for expected in ("kb.classify_problem", ROUTER_SPAN, "find_similar_problems",
                     "build_context_json", MODEL_SPAN, "parse_assessment", "merge"):
        assert _find(trace["spans"], expected) is not None, (
            f"no span for {expected!r}. Recorded: {names}"
        )


def test_router_decides_before_the_model_is_called(traced_evaluation):
    """The ordering claim, asserted rather than asserted-in-prose.

    Checks *every* routing span against the *first* model span. Anything that
    decides routing after the model has spoken breaks the claim, no matter how
    many legitimate routing spans came before it.
    """
    _result, trace = traced_evaluation
    routers = _find_all(trace["spans"], ROUTER_SPAN)
    models = _find_all(trace["spans"], MODEL_SPAN)

    assert routers, f"no routing span. Recorded: {[s['name'] for s in trace['spans']]}"
    assert models, f"no model span. Recorded: {[s['name'] for s in trace['spans']]}"

    assert len(routers) == 1, (
        f"expected exactly one routing span, found {len(routers)}: "
        f"{[r['name'] for r in routers]}.\nMore than one means the verdict is decided in "
        "more than one place, and this check can no longer say when.\n\n" + render(trace)
    )

    first_model_start = min(m["start_ms"] for m in models)
    last_router_end = max(_end_ms(r) for r in routers)

    assert last_router_end <= first_model_start, (
        "route_platform() must close before the model call opens.\n"
        f"last routing span ended at {last_router_end:.2f} ms, "
        f"first model span started at {first_model_start:.2f} ms\n\n" + render(trace)
    )


def test_nothing_routes_after_the_model_answers(traced_evaluation):
    """A second routing decision downstream of the model would be invisible above
    if the check only looked at the first one. It is called out separately so the
    failure message says what actually went wrong."""
    _result, trace = traced_evaluation
    models = _find_all(trace["spans"], MODEL_SPAN)
    first_model_start = min(m["start_ms"] for m in models)

    late = [r for r in _find_all(trace["spans"], ROUTER_SPAN)
            if r["start_ms"] >= first_model_start]
    assert not late, (
        f"{len(late)} routing span(s) start after the model call: "
        f"{[r['name'] for r in late]}.\nThe published verdict would then depend on what "
        "the model said.\n\n" + render(trace)
    )


def test_router_span_reports_it_did_not_call_a_model(traced_evaluation):
    _result, trace = traced_evaluation
    router = _find(trace["spans"], ROUTER_SPAN)
    assert router["attributes"]["model_called"] is False
    assert router["attributes"]["verdict"], "the router span must carry the verdict it chose"


def test_published_verdict_is_the_routers_not_the_models(traced_evaluation):
    """The stub model returns QUANTUM_ADVANTAGE; the router says otherwise.

    The published answer must be the router's, and the disagreement must be
    recorded rather than applied.
    """
    result, trace = traced_evaluation
    router = _find(trace["spans"], ROUTER_SPAN)
    merge = _find(trace["spans"], "merge")

    assert result["verdict"] == router["attributes"]["verdict"]
    assert merge["attributes"]["published_verdict"] == router["attributes"]["verdict"]
    assert merge["attributes"]["dissent_applied"] is False

    if result["verdict"] != "QUANTUM_ADVANTAGE":
        # The stub model proposed QUANTUM_ADVANTAGE, so this run should have
        # recorded dissent and ignored it.
        assert merge["attributes"]["dissent_recorded"] is True
        assert result["model_dissent"].get("verdict") == "QUANTUM_ADVANTAGE"


def test_trace_survives_a_failing_step():
    """An exception must close its span as an error, not lose the trace."""
    with start_trace("failure") as _tr:
        with span("step.ok"):
            pass
        with pytest.raises(ValueError):
            with span("step.boom"):
                raise ValueError("deliberate")
        payload = trace_payload()

    boom = _find(payload["spans"], "step.boom")
    assert boom["status"] == "error"
    assert "ValueError" in boom["error"]
    assert _find(payload["spans"], "step.ok")["duration_ms"] is not None


def test_span_outside_a_trace_is_a_no_op():
    """The orchestrator runs from the CLI and the ingest job with no trace open."""
    with span("orphan") as s:
        s.set(anything=1)
    assert trace_payload() == {}


def test_trace_reports_whether_azure_export_is_on():
    """A silent no-op exporter is the failure this repo has shipped twice.

    The payload always says whether the spans went anywhere, so "is telemetry
    working" is answerable from the response rather than from container logs.
    """
    with start_trace("status") as _tr:
        with span("step"):
            pass
        payload = trace_payload()

    assert "exported_to_app_insights" in payload
    status = exporter_status()
    assert status["local_tracing"] is True
    assert payload["exported_to_app_insights"] == status["enabled"]
    # Off is fine; unexplained is not.
    assert status["reason"], "the exporter must say why it is on or off"


def test_operation_id_is_present_exactly_when_export_is_on():
    """Correlation regression guard.

    The first working version exported every step under its own `operation_Id`,
    so Application Insights showed twenty unrelated dependencies instead of one
    request tree - telemetry that arrived and still could not answer "what
    happened during this request". `start_trace` now opens a root span, and the
    id it produces is returned so a response can be tied to the portal record.
    """
    with start_trace("correlation") as _tr:
        with span("step"):
            pass
        payload = trace_payload()

    if payload["exported_to_app_insights"]:
        assert payload.get("operation_id"), (
            "export is on but no operation_id was returned, so nothing links this "
            "response to the record in Application Insights"
        )
        assert len(payload["operation_id"]) == 32
    else:
        assert "operation_id" not in payload


def test_render_shows_the_order(traced_evaluation):
    _result, trace = traced_evaluation
    drawing = render(trace)
    assert ROUTER_SPAN in drawing
    assert MODEL_SPAN in drawing
    assert drawing.index(ROUTER_SPAN) < drawing.index(MODEL_SPAN)
