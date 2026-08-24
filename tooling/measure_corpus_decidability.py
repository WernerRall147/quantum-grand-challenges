"""Measure how much of the papers corpus can carry a speedup claim at all, by origin.

The question this answers is not "is the classifier any good" - eval_paper_classifier.py
answers that. It is "is there anything in the corpus for a classifier to find", which
turns out to be the binding constraint.

Measured 2026-08-24 over all 2,239 documents:

    origin           total   STRONG     WEAK    INDET  decided%  avg len
    zoo                451       44       17      390     13.5%      966
    arxiv_sweep       1788       19       23     1746      2.3%     1386
    ALL               2239                                  4.6%

The curated Zoo references are roughly six times more decidable than the daily arXiv
sweep despite having shorter abstracts, so the gap is not length - it is population.
References cited by an algorithm state that algorithm's scaling; the daily sweep returns
application, NISQ and implementation papers that make no scaling claim at all.

That explains a result which otherwise looks like a broken classifier: over the five demo
prompts, retrieval returned 25 papers and the classifier decided on none of them. At 2.3%
decidability, seeing zero in twenty-five is the likeliest single outcome.

Run this after any change to ingestion. A sweep that adds volume without adding
decidability is diluting the corpus, and the ALL row will show it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from azure.core.credentials import AzureKeyCredential  # noqa: E402
from azure.identity import DefaultAzureCredential  # noqa: E402
from azure.search.documents import SearchClient  # noqa: E402

from agents.classifier.paper_classifier import (  # noqa: E402
    INDETERMINATE, STRONG, WEAK, classify_paper,
)
from knowledge.search.kb_client import SEARCH_ENDPOINT  # noqa: E402

ZOO_PATH = REPO_ROOT / "knowledge" / "data" / "zoo_references.json"
PAPERS_INDEX = "quantum-papers"

# The daily sweep is allowed to be less decidable than curated references - it is a
# firehose, not a reading list. But if it falls below this the sweep is pure dilution.
MIN_SWEEP_DECIDED_RATE = 0.01


def summarise(counts: Counter, lengths: Counter, origin: str) -> str:
    total = counts[(origin, "TOTAL")]
    if not total:
        return f"{origin:14s} {0:>7d}"
    strong = counts[(origin, STRONG)]
    weak = counts[(origin, WEAK)]
    indet = counts[(origin, INDETERMINATE)]
    rate = 100 * (strong + weak) / total
    return (f"{origin:14s} {total:>7d} {strong:>8d} {weak:>8d} {indet:>8d} "
            f"{rate:>8.1f}% {lengths[origin] // total:>8d}")


def sweep_is_pure_dilution(decided: int, total: int, floor: float) -> bool:
    """True when the daily sweep has stopped contributing anything readable.

    An empty sweep is not dilution - there is nothing to dilute with - so it passes.
    Guarding this separately keeps a fresh index or a failed ingest from reading as a
    corpus-quality regression.
    """
    if total <= 0:
        return False
    return (decided / total) < floor


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure corpus decidability by origin.")
    parser.add_argument("--min-sweep-rate", type=float, default=MIN_SWEEP_DECIDED_RATE,
                        help="fail if the arXiv sweep decides on less than this fraction")
    args = parser.parse_args()

    key = os.environ.get("SEARCH_ADMIN_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()
    client = SearchClient(SEARCH_ENDPOINT, PAPERS_INDEX, credential)

    zoo_ids = {r["arxiv_id"] for r in json.loads(ZOO_PATH.read_text(encoding="utf-8"))["references"]}

    counts: Counter = Counter()
    lengths: Counter = Counter()
    scanned = 0

    for doc in client.search(search_text="*", select=["arxiv_id", "title", "abstract"], top=100000):
        scanned += 1
        origin = "zoo" if doc.get("arxiv_id", "") in zoo_ids else "arxiv_sweep"
        abstract = doc.get("abstract") or ""
        lengths[origin] += len(abstract)
        result = classify_paper(doc.get("title", ""), abstract)
        counts[(origin, result.speedup_class)] += 1
        counts[(origin, "TOTAL")] += 1

    print(f"zoo reference ids: {len(zoo_ids)}")
    print(f"documents scanned: {scanned}")
    print()
    print(f"{'origin':14s} {'total':>7s} {'STRONG':>8s} {'WEAK':>8s} {'INDET':>8s} "
          f"{'decided%':>9s} {'avg len':>8s}")
    print("-" * 70)
    for origin in ("zoo", "arxiv_sweep"):
        print(summarise(counts, lengths, origin))

    total_all = sum(counts[(o, "TOTAL")] for o in ("zoo", "arxiv_sweep"))
    decided_all = sum(counts[(o, c)] for o in ("zoo", "arxiv_sweep") for c in (STRONG, WEAK))
    print("-" * 70)
    print(f"{'ALL':14s} {total_all:>7d} {'':>8s} {'':>8s} {'':>8s} "
          f"{100 * decided_all / total_all if total_all else 0:>8.1f}%")

    sweep_total = counts[("arxiv_sweep", "TOTAL")]
    sweep_decided = counts[("arxiv_sweep", STRONG)] + counts[("arxiv_sweep", WEAK)]
    sweep_rate = sweep_decided / sweep_total if sweep_total else 0.0
    print()
    print(f"sweep decided rate: {sweep_rate:.3f}   floor {args.min_sweep_rate:.3f}")
    if sweep_is_pure_dilution(sweep_decided, sweep_total, args.min_sweep_rate):
        print("FAIL: the daily sweep is adding volume without adding anything decidable.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
