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


def evaluate(base: str, problem: str, timeout: int) -> Tuple[dict, float]:
    body = json.dumps({"problem": problem, "generate_code": False}).encode()
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=DEFAULT_BASE, help="evaluator API base URL")
    parser.add_argument("--timeout", type=int, default=180, help="per-request timeout, seconds")
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
    if failures:
        print("\nDo not record against this. Re-check the router, the algorithm zoo and the search index.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
