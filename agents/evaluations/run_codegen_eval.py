#!/usr/bin/env python3
"""Measure Q# generation end to end: does the program compile, estimate, and do quantum work?

Why this exists: production telemetry for 2026-09-01 to 2026-09-25 showed 29 generation
requests, of which 6 never compiled after three attempts, 12 needed a repair, and two
Shor programs estimated at 17 physical qubits - one logical qubit, so almost no quantum
work. Nothing measured any of that; the uptime probe does not generate code. This runs the
real pipeline (generate, compile, repair, estimate) on codegen_cases.json and judges each
returned program directly, by compiling and tracing it, so the numbers do not depend on
what the generator says about its own output.

It calls the live model and costs tokens, so CI does not run it. Typical use:

    python agents/evaluations/run_codegen_eval.py --repeats 2 --workers 3
    python agents/evaluations/run_codegen_eval.py --subscription <id>   # local Azure CLI

--subscription asks the Azure CLI for a token by subscription, for machines whose default
CLI account is in another tenant. Exit code is non-zero below --min-compile-rate.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tooling"))

CASES_PATH = HERE / "codegen_cases.json"
RESULTS_PATH = HERE / "codegen_eval_results.json"

_ERROR_CODE = re.compile(r"Qdk\.Qsc\.[A-Za-z]+(?:\.[A-Za-z]+)*")
_EXPECTED = re.compile(r"expected ([^\n]+?), found ([^\n]+)")


class SubscriptionCliCredential:
    """Token from `az account get-access-token --subscription`, not the default account."""

    def __init__(self, subscription: str):
        self.subscription = subscription
        self._token = None

    def get_token(self, *scopes: str, **_kwargs):
        from azure.core.credentials import AccessToken

        if self._token and self._token.expires_on - time.time() > 300:
            return self._token
        out = subprocess.run(
            ["az", "account", "get-access-token", "--subscription", self.subscription,
             "--resource", scopes[0].removesuffix("/.default"), "-o", "json"],
            capture_output=True, text=True, shell=sys.platform == "win32", timeout=90, check=True,
        )
        data = json.loads(out.stdout)
        self._token = AccessToken(data["accessToken"], int(data["expires_on"]))
        return self._token


def error_class(error: str) -> str:
    """The compiler's error code plus its expected/found pair, which is what varies."""
    if not error:
        return ""
    code = _ERROR_CODE.search(error)
    pair = _EXPECTED.search(error)
    label = code.group(0).removeprefix("Qdk.Qsc.") if code else error.splitlines()[0][:60]
    if pair:
        label += f" (expected {pair.group(1).strip()}, found {pair.group(2).strip()[:40]})"
    return label


def judge(code: str, entry: str) -> dict:
    """Compile and trace the returned program independently of the generator.

    Runs on the generator's qsharp thread when it has one: the interpreter is thread-bound,
    and older generators, which have no such thread, use the calling thread.
    """
    try:
        from agents.code_generator.generate import _QSHARP_THREAD
    except ImportError:
        return _judge(code, entry)
    return _QSHARP_THREAD.submit(_judge, code, entry).result()


def _judge(code: str, entry: str) -> dict:
    from qdk import qsharp

    with tempfile.TemporaryDirectory() as td:
        proj = Path(td)
        (proj / "qsharp.json").write_text("{}")
        (proj / "src").mkdir()
        (proj / "src" / "Main.qs").write_text(code, encoding="utf-8")
        try:
            qsharp.init(project_root=str(proj))
        except Exception as e:  # noqa: BLE001
            return {"judged_compiles": False, "judge_error": str(e)[:200]}
        try:
            from qdk.qre.interop import trace_from_entry_expr

            trace = trace_from_entry_expr(entry)
            return {"judged_compiles": True, "num_qubits": trace.total_qubits, "depth": trace.depth}
        except Exception as e:  # noqa: BLE001
            return {"judged_compiles": True, "num_qubits": None, "judge_error": str(e)[:200]}


def run_one(job: dict, subscription: str | None) -> dict:
    from agents.code_generator.generate import QSharpCodeGenerator, entry_expression

    gen = QSharpCodeGenerator()
    if subscription:
        gen.credential = SubscriptionCliCredential(subscription)

    started = time.time()
    record = {"id": job["id"], "family": job["family"], "repeat": job["repeat"]}
    try:
        out = gen.generate_with_estimate(job["problem"], job["algorithm"], multi_profile=False)
    except Exception as e:  # noqa: BLE001 - a raised generation is a result, not a crash
        record.update({"compiled": False, "attempts": 0, "raised": f"{type(e).__name__}: {str(e)[:200]}",
                       "seconds": round(time.time() - started, 1)})
        return record

    est = out.get("estimation") or {}
    code = out.get("qsharp_code") or ""
    attempts = est.get("attempts") or []
    record.update({
        "seconds": round(time.time() - started, 1),
        "compiled": bool(est.get("compiled")),
        "attempts": len(attempts),
        "attempt_errors": [error_class(a.get("error", "")) for a in attempts if a.get("error")],
        "physical_qubits": est.get("physical_qubits"),
        "estimate_error": est.get("estimate_error"),
        "reference": est.get("reference"),
        "model": est.get("codegen_model"),
        "chars": len(code),
    })
    if record["compiled"]:
        record.update(judge(code, est.get("entry_expression") or entry_expression(code)))
        record["trivial"] = record.get("num_qubits") is not None and record["num_qubits"] < 2
    record["code"] = code
    return record


def summarise(records: list[dict]) -> dict:
    n = len(records)
    compiled = [r for r in records if r.get("compiled")]
    first_try = [r for r in compiled if r.get("attempts") == 1]
    estimated = [r for r in compiled if isinstance(r.get("physical_qubits"), (int, float))]
    trivial = [r for r in compiled if r.get("trivial")]
    errors = Counter(e for r in records for e in r.get("attempt_errors", []))
    final_errors = Counter(r["attempt_errors"][-1] for r in records
                           if not r.get("compiled") and r.get("attempt_errors"))
    return {
        "runs": n,
        "compiled": len(compiled),
        "compiled_first_try": len(first_try),
        "compiled_after_repair": len(compiled) - len(first_try),
        "never_compiled": n - len(compiled),
        "estimate_failed": len(compiled) - len(estimated),
        "trivial_programs": len(trivial),
        "usable": len([r for r in estimated if not r.get("trivial")]),
        "median_seconds": statistics.median(r["seconds"] for r in records) if records else None,
        "attempt_error_classes": errors.most_common(),
        "final_error_classes": final_errors.most_common(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--workers", type=int, default=2,
                    help="separate processes: the qsharp interpreter is process-global")
    ap.add_argument("--cases", nargs="*", help="case ids to run (default: all)")
    ap.add_argument("--subscription", help="use an Azure CLI token for this subscription")
    ap.add_argument("--out", type=Path, default=RESULTS_PATH)
    ap.add_argument("--min-compile-rate", type=float, default=0.0)
    args = ap.parse_args()

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    if args.cases:
        cases = [c for c in cases if c["id"] in set(args.cases)]
    jobs = [{**c, "repeat": r} for r in range(args.repeats) for c in cases]

    records: list[dict] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, job, args.subscription) for job in jobs]
        for fut in as_completed(futures):
            r = fut.result()
            records.append(r)
            status = ("usable" if r.get("compiled") and r.get("physical_qubits") and not r.get("trivial")
                      else "TRIVIAL" if r.get("trivial")
                      else "NO ESTIMATE" if r.get("compiled")
                      else "FAILED")
            detail = r.get("raised") or (r.get("attempt_errors") or [""])[-1]
            print(f"{r['id']:<26} #{r['repeat']} {status:<11} attempts={r.get('attempts')} "
                  f"qubits={r.get('num_qubits')} pq={r.get('physical_qubits')} {r['seconds']}s "
                  f"{'' if status == 'usable' else detail}", flush=True)

    summary = summarise(records)
    args.out.write_text(json.dumps({"summary": summary, "records": sorted(
        records, key=lambda r: (r["id"], r["repeat"]))}, indent=2), encoding="utf-8")
    print("\n" + json.dumps(summary, indent=2))
    rate = summary["compiled"] / summary["runs"] if summary["runs"] else 0.0
    return 1 if rate < args.min_compile_rate else 0


if __name__ == "__main__":
    sys.exit(main())
