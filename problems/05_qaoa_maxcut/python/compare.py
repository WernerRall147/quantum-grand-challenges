"""Generate a markdown quantum-vs-classical summary for QAOA Max-Cut."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def load_classical_best(estimates_dir: Path) -> Dict[str, float]:
    payload = json.loads((estimates_dir / "classical_baseline.json").read_text(encoding="utf-8"))
    results = payload.get("results", [])
    out: Dict[str, float] = {}
    for item in results:
        instance = str(item.get("instance_id", "")).strip()
        if not instance:
            continue
        out[instance] = float(item.get("best_cut", 0.0))
    return out


def load_quantum_reports(estimates_dir: Path) -> List[dict]:
    reports: List[dict] = []
    for path in sorted(estimates_dir.glob("quantum_baseline_*_d*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        aggregate = payload.get("aggregate", {})
        refined = aggregate.get("refined_expectation", {})
        reports.append(
            {
                "instance_id": str(payload.get("instance_id", "")).strip(),
                "depth": int(payload.get("depth", 1)),
                "trials": int(payload.get("trials", 0)),
                "mean": float(refined.get("mean", 0.0)),
                "ci95": float(refined.get("ci95", 0.0)),
                "gap": float(aggregate.get("mean_optimality_gap", 0.0)),
                "source": path.name,
            }
        )
    return reports


def pick_best_report_per_instance(reports: List[dict]) -> Dict[str, dict]:
    selected: Dict[str, dict] = {}
    for report in reports:
        instance = report["instance_id"]
        if not instance:
            continue
        current = selected.get(instance)
        if current is None:
            selected[instance] = report
            continue
        if (report["depth"], report["trials"]) > (current["depth"], current["trials"]):
            selected[instance] = report
    return selected


def build_markdown(classical_best: Dict[str, float], selected_reports: Dict[str, dict]) -> str:
    lines: List[str] = []
    lines.append("# QAOA Quantum vs Classical Summary")
    lines.append("")
    lines.append("This summary is auto-generated from `estimates/classical_baseline.json` and `estimates/quantum_baseline_*_d*.json`.")
    lines.append("")
    lines.append("| Instance | Classical Optimum | Quantum Refined Mean +/- 95% CI | Mean Gap | Depth | Trials | Source |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")

    all_instances = sorted(set(classical_best.keys()) | set(selected_reports.keys()))
    for instance in all_instances:
        classical = classical_best.get(instance)
        report = selected_reports.get(instance)
        if report is None:
            lines.append(
                f"| {instance} | {classical:.4f} | n/a | n/a | n/a | n/a | n/a |" if classical is not None
                else f"| {instance} | n/a | n/a | n/a | n/a | n/a | n/a |"
            )
            continue

        classical_text = f"{classical:.4f}" if classical is not None else "n/a"
        quantum_text = f"{report['mean']:.4f} +/- {report['ci95']:.4f}"
        gap_text = f"{report['gap']:.4f}"
        lines.append(
            f"| {instance} | {classical_text} | {quantum_text} | {gap_text} | {report['depth']} | {report['trials']} | `{report['source']}` |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates_dir = root / "estimates"

    classical_path = estimates_dir / "classical_baseline.json"
    if not classical_path.exists():
        raise FileNotFoundError("Run `make classical` before generating the comparison summary.")

    reports = load_quantum_reports(estimates_dir)
    if not reports:
        raise FileNotFoundError(
            "No quantum baseline reports found. Run `make run` for one or more instances before generating summary."
        )

    classical_best = load_classical_best(estimates_dir)
    selected = pick_best_report_per_instance(reports)

    output_path = estimates_dir / "quantum_classical_summary.md"
    output_path.write_text(build_markdown(classical_best, selected), encoding="utf-8")

    try:
        rel = output_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel = output_path
    print(f"Wrote {rel}")


if __name__ == "__main__":
    main()
