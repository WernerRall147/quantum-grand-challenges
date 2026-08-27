"""The architecture document names files. Some of them do not exist.

Three separate claims in this repo turned out to be false this week, all the same shape:
a document asserting something complete that the code contradicted. CITATION.cff said all
twenty problems had reached Stage C. architecture.md ticked two MCP servers as built while
saying "Not built" a hundred and fifty lines above. And its directory tree lists source
files that were never written.

Each was fixed by correcting the prose, which is why it kept happening. Prose does not
fail a build. This does: every filename the architecture document names must exist
somewhere in the repository.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE = REPO_ROOT / "docs" / "architecture.md"

# Extensions worth checking. Anything outside this set is prose - "Stage C", "v3.1.0",
# "0.9 confidence" - and matching on a bare dot would flag all of it.
CHECKED_SUFFIXES = {
    ".py", ".json", ".yaml", ".yml", ".bicep", ".tsx", ".ts", ".qs", ".md", ".txt",
}

_FILENAME = re.compile(r"[A-Za-z0-9_.-]+\.[A-Za-z0-9]+")

_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "out", ".next"}


def _tree_block() -> str:
    """The fenced directory tree, which is the part that names files.

    Tolerates prose between the heading and the fence; requiring them adjacent broke the
    moment a sentence was added under the heading.
    """
    text = ARCHITECTURE.read_text(encoding="utf-8")
    match = re.search(
        r"## Directory Structure.*?^```[^\n]*\n(.*?)^```", text, re.S | re.M
    )
    assert match, "architecture.md has no fenced Directory Structure block"
    return match.group(1)


def _named_files(block: str) -> set[str]:
    """Filenames the tree claims exist.

    Only the part of each line before '#' counts: the trailing comments are prose and
    mentioning a file there is not a claim that the tree contains it.
    """
    names: set[str] = set()
    for line in block.splitlines():
        for token in _FILENAME.findall(line.split("#", 1)[0]):
            if Path(token).suffix.lower() in CHECKED_SUFFIXES:
                names.add(token)
    return names


@lru_cache(maxsize=1)
def _repo_filenames() -> frozenset[str]:
    """Cached: the parametrised tests would otherwise walk the repo once per case."""
    return frozenset(
        path.name
        for path in REPO_ROOT.rglob("*")
        if path.is_file() and not _SKIP_DIRS.intersection(path.parts)
    )


@pytest.mark.parametrize("name", sorted(_named_files(_tree_block())))
def test_documented_file_exists(name: str) -> None:
    """Every file the directory tree names must exist somewhere in the repo.

    Parametrised so a failure names the offending file instead of dumping a set diff.
    Matching on basename rather than full path keeps the test from re-implementing the
    tree's indentation, and is still enough to catch a file that was never written.
    """
    assert name in _repo_filenames(), (
        f"architecture.md's directory tree lists {name!r}, which does not exist "
        f"anywhere in the repository"
    )


def test_tree_names_something() -> None:
    """Guard the parser: a regex that silently matches nothing would pass everything."""
    assert len(_named_files(_tree_block())) >= 5
