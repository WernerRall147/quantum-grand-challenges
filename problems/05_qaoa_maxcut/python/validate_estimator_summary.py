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
    args = parser.parse_args()

    instances = [part.strip() for part in args.instances.split(",") if part.strip()]
    if not instances:
        raise ValueError("No required instances specified.")

    summary_path = Path(args.summary)
    validate_summary(summary_path, instances)
    print(f"Estimator summary coverage validated for: {', '.join(instances)}")


if __name__ == "__main__":
    main()
