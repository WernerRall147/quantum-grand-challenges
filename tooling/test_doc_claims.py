"""Numbers in prose go stale. This makes that fail instead of shipping.

The test count in `deck-notes.md` was 116 when the suite had 214. It was corrected by
hand, and three days later it read 214 against a suite of 242 - stale again inside the
same week, in the one table written to be quoted on camera instead of the deck.

Hand-updating a number that changes whenever anyone adds a test does not work. So the
number is checked here, and the fix when this fails is one edit.

Archival documents are exempt: a frozen hackathon submission or a dated planning note is
a record of what was true then, and rewriting history to satisfy a linter is worse than
the drift.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KPIS = REPO_ROOT / "docs" / "objective-kpis.json"

# Records of a moment, not claims about now.
ARCHIVAL = (
    "docs/Hackathon2026/",
    "docs/AI_Expanations/",
    "docs/planning/",
    "docs/MILESTONE_",
    "docs/QAE_PROJECT_COMPLETION",
)

_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "out", ".next", "problems"}

_TEST_COUNT = re.compile(r"\b(\d{2,4})\s+tests?\b")

# Prose about past counts is not a claim about now. A line-level marker beats exempting
# a whole file, which would also hide any live claim it grows later.
HISTORICAL = "<!-- historical -->"

# For lines that state a wrong number on purpose - a "do not say" entry, or a worked
# example of the bug. Without this the stage check fires on the very lists written to
# stop people repeating the claim.
NOT_A_CLAIM = "<!-- not-a-claim -->"

# Tolerant of phrasing: "9 problems are at Stage C" and "9 have reached Stage C" are the
# same claim. Excluding digits and full stops from the filler stops a match running
# across a sentence boundary. The trailing \w guard is what keeps `15_database_search`
# from reading as a claim that 15 problems sit at whatever stage the line mentions next.
_STAGE_CLAIM = re.compile(r"(\d+)(?!\w)[^.\d]{0,40}?Stage\s+([A-D])\b")


@lru_cache(maxsize=1)
def _collected_count() -> int:
    """How many tests pytest actually collects.

    A subprocess rather than `request.session.items`, because the session count is wrong
    whenever someone runs a single file and a test that only works under a full run is a
    test people learn to ignore.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--no-header"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    match = re.search(r"(\d+)\s+tests?\s+collected", result.stdout)
    assert match, f"could not read a collected count from pytest:\n{result.stdout[-800:]}"
    return int(match.group(1))


def _live_docs() -> list[Path]:
    return [
        path
        for path in REPO_ROOT.rglob("*.md")
        if not _SKIP_DIRS.intersection(path.parts)
        and not any(
            path.relative_to(REPO_ROOT).as_posix().startswith(prefix) for prefix in ARCHIVAL
        )
    ]


def _claims() -> list[tuple[str, int, int]]:
    """Every (file, line, count) where a live document states a test count."""
    found = []
    for path in _live_docs():
        rel = path.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if HISTORICAL in line:
                continue
            for match in _TEST_COUNT.finditer(line):
                found.append((rel, lineno, int(match.group(1))))
    return found


def test_documented_test_count_is_current() -> None:
    """One test, not one per claim.

    Parametrising over the claims made the suite size depend on how many documents
    mentioned it, so adding a claim shifted the very number every claim had to state.
    A single test contributes exactly one whatever the documents say.
    """
    actual = _collected_count()
    stale = [
        f"{doc}:{lineno} claims {claimed}"
        for doc, lineno, claimed in _claims()
        if claimed != actual
    ]
    assert not stale, (
        f"pytest collects {actual} tests, but: {'; '.join(stale)}. "
        f"Update the document, or move it under an ARCHIVAL prefix if it is a record "
        f"of a past moment rather than a claim about now."
    )


@lru_cache(maxsize=1)
def _stage_counts() -> tuple[tuple[str, int], ...]:
    records = json.loads(KPIS.read_text(encoding="utf-8"))["records"]
    return tuple(sorted(Counter(r["stage"] for r in records).items()))


def _stage_claims() -> list[tuple[str, int, int, str]]:
    """Every (file, line, count, stage) where a live document states a stage count."""
    found = []
    for path in _live_docs():
        rel = path.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if HISTORICAL in line or NOT_A_CLAIM in line:
                continue
            for match in _STAGE_CLAIM.finditer(line):
                found.append((rel, lineno, int(match.group(1)), match.group(2)))
    return found


def test_documented_stage_counts_are_current() -> None:
    """Maturity claims in prose must match what the pipeline recorded.

    This is the claim the project exists to police, and the paper got it wrong in three
    places: it reported all 20 problems at Stage C and four at Stage D while
    objective-kpis.json recorded 3 at C and none at D. Prose does not fail a build, so
    the over-claim outlived two releases in the one document written to be cited.
    """
    counts = dict(_stage_counts())
    wrong = [
        f"{doc}:{lineno} claims {claimed} at Stage {stage} (actual {counts.get(stage, 0)})"
        for doc, lineno, claimed, stage in _stage_claims()
        if claimed != counts.get(stage, 0)
    ]
    assert not wrong, (
        f"objective-kpis.json records {counts}, but: {'; '.join(wrong)}. "
        f"Update the document, or mark the line {NOT_A_CLAIM} if it states the wrong "
        f"number deliberately."
    )
