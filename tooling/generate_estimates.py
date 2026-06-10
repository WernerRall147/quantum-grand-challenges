#!/usr/bin/env python3
"""Generate resource estimation JSON for all Q# problems using qsharp.estimate().

Saves estimate.json to each problem's circuits/ directory.
"""

import json
import sys
from pathlib import Path

from discover_problems import discover_all_problems
from estimator_config import ENTRY_POINTS, extract_summary


def main():
    import qsharp

    problem_dirs = discover_all_problems()

    ok = 0
    fail = 0

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
            estimate = qsharp.estimate(ep.expr())
            data = estimate.data() if hasattr(estimate, "data") else estimate
            summary = {"problem": name, **extract_summary(data)}

            out_path = circuits_dir / "estimate.json"
            out_path.write_text(
                json.dumps(summary, indent=2, default=str), encoding="utf-8"
            )

            pq = summary.get("physicalQubits", "?")
            lq = summary.get("logicalQubits", "?")
            tc = summary.get("tCount", "?")
            print(f"OK {name}: {pq} physical qubits, {lq} logical qubits, {tc} T-gates")
            ok += 1

        except Exception as e:
            err = str(e)[:150]
            print(f"XX {name}: {err}")
            fail += 1

    print(f"\nDone: {ok} estimates generated, {fail} failed")


if __name__ == "__main__":
    sys.exit(main() or 0)
