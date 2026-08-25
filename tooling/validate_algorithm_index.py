"""Check the 47 entries the router decides on, and scaffold new ones so they start valid.

algorithm_zoo_index.json is the corpus every verdict rests on, it is edited by hand, and
until now nothing looked at it. That combination has one obvious failure mode and it is
silent: a speedup_class the router does not recognise matches none of its membership tests,
so the entry quietly stops being able to produce a QUANTUM verdict. Five of the 47 sit
outside the router's three buckets today - and all five are deliberate, which is precisely
why the accidental case would be invisible.

The rules enforced here were derived from the committed file rather than invented, by
testing candidate invariants against all 47 and keeping the ones that held. One obvious
candidate did not hold and is deliberately absent: QUANTUM_ADVANTAGE does not imply
naturally_quantum. Shor, Discrete Logarithm, Abelian Hidden Subgroup, Quantum Cryptanalysis,
Pell's Equation and Bernstein-Vazirani are structural speedups over classical hardness
assumptions, not simulations of quantum systems. Enforcing that rule would have broken the
distinction the evaluator exists to draw.

Scaffolding matters as much as checking. tooling/reconcile_algorithm_zoo.py counts 17
superpolynomial gaps; closing one meant hand-writing JSON into a 47-entry array and hoping.
`--scaffold "Group Isomorphism"` emits a correctly shaped entry with the source-derived
fields filled and the judgement fields left blank, so promotion is a review rather than
a transcription.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from agents.classifier.platform_router import (  # noqa: E402
    KNOWN_SPEEDUPS, QUALIFIED_SPEEDUPS, STRONG_QUANTUM_SPEEDUPS, TROYER_VERDICTS,
)

INDEX_PATH = REPO / "knowledge" / "data" / "algorithm_zoo_index.json"
ZOO_PATH = REPO / "knowledge" / "data" / "zoo_references.json"

REQUIRED_FIELDS = ("name", "category", "speedup_class", "troyer_verdict",
                   "io_bottleneck", "naturally_quantum", "notes")

# Zoo speedup wording -> our vocabulary. Anything else scaffolds blank for a human.
SPEEDUP_FROM_ZOO = {
    "superpolynomial": "superpolynomial",
    "exponential": "exponential",
    "polynomial": "polynomial",
    "constant factor": "quadratic_at_most",
}


def validate(entries: list[dict], declared_total: int | None = None) -> list[str]:
    """Return every violation as a readable line. Empty means the index is coherent."""
    problems: list[str] = []

    if declared_total is not None and declared_total != len(entries):
        problems.append(
            f"total_algorithms says {declared_total} but the array holds {len(entries)}"
        )

    seen: set[str] = set()
    for entry in entries:
        name = str(entry.get("name", "")).strip()
        label = name or "<unnamed entry>"

        if not name:
            problems.append("an entry has no name")
        elif name in seen:
            problems.append(f"{label}: duplicate name")
        seen.add(name)

        for field in REQUIRED_FIELDS:
            if field not in entry:
                problems.append(f"{label}: missing required field '{field}'")

        for field in ("io_bottleneck", "naturally_quantum"):
            if field in entry and not isinstance(entry[field], bool):
                problems.append(
                    f"{label}: {field} is {entry[field]!r}, must be a real boolean - "
                    "a string is truthy and would invert the filter"
                )

        speedup = entry.get("speedup_class")
        if speedup is not None and speedup not in KNOWN_SPEEDUPS:
            problems.append(
                f"{label}: speedup_class '{speedup}' means nothing to the router, so this "
                f"entry can never produce a QUANTUM verdict. Known: {sorted(KNOWN_SPEEDUPS)}"
            )

        verdict = entry.get("troyer_verdict")
        if verdict is not None and verdict not in TROYER_VERDICTS:
            problems.append(f"{label}: troyer_verdict '{verdict}' is not one of "
                            f"{sorted(TROYER_VERDICTS)}")

        # exponential_core exists to say "exponential but I/O kills it". Without the
        # bottleneck the label is just a misspelling of exponential that silently
        # downgrades a real advantage.
        if speedup == "exponential_core" and entry.get("io_bottleneck") is not True:
            problems.append(
                f"{label}: speedup_class 'exponential_core' requires io_bottleneck=True. "
                "If I/O is not the constraint, the class is wrong."
            )

        if verdict == "QUANTUM_ADVANTAGE":
            if speedup not in STRONG_QUANTUM_SPEEDUPS:
                problems.append(
                    f"{label}: QUANTUM_ADVANTAGE with speedup_class '{speedup}'. Only "
                    f"{sorted(STRONG_QUANTUM_SPEEDUPS)} survive error correction."
                )
            if entry.get("io_bottleneck") is True:
                problems.append(
                    f"{label}: QUANTUM_ADVANTAGE with io_bottleneck=True. If the data "
                    "cannot get in or out, the speedup is not reachable."
                )

        # Concluding that classical wins despite a strong speedup is exactly what
        # exponential_core records. Reaching HPC_PREFERRED from a bare strong class
        # throws that reason away, which is what relabelling HHL would look like.
        # The three genuine strong-and-I/O-bound entries are all INCONCLUSIVE.
        if (speedup in STRONG_QUANTUM_SPEEDUPS
                and entry.get("io_bottleneck") is True
                and verdict == "HPC_PREFERRED"):
            problems.append(
                f"{label}: speedup_class '{speedup}' with io_bottleneck=True resolved to "
                "HPC_PREFERRED. Use 'exponential_core' to record that I/O is what decides "
                "it, or INCONCLUSIVE if that is not settled."
            )

        # The under-claiming direction. An entry that passes every filter and is still
        # not marked QUANTUM_ADVANTAGE is either mislabelled or needs its reason stated.
        if (speedup in STRONG_QUANTUM_SPEEDUPS
                and entry.get("io_bottleneck") is False
                and entry.get("naturally_quantum") is True
                and verdict != "QUANTUM_ADVANTAGE"):
            problems.append(
                f"{label}: strong speedup, no I/O bottleneck and naturally quantum, but "
                f"troyer_verdict is '{verdict}'."
            )

    return problems


def scaffold(zoo_name: str) -> dict | None:
    """Build a starting entry for a Zoo algorithm, judgement fields left blank."""
    zoo = json.loads(ZOO_PATH.read_text(encoding="utf-8"))
    match = next((a for a in zoo["algorithms"]
                  if a["name"].lower() == zoo_name.lower()), None)
    if not match:
        return None

    raw = (match.get("speedup") or "").strip().lower()
    return {
        "name": match["name"],
        "category": "TODO",
        "speedup_class": SPEEDUP_FROM_ZOO.get(raw, f"TODO (Zoo says: {raw or 'nothing'})"),
        "quantum_complexity": "TODO",
        "classical_best": "TODO",
        "io_bottleneck": "TODO: true if state preparation or readout dominates",
        "oracle_polynomial": "TODO",
        "naturally_quantum": "TODO: true only for simulating quantum systems",
        "troyer_verdict": "TODO: QUANTUM_ADVANTAGE | HPC_PREFERRED | INCONCLUSIVE",
        "notes": "TODO",
        "reference": "TODO: arXiv id from the Zoo bibliography",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scaffold", metavar="ZOO_NAME",
                        help="print a starting entry for a Zoo algorithm and exit")
    args = parser.parse_args()

    if args.scaffold:
        entry = scaffold(args.scaffold)
        if not entry:
            print(f"no algorithm named {args.scaffold!r} in {ZOO_PATH.name}")
            return 1
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        print("\nFill every TODO, paste into algorithm_zoo_index.json, bump "
              "total_algorithms, re-run this without --scaffold, then re-seed the index.",
              file=sys.stderr)
        return 0

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    entries = index["algorithms"] if isinstance(index, dict) else index
    declared = index.get("total_algorithms") if isinstance(index, dict) else None

    problems = validate(entries, declared)
    print(f"entries checked: {len(entries)}")
    print(f"qualified classes in use: {sorted(QUALIFIED_SPEEDUPS)}")

    if problems:
        print(f"\nFAIL: {len(problems)} problem(s) in {INDEX_PATH.relative_to(REPO)}")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print("index is coherent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
