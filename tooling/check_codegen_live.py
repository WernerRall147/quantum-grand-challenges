#!/usr/bin/env python3
"""Ask the live evaluator for Q# and check what comes back, as a user would see it.

Why this exists: nothing watched code generation in production. The uptime probe posts a
problem without asking for code, the demo smoke test stopped failing on code generation
(#249), and so from 1 to 25 September 2026 one generation request in five never compiled,
and two of three Shor requests returned a classical placeholder estimated at 17 physical
qubits, without any check going red. This posts real problems with generate_code on and
fails on anything a user should not be shown.

Standard library only, and no Azure credentials: the API is public, so the check keeps
working when a secret expires. Exit code 1 if any prompt fails.

    python tooling/check_codegen_live.py
    python tooling/check_codegen_live.py --base http://localhost:8000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io"

# One prompt per generator exemplar family that production requests use, with problems the
# router sends to QUANTUM (agents/evaluations/cases.json).
PROMPTS = [
    ("QPE", "Calculate the ground state energy of the FeMoco nitrogenase cofactor to chemical accuracy"),
    ("Shor", "Factor a 2048-bit RSA integer to test post-quantum readiness"),
    ("Trotter", "Simulate real-time dynamics of a lattice gauge theory with a fermion sign problem"),
]


def problems_with(status: int, body: dict) -> list[str]:
    """Everything wrong with one response, as a user would experience it; [] if it is usable."""
    if status != 200:
        return [f"HTTP {status}"]
    if body.get("verdict") != "QUANTUM_ADVANTAGE" and body.get("recommended_platform") != "QUANTUM":
        return [f"verdict {body.get('verdict')}: no Q# is generated for a non-quantum verdict"]
    found = []
    est = body.get("estimation") or {}
    if not (body.get("qsharp_code") or "").strip():
        found.append(f"no Q# returned ({est.get('error') or 'no error given'})")
    if est.get("compiled") is not True:
        found.append(f"did not compile after {est.get('attempt_count', '?')} attempts: {str(est.get('error', ''))[:160]}")
    elif est.get("quantum_work") is False:
        found.append(f"compiled but does no quantum work ({est.get('num_qubits')} qubits)")
    elif not isinstance(est.get("physical_qubits"), (int, float)):
        found.append(f"no resource estimate: {str(est.get('estimate_error', ''))[:160]}")
    errored = [row.get("config") for row in body.get("resource_estimate_pareto") or [] if row.get("error")]
    if errored:
        found.append(f"Pareto rows failed: {', '.join(str(e) for e in errored)}")
    return found


def call(base: str, problem: str, timeout: float) -> tuple[int, dict, float]:
    request = urllib.request.Request(
        f"{base.rstrip('/')}/api/evaluate",
        data=json.dumps({"problem": problem, "generate_code": True}).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed https endpoint
            return response.status, json.loads(response.read()), time.time() - started
    except urllib.error.HTTPError as e:
        return e.code, {}, time.time() - started
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return 0, {"error": f"{type(e).__name__}: {e}"}, time.time() - started


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("CODEGEN_CHECK_API_BASE") or DEFAULT_BASE)
    ap.add_argument("--timeout", type=float, default=300)
    args = ap.parse_args()

    rows, failures = [], 0
    for family, problem in PROMPTS:
        status, body, seconds = call(args.base, problem, args.timeout)
        found = problems_with(status, body) if status else [body.get("error", "request failed")]
        failures += bool(found)
        est = body.get("estimation") or {}
        rows.append((family, "FAIL" if found else "ok", f"{seconds:.1f}s", est.get("reference", ""),
                     est.get("attempt_count", ""), est.get("num_qubits", ""),
                     f"{est['physical_qubits']:,}" if isinstance(est.get("physical_qubits"), (int, float)) else "",
                     "; ".join(found)))

    table = ["| Family | Result | Time | Exemplar | Attempts | Qubits | Physical qubits | Problem |",
             "|---|---|---|---|---|---|---|---|"]
    table += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    report = f"### Live Q# generation check ({args.base})\n\n" + "\n".join(table) + "\n"
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report)
    print(f"{failures} of {len(PROMPTS)} prompts failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
