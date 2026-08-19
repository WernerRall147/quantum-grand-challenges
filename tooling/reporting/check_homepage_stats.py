#!/usr/bin/env python3
"""Check the home page's headline numbers against the repository.

These were hardcoded in website/pages/index.tsx and had already drifted once: the
filter count said 5 after F6 landed, and the estimate count said 141, a figure no
rule in this repository reproduces. Every number here is now derived from a file
that a script generates, so a stale claim fails the build instead of shipping.

A value written as "N+" is treated as a lower bound, which is what it claims.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "website" / "pages" / "index.tsx"

STAT_RE = re.compile(r"\{\s*val:\s*'([^']+)'\s*,\s*label:\s*'([^']+)'\s*\}")


def active_problems() -> int:
    return sum(
        1
        for p in (ROOT / "problems").iterdir()
        if p.is_dir() and re.match(r"^\d\d_", p.name) and (p / "qsharp" / "qsharp.json").exists()
    )


def algorithms_indexed() -> int:
    zoo = json.loads((ROOT / "knowledge" / "data" / "algorithm_zoo_index.json").read_text(encoding="utf-8"))
    return len(zoo["algorithms"])


def azure_runs() -> int:
    hist = json.loads((ROOT / "website" / "data" / "azureRunHistory.json").read_text(encoding="utf-8"))
    return len(hist["runs"])


def resource_estimates() -> int:
    mm = json.loads((ROOT / "website" / "data" / "multiModelEstimates.json").read_text(encoding="utf-8"))
    return mm["total_estimates"]


def troyer_filters() -> int:
    sys.path.insert(0, str(ROOT))
    from agents.classifier.platform_router import compute_troyer_filters

    return len(compute_troyer_filters({}, ""))


EXPECTED = {
    "Active problems": active_problems,
    "Azure Quantum runs": azure_runs,
    "Resource estimates": resource_estimates,
    "Algorithms indexed": algorithms_indexed,
    "Troyer filters": troyer_filters,
}


def main() -> int:
    stats = STAT_RE.findall(INDEX.read_text(encoding="utf-8"))
    if not stats:
        print(f"No stat entries found in {INDEX.name}; has the markup changed?")
        return 2

    failures = []
    for val, label in stats:
        compute = EXPECTED.get(label)
        if compute is None:
            print(f"  {label:<22} {val:>6}   no check defined")
            continue

        actual = compute()
        if val.endswith("+"):
            ok = actual >= int(val[:-1])
            shown = f"{val} (>= {val[:-1]})"
        else:
            ok = str(actual) == val
            shown = val

        print(f"  {label:<22} {shown:>16}   repo says {actual}   {'ok' if ok else 'STALE'}")
        if not ok:
            failures.append(f"{label}: page says {val}, repository says {actual}")

    if failures:
        print("\nHome page statistics are stale:")
        for f in failures:
            print(f"  {f}")
        return 1

    print("\nHome page statistics match the repository.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
