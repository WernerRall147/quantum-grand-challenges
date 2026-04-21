"""Prune stale timestamped estimator artifacts while preserving stable latest files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

TARGETS = ("surface_code_generic_v1", "qubit_gate_ns_e3")
TIMESTAMP_RE = re.compile(
    r"^(surface_code_generic_v1|qubit_gate_ns_e3)_(\d{4}-\d{2}-\d{2}T\d{6}\.\d+Z)\.json$"
)


def group_timestamped_files(estimates_dir: Path) -> Dict[str, List[Tuple[str, Path]]]:
    grouped: Dict[str, List[Tuple[str, Path]]] = {target: [] for target in TARGETS}
    for path in estimates_dir.glob("*.json"):
        match = TIMESTAMP_RE.match(path.name)
        if not match:
            continue
        target = match.group(1)
        stamp = match.group(2)
        grouped[target].append((stamp, path))

    for target in TARGETS:
        grouped[target].sort(key=lambda item: item[0], reverse=True)
    return grouped


def prune(estimates_dir: Path, keep_per_target: int, dry_run: bool) -> int:
    grouped = group_timestamped_files(estimates_dir)
    removed = 0

    for target, items in grouped.items():
        stale = items[keep_per_target:]
        for _, path in stale:
            if dry_run:
                print(f"[DRY-RUN] remove {path.name}")
            else:
                path.unlink(missing_ok=True)
                print(f"Removed {path.name}")
            removed += 1

    print(f"Prune complete: removed={removed}, keep_per_target={keep_per_target}")
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prune stale timestamped estimator artifacts in problems/05_qaoa_maxcut/estimates"
    )
    parser.add_argument(
        "--keep-per-target",
        type=int,
        default=3,
        help="Number of most recent timestamped artifacts to keep per target.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would be removed without deleting them.",
    )
    args = parser.parse_args()

    if args.keep_per_target < 1:
        raise ValueError("--keep-per-target must be >= 1")

    root = Path(__file__).resolve().parents[1]
    estimates_dir = root / "estimates"
    prune(estimates_dir, keep_per_target=args.keep_per_target, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
