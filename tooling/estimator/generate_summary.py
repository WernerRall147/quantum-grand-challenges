#!/usr/bin/env python3
"""Generate estimator_profile_summary.md for specified problems from latest artifacts."""

import json
import sys
from pathlib import Path

TARGETS = ("surface_code_generic_v1", "qubit_gate_ns_e3")

PROBLEMS = {
    "01_hubbard": "Hubbard VQE",
    "02_catalysis": "VQE Chemistry",
    "03_qae_risk": "Canonical QAE",
    "04_linear_solvers": "HHL Linear Solver",
    "05_qaoa_maxcut": "QAOA MaxCut",
    "06_high_frequency_trading": "Quantum VaR",
    "07_drug_discovery": "VQE Binding",
    "08_protein_folding": "QAOA Folding",
    "09_factorization": "Shor Factorization",
    "10_post_quantum_cryptography": "Grover Key Search",
    "11_quantum_machine_learning": "Swap Test Kernel",
    "12_quantum_optimization": "QAOA Scheduling",
    "13_climate_modeling": "HHL Diffusion",
    "14_materials_discovery": "VQE Band Gap",
    "15_database_search": "Grover Database Search",
    "16_error_correction": "Repetition Code QEC",
    "17_nuclear_physics": "VQE Deuteron",
    "18_photovoltaics": "Quantum Walk",
    "19_quantum_chromodynamics": "Trotter Gauge",
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


def _row(instance, target, payload):
    m = payload.get("metrics", {})
    src = payload.get("_metadata", {}).get("artifact_path", "n/a")
    return (
        f"| {instance} | {target} "
        f"| {fmt(m.get('logical_qubits'))} "
        f"| {fmt(m.get('physical_qubits'))} "
        f"| {fmt(m.get('t_count'))} "
        f"| {fmt(m.get('runtime_seconds'))} "
        f"| `{src}` |"
    )


def main():
    repo = Path(__file__).resolve().parents[2]
    problems = PROBLEMS
    if len(sys.argv) > 1:
        problems = {k: v for k, v in PROBLEMS.items() if k in sys.argv[1:]}

    for pid, label in problems.items():
        edir = repo / "problems" / pid / "estimates"
        if not edir.is_dir():
            # Problems downgraded in the Troyer restructure moved under
            # problems/archived/. Writing into a directory that no longer exists
            # raised FileNotFoundError and killed the whole run at the first one.
            print(f"Skipping {pid}: no {edir.relative_to(repo).as_posix()}")
            continue
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
