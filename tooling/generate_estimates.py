#!/usr/bin/env python3
"""Generate resource estimation JSON for all Q# problems using the QRE v3 estimator.

Saves estimate.json to each problem's circuits/ directory, and exports the
Pareto frontiers to website/data/paretoFrontiers.json so the site can show the
qubit-versus-runtime trade rather than a single point.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from discover_problems import discover_all_problems
from estimator_config import DEFAULT_QEC_SCHEME, DEFAULT_QUBIT_MODEL, ENTRY_POINTS, estimate_summary

FRONTIERS_PATH = Path(__file__).resolve().parent.parent / "website" / "data" / "paretoFrontiers.json"


def main():
    from qdk import qsharp

    problem_dirs = discover_all_problems()

    ok = 0
    fail = 0
    frontiers: dict[str, dict] = {}

    for pd in problem_dirs:
        qsharp_dir = pd / "qsharp"
        circuits_dir = pd / "circuits"
        circuits_dir.mkdir(exist_ok=True)

        if not (qsharp_dir / "qsharp.json").exists():
            continue

        name = pd.name

        try:
            qsharp.init(project_root=str(qsharp_dir))
        except Exception as e:
            print(f"XX {name}: compile error -- {str(e)[:100]}")
            fail += 1
            continue

        ep = ENTRY_POINTS.get(name)
        if ep is None:
            print(f"-- {name}: no entry point mapped")
            continue

        try:
            summary = {
                "problem": name,
                "qubitModel": DEFAULT_QUBIT_MODEL,
                "qecScheme": DEFAULT_QEC_SCHEME,
                **estimate_summary(ep.expr(), DEFAULT_QUBIT_MODEL, DEFAULT_QEC_SCHEME),
            }

            out_path = circuits_dir / "estimate.json"
            out_path.write_text(
                json.dumps(summary, indent=2, default=str), encoding="utf-8"
            )

            pq = summary.get("physicalQubits", "?")
            lq = summary.get("logicalQubits", "?")
            tc = summary.get("tCount", "?")
            print(f"OK {name}: {pq} physical qubits, {lq} logical qubits, {tc} T-gates")
            ok += 1

            points = summary.get("paretoFrontier") or []
            if points:
                frontiers[name] = {
                    "qubitModel": DEFAULT_QUBIT_MODEL,
                    "qecScheme": DEFAULT_QEC_SCHEME,
                    "selected": "min-qubits",
                    "points": points,
                }

        except Exception as e:
            err = str(e)[:150]
            print(f"XX {name}: {err}")
            fail += 1

    if frontiers:
        FRONTIERS_PATH.parent.mkdir(parents=True, exist_ok=True)
        FRONTIERS_PATH.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "generated_utc": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "maxError": 1e-3,
                    "problems": frontiers,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Frontiers for {len(frontiers)} problems -> {FRONTIERS_PATH.name}")

    print(f"\nDone: {ok} estimates generated, {fail} failed")


if __name__ == "__main__":
    sys.exit(main() or 0)
