# Tracing: how to see what the evaluator did

Every call to `POST /api/evaluate` records what each step of the pipeline decided
and returns it in the response under `trace`. Nothing needs to be enabled for
that, and there is no portal round-trip: the trace for the request you just made
comes back in the answer to that request.

The point is not performance monitoring. It is that this system makes an
*ordering* claim - the verdict is decided by `route_platform()` before the model
is ever called - and a trace is the only way to show that rather than assert it.

## Look at one

```powershell
python tooling/show_trace.py "Optimize a portfolio of 500 assets using mean-variance optimisation"
```

Add `--demo` to print only the attributes that carry the argument. The full set is right
for debugging and too dense for a shared screen - a seventeen-digit float and a sentence
of routing reason are noise when the point is the order of two spans.

Measured against the live API on 2026-09-01:

```
trace ec71b682cdd8449e85d81c551bf23180   POST /api/evaluate   36387 ms total

1. kb.classify_problem                       |######                                      |   5040.0 ms
                                              top_match=Probabilistic Sampling (Quantum Supremacy)
                                              top_score=0.01666666753590107
                                              kb_verdict=QUANTUM_ADVANTAGE
                                              model_called=False
1b. route_platform  <-- VERDICT DECIDED HERE |      #                                     |      0.1 ms
                                              verdict=HPC_PREFERRED
                                              platform=HPC
                                              confidence=0.8
                                              model_called=False
...
4. model call                                |      ######################################|  31334.1 ms
                                              verdict_already_decided=HPC_PREFERRED
                                              model_used=gpt-5.6-luna-2026-07-09
6. merge  <-- router's verdict wins          |                                           #|      0.0 ms
                                              published_verdict=HPC_PREFERRED
                                              dissent_recorded=False
```

Three things are visible there that are otherwise a matter of trust.

**The retrieval bug and its fix, in one screen.** The top hit for portfolio
optimisation is still *Probabilistic Sampling (Quantum Supremacy)* and the raw
knowledge-base verdict is still `QUANTUM_ADVANTAGE`. That is the failure the
storyboard describes. The score is `0.0167`, the relevance gate rejects it, and
the router publishes `HPC_PREFERRED`. The trace shows the wrong answer being
found *and* declined.

**The verdict costs 0.1 ms; the prose costs 31 seconds.** The expensive part of
this system is not the part that decides.

**The model did not get a vote.** `route_platform` closes before `model call`
opens, and step 6 records `published_verdict` alongside whatever the model
proposed. When the two differ, `dissent_recorded=True` and `dissent_applied` is
still `False`.

## The ordering claim is a test, not a picture

A timeline that looks right and is never asserted is decoration. Two things
check it:

- `agents/tests/test_trace_ordering.py` runs the real `evaluate()` against a
  stubbed knowledge base and a stubbed model, offline, and fails if any routing
  span starts after the model span.
- `tooling/show_trace.py` makes the same assertion against whatever API you point
  it at, and exits non-zero if it does not hold.

Both were confirmed to fail before they were trusted. A second `route_platform`
span was inserted after the model call on purpose; the first version of the check
**passed anyway**, because it compared only the first span whose name matched and
never saw the second. It now looks at every routing span, and the sabotage
produces:

```
AssertionError: expected exactly one routing span, found 2
AssertionError: 1 routing span(s) start after the model call
```

## Application Insights

The same spans go to Application Insights when
`APPLICATIONINSIGHTS_CONNECTION_STRING` is set. The local trace does not depend
on it - if the exporter is misconfigured you lose durable history, not the
request.

| | |
|---|---|
| Component | `qgc-eval-insights` (resource group `qgc-evaluator`) |
| Backed by | the Log Analytics workspace the Container App environment already used |
| Set on | Container App `qgc-eval-api`, as an environment variable |

Whether it is working is reported, never inferred:

```powershell
Invoke-RestMethod "https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io/"
# tracing: { enabled, reason, local_tracing }
```

`reason` says *why* export is off - not set, not installed, or the exception the
exporter raised. An exporter that silently does nothing has already shipped here
twice; this one has to explain itself.

### Finding a request in the portal

Every response carries `trace.operation_id`. That is the `operation_Id` in
Application Insights, so a single query returns the whole request:

```kusto
union requests, dependencies
| where operation_Id == "4de80f722fb52573386dfd92ba125af0"
| project itemType, name, duration, timestamp
| order by timestamp asc
```

Which returns the request and its steps together - measured on 2026-09-01, 17
rows for one call:

```
request      POST /api/evaluate                                 43,495 ms
dependency     1. kb.classify_problem                            9,001 ms
dependency       DocumentsOperations.search_post                 3,902 ms
dependency         POST /indexes('quantum-algorithms')/docs/...  2,383 ms
dependency     1b. route_platform  <-- VERDICT DECIDED HERE          0 ms
dependency     4. model call                                    31,943 ms
dependency     8. verify_citations                               1,441 ms
```

The Azure AI Search call nested inside `kb.classify_problem` and the managed
identity token fetches come from the distro's auto-instrumentation; the numbered
steps are ours.

> This correlation was broken in the first working version and the telemetry
> still arrived. Every step landed under its own `operation_Id`, so the portal
> held twenty unrelated dependencies and could not answer "what happened during
> this request" - data present, question unanswerable. `start_trace()` now opens
> one root span per request. `test_operation_id_is_present_exactly_when_export_is_on`
> guards it.

### Queries worth keeping

Where the time goes, across every request:

```kusto
dependencies
| where timestamp > ago(24h) and name startswith_cs "1." or name startswith_cs "4."
| summarize p50=percentile(duration,50), p95=percentile(duration,95), n=count() by name
| order by p95 desc
```

Every case where the model disagreed and was overruled:

```kusto
dependencies
| where name has "merge"
| extend d = parse_json(customDimensions)
| where tostring(d.dissent_recorded) == "True"
| project timestamp, operation_Id,
          published=tostring(d.published_verdict),
          model_wanted=tostring(d.model_proposed_verdict)
```

Citations the model invented and the gate rejected:

```kusto
dependencies
| where name has "verify_citations"
| extend d = parse_json(customDimensions)
| where toint(d.rejected) > 0
| project timestamp, operation_Id, proposed=toint(d.proposed), rejected=toint(d.rejected)
```

Q# that needed more than one compile attempt:

```kusto
dependencies
| where name startswith "codegen.attempt"
| extend d = parse_json(customDimensions)
| summarize attempts=count(), compiled=countif(tostring(d.compiled)=="True") by operation_Id
| where attempts > 1
```

## Adding a step

Instrumenting a new step is one context manager. Record what it *decided*, not
just that it ran - a duration tells you the system was slow, an attribute tells
you why the answer is what it is.

```python
from agents.observability.trace import span

with span("11. my_step", note="what this is for") as s:
    result = do_the_work()
    s.set(rows=len(result), chose=result.winner)
```

Outside a request the same code is a no-op, so the orchestrator still runs
unchanged from the CLI, from pytest and from the ingestion job.

## Cost and payload

Application Insights bills on ingested volume, with 5 GB per month included. At
roughly 17 records per evaluation this is far inside the free grant; the
scheduled uptime probe is the only steady traffic.

The inline trace adds 1-2 KB to a response that already carries the explanation,
the citations and often generated Q#. Attribute values are truncated at 400
characters, and a trace is capped at 200 spans.

## Turning it off

| Variable | Effect |
|---|---|
| `APPLICATIONINSIGHTS_CONNECTION_STRING` unset | local tracing only; the response still carries `trace` |
| `QGC_TRACE_TO_AZURE=0` | keeps the connection string but stops exporting |
| `CLARITY_PROJECT_ID` repo variable cleared | the Clarity tag is not built into the site at all |

There is deliberately no switch that removes `trace` from the response. It is
the evidence for the claim the rest of the system is built on.

## The browser half: Microsoft Clarity

Everything above starts at `POST /api/evaluate`. The part a person actually
experiences - landing on the page, typing a problem, ticking *generate code*,
then waiting twenty to fifty seconds - is not in it. Application Insights can
tell you a request took 31 seconds. It cannot tell you whether anyone waited.

[Microsoft Clarity](https://clarity.microsoft.com/) covers that half: session
recordings, heatmaps, and rage/dead-click detection. It is free and has no
sampling. It does **not** understand backend spans, and it is not a second copy
of the trace above - the two tools each know half of a story.

### What joins them

Every evaluation sets `qgc_operation_id` as a Clarity custom tag, taken from
`trace.operation_id` in the response. So the sequence is:

1. Watch a session recording in Clarity.
2. Read the `qgc_operation_id` badge on that session.
3. Run the query from *Finding a request in the portal* above with that id.

You now have the browser interaction and the backend decisions for the same
request. Neither tool does that alone.

### Tags that are set

| Tag | Why it is worth filtering on |
|---|---|
| `qgc_operation_id` | the join to Application Insights |
| `qgc_verdict` | do people behave differently when told *no*? |
| `qgc_platform` | `QUANTUM` / `HPC` / `AI_ML` |
| `qgc_latency_bucket` | `under_10s`, `10_30s`, `30_60s`, `over_60s` - bucketed, because Clarity filters on equality |
| `qgc_code_requested` | the slow path, opted into |
| `qgc_demo_mode` | **the blind spot this closes** |

`qgc_demo_mode` is the one that earns its place. When the backend call fails the
site renders a plausible DEMO MODE page, so a broken demo and a working one look
the same from outside. The uptime probe checks the API; it has never checked what
a browser rendered. This makes that countable.

Events `qgc_evaluation_shown` and `qgc_demo_mode` are recorded too, so sessions
can be filtered by what happened rather than only by what was set.

### Turning it on and off

One repository variable, `CLARITY_PROJECT_ID`, read by
`.github/workflows/deploy-website.yml`. The site is a static export, so the value
is inlined at build time: clear the variable, re-run the workflow, and the tag is
gone from the bundle entirely. There is no runtime switch and no code change.

With it unset, `website/lib/clarity.ts` no-ops and nothing is requested -
verified by building both ways and grepping the output.

### Verified in a browser, not in the bundle

`website/scripts/verify-clarity.mjs` drives the built site in Chromium, stubs the
Clarity CDN, and asserts on the arguments actually passed to `clarity()` - both
for a good response and for a failed one. It runs in the deploy workflow when the
variable is set.

Grepping the bundle for `clarity.ms` would have been shape. It was watched
failing first: rebuilt with the variable cleared, the verifier reports 2/11 with
`nothing fetched clarity.ms/tag/ - loadClarity() did not run`. The two that still
pass are the two that should - no DEMO MODE tag, and no page errors, which is
also the evidence that the site is unharmed with Clarity off.

### What it will not do

- It cannot show the pipeline. There is no Clarity view in which
  `route_platform` precedes the model call; that is the timeline above.
- It records the public demo site only. The API has no browser.
- Text is masked by default. Recordings show *that* someone typed a problem, not
  necessarily what they typed - the verdict tag is the reliable signal.

### A note for the recording

Do not demo Clarity on Azure Friday. The brief is 6-9 minutes and explicitly not
a feature parade, and a session replay of yourself is not interesting television.
Its value is the traffic the episode drives afterwards, which is the one moment
this project will have real users to learn from.

