"""The committed Quantinuum run must match what its README says about it.

This folder is evidence: the exact QIR submitted, the exact payload returned, and a
README whose numbers get quoted out loud. Nothing else in the repo checks that the
prose still matches the artifacts, so re-fetching a different job - or editing the
README by hand - could silently leave the two disagreeing.

The figures guarded here are the ones that would be said on camera: 80 of 100 shots
on the marked state, against a ~96% analytic ideal.
"""

import json
import math
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RUN = REPO / "problems" / "archived" / "15_database_search" / "azure_runs" / "2026-09-02-grover-h2-1e"

MARKED = "[0, 1, 1, 1]"


@pytest.fixture(scope="module")
def output() -> dict:
    return json.loads((RUN / "output.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def job() -> dict:
    return json.loads((RUN / "job.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def readme() -> str:
    return (RUN / "README.md").read_text(encoding="utf-8")


def test_artifacts_present():
    for name in ("README.md", "job.json", "output.json", "input.qir.ll"):
        assert (RUN / name).exists(), f"{name} missing from the run folder"


def test_job_actually_succeeded_on_the_emulator(job):
    """h2-1sc is a syntax checker and returns zeros; only h2-1e means anything here."""
    assert job["status"] == "Succeeded"
    assert job["target"] == "quantinuum.sim.h2-1e"
    assert job["inputParams"]["shots"] == 100


def test_histogram_accounts_for_every_shot(output):
    hist = output["Results"][0]["Histogram"]
    assert sum(row["Count"] for row in hist) == 100
    assert len(output["Results"][0]["Shots"]) == 100


def test_marked_state_dominates_at_the_documented_count(output, readme):
    """80 of 100 is the number said on camera."""
    hist = {row["Display"]: row["Count"] for row in output["Results"][0]["Histogram"]}
    assert hist[MARKED] == 80, f"marked state is {hist[MARKED]}/100, README says 80"
    assert max(hist.values()) == hist[MARKED], "the marked state is no longer the top outcome"
    assert "80 of 100" in readme or "80 shots out of 100" in readme


def test_noise_is_spread_not_a_competing_answer(output, readme):
    """The README's claim is 'twelve other outcomes at 1-3 shots each'."""
    hist = {row["Display"]: row["Count"] for row in output["Results"][0]["Histogram"]}
    others = {k: v for k, v in hist.items() if k != MARKED}
    assert len(others) == 12, f"README says twelve other outcomes, found {len(others)}"
    assert max(others.values()) <= 3, "an outcome above 3 shots is a competing answer, not noise"


def test_analytic_ideal_matches_the_readme():
    """96.1% is analytic, not a sampled run - that distinction is the point."""
    n, m, k = 16, 1, 3
    ideal = math.sin((2 * k + 1) * math.asin(math.sqrt(m / n))) ** 2
    assert f"{ideal:.1%}" == "96.1%"
    readme = (RUN / "README.md").read_text(encoding="utf-8")
    assert "96.1%" in readme

    # An allowlist, not a blocklist. A blocklist of phrasings looked like it worked and
    # missed "Roughly 97% down to 80%" entirely, because that sentence contains none of
    # the words it was hunting for. Instead: every occurrence of 97% must be one of the
    # two contexts the README legitimately needs, and anything else fails.
    allowed = (
        r"\d\d-97%",        # the sampled range, e.g. "92-97% across runs"
        r'said "97%"',      # quoting the old wrong figure to correct it
    )
    spans = [m.span() for m in re.finditer(r"97%", readme)]
    for start, end in spans:
        window = readme[max(0, start - 12):end + 2]
        if not any(re.search(p, window) for p in allowed):
            line = readme.count("\n", 0, start) + 1
            raise AssertionError(
                f"line {line}: 97% appears outside the two allowed contexts "
                f"(...{readme[max(0, start - 40):end + 10]!r}...). It was one lucky "
                "200-shot sample; the analytic ideal is 96.1%."
            )


def test_iteration_table_is_correct():
    """The README claims running Grover longer makes it worse. Check the numbers."""
    n, m = 16, 1
    expected = {1: "47.3%", 2: "90.8%", 3: "96.1%", 4: "58.2%", 5: "12.5%"}
    readme = (RUN / "README.md").read_text(encoding="utf-8")
    for k, text in expected.items():
        p = math.sin((2 * k + 1) * math.asin(math.sqrt(m / n))) ** 2
        assert f"{p:.1%}" == text, f"k={k} is {p:.1%}, README table says {text}"
        assert text in readme, f"k={k} value {text} missing from the README table"
    assert expected[4] != expected[3], "the 'longer is worse' claim needs k=4 below k=3"


def test_cited_resource_estimate_matches_the_committed_estimate(readme):
    estimate = json.loads(
        (REPO / "problems" / "archived" / "15_database_search" / "circuits" / "estimate.json")
        .read_text(encoding="utf-8")
    )

    def find(obj, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    return v
                found = find(v, key)
                if found is not None:
                    return found
        return None

    assert f"{find(estimate, 'physicalQubits'):,}" in readme
    assert str(find(estimate, "logicalQubits")) in readme


def test_no_sas_credential_was_committed():
    """The URIs are kept for provenance; the signature must not be."""
    for path in RUN.iterdir():
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert "sig=" not in text, f"{path.name} contains a SAS signature"
            assert "skoid=" not in text, f"{path.name} contains a SAS key id"


def test_input_is_real_qir_for_the_right_entry_point():
    qir = (RUN / "input.qir.ll").read_text(encoding="utf-8")
    assert "%Qubit = type opaque" in qir, "this does not look like QIR"
    assert len(qir) > 5000, "QIR is suspiciously small"
    assert re.search(r"ENTRYPOINT__main|GroverSearchKernel", qir), "no recognisable entry point"


def test_readme_warns_about_the_syntax_checker_artifacts(readme):
    """The folder still contains h2-1sc zeros that look like Grover results."""
    old = json.loads(
        (REPO / "problems" / "archived" / "15_database_search" / "estimates"
         / "azure_result_grover_4q.json").read_text(encoding="utf-8")
    )
    assert set(old["c"]) == {"0000"}, "the old artifact changed; re-check the README warning"
    assert "h2-1sc" in readme and "syntax checker" in readme, (
        "the README must keep warning that those zeros are not a Grover result"
    )
