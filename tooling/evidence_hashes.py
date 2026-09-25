"""Hashes that bind an evidence artifact to the Q# sources it describes.

A calibration ensemble records these when it is generated; tooling/reporting/stage_kpis.py
recomputes them and treats any difference as stale evidence. Five problems once kept Stage C
labels on ensembles from kernels that had since been rewritten, because nothing compared the
two. Standard library only, so the nightly report job can run it without the QDK.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def problem_source_files(qsharp_dir: Path) -> list[Path]:
    """The Q# a problem's programs are built from: manifest, hardware kernel and src/."""
    candidates = [qsharp_dir / "qsharp.json", qsharp_dir / "HardwareKernel.qs", *(qsharp_dir / "src").glob("*.qs")]
    return sorted(f for f in candidates if f.is_file())


def file_digest(path: Path) -> str:
    """sha256 with line endings normalised, so Windows and Linux checkouts of one blob agree."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def source_hashes(qsharp_dir: Path, repo_root: Path) -> dict[str, str]:
    return {f.relative_to(repo_root).as_posix(): file_digest(f) for f in problem_source_files(qsharp_dir)}
