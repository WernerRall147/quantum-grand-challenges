#!/usr/bin/env python3
"""Score verdict quality as one number and, when asked, push it to Foundry.

Why this exists on top of run_eval.py: run_eval.py proves the router is right
offline. This wires the same labelled cases into an evaluator object that Azure
AI Foundry can host, so "verdict quality" becomes a metric a judge can watch in
the portal rather than a smoke test that only exists in CI logs.

The money shot is a tracked assertion, not a hope. `opt-portfolio` MUST route
HPC - the agent declining quantum is demo beat 2 (docs/Hackathon2026 section 8).
If routing ever regresses to a confident QUANTUM there, this exits non-zero.

Modes:
  --offline   (default) Score with the recorded KB matches in cases_kb_cache.json.
              Deterministic, no Azure, safe in CI. Produces verdict_accuracy.
  --live      Query the live knowledge base for each case instead.
  --upload    Additionally submit the run to the Foundry project so it appears in
              the portal. Requires azure-ai-evaluation and QGC_PROJECT_ENDPOINT.
              Absence is reported, never a crash - the offline number still stands.

Exit code is non-zero if verdict_accuracy falls below --min-accuracy or the money
shot regresses, so this gates a pull request the same way run_eval.py does.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO))

from agents.evaluations.verdict_evaluator import VerdictMatchEvaluator  # noqa: E402

CASES_PATH = HERE / "cases.json"
CACHE_PATH = HERE / "cases_kb_cache.json"
RESULTS_PATH = HERE / "foundry_eval_results.json"

MIN_ACCURACY = 0.80
# The case that carries demo beat 2. Declining quantum here is the point.
MONEY_SHOT_ID = "opt-portfolio"
MONEY_SHOT_EXPECTED = "HPC"


def _allowed(case: dict) -> list[str]:
    return case.get("expect_platform_in") or [case["expect_platform"]]


def route_cases(cases: list[dict], offline: bool) -> list[dict]:
    """Route every case and attach the evaluator's per-case metrics."""
    from agents.classifier.platform_router import route_platform

    if offline:
        if not CACHE_PATH.exists():
            print(f"No cache at {CACHE_PATH.name}. Run agents/evaluations/run_eval.py "
                  f"once without --offline to build it, or pass --live.")
            sys.exit(2)
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))["cases"]
        kb = None
    else:
        from knowledge.search.kb_client import QuantumKnowledgeBase
        kb = QuantumKnowledgeBase()
        cache = {}

    verdict_match = VerdictMatchEvaluator()
    rows: list[dict] = []

    for case in cases:
        if offline:
            entry = cache.get(case["id"])
            if entry is None:
                print(f"  {case['id']}: not in cache, skipping")
                continue
            matches, score = entry["matches"], entry["score"]
        else:
            result = kb.classify_problem(case["problem"])
            matches = result.get("matches", [])
            score = matches[0].get("score", 0) if matches else 0

        routing = route_platform(case["problem"], matches, score)
        metrics = verdict_match(actual=routing.get("platform"), allowed=_allowed(case))
        rows.append({
            "id": case["id"],
            "problem": case["problem"],
            "adversarial": case.get("adversarial"),
            **metrics,
        })

    return rows


def upload_to_foundry(rows: list[dict]) -> None:
    """Submit the scored cases to the Foundry project so they show in the portal.

    Lazily imported and fully guarded: a missing SDK or endpoint prints why and
    returns, because the offline verdict_accuracy is the number that gates CI and
    it must not depend on Azure being reachable.
    """
    endpoint = os.environ.get("QGC_PROJECT_ENDPOINT")
    if not endpoint:
        print("  --upload skipped: QGC_PROJECT_ENDPOINT is not set "
              "(project qgc-eval-proj endpoint).")
        return
    try:
        from azure.ai.evaluation import evaluate  # noqa: F401
    except ImportError as exc:
        print(f"  --upload skipped: azure-ai-evaluation not installed ({exc}). "
              f"Install with `pip install azure-ai-evaluation`.")
        return

    # One row per case: the input the evaluator sees and the graded outcome.
    dataset = HERE / "foundry_eval_dataset.jsonl"
    with dataset.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps({
                "id": row["id"],
                "expected": row["expected"],
                "actual": row["actual"],
                "verdict_match": row["verdict_match"],
            }) + "\n")

    # A CognitiveServices Foundry project is addressed by its endpoint, not the
    # old hub {subscription, resource_group, project} dict.
    try:
        evaluate(
            data=str(dataset),
            evaluators={"verdict_match": VerdictMatchEvaluator()},
            evaluator_config={
                "verdict_match": {"column_mapping": {
                    "expected": "${data.expected}",
                    "actual": "${data.actual}",
                }}
            },
            azure_ai_project=endpoint,
        )
        print(f"  uploaded {len(rows)} cases to Foundry project qgc-eval-proj "
              f"- view the run in the portal.")
    except Exception as exc:  # noqa: BLE001 - a portal failure must not fail the gate
        print(f"  --upload failed (offline number still stands): "
              f"{type(exc).__name__}: {str(exc)[:300]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", default=True,
                    help="score with recorded KB matches (default)")
    ap.add_argument("--live", dest="offline", action="store_false",
                    help="query the live knowledge base instead")
    ap.add_argument("--upload", action="store_true",
                    help="also submit the run to the Foundry project")
    ap.add_argument("--min-accuracy", type=float, default=MIN_ACCURACY)
    args = ap.parse_args()

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    rows = route_cases(cases, offline=args.offline)
    if not rows:
        print("No cases evaluated.")
        return 2

    passed = sum(1 for r in rows if r["verdict_pass"])
    accuracy = passed / len(rows)

    print(f"{'case':<26} {'expected':<18} {'actual':<10} result")
    for r in rows:
        flag = "ok" if r["verdict_pass"] else "FAIL"
        print(f"{r['id']:<26} {r['expected']:<18} {str(r['actual']):<10} {flag}")

    # The money shot is asserted by value, not assumed from the aggregate.
    money = next((r for r in rows if r["id"] == MONEY_SHOT_ID), None)
    money_ok = money is not None and money["actual"] == MONEY_SHOT_EXPECTED

    print()
    print(f"verdict_accuracy {passed}/{len(rows)} = {accuracy:.0%}  "
          f"(threshold {args.min_accuracy:.0%})")
    if money is None:
        print(f"money shot     MISSING: case '{MONEY_SHOT_ID}' not found")
    else:
        print(f"money shot     {MONEY_SHOT_ID} -> {money['actual']} "
              f"(must be {MONEY_SHOT_EXPECTED}): {'ok' if money_ok else 'FAIL'}")

    RESULTS_PATH.write_text(json.dumps({
        "schema_version": "1.0",
        "verdict_accuracy": accuracy,
        "passed": passed,
        "total": len(rows),
        "money_shot": {"id": MONEY_SHOT_ID, "actual": money["actual"] if money else None,
                       "expected": MONEY_SHOT_EXPECTED, "pass": money_ok},
        "cases": rows,
    }, indent=2), encoding="utf-8")
    print(f"\nmetrics written to {RESULTS_PATH.name}")

    if args.upload:
        print("\nFoundry upload:")
        upload_to_foundry(rows)

    failed = accuracy < args.min_accuracy or not money_ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
