"""The demo surface must not state a number the estimate artifacts do not support.

Three false claims were on the pages a judge reads, all of the same shape: a value
rendered with the confidence of a measurement that was never taken.

- Seven problem descriptions quoted "132k physical qubits, 18 logical" against real
  figures of 54k/12, 58k/12 and 163k/12. The phrase predated #176 replacing VQE with
  QPE, and nothing regenerated it, because prose is not generated.
- The comparison table coerced a null T-gate count to 0 with `est.tCount || 0`, so 16
  of 20 problems advertised "0 T-Gates". None of them has a genuine zero.
- Every row of that table rendered a hardcoded "Stage C" badge while the computed
  status sat unused, on a project whose central claim is that 11 of 20 were honestly
  downgraded.

The first is checkable against data and is checked here. The second and third are
rendering defects; CI does not build the site, so they are guarded at source with the
narrow, literal assertions below rather than left unguarded. Both were also verified
in a browser against the built page: stages render as 11 Archived, 5 Stage B and
4 Stage C, and unreported counts render as an em dash.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ESTIMATES = REPO_ROOT / "website" / "data" / "resourceEstimates.json"
PROJECT_STATUS = REPO_ROOT / "website" / "data" / "projectStatus.ts"
COMPARE_PAGE = REPO_ROOT / "website" / "pages" / "compare.tsx"

# "132k physical qubits, 18 logical"
_QUBIT_CLAIM = re.compile(r"([\d.]+)k physical qubits,\s*(\d+) logical")
# Single- or double-quoted descriptions, on the key's line or the next. Matching only the
# single-quoted form let the Factorization card quote 77k qubits against an estimate of 53k.
_ENTRY = re.compile(
    r"\{\s*title: '([^']*)',\s*status: '([^']*)',\s*description:\s*(?:'([^']*)'|\"([^\"]*)\"),\s*href: '([^']*)'"
)
_PROBLEM_ID = re.compile(r"problems/(\d\d_[a-z_]+)")


def _estimates() -> dict:
    return json.loads(ESTIMATES.read_text(encoding="utf-8"))


def _claims() -> list[tuple[str, float, int]]:
    """Every (problem id, claimed physical, claimed logical) stated in a description."""
    found = []
    for _title, _status, single, double, href in _ENTRY.findall(
        PROJECT_STATUS.read_text(encoding="utf-8")
    ):
        description = single or double
        problem = _PROBLEM_ID.search(href)
        claim = _QUBIT_CLAIM.search(description)
        if problem and claim:
            found.append((problem.group(1), float(claim.group(1)) * 1000, int(claim.group(2))))
    return found


CLAIMS = _claims()


def test_there_are_descriptions_to_check():
    """Guard the guard: a regex that stopped matching would pass forever."""
    assert len(CLAIMS) >= 7, (
        f"expected at least 7 descriptions stating qubit counts, found {len(CLAIMS)}. "
        f"If the wording changed, update _QUBIT_CLAIM rather than deleting the check."
    )


@pytest.mark.parametrize("problem,claimed_physical,claimed_logical", CLAIMS, ids=[c[0] for c in CLAIMS])
def test_description_matches_the_estimate(problem, claimed_physical, claimed_logical):
    """A figure in prose is a claim, and goes stale silently."""
    estimate = _estimates().get(problem)
    assert estimate, f"{problem}: described on the site but absent from resourceEstimates.json"

    actual_physical = estimate.get("physicalQubits")
    actual_logical = estimate.get("logicalQubits")
    assert actual_physical and actual_logical, f"{problem}: estimate has no qubit counts"

    # The prose rounds to whole thousands, so compare within that rounding.
    drift = abs(claimed_physical - actual_physical) / actual_physical
    assert drift < 0.05, (
        f"{problem}: description says {claimed_physical/1000:.0f}k physical qubits, "
        f"the estimate says {actual_physical:,}. Regenerate the estimate or correct the prose."
    )
    assert claimed_logical == actual_logical, (
        f"{problem}: description says {claimed_logical} logical qubits, "
        f"the estimate says {actual_logical}."
    )


def test_unreported_counts_are_null_not_zero():
    """The data contract the comparison table depends on.

    `estimate_summary` leaves tCount and rotationCount as None when the trace does not
    report them. If a generator ever writes 0 instead, the site would state a measured
    zero and this check would be the only thing that noticed.
    """
    estimates = _estimates()
    assert estimates, "resourceEstimates.json is empty"

    zeros = [
        problem
        for problem, estimate in estimates.items()
        if estimate.get("tCount") == 0 or estimate.get("rotationCount") == 0
    ]
    assert not zeros, (
        "these problems report a gate count of exactly 0: "
        + ", ".join(sorted(zeros))
        + ". A circuit with no T gates and no rotations is implausible here; the more "
        "likely cause is a null coerced to zero somewhere in the generator."
    )


def test_comparison_table_does_not_hardcode_a_stage():
    """Narrow source check, because CI does not build the site.

    Asserts the specific regression rather than a style: the badge must come from the
    row's status, not from a literal. Behaviour was verified separately against the
    built page.
    """
    source = COMPARE_PAGE.read_text(encoding="utf-8")
    literal_badge = re.search(r">\s*Stage [A-D]\s*<", source)
    assert not literal_badge, (
        f"compare.tsx renders a hardcoded {literal_badge.group(0).strip()} badge. "
        f"Every row showed 'Stage C' this way, including the 11 archived problems. "
        f"Derive the badge from the row's recorded status."
    )


def test_comparison_table_does_not_coerce_missing_counts_to_zero():
    """The `|| 0` that turned "not reported" into "measured zero" for 16 problems."""
    source = COMPARE_PAGE.read_text(encoding="utf-8")
    offenders = re.findall(r"(tCount|rotationCount)\s*:\s*est\.\w+\s*\|\|\s*0", source)
    assert not offenders, (
        f"compare.tsx coerces {', '.join(sorted(set(offenders)))} to 0 with `|| 0`. "
        f"Use `?? null` so an unreported count renders as absent rather than as a "
        f"measurement of zero."
    )
