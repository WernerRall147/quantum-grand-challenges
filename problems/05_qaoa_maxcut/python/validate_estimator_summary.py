"""Validate QAOA estimator profile summary coverage for required instances."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def validate_summary(summary_path: Path, required_instances: list[str]) -> None:
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing estimator summary: {summary_path}")

    text = summary_path.read_text(encoding="utf-8")
    for instance in required_instances:
        pattern = re.compile(
            rf"^\|\s*{re.escape(instance)}\s*\|.*\|\s*(?!n/a)([^|]+)\|\s*(?!n/a)([^|]+)\|",
            re.IGNORECASE | re.MULTILINE,
        )
        if not pattern.search(text):
            raise ValueError(
                f"Estimator summary lacks populated metrics for instance '{instance}'"
            )


def validate_stable_artifacts(
    estimates_dir: Path,
    required_instances: list[str],
    required_targets: list[str],
) -> None:
    for target in required_targets:
        target_path = estimates_dir / f"latest_{target}.json"
        if not target_path.exists():
            raise FileNotFoundError(f"Missing stable estimator artifact: {target_path}")

        for instance in required_instances:
            path = estimates_dir / f"latest_{target}_{instance}.json"
            if not path.exists():
                raise FileNotFoundError(f"Missing stable estimator artifact: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate estimator_profile_summary.md has populated rows for required instances."
    )
    parser.add_argument(
        "--summary",
        default="problems/05_qaoa_maxcut/estimates/estimator_profile_summary.md",
        help="Path to estimator profile markdown summary.",
    )
    parser.add_argument(
        "--instances",
        default="small,medium,large",
        help="Comma-separated instance IDs that must have populated metrics.",
    )
    parser.add_argument(
        "--targets",
        default="surface_code_generic_v1,qubit_gate_ns_e3",
        help="Comma-separated estimator targets that must have stable latest artifacts.",
    )
    parser.add_argument(
        "--require-stable-artifacts",
        action="store_true",
        default=True,
        help="Require latest_<target>.json and latest_<target>_<instance>.json artifacts to exist (default: enabled).",
    )
    parser.add_argument(
        "--no-require-stable-artifacts",
        dest="require_stable_artifacts",
        action="store_false",
        help="Disable stable artifact existence checks.",
    )
    args = parser.parse_args()

    instances = [part.strip() for part in args.instances.split(",") if part.strip()]
    if not instances:
        raise ValueError("No required instances specified.")
    targets = [part.strip() for part in args.targets.split(",") if part.strip()]
    if not targets:
        raise ValueError("No required targets specified.")

    summary_path = Path(args.summary)
    validate_summary(summary_path, instances)
    if args.require_stable_artifacts:
        validate_stable_artifacts(summary_path.parent, instances, targets)
    print(
        "Estimator summary validation passed for instances "
        f"{', '.join(instances)} and targets {', '.join(targets)}"
    )


if __name__ == "__main__":
    main()
