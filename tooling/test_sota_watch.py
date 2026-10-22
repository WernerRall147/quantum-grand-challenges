"""The weekly state-of-the-art watch has to list what is new, drop what is known and fail loudly.

tooling/sota_watch.py turns arXiv results into one GitHub issue for a person to triage (#292).
Its failures would be quiet ones: a query that returns nothing reads as a quiet week, a known
paper listed again every week teaches people to skip the issue, and a run that fetched nothing
could still overwrite last week's list. Everything here is offline. The feeds in
tooling/fixtures/sota_watch/ are real arXiv responses recorded on 2026-10-18 (arXiv metadata is
CC0); each feed's <title> echoes the query and window it answered.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import urllib.error
from datetime import date, datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "sota_watch"

spec = importlib.util.spec_from_file_location("sota_watch", REPO / "tooling" / "sota_watch.py")
watch = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = watch  # a dataclass looks its module up while the class is built
spec.loader.exec_module(watch)

from knowledge.ingest import arxiv_ingester  # noqa: E402  sota_watch put the repository on sys.path

LLM_LIVE_WINDOW = FIXTURES / "llm-guided-discovery_2026-10-14_2026-10-17.xml"
LLM_OVERLAP = FIXTURES / "llm-guided-discovery_2026-10-12_2026-10-13.xml"
LEAN_OVERLAP = FIXTURES / "lean-formal-verification_2026-10-12_2026-10-13.xml"
EMPTY = FIXTURES / "femoco-iron-sulfur_2026-10-14_2026-10-17.xml"
ERROR = FIXTURES / "error_malformed-id.xml"
REGISTER = FIXTURES / "register.json"

NOW = datetime(2026, 10, 18, 12, 0, tzinfo=timezone.utc)
SINCE, UNTIL = date(2026, 10, 14), date(2026, 10, 17)


def topic(topic_id: str, title: str) -> dict:
    return {"id": topic_id, "title": title, "query": f"abs:{topic_id}fixture",
            "bears_on": [{"path": "tooling/sota_watch.py", "check": "a fixture topic"}]}


LLM, LEAN, FEMOCO = topic("llm", "LLM-guided discovery"), topic("lean", "Lean proofs"), topic("femoco", "FeMoco")


def fake_arxiv(answers: dict) -> callable:
    """A fetch that answers each topic from a recorded feed, or raises, and records each URL."""
    def fetch(url: str) -> str:
        fetch.calls.append(url)
        for topic_id, answer in answers.items():
            if f"abs:{topic_id}fixture" in url:
                if isinstance(answer, Exception):
                    raise answer
                return answer.read_text(encoding="utf-8")
        raise AssertionError(f"unexpected request {url}")
    fetch.calls = []
    return fetch


class Gh:
    """Stands in for subprocess.run when the script calls gh, and records every command."""

    def __init__(self, open_issues=()):
        self.open_issues = list(open_issues)
        self.calls = []

    def __call__(self, argv, input=None, **kwargs):
        self.calls.append((argv, input))
        stdout = ""
        if argv[:3] == ["gh", "issue", "list"]:
            stdout = json.dumps(self.open_issues)
        elif argv[:3] == ["gh", "issue", "create"]:
            stdout = "https://github.com/owner/repo/issues/99\n"
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    def commands(self):
        return [argv for argv, _ in self.calls]


def run_main(tmp_path, topics, answers, *flags, register=REGISTER, gh=None,
             window=("2026-10-14", "2026-10-17")):
    watchlist = tmp_path / "watchlist.json"
    watchlist.write_text(json.dumps({"topics": topics}), encoding="utf-8")
    fetch = fake_arxiv(answers)
    code = watch.main(["--since", window[0], "--until", window[1], "--watchlist", str(watchlist),
                       "--register", str(register), *flags],
                      fetch=fetch, sleep=lambda seconds: None, run=gh or Gh(), now=NOW)
    return code, fetch


def sections(body: str) -> dict[str, str]:
    """Topic title -> the text under its heading."""
    return dict(re.findall(r"^### \d+\. (.+?)\n(.*?)(?=^### |^---)", body, re.M | re.S))


def listed(section: str) -> list[str]:
    return re.findall(r"^- \[arXiv:([^\]]+)\]", section, re.M)


# --- reading arXiv -----------------------------------------------------------------------


def test_parses_a_recorded_arxiv_feed():
    papers, reported = watch.parse_feed(LLM_LIVE_WINDOW.read_text(encoding="utf-8"))
    assert reported == 1
    [paper] = papers
    assert paper["arxiv_id"] == "2610.22367v1"
    assert paper["title"] == "Discovering state-of-the-art quantum circuits with large language models"
    assert paper["published"].startswith("2026-10-15")
    assert paper["authors"][:2] == ["Andi Gu", "Alek H. Kemeny"]
    assert paper["categories"] == ["quant-ph", "cs.AI"]


def test_an_empty_week_parses_to_no_papers():
    assert watch.parse_feed(EMPTY.read_text(encoding="utf-8")) == ([], 0)


def test_an_arxiv_error_entry_is_a_failed_query_not_an_empty_week():
    """arXiv reports a bad request as a feed with one entry titled Error. Read as a paper it
    would crash the ingester's parser, which expects a published date; read as no papers it
    would look like a quiet week."""
    with pytest.raises(watch.ArxivError, match="incorrect id format"):
        watch.parse_feed(ERROR.read_text(encoding="utf-8"))


def test_each_request_is_bracketed_and_limited_to_the_window():
    """arXiv nests OR to the right (the recorded feeds' <link> shows how it parsed each query),
    so without the brackets the date clause would bind to the last OR term only and papers from
    any date would match the others. The ingester once computed a window and never sent it."""
    url = watch.search_url('abs:"magic state" OR abs:RSA', SINCE, UNTIL, start=50)
    assert url.startswith(arxiv_ingester.ARXIV_API + "?")
    search = url.split("search_query=", 1)[1].split("&", 1)[0]
    assert search == "%28abs:%22magic+state%22+OR+abs:RSA%29+AND+submittedDate:[202610140000+TO+202610172359]"
    assert "&start=50&" in url and url.endswith(f"&max_results={arxiv_ingester.ARXIV_PAGE_SIZE}")


def test_the_window_comes_from_since_and_until_with_a_default():
    args = watch.parse_args(["--since", "2026-10-14", "--until", "2026-10-17"], date(2026, 10, 18))
    assert (args.since, args.until) == (SINCE, UNTIL)
    default = watch.parse_args([], date(2026, 10, 18))
    assert default.until == date(2026, 10, 18)
    assert (default.until - default.since).days == watch.DEFAULT_LOOKBACK_DAYS
    for bad in (["--since", "14/10/2026"], ["--since", "2026-10-18", "--until", "2026-10-17"]):
        with pytest.raises(SystemExit) as stopped:
            watch.parse_args(bad, date(2026, 10, 18))
        assert stopped.value.code == 2


def test_uses_the_ingesters_fetch_and_parser_rather_than_copies():
    assert watch._open_arxiv_with_retry is arxiv_ingester._open_arxiv_with_retry
    assert watch._parse_entries is arxiv_ingester._parse_entries
    source = (REPO / "tooling" / "sota_watch.py").read_text(encoding="utf-8")
    assert not re.search(r"def _(open_arxiv|retry_delay|parse_entries)\b", source)


def test_requests_are_sequential_and_spaced_as_the_ingester_spaces_them(monkeypatch):
    """Two back-to-back requests earned a 429 (see arxiv_ingester.py). A full page is followed
    by the next page after the page delay; the next topic waits for the source delay."""
    monkeypatch.setattr(watch, "ARXIV_PAGE_SIZE", 2)  # the recorded Lean feed's two papers fill a page
    events, pages = [], iter([LEAN_OVERLAP, EMPTY])

    def fetch(url):
        events.append(("fetch", url.split("search_query=%28abs:", 1)[1].split("fixture", 1)[0],
                       re.search(r"start=(\d+)", url).group(1)))
        return (next(pages) if "leanfixture" in url else LLM_LIVE_WINDOW).read_text(encoding="utf-8")

    results = watch.collect([LEAN, LLM], SINCE, UNTIL, {}, fetch=fetch,
                            sleep=lambda s: events.append(("sleep", s)), log=lambda message: None)
    assert events == [
        ("fetch", "lean", "0"),
        ("sleep", arxiv_ingester.ARXIV_PAGE_DELAY),
        ("fetch", "lean", "2"),
        ("sleep", arxiv_ingester.ARXIV_SOURCE_DELAY),
        ("fetch", "llm", "0"),
    ]
    assert [len(r.new) for r in results] == [2, 1]


# --- what is new and what is known --------------------------------------------------------


def test_papers_in_the_register_are_marked_known_not_listed(tmp_path, capsys):
    """The register holds 2610.22367v1 as recorded, and 2610.17286 at a later version than the
    feed's; both are known. An entry with only a DOI cannot be matched and is skipped."""
    assert watch.load_known(REGISTER) == {"2610.22367": "gu-2026-llm-discovered-circuits",
                                          "2610.17286": "fixture-later-version"}
    code, _ = run_main(tmp_path, [LLM, LEAN], {"llm": LLM_LIVE_WINDOW, "lean": LEAN_OVERLAP}, "--dry-run")
    body = capsys.readouterr().out
    assert code == 0
    found = sections(body)
    assert listed(found["LLM-guided discovery"]) == []
    assert ("Already in the register: [arXiv:2610.22367](https://arxiv.org/abs/2610.22367v1) "
            "(`gu-2026-llm-discovered-circuits`).") in found["LLM-guided discovery"]
    assert listed(found["Lean proofs"]) == ["2610.17708"]
    assert "[arXiv:2610.17286](https://arxiv.org/abs/2610.17286v1) (`fixture-later-version`)" in found["Lean proofs"]
    assert "**1 new paper** from 2 of 2 topic queries answered; 2 papers dropped as already in the register." in body


def test_a_missing_register_is_an_empty_known_set_and_the_body_says_so(tmp_path, capsys):
    code, _ = run_main(tmp_path, [LLM], {"llm": LLM_LIVE_WINDOW}, "--dry-run", register=tmp_path / "absent.json")
    out = capsys.readouterr()
    assert code == 0
    assert listed(sections(out.out)["LLM-guided discovery"]) == ["2610.22367"]
    assert "was not found, so no paper was dropped as already known." in out.out
    assert "not found, so nothing is dropped as already known" in out.err


def test_an_unreadable_register_stops_the_run_before_any_request(tmp_path):
    broken = tmp_path / "register.json"
    broken.write_text("{not json", encoding="utf-8")
    code, fetch = run_main(tmp_path, [LLM], {"llm": LLM_LIVE_WINDOW}, "--dry-run", register=broken)
    assert code == 2
    assert fetch.calls == []


def test_candidates_are_grouped_under_the_topic_that_found_them(tmp_path, capsys):
    """The two recorded feeds for 12 to 13 October share QEDIA, arXiv:2610.17708."""
    code, _ = run_main(tmp_path, [LLM, LEAN, FEMOCO],
                       {"llm": LLM_OVERLAP, "lean": LEAN_OVERLAP, "femoco": EMPTY}, "--dry-run",
                       register=tmp_path / "absent.json", window=("2026-10-12", "2026-10-13"))
    body = capsys.readouterr().out
    assert code == 0
    found = sections(body)
    assert list(found) == ["LLM-guided discovery", "Lean proofs", "FeMoco"]
    assert listed(found["LLM-guided discovery"]) == ["2610.17708"]
    assert listed(found["Lean proofs"]) == ["2610.17708", "2610.17286"]
    assert "No new papers." in found["FeMoco"]
    assert "Also under: Lean proofs." in found["LLM-guided discovery"]
    assert "Also under: LLM-guided discovery." in found["Lean proofs"]
    assert "**2 new papers**" in body, "a paper under two topics is still one paper"


# --- failing loudly and writing the issue --------------------------------------------------


def test_every_query_failing_exits_non_zero_and_writes_nothing(tmp_path, capsys):
    """One topic cannot reach arXiv and the other gets an error entry: nothing was fetched, so
    the run fails and last week's issue is left as it was."""
    gh = Gh(open_issues=[{"number": 7, "title": "SOTA watch"}])
    code, fetch = run_main(tmp_path, [LLM, LEAN], {"llm": urllib.error.URLError("arXiv unreachable"),
                                                   "lean": ERROR}, gh=gh)
    out = capsys.readouterr()
    assert code == 1
    assert len(fetch.calls) == 2
    assert gh.calls == []
    assert out.out == ""
    assert "all 2 arXiv queries failed" in out.err


def test_one_failed_query_is_reported_in_the_issue_and_is_not_fatal(tmp_path, capsys):
    gh = Gh(open_issues=[{"number": 7, "title": "SOTA watch"}])
    code, _ = run_main(tmp_path, [LLM, LEAN], {"llm": LLM_LIVE_WINDOW, "lean": watch.ArxivError("boom")},
                       gh=gh, register=tmp_path / "absent.json")
    assert code == 0
    [body] = [stdin for argv, stdin in gh.calls if argv[:3] == ["gh", "issue", "edit"]]
    assert listed(sections(body)["LLM-guided discovery"]) == ["2610.22367"]
    assert "**Not checked this run:** the query failed (ArxivError: boom)." in sections(body)["Lean proofs"]
    assert "from 1 of 2 topic queries answered" in body
    assert "queries failed for lean" in capsys.readouterr().err


def test_dry_run_prints_the_body_and_writes_nothing(tmp_path, capsys):
    gh = Gh(open_issues=[{"number": 7, "title": "SOTA watch"}])
    code, fetch = run_main(tmp_path, [LLM], {"llm": LLM_LIVE_WINDOW}, "--dry-run", gh=gh)
    assert code == 0
    assert gh.calls == []
    assert capsys.readouterr().out.startswith("## SOTA watch: arXiv submissions from 2026-10-14 to 2026-10-17\n")
    assert "submittedDate:[202610140000+TO+202610172359]" in fetch.calls[0]


def test_updates_the_open_sota_watch_issue_rather_than_opening_another():
    gh = Gh(open_issues=[{"number": 12, "title": "SOTA watch (old)"}, {"number": 7, "title": "SOTA watch"}])
    assert watch.write_issue("BODY", "COMMENT", run=gh) == "updated #7"
    assert gh.calls == [
        (["gh", "issue", "list", "--state", "open", "--label", "reporting", "--limit", "200",
          "--json", "number,title"], None),
        (["gh", "issue", "edit", "7", "--body-file", "-"], "BODY"),
        (["gh", "issue", "comment", "7", "--body", "COMMENT"], None),
    ]


def test_opens_the_issue_with_its_label_when_none_is_open():
    gh = Gh(open_issues=[{"number": 12, "title": "SOTA watch (old)"}])
    assert watch.write_issue("BODY", "COMMENT", run=gh) == "created https://github.com/owner/repo/issues/99"
    assert gh.calls[-1] == (["gh", "issue", "create", "--title", "SOTA watch", "--label", "reporting",
                             "--body-file", "-"], "BODY")
    assert len(gh.calls) == 2


def test_a_busy_week_still_fits_in_one_issue():
    """GitHub rejects a body over 65,536 characters, and then nothing is written at all."""
    [paper], _ = watch.parse_feed(LLM_LIVE_WINDOW.read_text(encoding="utf-8"))
    many = [dict(paper, arxiv_id=f"2610.{n:05d}v1") for n in range(400)]
    body = watch.fit([watch.TopicResult(LLM, new=many)], SINCE, UNTIL, {}, register="r.json", written_at=NOW)
    assert len(body) <= watch.MAX_BODY_CHARS < 65_536
    assert re.search(r"^- And \d+ more, listed in the run log\.$", body, re.M)


def test_an_incomplete_list_says_so():
    """arXiv sometimes sends a short page, and paging stops there as the ingester's does, so the
    total arXiv reports is the only sign that papers are missing. The page cap is the other."""
    [paper], _ = watch.parse_feed(LLM_LIVE_WINDOW.read_text(encoding="utf-8"))
    short = watch.TopicResult(LLM, new=[paper], reported=3)
    capped = watch.TopicResult(LEAN, known=[(paper, "an-entry")], reported=1, truncated=True)
    complete = watch.TopicResult(FEMOCO, new=[paper], reported=1)
    found = sections(watch.render([short, capped, complete], SINCE, UNTIL, {}, register="r.json", written_at=NOW))
    assert "arXiv reported 3 results for this query but sent 1, so this list may be incomplete." in found["LLM-guided discovery"]
    assert f"Stopped at the {arxiv_ingester.ARXIV_MAX_PAGES}-page cap" in found["Lean proofs"]
    assert "incomplete" not in found["FeMoco"]


# --- the watchlist and the workflow ----------------------------------------------------------

WATCHLIST = json.loads((REPO / "knowledge" / "data" / "sota_watchlist.json").read_text(encoding="utf-8"))["topics"]


def test_watchlist_has_the_topics_issue_292_asks_for():
    ids = [t["id"] for t in WATCHLIST]
    assert len(ids) == len(set(ids))
    assert set(ids) >= {"magic-state-factories", "rsa-ecdlp-estimates", "decoded-quantum-interferometry",
                        "femoco-iron-sulfur", "lattice-gauge-estimates", "llm-guided-discovery",
                        "lean-formal-verification"}
    assert all(t["title"] and t["query"].strip() and t["bears_on"] for t in WATCHLIST)


def test_what_each_topic_bears_on_exists():
    """Paths and zoo names here are claims about the repository. A path marked planned must not
    exist yet: once it does, the mark comes off."""
    zoo = {a["name"] for a in json.loads((REPO / "knowledge" / "data" / "algorithm_zoo_index.json")
                                         .read_text(encoding="utf-8"))["algorithms"]}
    problems = []
    for t in WATCHLIST:
        for item in t["bears_on"]:
            where = f"{t['id']}: {item.get('zoo') or item.get('path')}"
            if not item.get("check") or ("zoo" in item) == ("path" in item):
                problems.append(f"{where} needs a check and exactly one of zoo or path")
            elif "zoo" in item:
                if item["zoo"] not in zoo:
                    problems.append(f"{where} is not a zoo entry")
            elif item.get("planned"):
                if (REPO / item["path"]).exists():
                    problems.append(f"{where} exists now; remove planned")
            elif not (REPO / item["path"]).exists():
                problems.append(f"{where} does not exist")
            elif re.fullmatch(r"[A-Za-z_]\w*", item.get("where", "")) and \
                    item["where"] not in (REPO / item["path"]).read_text(encoding="utf-8"):
                problems.append(f"{where} has no {item['where']}")
    assert not problems, problems


def test_workflow_runs_weekly_and_on_demand_with_least_privilege():
    """A scheduled run cannot be exercised offline, so this reads what #292 asks of its config."""
    text = (REPO / ".github" / "workflows" / "sota-watch.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    triggers = workflow.get("on", workflow.get(True))  # PyYAML reads a bare `on` as True
    [schedule] = triggers["schedule"]
    _, _, day_of_month, month, day_of_week = schedule["cron"].split()
    assert (day_of_month, month) == ("*", "*") and re.fullmatch(r"[0-6]", day_of_week)
    assert "workflow_dispatch" in triggers
    assert workflow["permissions"] == {"contents": "read", "issues": "write"}
    [job] = workflow["jobs"].values()
    assert "permissions" not in job
    assert [s["run"] for s in job["steps"] if "run" in s] == ["python tooling/sota_watch.py"]
    assert set(re.findall(r"secrets\.(\w+)", text)) == {"GITHUB_TOKEN"}
