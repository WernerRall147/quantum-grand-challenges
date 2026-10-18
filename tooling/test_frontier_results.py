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

The algorithm zoo is held to the register too. Its Shor entry said "Needs ~4000
logical qubits for RSA-2048" with no source, a figure that matches neither published
estimate, and the evaluator serves the zoo (#297). So a resource count in the zoo must
cite, in the same sentence, a dated and versioned source that the register holds.
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

# A sentence in the zoo that mentions one of these and a digit states a resource count.
RESOURCE_WORDS = re.compile(r"\b(?:qubits?|toffolis?|t gates?|t-counts?|ccz)\b", re.IGNORECASE)
# The one citation form the zoo uses for a count: "(Gidney 2025, arXiv:2505.15917v1)".
DATED_CITATION = re.compile(r"\b(?P<year>(?:19|20)\d{2}), arXiv:(?P<arxiv>\d{4}\.\d{4,5}v\d+)")
# A full stop or semicolon followed by a capital ends a sentence; "et al. (" does not.
SENTENCE_BREAK = re.compile(r"(?<=[.;!?])\s+(?=[A-Z])")
ZOO_PROSE_FIELDS = ("notes", "quantum_complexity", "classical_best")


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


def unsourced_zoo_counts(zoo, register) -> list[str]:
    """Every zoo sentence that states a resource count without a dated source the register holds."""
    years = {
        entry["identifiers"]["arxiv"]: entry["citation"]["year"]
        for entry in register["entries"]
        if "arxiv" in entry["identifiers"]
    }
    found = []
    for algorithm in zoo["algorithms"]:
        for field in ZOO_PROSE_FIELDS:
            for sentence in SENTENCE_BREAK.split(str(algorithm.get(field, ""))):
                if not (RESOURCE_WORDS.search(sentence) and re.search(r"[0-9]", sentence)):
                    continue
                where = f"{algorithm['name']} ({field}): {sentence!r}"
                citations = list(DATED_CITATION.finditer(sentence))
                if not citations:
                    found.append(
                        f"{where} states a resource count without a dated citation "
                        "such as '(Gidney 2025, arXiv:2505.15917v1)'"
                    )
                for cite in citations:
                    year = years.get(cite["arxiv"])
                    if year is None:
                        found.append(f"{where} cites arXiv:{cite['arxiv']}, which has no entry in {REGISTER.name}")
                    elif int(cite["year"]) != year:
                        found.append(f"{where} dates arXiv:{cite['arxiv']} {cite['year']}, but the register says {year}")
    return found


def test_every_resource_count_in_the_zoo_cites_a_registered_source():
    assert unsourced_zoo_counts(_load(ZOO), _load(REGISTER)) == []


# Each zoo rule is shown to fire on a copy of the zoo with one entry's notes replaced. The
# first case is the Shor note as it was published until 2026-10-18.
ZOO_BREAKAGES = {
    "the published RSA-2048 count, with no source": (
        "The canonical example. Breaks RSA. Needs ~4000 logical qubits for RSA-2048.",
        "without a dated citation",
    ),
    "a source the register does not hold": (
        "About 1,400 logical qubits for RSA-2048 (Gidney 2025, arXiv:2505.99999v1).",
        "which has no entry",
    ),
    "a year that disagrees with the register": (
        "About 1,400 logical qubits for RSA-2048 (Gidney 2019, arXiv:2505.15917v1).",
        "but the register says 2025",
    ),
}


@pytest.mark.parametrize("breakage", sorted(ZOO_BREAKAGES))
def test_an_unsourced_zoo_count_is_reported(breakage):
    notes, expected = ZOO_BREAKAGES[breakage]
    zoo = copy.deepcopy(_load(ZOO))
    _first(zoo["algorithms"], lambda algorithm: algorithm["name"] == "Shor's Algorithm", "Shor entry")["notes"] = notes
    found = unsourced_zoo_counts(zoo, _load(REGISTER))
    assert any(expected in violation for violation in found), (
        f"{breakage}: expected a violation containing {expected!r}, got {found}"
    )
