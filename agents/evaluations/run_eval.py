#!/usr/bin/env python3
"""Score the deterministic platform router against labelled cases.

Why this exists: before this harness there was no way to tell whether a change to
the router, the filters or the knowledge base made verdicts better or worse. The
only evidence was running a demo prompt by hand and seeing whether it looked right.

Two things are measured:

  accuracy    Does the routed platform match the label?
  consistency Do paraphrases of the same problem route the same way? A verdict that
              changes when you rename "RSA integer" to "RSA key" is not a verdict.

Modes:
  --offline   Use the recorded knowledge-base matches in cases_kb_cache.json.
              Deterministic and needs no Azure, so it can run in CI.
  (default)   Query the live knowledge base and refresh the cache.

Exit code is non-zero if accuracy or consistency falls below the thresholds, so
this can gate a pull request.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CASES_PATH = HERE / "cases.json"
CACHE_PATH = HERE / "cases_kb_cache.json"

MIN_ACCURACY = 0.80
MIN_CONSISTENCY = 1.00  # paraphrases must never disagree


def load_cases() -> list[dict]:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]


def kb_matches_live(kb, problem: str) -> tuple[list, float]:
    result = kb.classify_problem(problem)
    matches = result.get("matches", [])
    score = matches[0].get("score", 0) if matches else 0
    return matches, score


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="use recorded KB matches instead of querying Azure")
    ap.add_argument("--min-accuracy", type=float, default=MIN_ACCURACY)
    args = ap.parse_args()

    sys.path.insert(0, str(REPO))
    from agents.classifier.platform_router import classify_electronic_structure, route_platform

    cases = load_cases()
    cache: dict[str, dict] = {}
    if args.offline:
        if not CACHE_PATH.exists():
            print(f"No cache at {CACHE_PATH.name}. Run once without --offline to build it.")
            return 2
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))["cases"]
        kb = None
    else:
        from knowledge.search.kb_client import QuantumKnowledgeBase
        kb = QuantumKnowledgeBase()

    results = []
    fresh_cache: dict[str, dict] = {}

    for case in cases:
        problem = case["problem"]
        if args.offline:
            entry = cache.get(case["id"])
            if entry is None:
                print(f"  {case['id']}: not in cache, skipping")
                continue
            matches, score = entry["matches"], entry["score"]
        else:
            matches, score = kb_matches_live(kb, problem)
            fresh_cache[case["id"]] = {"matches": matches, "score": score}

        routing = route_platform(problem, matches, score)
        actual = routing.get("platform")
        structure = classify_electronic_structure(problem)

        # Underspecified problems have more than one defensible answer; what matters
        # is that they do not get a confident quantum verdict.
        allowed = case.get("expect_platform_in") or [case["expect_platform"]]
        expected = "|".join(allowed)

        ok = actual in allowed
        struct_ok = ("expect_structure_class" not in case
                     or structure == case["expect_structure_class"])

        results.append({
            "id": case["id"],
            "expected": expected,
            "actual": actual,
            "pass": ok and struct_ok,
            "structure": structure,
            "expect_structure": case.get("expect_structure_class"),
            "group": case.get("paraphrase_group"),
            "adversarial": case.get("adversarial"),
        })

    if not results:
        print("No cases evaluated.")
        return 2

    # Accuracy
    passed = sum(1 for r in results if r["pass"])
    accuracy = passed / len(results)

    print(f"{'case':<26} {'expected':<18} {'actual':<10} {'structure':<10} result")
    for r in results:
        flag = "ok" if r["pass"] else "FAIL"
        print(f"{r['id']:<26} {r['expected']:<18} {str(r['actual']):<10} {r['structure']:<10} {flag}")

    adversarial = [r for r in results if r["adversarial"]]
    if adversarial:
        adv_passed = sum(1 for r in adversarial if r["pass"])
        print()
        print(f"adversarial {adv_passed}/{len(adversarial)} passed")
        for r in adversarial:
            if not r["pass"]:
                print(f"  {r['id']} ({r['adversarial']}): expected {r['expected']}, got {r['actual']}")

    # Paraphrase consistency
    groups: dict[str, list] = defaultdict(list)
    for r in results:
        if r["group"]:
            groups[r["group"]].append(r)

    inconsistent = []
    for name, members in groups.items():
        platforms = {m["actual"] for m in members}
        if len(platforms) > 1:
            inconsistent.append((name, platforms))

    consistency = 1.0 if not groups else (len(groups) - len(inconsistent)) / len(groups)

    print()
    print(f"accuracy    {passed}/{len(results)} = {accuracy:.0%}  (threshold {args.min_accuracy:.0%})")
    print(f"consistency {len(groups) - len(inconsistent)}/{len(groups)} paraphrase groups agree"
          f"  (threshold {MIN_CONSISTENCY:.0%})")
    for name, platforms in inconsistent:
        print(f"  group '{name}' disagrees: {sorted(platforms)}")

    if fresh_cache:
        CACHE_PATH.write_text(
            json.dumps({"schema_version": "1.0", "cases": fresh_cache}, indent=2),
            encoding="utf-8",
        )
        print(f"\nKB matches cached to {CACHE_PATH.name} for --offline runs")

    failed = accuracy < args.min_accuracy or consistency < MIN_CONSISTENCY
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
