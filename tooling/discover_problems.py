"""Shared utility to discover all problem directories (active + archived)."""

from pathlib import Path
from typing import List

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"
ARCHIVED_DIR = PROBLEMS_DIR / "archived"


def _is_problem_dir(d: Path) -> bool:
    """Return True if directory name starts with two digits (e.g. '03_qae_risk')."""
    return d.is_dir() and len(d.name) >= 2 and d.name[:2].isdigit()


def discover_all_problems() -> List[Path]:
    """Return sorted list of all problem directories (active + archived)."""
    dirs = [d for d in PROBLEMS_DIR.iterdir() if _is_problem_dir(d)]
    if ARCHIVED_DIR.is_dir():
        dirs.extend(d for d in ARCHIVED_DIR.iterdir() if _is_problem_dir(d))
    return sorted(dirs, key=lambda d: d.name)


def discover_active_problems() -> List[Path]:
    """Return sorted list of active (non-archived) problem directories only."""
    return sorted(
        [d for d in PROBLEMS_DIR.iterdir() if _is_problem_dir(d)],
        key=lambda d: d.name,
    )


def discover_archived_problems() -> List[Path]:
    """Return sorted list of archived problem directories only."""
    if not ARCHIVED_DIR.is_dir():
        return []
    return sorted(
        [d for d in ARCHIVED_DIR.iterdir() if _is_problem_dir(d)],
        key=lambda d: d.name,
    )
