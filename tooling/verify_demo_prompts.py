"""Verify the Azure Friday demo prompts against the live evaluator API.

The runbook says to re-verify all five prompts after any change to the router, the
algorithm zoo or the search index. Doing that by hand meant it did not happen: the
prompts were last checked on 2026-08-14 against the Foundry agent path, and production
moved to chat-completions on 2026-08-19 without anyone re-running them.

Prompts are read from the runbook table rather than duplicated here, so the thing this
verifies is the same text that gets typed on air.

    python tooling/verify_demo_prompts.py
    python tooling/verify_demo_prompts.py --base http://localhost:8000

Exit code is 0 only if every prompt returned its expected verdict.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parents[1]
RUNBOOK = REPO / "docs" / "AzureFriday" / "README.md"
DEFAULT_BASE = "https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io"

# A demo row is `| "prompt" | `VERDICT` | ... |`. The backticked all-caps verdict is what
# separates it from the troubleshooting table further down the same file.
ROW = re.compile(r'^\|\s*"(?P<prompt>[^"]+)"\s*\|\s*`(?P<verdict>[A-Z_]+)`\s*\|')

# The runbook documents five. Fewer means the table moved and this check is measuring
# less than it claims to - that is a failure, not a pass.
MIN_PROMPTS = 5


def parse_prompts(path: Path) -> List[Tuple[str, str]]:
    if not path.exists():
        raise SystemExit(f"FAIL: runbook not found at {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW.match(line)
        if match:
            rows.append((match.group("prompt"), match.group("verdict")))
    return rows


def evaluate(base: str, problem: str, timeout: int, generate_code: bool = False) -> Tuple[dict, float]:
    body = json.dumps({"problem": problem, "generate_code": generate_code}).encode()
    request = urllib.request.Request(
        f"{base}/api/evaluate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    return payload, time.perf_counter() - started


def check_codegen(base: str, problem: str, timeout: int) -> int:
    """Run the code-generation path and report why it is unusable, not just that it is.

    The five checks above all post generate_code=false, so this tool passed clean while
    Q# generation was dead in production for months, and again while it returned 3,182
    characters of source whose every resource estimate was a compiler error. Non-empty is
    not usable, so this asserts the estimate too.

    Returns 0 even when generation is broken, and says so loudly instead. No beat in the
    reworked demo shows generated Q#: beat 1 says "leave Generate code unticked" and beat 3
    is the local Grover run. Blocking a recording on a path that is never on camera trains
    you to ignore a red check, which is worse than not having one.
    """
    print(f"\ncode generation - NOT a demo beat, does not block the recording")
    try:
        data, seconds = evaluate(base, problem, timeout, generate_code=True)
    except Exception as exc:
        print(f"  WARN: request failed: {str(exc)[:200]}")
        return 0

    qsharp = data.get("qsharp_code") or ""
    estimation = data.get("estimation") or {}
    pareto = data.get("resource_estimate_pareto") or []
    broken = [r for r in pareto if r.get("error")]

    print(f"  {seconds:.1f}s   ({problem[:40]}...)")

    def warn(detail: str) -> int:
        print(f"  WARN: {detail}")
        print("  Generation is flaky and is not on camera. Do not tick 'Generate code' live,")
        print("  and if Scott asks whether it writes Q#, say it does and that it is the")
        print("  least reliable part - which is true, and a better answer than a demo.")
        return 0

    if not qsharp:
        return warn(f"no Q# returned. {str(estimation.get('error'))[:200]}")
    if estimation.get("error"):
        return warn(str(estimation["error"])[:250])
    if estimation.get("estimate_error"):
        return warn(f"estimation failed: {str(estimation['estimate_error'])[:200]}")
    if estimation.get("physical_qubits") is None:
        return warn(f"no physical_qubits, entry={estimation.get('entry_expression')!r}")
    if broken:
        return warn(f"{len(broken)}/{len(pareto)} Pareto rows errored: "
                    f"{str(broken[0]['error'])[:200]}")

    print(f"  OK   {len(qsharp)} chars of Q#, entry {estimation.get('entry_expression')}, "
          f"{estimation.get('physical_qubits')} physical qubits, {len(pareto)} Pareto rows")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=DEFAULT_BASE, help="evaluator API base URL")
    parser.add_argument("--timeout", type=int, default=180, help="per-request timeout, seconds")
    parser.add_argument("--no-codegen", action="store_true",
                        help="skip the code-generation report; it costs another minute or two")
    args = parser.parse_args()

    prompts = parse_prompts(RUNBOOK)
    if len(prompts) < MIN_PROMPTS:
        print(f"FAIL: parsed {len(prompts)} prompts from {RUNBOOK.name}, expected at least {MIN_PROMPTS}.")
        print("The section 5 table changed shape. Fix the table or this pattern before trusting a pass.")
        return 1

    try:
        with urllib.request.urlopen(f"{args.base}/", timeout=30) as response:
            print(f"health: {json.load(response)}")
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"FAIL: health check failed against {args.base}: {exc}")
        return 1

    print(f"\n{'':4}{'PROMPT':<34}{'EXPECTED':<20}{'ACTUAL':<20}{'SECS':>7}{'REFS':>6}  MODEL")
    failures = 0
    latencies = []

    for problem, expected in prompts:
        try:
            data, seconds = evaluate(args.base, problem, args.timeout)
        except Exception as exc:
            print(f"ERR {problem[:32]:<34}{expected:<20}{str(exc)[:40]}")
            failures += 1
            continue

        actual = data.get("recommendation") or data.get("verdict") or "?"
        refs = len(data.get("references") or [])
        latencies.append(seconds)
        ok = actual == expected
        failures += 0 if ok else 1
        print(
            f"{'OK ' if ok else 'BAD'} {problem[:32]:<34}{expected:<20}{actual:<20}"
            f"{seconds:>6.1f}s{refs:>6}  {data.get('model_used') or data.get('model') or '?'}"
            f"{'' if not data.get('used_agent') else '  [agent path]'}"
        )

    if latencies:
        ordered = sorted(latencies)
        median = ordered[len(ordered) // 2]
        print(f"\nlatency: median {median:.1f}s, min {ordered[0]:.1f}s, max {ordered[-1]:.1f}s")

    print(f"mismatches: {failures} of {len(prompts)}")

    if not args.no_codegen:
        # Generated Q# is not on camera in the reworked demo - beat 1 leaves "Generate
        # code" unticked - so this reports and never adds to `failures`.
        quantum = next((p for p, v in prompts if v == "QUANTUM_ADVANTAGE"), None)
        if quantum is None:
            print("\nWARN: no QUANTUM_ADVANTAGE prompt in the table, so generation is unchecked.")
        else:
            check_codegen(args.base, quantum, max(args.timeout, 600))

    if failures:
        print("\nDo not record against this. Re-check the router, the algorithm zoo and the search index.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
