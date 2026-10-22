"""The frontier-results register: results from the literature, with the conditions they hold in.

Coverage of Google's magic state cultivation experiment called it "99.99% logical
fidelity". The paper (arXiv:2512.13908v1) reports a T-state fidelity of 0.9999(1),
"retaining 8% of attempts". Both qualifiers fell off somewhere between the source and
the headline, and prose cannot stop that from happening here. A field the schema
requires can.

knowledge/data/frontier_results.json records results that bear on this repository's
numbers and verdicts. These tests hold its shape in place, so every claim names its
conditions, one kind of evidence and what it does not establish. They also check what
a schema cannot: that arXiv identifiers carry a version, that no source was read in
the future, and that the problems and zoo entries it points at exist.
"""

from __future__ import annotations

import copy
import datetime
import json
import re
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA = REPO_ROOT / "knowledge" / "data"
REGISTER = DATA / "frontier_results.json"
SCHEMA = DATA / "frontier_results.schema.json"
ZOO = DATA / "algorithm_zoo_index.json"

# An arXiv citation without a version points at whatever the authors upload next.
ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}v\d+$")
ARXIV_ABS = re.compile(r"^https://arxiv\.org/abs/(?P<id>\S+)$")
PROBLEM_DIR = re.compile(r"^\d{2}_[a-z0-9_]+$")


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_allowed_date() -> datetime.date:
    """Today, read from the clock, in the earliest time zone on Earth.

    UTC+14 is a calendar day ahead of UTC, so a source read there today can carry
    tomorrow's UTC date. Anything later than that is a typo.
    """
    return datetime.datetime.now(datetime.timezone.utc).date() + datetime.timedelta(days=1)


def _problem_ids() -> set[str]:
    roots = (REPO_ROOT / "problems", REPO_ROOT / "problems" / "archived")
    return {p.name for root in roots for p in root.iterdir() if p.is_dir() and PROBLEM_DIR.match(p.name)}


def _zoo_names() -> set[str]:
    return {algorithm["name"] for algorithm in _load(ZOO)["algorithms"]}


def violations(register, schema, *, latest_date, problems, zoo) -> list[str]:
    """Every way the register is wrong, as readable strings; empty when it is right."""
    found = [
        f"schema: {error.message} (at {'/'.join(map(str, error.absolute_path)) or 'the root'})"
        for error in jsonschema.Draft7Validator(schema).iter_errors(register)
    ]
    if found:
        return found  # the checks below rely on the shape the schema guarantees

    seen: set[str] = set()
    for entry in register["entries"]:
        eid = entry["id"]
        if eid in seen:
            found.append(f"{eid}: duplicate id")
        seen.add(eid)

        arxiv = entry["identifiers"].get("arxiv")
        if arxiv is not None and not ARXIV_ID.match(arxiv):
            found.append(f"{eid}: arXiv identifier {arxiv!r} is not versioned (write it like 2610.22367v1)")
        url = ARXIV_ABS.match(entry["source_url"])
        if url and url.group("id") != arxiv:
            found.append(f"{eid}: source_url points at {url.group('id')!r} but identifiers.arxiv is {arxiv!r}")

        try:
            read_on = datetime.date.fromisoformat(entry["read_on"])
        except ValueError:
            found.append(f"{eid}: read_on {entry['read_on']!r} is not a calendar date")
        else:
            if read_on > latest_date:
                found.append(f"{eid}: read_on {read_on} is in the future")

        for problem in entry["related_problems"]:
            if problem not in problems:
                found.append(f"{eid}: related problem {problem!r} is not a directory under problems/ or problems/archived/")
        for name in entry["related_zoo_entries"]:
            if name not in zoo:
                found.append(f"{eid}: related zoo entry {name!r} is not in knowledge/data/algorithm_zoo_index.json")
    return found


def _check(register) -> list[str]:
    return violations(
        register,
        _load(SCHEMA),
        latest_date=_latest_allowed_date(),
        problems=_problem_ids(),
        zoo=_zoo_names(),
    )


def test_the_schema_is_a_valid_draft_07_schema():
    jsonschema.Draft7Validator.check_schema(_load(SCHEMA))


def test_the_register_has_no_violations():
    assert _check(_load(REGISTER)) == []


# The register passing means nothing unless the same checks report a register that is
# wrong, so each one is shown to fire on a copy broken in one specific way.


def _first(items, predicate, what):
    for item in items:
        if predicate(item):
            return item
    raise AssertionError(f"the register has no {what} to break; seed one before relying on this test")


def _a_claim(register):
    return register["entries"][0]["claims"][0]


def _a_number(register):
    claims = (claim for entry in register["entries"] for claim in entry["claims"])
    return _first(claims, lambda claim: claim.get("numbers"), "claim with numbers")["numbers"][0]


def _an_arxiv_entry(register):
    return _first(register["entries"], lambda entry: "arxiv" in entry["identifiers"], "arXiv entry")


def _drop_limits(register):
    del _a_claim(register)["does_not_establish"]


def _empty_conditions(register):
    _a_claim(register)["conditions"] = []


def _unknown_evidence(register):
    _a_claim(register)["evidence"] = "press-release"


def _unqualified_number(register):
    _a_number(register)["qualifiers"] = []


def _unversioned_arxiv(register):
    entry = _an_arxiv_entry(register)
    unversioned = entry["identifiers"]["arxiv"].split("v")[0]
    entry["identifiers"]["arxiv"] = unversioned
    entry["source_url"] = f"https://arxiv.org/abs/{unversioned}"


def _mismatched_source_url(register):
    _an_arxiv_entry(register)["source_url"] = "https://arxiv.org/abs/2401.00001v1"


def _future_read_on(register):
    register["entries"][0]["read_on"] = "2999-01-01"


def _impossible_read_on(register):
    register["entries"][0]["read_on"] = "2026-02-30"


def _unknown_problem(register):
    register["entries"][0]["related_problems"].append("99_perpetual_motion")


def _unknown_zoo_entry(register):
    register["entries"][0]["related_zoo_entries"].append("Quantum Supremacy Engine")


def _duplicate_id(register):
    register["entries"].append(copy.deepcopy(register["entries"][0]))


def _peer_reviewed_without_doi(register):
    entry = _an_arxiv_entry(register)
    entry["kind"] = "peer-reviewed"
    entry["identifiers"].pop("doi", None)


BREAKAGES = {
    "a claim that does not say what it does not establish": (_drop_limits, "'does_not_establish' is a required property"),
    "a claim with no conditions": (_empty_conditions, "/conditions)"),
    "evidence outside the vocabulary": (_unknown_evidence, "'press-release' is not one of"),
    "a number with no qualifiers": (_unqualified_number, "/qualifiers)"),
    "an unversioned arXiv identifier": (_unversioned_arxiv, "is not versioned"),
    "a source_url for a different paper": (_mismatched_source_url, "source_url points at '2401.00001v1'"),
    "a source read in the future": (_future_read_on, "is in the future"),
    "a date that does not exist": (_impossible_read_on, "is not a calendar date"),
    "a problem that does not exist": (_unknown_problem, "'99_perpetual_motion'"),
    "a zoo entry that does not exist": (_unknown_zoo_entry, "'Quantum Supremacy Engine'"),
    "two entries with one id": (_duplicate_id, "duplicate id"),
    "a peer-reviewed entry without a DOI": (_peer_reviewed_without_doi, "'doi' is a required property"),
}


@pytest.mark.parametrize("breakage", sorted(BREAKAGES))
def test_a_broken_register_is_reported(breakage):
    break_it, expected = BREAKAGES[breakage]
    register = copy.deepcopy(_load(REGISTER))
    break_it(register)
    found = _check(register)
    assert any(expected in violation for violation in found), (
        f"{breakage}: expected a violation containing {expected!r}, got {found}"
    )
