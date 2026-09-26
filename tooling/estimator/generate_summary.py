#!/usr/bin/env python3
"""Generate estimator_profile_summary.md for each problem from its single estimate.

Reads problems/<id>/circuits/estimate.json - the one source of truth, written by
tooling/generate_estimates.py for all 20 problems, archived ones included. It used to
read problems/<id>/estimates/latest_*.json, a second store retired because a fabricated
constant sat there undetected next to real numbers. Archived problems keep that store as
a record, but most of its files are the mock constant (build.qdk_version "mock"), and
the archived summaries printed it as their estimate until 2026-09-27. The store is now
read only when no real estimate exists, and mock rows are labelled.
"""

import json
import sys
from pathlib import Path

TARGETS = ("surface_code_generic_v1", "qubit_gate_ns_e3")

PROBLEMS = {
    "01_hubbard": "Hubbard QPE",
    "02_catalysis": "QPE Chemistry (H2)",
    "03_qae_risk": "Canonical QAE",
    "04_linear_solvers": "HHL Linear Solver",
    "05_qaoa_maxcut": "QAOA MaxCut",
    "06_high_frequency_trading": "Loss-Probability Sampling",
    "07_drug_discovery": "QPE Binding Model",
    "08_protein_folding": "QAOA Folding",
    "09_factorization": "Shor Factorization",
    "10_post_quantum_cryptography": "Grover Key Search",
    "11_quantum_machine_learning": "Swap Test Kernel",
    "12_quantum_optimization": "QAOA Scheduling",
    "13_climate_modeling": "HHL Diffusion",
    "14_materials_discovery": "QPE Band Gap",
    "15_database_search": "Grover Database Search",
    "16_error_correction": "Repetition Code QEC",
    "17_nuclear_physics": "QPE Deuteron",
    "18_photovoltaics": "Quantum Walk",
    "19_quantum_chromodynamics": "Trotter Ising Chain",
    "20_space_mission_planning": "QAOA Trajectory",
}


def fmt(v):
    if isinstance(v, bool) or v is None:
        return "n/a"
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, float):
        # Real estimates land in microseconds; %.2f rendered every one of them as
        # "0.00", which reads as "no runtime" rather than "too small for this format".
        if v and abs(v) < 0.01:
            return f"{v:.3g}"
        return f"{v:,.2f}"
    return "n/a"


def _is_mock(payload) -> bool:
    build = payload.get("build", {}) if isinstance(payload.get("build"), dict) else {}
    return str(build.get("qdk_version", "")).startswith("mock") or str(build.get("estimator_version", "")).startswith("mock")


def _row(instance, target, payload):
    m = payload.get("metrics", {})
    src = payload.get("_metadata", {}).get("artifact_path", "n/a")
    if _is_mock(payload):
        target = f"{target} (mock output, not an estimate)"
    return (
        f"| {instance} | {target} "
        f"| {fmt(m.get('logical_qubits'))} "
        f"| {fmt(m.get('physical_qubits'))} "
        f"| {fmt(m.get('t_count'))} "
        f"| {fmt(m.get('runtime_seconds'))} "
        f"| `{src}` |"
    )


def _row_from_circuits(pid, estimate, source):
    """One row from circuits/estimate.json, the single source of truth.

    Reports the qubit model and QEC scheme actually estimated rather than a
    target-profile name. The old profile names were not independent machines:
    surface_code_generic_v1 resolves to the same model as qubit_gate_ns_e3, so
    listing both printed one measurement as two.
    """
    runtime_ns = estimate.get("runtime")
    runtime_seconds = float(runtime_ns) / 1e9 if runtime_ns else None
    target = f"{estimate.get('qubitModel', '?')} + {estimate.get('qecScheme', '?')}"
    return (
        f"| not instance-specific | {target} "
        f"| {fmt(estimate.get('logicalQubits'))} "
        f"| {fmt(estimate.get('physicalQubits'))} "
        f"| {fmt(estimate.get('tCount'))} "
        f"| {fmt(runtime_seconds)} "
        f"| `{source}` |"
    )


def _rows_from_retired_store(edir):
    """Archived problems still carry problems/<id>/estimates/latest_*.json."""
    rows = []
    for target in TARGETS:
        per_instance = {
            instance: edir / f"latest_{target}_{instance}.json"
            for instance in ("small", "medium", "large")
        }
        found = {i: p for i, p in per_instance.items() if p.exists()}
        if found:
            for instance, path in found.items():
                rows.append(
                    _row(instance, target, json.loads(path.read_text(encoding="utf-8-sig")))
                )
            continue

        # No per-instance artifacts. This used to print the same fallback figures
        # under all three instance labels, which reads as three measurements that
        # happen to agree rather than one measurement shown three times.
        fallback = edir / f"latest_{target}.json"
        if not fallback.exists():
            rows.append(f"| not instance-specific | {target} | n/a | n/a | n/a | n/a | n/a |")
            continue
        rows.append(
            _row(
                "not instance-specific",
                target,
                json.loads(fallback.read_text(encoding="utf-8-sig")),
            )
        )
    return rows


def main():
    repo = Path(__file__).resolve().parents[2]
    problems = PROBLEMS
    if len(sys.argv) > 1:
        problems = {k: v for k, v in PROBLEMS.items() if k in sys.argv[1:]}

    for pid, label in problems.items():
        problem_dir = repo / "problems" / pid
        archived = False
        if not problem_dir.is_dir():
            # Problems downgraded in the Troyer restructure moved under
            # problems/archived/. Writing into a directory that no longer exists
            # raised FileNotFoundError and killed the whole run at the first one.
            problem_dir = repo / "problems" / "archived" / pid
            archived = True
        edir = problem_dir / "estimates"
        if not edir.is_dir():
            print(f"Skipping {pid}: no {edir.relative_to(repo).as_posix()}")
            continue

        circuits_estimate = problem_dir / "circuits" / "estimate.json"
        if circuits_estimate.exists():
            estimate = json.loads(circuits_estimate.read_text(encoding="utf-8-sig"))
            rows = [
                _row_from_circuits(
                    pid, estimate, circuits_estimate.relative_to(repo).as_posix()
                )
            ]
            provenance = (
                "Auto-generated from `circuits/estimate.json`, the single source of "
                "truth for this problem's resource estimate.\n\n"
            )
            mock_files = [
                path.name
                for path in sorted(edir.glob("latest*.json"))
                if _is_mock(json.loads(path.read_text(encoding="utf-8-sig")))
            ]
            if archived and mock_files:
                provenance += (
                    f"The retired store in `estimates/` ({', '.join(f'`{name}`' for name in mock_files)}) "
                    "holds mock output from a removed estimator path, a fixed constant that is "
                    "not an estimate of this program.\n\n"
                )
        else:
            rows = _rows_from_retired_store(edir)
            provenance = (
                "Auto-generated from the archived per-target artifacts in `estimates/`.\n\n"
            )

        md = (
            f"# {label} Estimator Summary\n\n"
            + provenance
            + "| Instance | Target | Logical Qubits | Physical Qubits | T Count | Runtime (s) | Source |\n"
            "|---|---|---:|---:|---:|---:|---|\n"
            + "\n".join(rows)
            + "\n"
        )
        out = edir / "estimator_profile_summary.md"
        out.write_text(md, encoding="utf-8")
        print(f"Wrote {out.relative_to(repo)}")


if __name__ == "__main__":
    main()
