"""End-to-end request tracing for the evaluator.

Why this exists rather than logging
-----------------------------------
The central architectural claim of this system is an *ordering* claim: the
verdict is decided by `route_platform()` at step 1b, before the model is called
at step 4. Every document in `docs/AzureFriday/` asserts it, and until now the
only evidence was reading `evaluate()` and taking the author's word for it.

A trace makes that claim checkable. Each step records when it started, how long
it took and - the part that matters - *what it decided*. Reading a trace tells
you why an answer came out the way it did, not merely how fast it was. If the
router's span closes before the model's span opens, the ordering claim is true
for that specific request, and `agents/tests/test_trace_ordering.py` asserts
exactly that against a real evaluation.

Two sinks, on purpose
---------------------
1. **In-process, always on.** Spans are collected per request and returned in
   the API response under `trace`. No configuration, no network, no portal, and
   no ingestion delay - you see the trace for the request you just made, in the
   response to that request. This is what makes it demonstrable live.

2. **Azure Monitor, when configured.** If `APPLICATIONINSIGHTS_CONNECTION_STRING`
   is set *and* `azure-monitor-opentelemetry` is installed, the same spans are
   mirrored to Application Insights for durable, queryable history across
   requests. Neither is required for sink 1 to work.

The second sink is deliberately optional and deliberately cannot break the
first. A telemetry exporter that takes the API down with it is worse than no
telemetry, so every OpenTelemetry call here is wrapped and failures degrade to
"local tracing only" rather than propagating.

Usage
-----
    from agents.observability.trace import start_trace, span, trace_payload

    with start_trace("evaluate") as tr:
        with span("kb.classify_problem") as s:
            ...
            s.set(match_count=len(matches), top_score=score)
        payload = trace_payload()
"""

from __future__ import annotations

import contextvars
import os
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

# How many spans a single trace will hold. A runaway loop that opens spans
# forever should degrade the trace, not exhaust the container's memory.
MAX_SPANS = 200

# Attribute values are truncated before they are stored. A span attribute is a
# label, not a payload: the generated Q# belongs in the response body, not
# repeated inside the telemetry for it.
MAX_ATTR_CHARS = 400

_current_trace: contextvars.ContextVar[Optional["Trace"]] = contextvars.ContextVar(
    "qgc_current_trace", default=None
)
_current_span: contextvars.ContextVar[Optional["Span"]] = contextvars.ContextVar(
    "qgc_current_span", default=None
)


def _clip(value: Any) -> Any:
    """Keep attributes small and JSON-safe."""
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    text = value if isinstance(value, str) else repr(value)
    if len(text) > MAX_ATTR_CHARS:
        return text[:MAX_ATTR_CHARS] + f"... ({len(text)} chars)"
    return text


class Span:
    """One step of the pipeline, with what it decided attached to it."""

    __slots__ = (
        "name", "start_ms", "duration_ms", "attributes", "status",
        "error", "depth", "_started", "_otel",
    )

    def __init__(self, name: str, start_ms: float, depth: int):
        self.name = name
        self.start_ms = start_ms
        self.duration_ms: Optional[float] = None
        self.attributes: Dict[str, Any] = {}
        self.status = "ok"
        self.error: Optional[str] = None
        self.depth = depth
        self._started = time.perf_counter()
        self._otel = None

    def set(self, **attributes: Any) -> "Span":
        """Record what this step decided. Chainable."""
        for key, value in attributes.items():
            self.attributes[key] = _clip(value)
            if self._otel is not None:
                try:
                    otel_value = value if isinstance(value, (str, int, float, bool)) else repr(value)
                    self._otel.set_attribute(key, _clip(otel_value))
                except Exception:  # noqa: BLE001 - telemetry must not break the request
                    pass
        return self

    def _finish(self, error: Optional[BaseException] = None) -> None:
        self.duration_ms = round((time.perf_counter() - self._started) * 1000, 1)
        if error is not None:
            self.status = "error"
            self.error = f"{type(error).__name__}: {str(error)[:200]}"

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "name": self.name,
            "start_ms": round(self.start_ms, 1),
            "duration_ms": self.duration_ms,
            "depth": self.depth,
        }
        if self.attributes:
            out["attributes"] = self.attributes
        if self.status != "ok":
            out["status"] = self.status
        if self.error:
            out["error"] = self.error
        return out


class Trace:
    """A request's worth of spans, in the order they were opened."""

    def __init__(self, name: str, trace_id: Optional[str] = None):
        self.name = name
        self.trace_id = trace_id or uuid.uuid4().hex
        self.started_utc = datetime.now(timezone.utc).isoformat()
        self.spans: List[Span] = []
        self.truncated = False
        # Set when Azure export is on: the id to search for in Application
        # Insights (`operation_Id`). Without it you have a local trace and a
        # portal full of records with no way to line the two up.
        self.otel_operation_id: Optional[str] = None
        self._origin = time.perf_counter()
        self._lock = threading.Lock()

    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self._origin) * 1000

    def add(self, span_obj: Span) -> bool:
        with self._lock:
            if len(self.spans) >= MAX_SPANS:
                self.truncated = True
                return False
            self.spans.append(span_obj)
            return True

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "trace_id": self.trace_id,
            "name": self.name,
            "started_utc": self.started_utc,
            "total_ms": round(self.elapsed_ms(), 1),
            "spans": [s.to_dict() for s in self.spans],
            "truncated": self.truncated,
            "exported_to_app_insights": _exporter_ready(),
        }
        if self.otel_operation_id:
            payload["operation_id"] = self.otel_operation_id
        return payload


# ---------------------------------------------------------------------------
# Azure Monitor bridge - optional, and never load-bearing
# ---------------------------------------------------------------------------

_otel_state = {"tried": False, "tracer": None, "reason": "not initialised"}
_otel_lock = threading.Lock()


def _init_exporter() -> None:
    """Wire up Azure Monitor once, if it is both configured and installed.

    Called lazily so that importing this module has no side effects and no
    import-time cost for the local-only path.
    """
    if _otel_state["tried"]:
        return
    with _otel_lock:
        if _otel_state["tried"]:
            return
        _otel_state["tried"] = True

        if os.environ.get("QGC_TRACE_TO_AZURE", "1") == "0":
            _otel_state["reason"] = "disabled by QGC_TRACE_TO_AZURE=0"
            return

        connection = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "").strip()
        if not connection:
            _otel_state["reason"] = "APPLICATIONINSIGHTS_CONNECTION_STRING is not set"
            return

        try:
            from azure.monitor.opentelemetry import configure_azure_monitor
            from opentelemetry import trace as otel_trace

            configure_azure_monitor(
                connection_string=connection,
                logger_name="qgc",
                # The API's own instrumentation is what we care about; the
                # distro's HTTP auto-instrumentation would also capture every
                # call the model client makes, which is noise at this volume.
                instrumentation_options={
                    "fastapi": {"enabled": True},
                    "django": {"enabled": False},
                    "flask": {"enabled": False},
                    "psycopg2": {"enabled": False},
                },
            )
            _otel_state["tracer"] = otel_trace.get_tracer("qgc.evaluator")
            _otel_state["reason"] = "ok"
        except ImportError as exc:
            _otel_state["reason"] = f"azure-monitor-opentelemetry not installed ({exc})"
        except Exception as exc:  # noqa: BLE001 - a bad connection string must not 500 the API
            _otel_state["reason"] = f"{type(exc).__name__}: {str(exc)[:160]}"


def _exporter_ready() -> bool:
    return _otel_state["tracer"] is not None


def exporter_status() -> Dict[str, Any]:
    """Why Azure export is or is not happening. Surfaced on the health endpoint.

    A silent no-op exporter is the failure this repo has already shipped twice,
    so the reason is always reportable rather than inferred from an absence.
    """
    _init_exporter()
    return {
        "enabled": _exporter_ready(),
        "reason": _otel_state["reason"],
        "local_tracing": True,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@contextmanager
def start_trace(name: str, trace_id: Optional[str] = None) -> Iterator[Trace]:
    """Begin a trace for one request and make it current.

    When Azure export is on, this also opens a single root OpenTelemetry span for
    the whole request. That root is what correlates the steps: without it every
    step arrived in Application Insights under its own `operation_Id`, so the
    portal showed twenty unrelated dependencies instead of one request tree, and
    the end-to-end view this module exists to provide did not exist. Relying on
    the FastAPI auto-instrumentation for that root is not enough - it only hooks
    apps that were created after `configure_azure_monitor()` ran.
    """
    _init_exporter()
    trace_obj = Trace(name, trace_id=trace_id)
    token = _current_trace.set(trace_obj)
    span_token = _current_span.set(None)

    root_cm = None
    tracer = _otel_state["tracer"]
    if tracer is not None:
        try:
            from opentelemetry.trace import SpanKind

            root_cm = tracer.start_as_current_span(name, kind=SpanKind.SERVER)
            root_span = root_cm.__enter__()
            try:
                # Lets you jump from a response straight to the portal record.
                root_span.set_attribute("qgc.trace_id", trace_obj.trace_id)
                context = root_span.get_span_context()
                trace_obj.otel_operation_id = format(context.trace_id, "032x")
            except Exception:  # noqa: BLE001
                pass
        except Exception:  # noqa: BLE001
            root_cm = None

    try:
        yield trace_obj
    except BaseException as exc:
        if root_cm is not None:
            try:
                root_cm.__exit__(type(exc), exc, exc.__traceback__)
            except Exception:  # noqa: BLE001
                pass
            root_cm = None
        raise
    finally:
        if root_cm is not None:
            try:
                root_cm.__exit__(None, None, None)
            except Exception:  # noqa: BLE001
                pass
        _current_trace.reset(token)
        _current_span.reset(span_token)


def current_trace() -> Optional[Trace]:
    return _current_trace.get()


@contextmanager
def span(name: str, **attributes: Any) -> Iterator[Span]:
    """Record one step.

    Safe to use when no trace is active - it yields a detached span that goes
    nowhere. That means the orchestrator can be instrumented once and still run
    unchanged from the CLI, from pytest, or from the ingestion job.
    """
    trace_obj = _current_trace.get()
    parent = _current_span.get()
    depth = 0 if parent is None else parent.depth + 1

    if trace_obj is None:
        detached = Span(name, 0.0, depth)
        if attributes:
            detached.set(**attributes)
        try:
            yield detached
        finally:
            detached._finish()
        return

    span_obj = Span(name, trace_obj.elapsed_ms(), depth)
    recorded = trace_obj.add(span_obj)

    otel_cm = None
    tracer = _otel_state["tracer"]
    if tracer is not None and recorded:
        try:
            otel_cm = tracer.start_as_current_span(name)
            span_obj._otel = otel_cm.__enter__()
        except Exception:  # noqa: BLE001
            otel_cm = None
            span_obj._otel = None

    if attributes:
        span_obj.set(**attributes)

    token = _current_span.set(span_obj)
    try:
        yield span_obj
    except BaseException as exc:
        span_obj._finish(error=exc)
        if otel_cm is not None:
            try:
                otel_cm.__exit__(type(exc), exc, exc.__traceback__)
            except Exception:  # noqa: BLE001
                pass
            otel_cm = None
        raise
    else:
        span_obj._finish()
    finally:
        _current_span.reset(token)
        if otel_cm is not None:
            try:
                otel_cm.__exit__(None, None, None)
            except Exception:  # noqa: BLE001
                pass


def trace_payload() -> Dict[str, Any]:
    """The current trace as a JSON-safe dict, or an empty dict if none."""
    trace_obj = _current_trace.get()
    return trace_obj.to_dict() if trace_obj is not None else {}


def annotate(**attributes: Any) -> None:
    """Attach attributes to the innermost open span, if there is one."""
    span_obj = _current_span.get()
    if span_obj is not None:
        span_obj.set(**attributes)


def render(trace_dict: Dict[str, Any], width: int = 44,
           only: Optional[List[str]] = None) -> str:
    """Draw a trace as a text timeline.

    This is what turns a list of timings into something you can hand to someone
    who has never seen the codebase: the bars show that the router finished
    before the model started, which is the whole argument.

    `only` restricts which attributes are printed. The full set is right for
    debugging and too dense to read on a shared screen - a 17-digit float and a
    full sentence of routing reason are noise when the point is the order.
    """
    spans = trace_dict.get("spans") or []
    if not spans:
        return "(no spans recorded)"

    total = trace_dict.get("total_ms") or 0.0
    for entry in spans:
        end = (entry.get("start_ms") or 0) + (entry.get("duration_ms") or 0)
        total = max(total, end)
    total = max(total, 1.0)

    label_width = max(len(f"{'  ' * s.get('depth', 0)}{s['name']}") for s in spans)
    label_width = min(max(label_width, 18), 46)

    lines = [
        f"trace {trace_dict.get('trace_id', '?')}   {trace_dict.get('name', '')}   "
        f"{total:.0f} ms total"
    ]
    if trace_dict.get("exported_to_app_insights"):
        operation_id = trace_dict.get("operation_id")
        if operation_id:
            lines.append(f"Application Insights: operation_Id == \"{operation_id}\"")
        else:
            lines.append("also exported to Application Insights")
    lines.append("")

    for entry in spans:
        start = entry.get("start_ms") or 0.0
        duration = entry.get("duration_ms") or 0.0
        label = f"{'  ' * entry.get('depth', 0)}{entry['name']}"[:label_width]

        lead = int(round(width * start / total))
        length = max(1, int(round(width * duration / total)))
        lead = min(lead, width - 1)
        length = min(length, width - lead)
        bar = " " * lead + ("#" * length)
        bar = bar.ljust(width)

        marker = "  " if entry.get("status", "ok") == "ok" else " !"
        lines.append(f"{label.ljust(label_width)} |{bar}| {duration:8.1f} ms{marker}")

        for key, value in (entry.get("attributes") or {}).items():
            if only is not None and key not in only:
                continue
            if isinstance(value, float):
                value = round(value, 4)
            lines.append(f"{' ' * label_width}  {key}={value}")
        if entry.get("error"):
            lines.append(f"{' ' * label_width}  ERROR {entry['error']}")

    return "\n".join(lines)
