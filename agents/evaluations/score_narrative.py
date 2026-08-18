#!/usr/bin/env python3
"""Score the LLM narrative layer against the contract its own prompt sets.

Why this exists: run_eval.py scores route_platform(), which decides the verdict.
But the verdict is not the whole answer. A reader sees the explanation, the red
flags, the references and the filter table, and every one of those comes from the
model. None of it was measured. `model_dissent` has been recorded on every single
evaluation since the router landed, and had never once been read.

Every check here is mechanical. Nothing grades a model with another model: a judge
would add variance to the thing being measured and would then need its own
validation. Each check is an assertion against the JSON the model returned.

  parse       Did the response parse as JSON at all?
  schema      Are all the keys the prompt's OUTPUT FORMAT promises present?
  enums       Are verdict, advantage_class, platform and DiVincenzo values legal?
  filters     Did the model echo the six deterministic filters it was handed, or
              quietly change one? It did not compute them, it was given them
              twice in the prompt, so a changed value is a fabrication.
  references  Did it produce the two concrete sources the prompt demands?
  honesty     If it recommends VQE or QAOA, did it carry the warning the prompt
              requires about there being at most a quadratic advantage?
  qec_codes   If it recommends QUANTUM, did it name the error-correction codes?

Dissent is reported as a rate, not a failure. The model is allowed to disagree
with the router, and evaluate.py records that under model_dissent rather than
applying it. But a rising dissent rate means the prompt has stopped landing, and
until now nothing would have noticed.

Modes:
  (default)   Call the live evaluator and record every response.
  --offline   Re-score the recorded responses. This is what CI runs. It catches
              the case where the schema contract moves and the prompt is not
              updated to match, which is how F6 came to be demanded but never
              defined.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CASES_PATH = HERE / "cases.json"
RESPONSES_PATH = HERE / "narrative_responses.json"

VERDICTS = {"QUANTUM_ADVANTAGE", "HPC_PREFERRED", "AI_ML_PREFERRED", "INCONCLUSIVE"}
PLATFORMS = {"QUANTUM", "AI_ML", "HPC", "HYBRID"}
ADVANTAGE_CLASSES = {"exponential", "superpolynomial", "quadratic", "none"}
DIVINCENZO_VALUES = {"met", "partial", "not_yet"}
DIVINCENZO_KEYS = [
    "scalable_qubits", "initialization", "coherence", "universal_gates", "measurement",
]

REQUIRED_KEYS = [
    "verdict", "confidence", "advantage_class", "recommended_algorithm",
    "recommended_platform", "platform_reason", "workspace_guidance",
    "troyer_filters", "divincenzo_assessment", "red_flags",
    "hpc_alternative", "ai_alternative", "explanation",
    "similar_problems", "references",
]

FILTER_KEYS = [
    "F1_proven_speedup", "F2_io_survives", "F3_qec_survives",
    "F4_naturally_quantum", "F5_crossover_feasible", "F6_state_preparation",
]

# A reference counts as grounded only if it can be looked up. "Recent literature"
# cannot; "arXiv:2409.08910" can.
CITATION_PATTERNS = [
    r"arxiv[:\s/]*\d{4}\.\d{4,5}",
    r"\b\d{4}\.\d{4,5}\b",
    r"errorcorrectionzoo\.org",
    r"learn\.microsoft\.com",
    r"doi[:\s/]",
    r"https?://",
    r"[A-Za-z]{3,}\s+(?:et al\.?,?\s*)?(?:19|20)\d{2}\b",
]

WEAK_ALGORITHM_MARKERS = ("VQE", "QAOA", "VARIATIONAL")
WARNING_MARKERS = (
    "quadratic", "no proven", "not proven", "unproven", "heuristic",
    "no guarantee", "no rigorous", "lacks a proven", "no asymptotic",
    "at most", "barren plateau",
)

PASS, FAIL, NA = "pass", "fail", "n/a"

# Set from the measured baseline. Anything a well-formed answer must always do is
# pinned at 1.00; the rest sit just under the observed rate so ordinary variance
# does not fail a build but a real regression does.
THRESHOLDS = {
    "parse": 1.00,
    "schema": 1.00,
    "enums": 1.00,
    "filters": 1.00,
    "references": 0.90,
    "honesty": 1.00,
    "qec_codes": 0.90,
}


def _is_grounded(ref: str) -> bool:
    return any(re.search(p, ref, re.IGNORECASE) for p in CITATION_PATTERNS)


def check_parse(record: dict, _a: dict | None) -> tuple[str, str]:
    if record.get("parse_ok"):
        return PASS, ""
    return FAIL, f"unparsable (finish_reason={record.get('finish_reason')})"


def check_schema(_record: dict, a: dict) -> tuple[str, str]:
    missing = [k for k in REQUIRED_KEYS if k not in a]
    return (FAIL, "missing " + ", ".join(missing)) if missing else (PASS, "")


def check_enums(_record: dict, a: dict) -> tuple[str, str]:
    bad = []
    if a.get("verdict") not in VERDICTS:
        bad.append(f"verdict={a.get('verdict')!r}")
    if a.get("recommended_platform") not in PLATFORMS:
        bad.append(f"platform={a.get('recommended_platform')!r}")
    if a.get("advantage_class") not in ADVANTAGE_CLASSES:
        bad.append(f"advantage_class={a.get('advantage_class')!r}")

    confidence = a.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        bad.append(f"confidence={confidence!r}")

    div = a.get("divincenzo_assessment")
    if not isinstance(div, dict):
        bad.append("divincenzo_assessment is not an object")
    else:
        for key in DIVINCENZO_KEYS:
            if key not in div:
                bad.append(f"divincenzo.{key} missing")
            elif div[key] not in DIVINCENZO_VALUES:
                bad.append(f"divincenzo.{key}={div[key]!r}")

    return (FAIL, "; ".join(bad)) if bad else (PASS, "")


def check_filters(record: dict, a: dict) -> tuple[str, str]:
    got = a.get("troyer_filters")
    if not isinstance(got, dict):
        return FAIL, "troyer_filters is not an object"

    missing = [k for k in FILTER_KEYS if k not in got]
    if missing:
        return FAIL, "missing " + ", ".join(missing)

    deterministic = record.get("deterministic_filters") or {}
    if not deterministic:
        return NA, "router supplied no filters"

    changed = [k for k in FILTER_KEYS
               if k in deterministic and bool(got[k]) != bool(deterministic[k])]
    if not changed:
        return PASS, ""

    # Requiring an exact echo was the wrong rule. On adv-class1-subtle the model
    # overrode three filters and was right to: retrieval had matched an unrelated
    # algorithm, so F6 had silently switched itself off on a single-reference
    # system. What matters is not whether the model disagrees but whether it says
    # so. Disclosed dissent is recorded; a silent rewrite is a fabrication.
    flags = " ".join(str(f) for f in (a.get("red_flags") or [])).lower()
    detail = "; ".join(f"{k}: given {deterministic[k]}, returned {got[k]}" for k in changed)
    disclosed = "filter" in flags or any(k.split("_")[0].lower() in flags for k in changed)
    if disclosed:
        return PASS, f"disclosed dissent ({detail})"
    return FAIL, f"silently changed {detail}"


def check_references(_record: dict, a: dict) -> tuple[str, str]:
    refs = a.get("references")
    if not isinstance(refs, list):
        return FAIL, "references is not a list"
    grounded = [r for r in refs if isinstance(r, str) and _is_grounded(r)]
    if len(grounded) >= 2:
        return PASS, ""
    return FAIL, f"{len(grounded)} of {len(refs)} references are checkable (need 2)"


def check_honesty(_record: dict, a: dict) -> tuple[str, str]:
    algorithm = str(a.get("recommended_algorithm", "")).upper()
    if not any(m in algorithm for m in WEAK_ALGORITHM_MARKERS):
        return NA, "no variational algorithm recommended"

    flags = a.get("red_flags") or []
    haystack = " ".join(
        [str(f) for f in flags] + [str(a.get("explanation", "")), str(a.get("platform_reason", ""))]
    ).lower()
    if any(m in haystack for m in WARNING_MARKERS):
        return PASS, ""
    return FAIL, f"recommends {a.get('recommended_algorithm')!r} without the required warning"


def check_qec_codes(_record: dict, a: dict) -> tuple[str, str]:
    if a.get("recommended_platform") != "QUANTUM":
        return NA, "not a quantum recommendation"
    codes = a.get("error_correction_codes")
    if isinstance(codes, list) and any(str(c).strip() for c in codes):
        return PASS, ""
    return FAIL, "quantum recommended with no error-correction codes named"


CHECKS = [
    ("parse", check_parse),
    ("schema", check_schema),
    ("enums", check_enums),
    ("filters", check_filters),
    ("references", check_references),
    ("honesty", check_honesty),
    ("qec_codes", check_qec_codes),
]


def score_record(record: dict) -> dict:
    """Run every check against one recorded evaluation."""
    assessment = record.get("llm_assessment")
    results: dict[str, tuple[str, str]] = {}

    for name, fn in CHECKS:
        if name != "parse" and not isinstance(assessment, dict):
            results[name] = (FAIL, "no assessment to check")
            continue
        results[name] = fn(record, assessment)

    dissent = {}
    if isinstance(assessment, dict):
        if assessment.get("verdict") and assessment["verdict"] != record.get("router_verdict"):
            dissent["verdict"] = assessment["verdict"]
        if (assessment.get("recommended_platform")
                and assessment["recommended_platform"] != record.get("router_platform")):
            dissent["platform"] = assessment["recommended_platform"]

    return {"checks": results, "dissent": dissent}


def load_recorded() -> dict[str, dict]:
    if not RESPONSES_PATH.exists():
        return {}
    return json.loads(RESPONSES_PATH.read_text(encoding="utf-8"))["responses"]


def save_recorded(recorded: dict[str, dict]) -> None:
    RESPONSES_PATH.write_text(
        json.dumps({"schema_version": "1.0", "responses": recorded}, indent=2),
        encoding="utf-8",
    )


def collect_live(cases: list[dict], limit: int | None, only: set[str] | None,
                 refresh: bool) -> dict[str, dict]:
    sys.path.insert(0, str(REPO))
    from agents.orchestrator.evaluate import QuantumEvaluator

    evaluator = QuantumEvaluator()
    # Written after every case. A live sweep takes minutes per call and used to
    # lose everything if it died on the last one.
    recorded = load_recorded()

    selected = [c for c in cases if not only or c["id"] in only]
    if not refresh:
        selected = [c for c in selected if c["id"] not in recorded]
    if limit:
        selected = selected[:limit]

    if not selected:
        print("  nothing to collect (all cases already recorded; --refresh to redo)")
        return recorded

    for index, case in enumerate(selected, 1):
        print(f"  [{index}/{len(selected)}] {case['id']}", flush=True)
        try:
            evaluator.evaluate(case["problem"])
            recorded[case["id"]] = dict(evaluator.last_diagnostics)
        except Exception as exc:  # noqa: BLE001 - one bad case must not lose the rest
            print(f"      call failed: {type(exc).__name__}: {exc}")
            recorded[case["id"]] = {
                "parse_ok": False, "finish_reason": "call_failed",
                "llm_assessment": None, "deterministic_filters": {},
                "router_verdict": None, "router_platform": None,
                "error": f"{type(exc).__name__}: {exc}",
            }
        save_recorded(recorded)

    return recorded


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="re-score recorded responses instead of calling the model")
    ap.add_argument("--limit", type=int, default=None,
                    help="only evaluate the first N outstanding cases (live mode)")
    ap.add_argument("--only", default=None,
                    help="comma-separated case ids to evaluate (live mode)")
    ap.add_argument("--refresh", action="store_true",
                    help="re-record cases that are already present")
    ap.add_argument("--strict", action="store_true",
                    help="fail on any check below its threshold")
    args = ap.parse_args()

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]

    if args.offline:
        if not RESPONSES_PATH.exists():
            print(f"No recorded responses at {RESPONSES_PATH.name}. "
                  f"Run once without --offline to build them.")
            return 2
        recorded = load_recorded()
    else:
        only = set(args.only.split(",")) if args.only else None
        print("Calling the live evaluator (recording after each case):")
        recorded = collect_live(cases, args.limit, only, args.refresh)
        print(f"\n{len(recorded)}/{len(cases)} cases recorded in {RESPONSES_PATH.name}\n")

    if not recorded:
        print("Nothing to score.")
        return 2

    scored = {cid: score_record(rec) for cid, rec in recorded.items()}

    names = [n for n, _ in CHECKS]
    print(f"{'case':<26} " + " ".join(f"{n:<11}" for n in names))
    for cid, result in scored.items():
        cells = " ".join(f"{result['checks'][n][0]:<11}" for n in names)
        print(f"{cid:<26} {cells}")

    print()
    failed_thresholds = []
    for name in names:
        outcomes = [r["checks"][name][0] for r in scored.values()]
        applicable = [o for o in outcomes if o != NA]
        skipped = len(outcomes) - len(applicable)
        if not applicable:
            print(f"{name:<12} no applicable cases")
            continue
        passed = sum(1 for o in applicable if o == PASS)
        rate = passed / len(applicable)
        threshold = THRESHOLDS.get(name, 0.0)
        note = f" ({skipped} n/a)" if skipped else ""
        marker = "" if rate >= threshold else "   BELOW THRESHOLD"
        print(f"{name:<12} {passed}/{len(applicable)} = {rate:.0%}{note}"
              f"  (threshold {threshold:.0%}){marker}")
        if rate < threshold:
            failed_thresholds.append(name)

    detail_lines = []
    for cid, result in scored.items():
        for name in names:
            status, detail = result["checks"][name]
            if status == FAIL:
                detail_lines.append(f"  {cid} / {name}: {detail}")
    if detail_lines:
        print("\nfailures:")
        print("\n".join(detail_lines))

    dissenting = {cid: r["dissent"] for cid, r in scored.items() if r["dissent"]}
    print(f"\ndissent     {len(dissenting)}/{len(scored)} cases where the model's own "
          f"verdict differs from the router's")
    for cid, dissent in dissenting.items():
        print(f"  {cid}: {dissent}")

    if failed_thresholds and args.strict:
        print(f"\nbelow threshold: {', '.join(failed_thresholds)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
