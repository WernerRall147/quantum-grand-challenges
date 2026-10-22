#!/usr/bin/env python3
"""List new arXiv papers on the topics this repository's numbers depend on, for a person to triage.

Numbers here go stale without anything failing, and the daily ingester feeds retrieval, not
review (#292). For each topic in knowledge/data/sota_watchlist.json this asks arXiv for papers
submitted in a window, drops those already in the frontier-results register
(knowledge/data/frontier_results.json), and writes the rest, grouped by topic, into the one open
issue titled "SOTA watch" and labelled "reporting", creating it when there is none. It never
edits a number, the register, the zoo or any document.

    python tooling/sota_watch.py --dry-run
    python tooling/sota_watch.py --since 2026-10-14 --until 2026-10-17 --dry-run
    python tooling/sota_watch.py      # writes the issue with gh, as sota-watch.yml does

Fetching, retries and rate limits come from knowledge/ingest/arxiv_ingester.py, whose comments
record why its delays are what they are. Requests are made one at a time.

Exit codes: 0 when at least one query was answered; 1 when every query failed, because a run
that fetched nothing has failed (AGENTS.md rule 1), or when the issue could not be written;
2 for bad arguments or a watchlist or register that cannot be read.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from knowledge.ingest.arxiv_ingester import (  # noqa: E402
    ARXIV_API,
    ARXIV_MAX_PAGES,
    ARXIV_PAGE_DELAY,
    ARXIV_PAGE_SIZE,
    ARXIV_SOURCE_DELAY,
    _open_arxiv_with_retry,
    _parse_entries,
)

WATCHLIST = REPO_ROOT / "knowledge" / "data" / "sota_watchlist.json"
REGISTER = REPO_ROOT / "knowledge" / "data" / "frontier_results.json"
ZOO = "knowledge/data/algorithm_zoo_index.json"

ISSUE_TITLE = "SOTA watch"
ISSUE_LABEL = "reporting"

# arXiv's schedule announces a submission up to about three days after it arrives (Friday 14:00
# to Monday 20:00, US Eastern), and moderation or a holiday can add days
# (https://info.arxiv.org/help/availability.html). Reaching back ten days overlaps the previous
# weekly window by three, which absorbs the scheduled lag: a paper can be listed two weeks
# running, and one held back longer than the overlap can still fall between runs.
DEFAULT_LOOKBACK_DAYS = 10

# GitHub rejects an issue body over 65,536 characters, and then nothing is written at all.
MAX_BODY_CHARS = 60_000

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}

_VERSION = re.compile(r"v\d+$")


class ArxivError(RuntimeError):
    """arXiv answered with an error entry instead of results."""


@dataclass
class TopicResult:
    topic: dict
    new: list = field(default_factory=list)
    known: list = field(default_factory=list)  # (paper, register entry id)
    error: str | None = None
    reported: int | None = None  # totalResults as arXiv reported it
    truncated: bool = False


def base_id(arxiv_id: str) -> str:
    """2610.22367v1 -> 2610.22367, so a new version of a known paper is still known."""
    text = arxiv_id.strip()
    if text.lower().startswith("arxiv:"):
        text = text[len("arxiv:"):]
    return _VERSION.sub("", text)


def _shown(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def load_watchlist(path: Path) -> list[dict]:
    topics = json.loads(path.read_text(encoding="utf-8"))["topics"]
    if not topics:
        raise ValueError(f"{_shown(path)} lists no topics")
    for topic in topics:
        missing = {"id", "title", "query", "bears_on"} - set(topic)
        if missing:
            raise ValueError(f"topic {topic.get('id', '?')} has no {', '.join(sorted(missing))}")
    return topics


def load_known(path: Path) -> dict[str, str] | None:
    """arXiv id without its version -> register entry id; None when there is no register.

    A register that exists but cannot be read raises: treating it as empty would hide the fault.
    """
    if not path.is_file():
        return None
    known = {}
    for entry in json.loads(path.read_text(encoding="utf-8"))["entries"]:
        arxiv_id = (entry.get("identifiers") or {}).get("arxiv")
        if arxiv_id:
            known[base_id(arxiv_id)] = entry.get("id", "?")
    return known


def search_url(query: str, since: date, until: date, start: int = 0) -> str:
    """One page of `query`, restricted to papers submitted from `since` to `until`.

    Both days are inclusive and in UTC, which is how arXiv stores submittedDate. The query is
    bracketed so that an OR inside it cannot capture the date clause.
    """
    window = f"[{since:%Y%m%d}0000+TO+{until:%Y%m%d}2359]"
    search = f"%28{urllib.parse.quote_plus(query, safe=':')}%29+AND+submittedDate:{window}"
    return (f"{ARXIV_API}?search_query={search}&sortBy=submittedDate&sortOrder=descending"
            f"&start={start}&max_results={ARXIV_PAGE_SIZE}")


def fetch_atom(url: str) -> str:
    """One arXiv response, with the ingester's retry and backoff."""
    request = urllib.request.Request(url, headers={"User-Agent": "QuantumGrandChallenges/2.0 sota-watch"})
    with _open_arxiv_with_retry(request, timeout=60) as response:
        return response.read().decode("utf-8")


def parse_feed(xml_text: str) -> tuple[list[dict], int | None]:
    """Papers in one Atom response, and the total arXiv reports for the query."""
    root = ET.fromstring(xml_text)
    for entry in root.findall("atom:entry", NS):
        if "/api/errors" in (entry.findtext("atom:id", "", NS) or ""):
            raise ArxivError((entry.findtext("atom:summary", "", NS) or "").strip() or "error entry")
    total = (root.findtext("opensearch:totalResults", "", NS) or "").strip()
    return _parse_entries(root, NS), int(total) if total.isdigit() else None


def fetch_topic(query: str, since: date, until: date, *, fetch=fetch_atom,
                sleep=time.sleep) -> tuple[list[dict], int | None, bool]:
    """Every paper matching `query` in the window: (papers, total reported, truncated)."""
    papers: list[dict] = []
    reported = None
    for page in range(ARXIV_MAX_PAGES):
        if page:
            sleep(ARXIV_PAGE_DELAY)
        batch, reported = parse_feed(fetch(search_url(query, since, until, page * ARXIV_PAGE_SIZE)))
        papers.extend(batch)
        if len(batch) < ARXIV_PAGE_SIZE:
            return papers, reported, False
    return papers, reported, True


def collect(topics: list[dict], since: date, until: date, known: dict[str, str], *,
            fetch=fetch_atom, sleep=time.sleep, log=print) -> list[TopicResult]:
    results = []
    for index, topic in enumerate(topics):
        # The ingester's spacing between sources: back-to-back queries earned 429s.
        if index:
            sleep(ARXIV_SOURCE_DELAY)
        result = TopicResult(topic)
        try:
            papers, result.reported, result.truncated = fetch_topic(
                topic["query"], since, until, fetch=fetch, sleep=sleep)
        except Exception as exc:  # one failed topic must not lose the others
            result.error = f"{type(exc).__name__}: {exc}"
            log(f"  {topic['id']}: FAILED, {result.error}")
            results.append(result)
            continue
        for paper in papers:
            entry = known.get(base_id(paper["arxiv_id"]))
            if entry:
                result.known.append((paper, entry))
            else:
                result.new.append(paper)
        log(f"  {topic['id']}: {len(papers)} fetched (arXiv reports {result.reported}), "
            f"{len(result.new)} new, {len(result.known)} already in the register")
        results.append(result)
    return results


def _count(n: int, noun: str) -> str:
    return f"{n} {noun}{'' if n == 1 else 's'}"


def _plain(text: str) -> str:
    """One line that cannot open an HTML tag in the issue."""
    return " ".join(str(text).split()).replace("<", "&lt;").replace(">", "&gt;")


def _authors(names: list[str]) -> str:
    return ", ".join(names) if len(names) <= 4 else ", ".join(names[:3]) + " et al."


def _bears_on(item: dict) -> str:
    if "zoo" in item:
        target = f'zoo entry "{item["zoo"]}" (`{ZOO}`)'
    else:
        target = f"`{item['path']}`"
        if item.get("where"):
            target += f", {item['where']}"
        if item.get("planned") and not (REPO_ROOT / item["path"]).exists():
            target += f" (planned in {item['planned']}; not in the repository yet)"
    return f"- {target}: {item['check']}"


def _sentence(text: str) -> str:
    text = _plain(text)
    return text if text.endswith((".", "?", "!")) else text + "."


def _paper(paper: dict, also: list[str]) -> str:
    line = (f"- [arXiv:{base_id(paper['arxiv_id'])}](https://arxiv.org/abs/{paper['arxiv_id']}) "
            f"{_sentence(paper['title'])} {_sentence(_authors(paper['authors']))} "
            f"Submitted {paper['published'][:10]}; {', '.join(paper['categories'])}.")
    if also:
        line += f" Also under: {'; '.join(also)}."
    return line


def render(results: list[TopicResult], since: date, until: date, known: dict | None, *,
           register: str, written_at: datetime, run_url: str | None = None,
           cap: int | None = None) -> str:
    """The issue body. `cap` limits the papers shown per topic, to fit GitHub's size limit."""
    topics_of = defaultdict(list)  # base id -> titles of the topics that list it as new
    for result in results:
        for paper in result.new:
            topics_of[base_id(paper["arxiv_id"])].append(result.topic["title"])
    answered = sum(1 for r in results if r.error is None)
    dropped = sum(len(r.known) for r in results)

    lines = [
        f"## SOTA watch: arXiv submissions from {since} to {until}",
        "",
        "Papers that may change a number or claim in this repository, for a person to triage. "
        f"Read each one, then either add it to the frontier-results register (`{register}`) and "
        "open an issue for the claim it bears on, or leave it. Being listed here is not evidence "
        "of anything, and this watch never edits a number.",
        "",
        f"**{_count(len(topics_of), 'new paper')}** from {answered} of {len(results)} topic "
        f"queries answered; {_count(dropped, 'paper')} dropped as already in the register.",
    ]
    if known is None:
        lines += ["", f"The register `{register}` was not found, so no paper was dropped as already known."]
    for number, result in enumerate(results, 1):
        lines += ["", f"### {number}. {result.topic['title']}", "", "Re-check:"]
        lines += [_bears_on(item) for item in result.topic["bears_on"]]
        lines += ["", f"Query: `{result.topic['query']}`", ""]
        if result.error:
            lines.append(f"**Not checked this run:** the query failed ({_plain(result.error)}).")
            continue
        shown = result.new if cap is None else result.new[:cap]
        if not result.new:
            lines.append("No new papers.")
        for paper in shown:
            others = [t for t in topics_of[base_id(paper["arxiv_id"])] if t != result.topic["title"]]
            lines.append(_paper(paper, others))
        if len(shown) < len(result.new):
            lines.append(f"- And {len(result.new) - len(shown)} more, listed in the run log.")
        fetched = len(result.new) + len(result.known)
        if result.truncated:
            lines.append(f"Stopped at the {ARXIV_MAX_PAGES}-page cap, so this list is incomplete: "
                         "narrow the query.")
        elif result.reported is not None and fetched < result.reported:
            lines.append(f"arXiv reported {result.reported} results for this query but sent {fetched}, "
                         "so this list may be incomplete.")
        if result.known:
            lines += ["", "Already in the register: " + ", ".join(
                f"[arXiv:{base_id(p['arxiv_id'])}](https://arxiv.org/abs/{p['arxiv_id']}) (`{entry}`)"
                for p, entry in result.known) + "."]
    run = f" ([run]({run_url}))" if run_url else ""
    lines += ["", "---", f"Written by `tooling/sota_watch.py` at {written_at:%Y-%m-%d %H:%M} UTC{run}. "
              "Each run replaces this body. Topics and what they bear on: "
              "`knowledge/data/sota_watchlist.json`."]
    return "\n".join(lines) + "\n"


def fit(results: list[TopicResult], *args, **kwargs) -> str:
    """The body with as many papers as GitHub accepts; the run log keeps the full list."""
    for cap in (None, 30, 10, 3, 0):
        body = render(results, *args, cap=cap, **kwargs)
        if len(body) <= MAX_BODY_CHARS:
            break
    return body


def write_issue(body: str, comment: str, *, run=subprocess.run) -> str:
    """Replace the body of the open "SOTA watch" issue, or open one when there is none."""
    def gh(*args: str, stdin: str | None = None) -> str:
        return run(["gh", *args], input=stdin, capture_output=True, text=True,
                   encoding="utf-8", check=True).stdout

    listed = json.loads(gh("issue", "list", "--state", "open", "--label", ISSUE_LABEL,
                           "--limit", "200", "--json", "number,title") or "[]")
    numbers = sorted(issue["number"] for issue in listed if issue.get("title") == ISSUE_TITLE)
    if not numbers:
        return "created " + gh("issue", "create", "--title", ISSUE_TITLE, "--label", ISSUE_LABEL,
                               "--body-file", "-", stdin=body).strip()
    gh("issue", "edit", str(numbers[0]), "--body-file", "-", stdin=body)
    # Editing a body notifies nobody, so a short comment tells subscribers the list changed.
    gh("issue", "comment", str(numbers[0]), "--body", comment)
    extra = f"; also open with the same title: {numbers[1:]}" if len(numbers) > 1 else ""
    return f"updated #{numbers[0]}{extra}"


def _day(text: str) -> date:
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a date in YYYY-MM-DD form") from None


def parse_args(argv: list[str] | None, today: date) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", type=_day, help="first submission day, inclusive, UTC "
                        f"(default: --until minus {DEFAULT_LOOKBACK_DAYS} days)")
    parser.add_argument("--until", type=_day, help="last submission day, inclusive, UTC (default: today)")
    parser.add_argument("--dry-run", action="store_true", help="print the issue body instead of writing it")
    parser.add_argument("--watchlist", type=Path, default=WATCHLIST, help="topics to query")
    parser.add_argument("--register", type=Path, default=REGISTER, help="frontier-results register")
    args = parser.parse_args(argv)
    args.until = args.until or today
    args.since = args.since or args.until - timedelta(days=DEFAULT_LOOKBACK_DAYS)
    if args.since > args.until:
        parser.error(f"--since {args.since} is after --until {args.until}")
    return args


def main(argv: list[str] | None = None, *, fetch=fetch_atom, sleep=time.sleep,
         run=subprocess.run, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    args = parse_args(argv, now.date())

    def log(message: str) -> None:
        print(message, file=sys.stderr, flush=True)

    try:
        topics = load_watchlist(args.watchlist)
        known = load_known(args.register)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        log(f"error: cannot read the watchlist or the register: {type(exc).__name__}: {exc}")
        return 2
    register = _shown(args.register)
    log(f"SOTA watch: {_count(len(topics), 'topic')}, arXiv submissions from {args.since} to {args.until}")
    log(f"  register {register}: " + ("not found, so nothing is dropped as already known"
                                      if known is None else f"{_count(len(known), 'arXiv id')} known"))

    results = collect(topics, args.since, args.until, known or {}, fetch=fetch, sleep=sleep, log=log)
    failed = [r.topic["id"] for r in results if r.error]
    if len(failed) == len(results):
        log(f"FAIL: all {len(results)} arXiv queries failed, so nothing was fetched and nothing was written.")
        return 1

    server, repo, run_id = (os.environ.get(k) for k in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"))
    run_url = f"{server}/{repo}/actions/runs/{run_id}" if server and repo and run_id else None
    context = dict(register=register, written_at=now, run_url=run_url)
    print(render(results, args.since, args.until, known, **context))
    if failed:
        log(f"WARNING: queries failed for {', '.join(failed)}; the body says these topics were not checked.")
    if args.dry_run:
        return 0

    new = {base_id(p["arxiv_id"]) for r in results for p in r.new}
    comment = (f"Updated for arXiv submissions from {args.since} to {args.until}: "
               f"{_count(len(new), 'new paper')}, {len(results) - len(failed)} of {len(results)} "
               "topic queries answered." + (f" [Run]({run_url})" if run_url else ""))
    try:
        outcome = write_issue(fit(results, args.since, args.until, known, **context), comment, run=run)
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        log(f"FAIL: could not write the issue: {getattr(exc, 'stderr', None) or exc}")
        return 1
    log(f"SOTA watch issue {outcome}")
    return 0


if __name__ == "__main__":
    # arXiv titles carry symbols a Windows console code page cannot print.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
