"""Validate QAOA backend/transpilation/connectivity assumptions evidence."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_SECTIONS = [
    "## Execution Modes",
    "## Circuit and Gate Assumptions",
    "## Connectivity and Mapping Assumptions",
    "## Transpilation Assumptions",
    "## Noise and Measurement Assumptions",
    "## Reproducibility References",
]

REQUIRED_REFERENCES = [
    "qsharp/Program.qs",
    "host/Program.cs",
    "python/prepare_estimator_params.py",
    "tooling/estimator/run_estimation.py",
    "noise_sweep",
    "depth_sweep",
]


def validate_document(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing backend assumptions document: {path}")

    text = path.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            raise ValueError(f"Missing required section in assumptions document: {section}")

    for token in REQUIRED_REFERENCES:
        if token not in text:
            raise ValueError(f"Missing required reference token in assumptions document: {token}")


def validate_linked_artifacts(estimates_dir: Path) -> None:
    required = [
        "depth_sweep_small.md",
        "depth_sweep_medium.md",
        "depth_sweep_large.md",
        "noise_sweep_small_d3.md",
        "noise_sweep_medium_d2.md",
        "noise_sweep_large_d2.md",
    ]
    for name in required:
        path = estimates_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Missing referenced evidence artifact: {path}")


def resolve_doc_path(raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    roots = [Path.cwd(), Path(__file__).resolve().parents[1], Path(__file__).resolve().parents[3]]
    for root in roots:
        resolved = (root / candidate).resolve()
        if resolved.exists():
            return resolved
    return (Path.cwd() / candidate).resolve()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate backend/transpilation/connectivity assumptions evidence for QAOA Max-Cut."
    )
    parser.add_argument(
        "--doc",
        default="problems/05_qaoa_maxcut/estimates/backend_assumptions.md",
        help="Path to backend assumptions markdown document.",
    )
    parser.add_argument(
        "--require-artifacts",
        action="store_true",
        default=True,
        help="Require referenced depth/noise artifacts to exist (default: enabled).",
    )
    parser.add_argument(
        "--no-require-artifacts",
        dest="require_artifacts",
        action="store_false",
        help="Disable checks for referenced depth/noise artifacts.",
    )
    args = parser.parse_args()

    doc_path = resolve_doc_path(args.doc)
    validate_document(doc_path)

    if args.require_artifacts:
        validate_linked_artifacts(doc_path.parent)

    print(f"Backend assumptions validation passed: {doc_path}")


if __name__ == "__main__":
    main()
