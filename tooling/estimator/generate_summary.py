#!/usr/bin/env python3
"""Generate estimator_profile_summary.md for specified problems from latest artifacts."""

import json
import sys
from pathlib import Path

TARGETS = ("surface_code_generic_v1", "qubit_gate_ns_e3")

PROBLEMS = {
    "01_hubbard": "Hubbard VQE",
    "04_linear_solvers": "HHL Linear Solver",
    "15_database_search": "Grover Database Search",
}


def fmt(v):
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, float):
        return f"{v:,.2f}"
    return "n/a"


def main():
    repo = Path(__file__).resolve().parents[2]
    problems = PROBLEMS
    if len(sys.argv) > 1:
        problems = {k: v for k, v in PROBLEMS.items() if k in sys.argv[1:]}

    for pid, label in problems.items():
        edir = repo / "problems" / pid / "estimates"
        rows = []
        for instance in ("small", "medium", "large"):
            for target in TARGETS:
                lp = edir / f"latest_{target}_{instance}.json"
                if not lp.exists():
                    lp = edir / f"latest_{target}.json"
                if not lp.exists():
                    rows.append(f"| {instance} | {target} | n/a | n/a | n/a | n/a | n/a |")
                    continue
                p = json.loads(lp.read_text(encoding="utf-8-sig"))
                m = p.get("metrics", {})
                src = p.get("_metadata", {}).get("artifact_path", "n/a")
                rows.append(
                    f"| {instance} | {target} "
                    f"| {fmt(m.get('logical_qubits'))} "
                    f"| {fmt(m.get('physical_qubits'))} "
                    f"| {fmt(m.get('t_count'))} "
                    f"| {fmt(m.get('runtime_seconds'))} "
                    f"| `{src}` |"
                )
        md = (
            f"# {label} Estimator Summary\n\n"
            "Auto-generated from latest target artifacts in `estimates/`.\n\n"
            "| Instance | Target | Logical Qubits | Physical Qubits | T Count | Runtime (s) | Source |\n"
            "|---|---|---:|---:|---:|---:|---|\n"
            + "\n".join(rows)
            + "\n"
        )
        out = edir / "estimator_profile_summary.md"
        out.write_text(md, encoding="utf-8")
        print(f"Wrote {out.relative_to(repo)}")


if __name__ == "__main__":
    main()
