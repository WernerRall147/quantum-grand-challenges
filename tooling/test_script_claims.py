"""The recording script's headline numbers must match the code they describe.

"Searching sixteen items is four comparisons" sat in the script for weeks and was
said three times. Four is log2(16) - binary search on a *sorted* list - while the
whole episode is about unsorted search. The repo's own Main.qs uses
`searchSpace / 2` ("average for 1 target"), so the honest figure is eight.

Nothing parsed script.md, so only a human reading it could have caught that. These
tests check the two numbers that carry the episode against their actual sources:
the classical comparison count against Main.qs, and the resource estimate against
the committed estimate.json.

Prose is not asserted, only the figures - the script is rewritten often and a test
that pins wording would be deleted the first time it got in the way.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "docs" / "AzureFriday" / "script.md"
PROBLEM = REPO / "problems" / "archived" / "15_database_search"

WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "twelve": 12, "sixteen": 16,
}


@pytest.fixture(scope="module")
def script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_classical_convention_is_still_half_the_search_space():
    """If Main.qs changes its convention, the script's number must be revisited."""
    main = (PROBLEM / "qsharp" / "src" / "Main.qs").read_text(encoding="utf-8")
    assert re.search(r"classicalQueries1\s*=\s*searchSpace1\s*/\s*2", main), (
        "Main.qs no longer computes the classical baseline as searchSpace/2; "
        "the script's 'eight comparisons' claim depends on that convention"
    )


def test_script_says_eight_comparisons_not_four(script):
    """N=16 unsorted, one target: average is N/2 = 8. Four is log2(16), a sorted-list answer.

    Allowlisted, not blocklisted. The script deliberately *quotes* the wrong number in
    its "Do not say" list, so hunting for the string fails on the correction itself -
    the same trap that made the first version of this test red on a clean tree.
    """
    do_not_say_at = script.find("## Do not say")
    assert do_not_say_at != -1, "the Do not say section moved; re-check this test"

    for match in re.finditer(r"(\w+) comparisons", script):
        word = match.group(1).lower()
        if word not in WORDS:
            continue
        if match.start() > do_not_say_at:
            continue  # the warning is allowed to name the wrong number
        line = script.count("\n", 0, match.start()) + 1
        assert WORDS[word] in (8, 16), (
            f"line {line}: script says {word!r} comparisons. Unsorted search of sixteen "
            f"items is eight on average and sixteen worst case; four is log2(16), which "
            f"is binary search on a sorted list."
        )


def test_do_not_say_list_still_carries_the_correction(script):
    """The guard in the document itself, not just in this test."""
    assert "## Do not say" in script
    tail = script.split("## Do not say", 1)[1]
    assert "four comparisons" in tail, (
        "the do-not-say entry for 'four comparisons' was removed; it is the only "
        "warning a presenter reading the script would actually see"
    )


def test_resource_estimate_numbers_match_the_committed_estimate(script):
    """Every physical-qubit figure quoted must be the committed one.

    Checking "is 61,122 present somewhere" passes even after a figure is changed,
    because the script quotes it in three places - presence is shape, not correctness.
    This asserts on every occurrence instead.
    """
    estimate = json.loads((PROBLEM / "circuits" / "estimate.json").read_text(encoding="utf-8"))

    def find(obj, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    return v
                found = find(v, key)
                if found is not None:
                    return found
        return None

    physical = find(estimate, "physicalQubits")
    logical = find(estimate, "logicalQubits")

    quoted = re.findall(r"([\d,]+) physical qubits", script)
    assert quoted, "the script no longer quotes a physical-qubit figure at all"
    for figure in quoted:
        assert int(figure.replace(",", "")) == physical, (
            f"script quotes {figure} physical qubits; estimate.json says {physical:,}"
        )
    assert f"{physical:,}" in script
    assert str(logical) in script, f"script no longer quotes {logical} logical qubits"


def test_no_todo_markers_left_in_the_recording_script(script):
    """A TODO in the document being read live is a hole in the recording."""
    leftover = [
        f"line {script.count(chr(10), 0, m.start()) + 1}"
        for m in re.finditer(r"\bTODO\b|\bTBD\b|\bFIXME\b", script)
    ]
    assert not leftover, f"unanswered markers in script.md at {', '.join(leftover)}"


def test_no_truncated_markdown_links(script):
    """Two link truncations survived an edit pass; this catches the next one."""
    for i, line in enumerate(script.splitlines(), start=1):
        assert not re.search(r"\]\([^)]*$", line), (
            f"line {i} has an unclosed markdown link: {line.strip()!r}"
        )


def test_handoff_count_claim_matches_the_marks(script):
    """The script tells you how many hand-offs to expect; it was wrong by one."""
    claim = re.search(r"There are \*\*(\w+)\*\* of them inside the demo", script)
    assert claim, "the hand-off count sentence changed shape; re-check it by hand"
    claimed = WORDS[claim.group(1).lower()]

    lines = script.splitlines()
    def line_of(pattern):
        return next(i for i, l in enumerate(lines, 1) if re.match(pattern, l))

    start, end = line_of(r"^## Beat 1"), line_of(r"^## Wrap")
    actual = sum(
        1 for i, l in enumerate(lines, 1)
        if start < i < end and l.startswith("**>> Hand off")
    )
    assert claimed == actual, f"script claims {claimed} hand-offs in the demo, found {actual}"
