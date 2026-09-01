"""Query the evaluator and draw the trace of how it answered.

The response from `/api/evaluate` carries a `trace` field: every step of the
pipeline, in order, with what each one decided. This renders it as a timeline.

Why this is worth a tool rather than reading the JSON: the argument this system
makes is about *order*. `route_platform()` decides the verdict at step 1b; the
model is not called until step 4. Reading that in prose requires trusting the
author. Watching the router's bar close before the model's bar opens does not.

    python tooling/show_trace.py "Optimize a portfolio of 500 assets"
    python tooling/show_trace.py --generate-code "FeMoco ground state energy"
    python tooling/show_trace.py --base http://localhost:8000 "..."
    python tooling/show_trace.py --json trace.json      # re-render a saved trace

Exit code is 0 only if a trace came back with the expected step order.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from agents.observability.trace import render  # noqa: E402

DEFAULT_BASE = "https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io"

# The two spans whose relative order is the architectural claim.
ROUTER_SPAN = "route_platform"
MODEL_SPAN = "model call"


def evaluate(base: str, problem: str, generate_code: bool, timeout: int) -> dict:
    body = json.dumps({"problem": problem, "generate_code": generate_code}).encode()
    request = urllib.request.Request(
        f"{base}/api/evaluate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def find_span(spans: list, needle: str) -> dict | None:
    for entry in spans:
        if needle in entry.get("name", ""):
            return entry
    return None


def find_all(spans: list, needle: str) -> list:
    return [entry for entry in spans if needle in entry.get("name", "")]


def check_ordering(trace: dict) -> int:
    """Assert the router finished before the model started.

    This is the check, not the picture. A timeline that looks right but is not
    asserted is decoration, and this repo has shipped enough of those.

    It looks at *every* routing span, not the first one. The first version of
    this function compared only the earliest match, which meant a second routing
    decision inserted after the model call passed silently - the check was
    measuring something adjacent to the claim rather than the claim.
    """
    spans = trace.get("spans") or []
    routers = find_all(spans, ROUTER_SPAN)
    models = find_all(spans, MODEL_SPAN)

    if not routers:
        print(f"\nFAIL: no span matching '{ROUTER_SPAN}' - the pipeline is not traced.")
        return 1
    if not models:
        # A cached or short-circuited path may legitimately skip the model.
        print(f"\nNote: no '{MODEL_SPAN}' span in this trace; ordering not applicable.")
        return 0

    if len(routers) > 1:
        print(f"\nFAIL: {len(routers)} routing spans "
              f"({', '.join(r['name'] for r in routers)}).\nThe verdict is decided in more "
              "than one place, so 'decided before the model ran' is no longer well defined.")
        return 1

    first_model_start = min(m.get("start_ms") or 0 for m in models)
    last_router_end = max((r.get("start_ms") or 0) + (r.get("duration_ms") or 0)
                          for r in routers)
    router = routers[0]
    model = models[0]

    if last_router_end <= first_model_start:
        gap = first_model_start - last_router_end
        print(
            f"\nOrdering holds: the verdict was decided {gap:.1f} ms before the model "
            f"was called,\nand the router took {router.get('duration_ms'):.1f} ms against "
            f"the model's {model.get('duration_ms', 0) / 1000:.1f} s."
        )
        return 0

    print(
        f"\nFAIL: the router closed at {last_router_end:.1f} ms but the model started at "
        f"{first_model_start:.1f} ms.\nThe verdict is no longer decided before the model "
        "runs - that is the claim every doc in docs/AzureFriday/ makes."
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("problem", nargs="?", help="the problem to evaluate")
    parser.add_argument("--base", default=DEFAULT_BASE, help="evaluator API base URL")
    parser.add_argument("--generate-code", action="store_true",
                        help="also generate Q# or Bicep, which adds the codegen spans")
    parser.add_argument("--timeout", type=int, default=600, help="request timeout, seconds")
    parser.add_argument("--json", dest="json_path",
                        help="render a saved trace or response instead of calling the API")
    parser.add_argument("--save", help="write the trace JSON here")
    parser.add_argument("--width", type=int, default=44, help="timeline width in characters")
    args = parser.parse_args()

    if args.json_path:
        payload = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
        trace = payload.get("trace", payload)
    else:
        if not args.problem:
            parser.error("give a problem to evaluate, or --json to re-render a saved one")
        try:
            payload = evaluate(args.base, args.problem, args.generate_code, args.timeout)
        except urllib.error.HTTPError as exc:
            print(f"FAIL: HTTP {exc.code} from {args.base}: {exc.read()[:300]!r}")
            return 1
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL: {type(exc).__name__}: {exc}")
            return 1

        print(f"problem : {args.problem}")
        print(f"verdict : {payload.get('verdict')} / {payload.get('recommended_platform')} "
              f"at {payload.get('confidence')} confidence")
        print(f"model   : {payload.get('model_used')}  "
              f"({payload.get('tokens_used')} tokens)")
        print()
        trace = payload.get("trace") or {}

    if not trace or not trace.get("spans"):
        print("FAIL: the response carried no trace. Is this an older revision of the API?")
        return 1

    print(render(trace, width=args.width))

    if args.save:
        Path(args.save).write_text(json.dumps(trace, indent=2), encoding="utf-8")
        print(f"\nsaved to {args.save}")

    return check_ordering(trace)


if __name__ == "__main__":
    sys.exit(main())
