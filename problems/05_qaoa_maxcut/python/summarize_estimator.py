"""Generate a markdown summary of latest QAOA estimator artifacts by instance and target."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

TARGETS = ("surface_code_generic_v1", "qubit_gate_ns_e3")


def parse_timestamp(value: Optional[str]) -> datetime:
    if not value:
        return datetime.min
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return datetime.min


def discover_latest_by_instance_and_target(estimates_dir: Path) -> Dict[Tuple[str, str], dict]:
    latest: Dict[Tuple[str, str], dict] = {}

    for path in sorted(estimates_dir.glob("*.json")):
        name = path.name
        if name.startswith("quantum_baseline_") or name.startswith("estimator_params_"):
            continue
        if name in {"classical_baseline.json", "latest.json"}:
            continue

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        target = payload.get("estimator_target")
        if target not in TARGETS:
            continue

        params = payload.get("instance", {}).get("parameters", {})
        instance = params.get("size") or params.get("instance")
        if not instance:
            instance = payload.get("instance", {}).get("description", "")
        instance = str(instance).strip().lower()
        if instance not in {"small", "medium", "large"}:
            continue

        stamp = parse_timestamp(payload.get("_metadata", {}).get("generated_at_utc"))
        key = (instance, target)
        current = latest.get(key)
        current_stamp = parse_timestamp(
            current.get("_metadata", {}).get("generated_at_utc") if current else None
        )
        if current is None or stamp >= current_stamp:
            latest[key] = payload

    return latest


def fmt_num(value: object) -> str:
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return "n/a"


def build_markdown(latest: Dict[Tuple[str, str], dict]) -> str:
    lines: List[str] = []
    lines.append("# QAOA Estimator Summary")
    lines.append("")
    lines.append("Auto-generated from latest target artifacts in `estimates/`.")
    lines.append("")
    lines.append("| Instance | Target | Logical Qubits | Physical Qubits | T Count | Runtime (s) | Source |")
    lines.append("|---|---|---:|---:|---:|---:|---|")

    for instance in ("small", "medium", "large"):
        for target in TARGETS:
            payload = latest.get((instance, target))
            if payload is None:
                lines.append(f"| {instance} | {target} | n/a | n/a | n/a | n/a | n/a |")
                continue

            metrics = payload.get("metrics", {})
            source = payload.get("_metadata", {}).get("artifact_path")
            source_text = f"`{source}`" if source else "n/a"
            lines.append(
                "| "
                f"{instance} | {target} | {fmt_num(metrics.get('logical_qubits'))} | "
                f"{fmt_num(metrics.get('physical_qubits'))} | {fmt_num(metrics.get('t_count'))} | "
                f"{fmt_num(metrics.get('runtime_seconds'))} | {source_text} |"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    estimates_dir = root / "estimates"
    latest = discover_latest_by_instance_and_target(estimates_dir)

    output_path = estimates_dir / "estimator_profile_summary.md"
    output_path.write_text(build_markdown(latest), encoding="utf-8")

    try:
        rel = output_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel = output_path
    print(f"Wrote {rel}")


if __name__ == "__main__":
    main()
