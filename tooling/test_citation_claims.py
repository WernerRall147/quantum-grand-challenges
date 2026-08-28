"""The citation metadata is the one file written to be quoted by strangers.

This repository's argument is that it does not over-claim. It was over-claiming in
CITATION.cff: the abstract said "All 20 problems at Stage C" while
docs/objective-kpis.json recorded 9 at C, 8 still at B, and 3 at D. Nobody noticed
because nothing read the two files together, and prose does not fail a build.

So read them together. These tests do not check that the abstract is well written.
They check that the numbers in it are the numbers the pipeline actually produced,
which is the only part a reader can be misled by.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CITATION = REPO_ROOT / "CITATION.cff"
KPIS = REPO_ROOT / "docs" / "objective-kpis.json"

# Zenodo mints two DOIs: one per version, and one "concept" DOI for the record as a
# whole that always resolves to the newest version. CITATION.cff wants the concept DOI.
# 10.5281/zenodo.19222021 is the version DOI for the v1.0.1 archive from 2026-03-25, and
# it sat here beside `version: 3.1.0` for months - a citation pointing five versions back.
CONCEPT_DOI = "10.5281/zenodo.19222020"
VERSION_DOI_V1 = "10.5281/zenodo.19222021"


def _abstract() -> str:
    """The abstract block, unwrapped to a single line.

    CITATION.cff is YAML, but adding a YAML dependency to assert on one string is a
    poor trade. The abstract is a folded block starting at 'abstract: >-' and running
    until the next top-level key, which is enough structure to slice on.
    """
    text = CITATION.read_text(encoding="utf-8")
    match = re.search(r"^abstract: >-\n(.*?)^\S", text, re.S | re.M)
    assert match, "CITATION.cff has no folded abstract block"
    return " ".join(match.group(1).split())


def _stage_counts() -> Counter[str]:
    records = json.loads(KPIS.read_text(encoding="utf-8"))["records"]
    return Counter(record["stage"] for record in records)


# Deliberately tolerant of phrasing. "9 problems are at Stage C", "8 remain at
# Stage B" and "3 have reached Stage D" are all the same claim, and a test that
# only accepts one wording fails on honest rewording, which trains people to
# delete it. Excluding digits and full stops from the filler stops a match from
# running across a sentence boundary and pairing an unrelated number to a stage.
_STAGE_CLAIM = re.compile(r"(\d+)[^.\d]{0,40}?Stage\s+([A-D])\b")


def _claimed_stages() -> list[tuple[int, str]]:
    return [(int(n), stage) for n, stage in _STAGE_CLAIM.findall(_abstract())]


def test_abstract_stage_counts_match_the_kpi_file() -> None:
    """Every stage count claimed in the abstract must match objective-kpis.json.

    Checking the rendered claim rather than a variable means the test fails when a
    human edits the prose, which is exactly when it drifts.
    """
    counts = _stage_counts()
    claimed = _claimed_stages()
    assert claimed, f"abstract makes no per-stage claim to verify: {_abstract()!r}"

    for n, stage in claimed:
        assert n == counts[stage], (
            f"abstract says {n} problems at Stage {stage}, "
            f"objective-kpis.json records {counts[stage]}"
        )


def test_abstract_does_not_claim_every_problem_reached_one_stage() -> None:
    """The specific false claim that was there, pinned so it cannot come back.

    "All 20 problems at Stage C" is the shape of over-claim this project exists to
    argue against, and it survived in the citation file for months.
    """
    abstract = _abstract()
    assert not re.search(r"all\s+20\s+problems?\s+(?:are\s+)?at\s+Stage", abstract, re.I), (
        "abstract claims all 20 problems reached a single stage; "
        f"they are distributed {dict(_stage_counts())}"
    )


def test_abstract_accounts_for_all_twenty_problems() -> None:
    """Stage claims must sum to the problem count, so none are quietly dropped.

    Reporting only the flattering stages would pass the equality check above while
    still misleading, because a reader sums what they are given.
    """
    counts = _stage_counts()
    claimed = _claimed_stages()
    assert sum(n for n, _ in claimed) == sum(counts.values()), (
        f"abstract accounts for {sum(n for n, _ in claimed)} problems, "
        f"objective-kpis.json has {sum(counts.values())}"
    )


@pytest.mark.parametrize("field", ["version", "date-released", "doi"])
def test_citation_declares_release_identity(field: str) -> None:
    """A citation without a version, date and DOI cannot be cited reproducibly."""
    text = CITATION.read_text(encoding="utf-8")
    assert re.search(rf"^{re.escape(field)}:\s*\S+", text, re.M), (
        f"CITATION.cff is missing {field}"
    )


def test_doi_is_the_concept_doi() -> None:
    """The DOI must resolve to the newest version, not to whichever one was current once.

    A version DOI freezes the citation at one release. Anyone following it lands on the
    archive it was minted for, however many versions have shipped since.
    """
    text = CITATION.read_text(encoding="utf-8")
    assert CONCEPT_DOI in text, f"CITATION.cff should cite the concept DOI {CONCEPT_DOI}"
    assert VERSION_DOI_V1 not in text, (
        f"CITATION.cff cites {VERSION_DOI_V1}, which is the version DOI for the v1.0.1 "
        f"archive. Use the concept DOI {CONCEPT_DOI}."
    )


# Fixing CITATION.cff alone left the same stale DOI in eleven other places, including the
# README badge and the website's BibTeX block. One owner per fact only works if something
# checks the other owners, so this walks the tree rather than trusting a one-line fix.
_SKIP_DIRS = frozenset(
    {".git", "node_modules", "out", ".next", "__pycache__", ".venv", "venv", ".pytest_cache"}
)
_CITING_SUFFIXES = frozenset({".md", ".cff", ".tsx", ".ts", ".html", ".py", ".json", ".yml"})

# Documents that record something already sent or already published are not rewritten in
# place. The storyboard says so itself: it is "the record of what the producers have".
_RECORDS = (
    "docs/Hackathon2026/",
    "docs/AzureFriday/storyboard.md",
    "tooling/test_citation_claims.py",
)


def _live_files_citing(doi: str) -> list[str]:
    found = []
    stack = [REPO_ROOT]
    while stack:
        for entry in stack.pop().iterdir():
            if entry.is_dir():
                if entry.name not in _SKIP_DIRS:
                    stack.append(entry)
                continue
            if entry.suffix not in _CITING_SUFFIXES:
                continue
            rel = entry.relative_to(REPO_ROOT).as_posix()
            if rel.startswith(_RECORDS):
                continue
            if doi in entry.read_text(encoding="utf-8", errors="ignore"):
                found.append(rel)
    return sorted(found)


def test_no_live_document_cites_the_superseded_version_doi() -> None:
    """The v1.0.1 DOI must not appear anywhere a reader would take as the project's DOI.

    Version DOIs are legitimate when you mean that release - the paper's erratum cites
    v2.0.0 deliberately. This one is different: it was pasted around as the project DOI
    while five versions shipped, so any live occurrence is the stale-citation bug again.
    """
    offenders = _live_files_citing(VERSION_DOI_V1)
    assert not offenders, (
        f"{len(offenders)} live file(s) cite {VERSION_DOI_V1}, the superseded v1.0.1 "
        f"version DOI: {', '.join(offenders)}. Use the concept DOI {CONCEPT_DOI}."
    )
