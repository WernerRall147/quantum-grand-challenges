"""Account for every algorithm in the Quantum Algorithm Zoo against the index that decides.

The index the router reads holds 47 entries. The Zoo holds 74. Those numbers were never
reconciled, and the obvious way to reconcile them does not work: matching on name reports
"Factoring" and "Linear Systems" as missing from an index containing Shor's Algorithm and
HHL. The Zoo names the problem, we tend to name the algorithm or its author, and no amount
of string normalisation bridges that.

So the mapping is a judgement call, recorded once in knowledge/data/zoo_reconciliation.json
and checked mechanically from then on. Every Zoo algorithm must be one of:

    matched    - same as one of ours, by exact name or by a recorded alias
    excluded   - deliberately absent, with the reason stated
    candidate  - a real gap, counted rather than discovered

Anything with no disposition is UNRECONCILED and fails. That is the whole point: a new Zoo
entry cannot sit unnoticed waiting for someone to remember it. Run in CI hermetically, and
nightly after re-fetching the live Zoo, which is what turns "the Zoo changed" into a build
failure instead of a loose end.

Reconciled 2026-08-25: 31 matched, 22 excluded, 21 candidates, of which 17 carry a
superpolynomial or exponential claim. Those 17 are problems the router structurally cannot
return QUANTUM for, however well it reasons.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ZOO_PATH = REPO / "knowledge" / "data" / "zoo_references.json"
INDEX_PATH = REPO / "knowledge" / "data" / "algorithm_zoo_index.json"
LEDGER_PATH = REPO / "knowledge" / "data" / "zoo_reconciliation.json"

STRONG_SPEEDUPS = {"superpolynomial", "exponential"}


def normalise(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def reconcile(zoo_algorithms: list[dict], our_names: list[str], ledger: dict) -> dict:
    """Sort every Zoo algorithm into matched, excluded, candidate or unreconciled.

    Pure so it can be tested without touching disk. Also reports dangling aliases -
    ledger entries pointing at an index name that no longer exists, which is how a
    rename would silently turn a match back into a gap.
    """
    ours = {normalise(n): n for n in our_names}
    aliases = {k: v for k, v in ledger.get("aliases", {}).items() if not k.startswith("_")}
    excluded = {k for k in ledger.get("excluded", {}) if not k.startswith("_")}
    candidates = {k for k in ledger.get("candidates", {}) if not k.startswith("_")}

    result: dict[str, list] = {
        "matched": [], "excluded": [], "candidates": [], "unreconciled": [],
        "dangling_aliases": [], "strong_candidates": [],
    }

    our_names_set = set(our_names)
    for key, target in aliases.items():
        if target not in our_names_set:
            result["dangling_aliases"].append((key, target))

    for algorithm in zoo_algorithms:
        name = algorithm["name"]
        key = normalise(name)
        speedup = (algorithm.get("speedup") or "").strip().lower()

        if key in ours:
            result["matched"].append((name, ours[key]))
        elif key in aliases:
            result["matched"].append((name, aliases[key]))
        elif key in excluded:
            result["excluded"].append((name, speedup))
        elif key in candidates:
            result["candidates"].append((name, speedup))
            if speedup in STRONG_SPEEDUPS:
                result["strong_candidates"].append((name, speedup))
        else:
            result["unreconciled"].append((name, speedup))

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-candidates", action="store_true",
                        help="print the gaps, strongest first")
    args = parser.parse_args()

    zoo = json.loads(ZOO_PATH.read_text(encoding="utf-8"))
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))

    entries = index["algorithms"] if isinstance(index, dict) else index
    result = reconcile(zoo["algorithms"], [e["name"] for e in entries], ledger)

    print(f"zoo algorithms : {len(zoo['algorithms'])}")
    print(f"indexed        : {len(entries)}")
    print()
    print(f"  matched      : {len(result['matched'])}")
    print(f"  excluded     : {len(result['excluded'])}")
    print(f"  candidates   : {len(result['candidates'])} "
          f"({len(result['strong_candidates'])} superpolynomial or exponential)")
    print(f"  unreconciled : {len(result['unreconciled'])}")

    if args.list_candidates:
        print("\ngaps, strongest claim first:")
        ordered = sorted(result["candidates"],
                         key=lambda c: (c[1] not in STRONG_SPEEDUPS, c[0]))
        for name, speedup in ordered:
            print(f"  {speedup:18s} {name}")

    failed = False

    if result["dangling_aliases"]:
        failed = True
        print("\nFAIL: aliases point at index entries that no longer exist.")
        print("An index rename turns a reconciled match back into an untracked gap.")
        for key, target in result["dangling_aliases"]:
            print(f"  {key} -> {target}")

    if result["unreconciled"]:
        failed = True
        print("\nFAIL: these Zoo algorithms have no disposition.")
        print("Add each to aliases, excluded or candidates in "
              f"{LEDGER_PATH.relative_to(REPO)}.")
        for name, speedup in result["unreconciled"]:
            print(f"  {speedup:18s} {name}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
