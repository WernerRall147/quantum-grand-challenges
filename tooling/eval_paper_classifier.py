"""Measure the paper classifier against the Zoo-labelled set.

Labels come from knowledge/data/zoo_references.json: each reference carries the speedup
class of the algorithm citing it, which makes 358 papers usable as a two-class set
without anyone hand-labelling them.

Accuracy is reported but is not the number to read. The set is 239 STRONG against 119
WEAK, so answering STRONG every time scores 67% while being wrong about every paper whose
speedup does not survive error correction. The figure that decides whether this may ever
inform a verdict is the over-claim rate: WEAK papers called STRONG.

    python tooling/eval_paper_classifier.py

Needs abstracts, so it reads them from the search index. Exits non-zero if the over-claim
rate exceeds the threshold.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from agents.classifier.paper_classifier import (  # noqa: E402
    INDETERMINATE, STRONG, WEAK, classify_paper,
)

ZOO_PATH = REPO / "knowledge" / "data" / "zoo_references.json"
SEARCH_ENDPOINT = "https://qgcsearcheval.search.windows.net"

STRONG_SPEEDUPS = {"superpolynomial", "exponential"}
WEAK_SPEEDUPS = {"polynomial", "constant factor"}

# An over-claim is a paper whose speedup does not survive error correction being read as
# one that does. Zero is the only defensible target if this ever informs a verdict; the
# threshold exists so the number is visible rather than aspirational.
MAX_OVERCLAIM_RATE = 0.05


def truth_label(cited_by: list[dict]) -> str:
    """The label implied by every algorithm citing this paper, or nothing if they disagree."""
    buckets = set()
    for citation in cited_by:
        speedup = citation["speedup"].strip().lower()
        if speedup in STRONG_SPEEDUPS:
            buckets.add(STRONG)
        elif speedup in WEAK_SPEEDUPS:
            buckets.add(WEAK)
    if len(buckets) == 1:
        return buckets.pop()
    return INDETERMINATE  # silent or contradictory; not usable as ground truth


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-overclaim", type=float, default=MAX_OVERCLAIM_RATE)
    args = parser.parse_args()

    zoo = json.loads(ZOO_PATH.read_text(encoding="utf-8"))
    truth = {r["arxiv_id"]: truth_label(r["cited_by"]) for r in zoo["references"]}
    labelled = {k: v for k, v in truth.items() if v in (STRONG, WEAK)}
    print(f"labelled papers: {len(labelled)} "
          f"(STRONG {sum(1 for v in labelled.values() if v == STRONG)}, "
          f"WEAK {sum(1 for v in labelled.values() if v == WEAK)})")

    key = os.environ.get("SEARCH_ADMIN_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()
    client = SearchClient(SEARCH_ENDPOINT, "quantum-papers", credential)

    matrix: Counter = Counter()
    missing = 0
    overclaimed: list[tuple[str, str, list[str]]] = []

    for arxiv_id, expected in labelled.items():
        doc_id = arxiv_id.replace("/", "_").replace(".", "_")
        try:
            doc = client.get_document(key=doc_id)
        except Exception:
            missing += 1
            continue
        result = classify_paper(doc.get("title", ""), doc.get("abstract", ""))
        matrix[(expected, result.speedup_class)] += 1
        if expected == WEAK and result.speedup_class == STRONG:
            overclaimed.append((arxiv_id, doc.get("title", "")[:70], result.evidence))

    scored = sum(matrix.values())
    if not scored:
        print("FAIL: no labelled paper could be read from the index.")
        return 1

    print(f"scored: {scored}   not in index: {missing}\n")
    print(f"{'':14}{'->STRONG':>10}{'->WEAK':>9}{'->INDET':>9}")
    for expected in (STRONG, WEAK):
        row = [matrix[(expected, got)] for got in (STRONG, WEAK, INDETERMINATE)]
        print(f"  truth {expected:<7}{row[0]:>10}{row[1]:>9}{row[2]:>9}")

    decided = sum(v for (_, got), v in matrix.items() if got != INDETERMINATE)
    correct = matrix[(STRONG, STRONG)] + matrix[(WEAK, WEAK)]
    weak_total = sum(v for (exp, _), v in matrix.items() if exp == WEAK)
    overclaim_rate = len(overclaimed) / weak_total if weak_total else 0.0

    print(f"\nabstained         : {scored - decided}/{scored} "
          f"({(scored - decided) / scored:.0%})")
    print(f"accuracy when decided: {correct}/{decided} "
          f"({correct / decided:.0%})" if decided else "accuracy: n/a")
    print(f"always-STRONG would score: "
          f"{sum(v for (exp, _), v in matrix.items() if exp == STRONG)}/{scored} "
          f"({sum(v for (exp, _), v in matrix.items() if exp == STRONG) / scored:.0%})")
    print(f"\nOVER-CLAIM RATE   : {len(overclaimed)}/{weak_total} ({overclaim_rate:.1%})"
          f"   threshold {args.max_overclaim:.0%}")

    if overclaimed:
        print("\nWEAK papers read as STRONG:")
        for arxiv_id, title, evidence in overclaimed[:10]:
            print(f"  {arxiv_id:<18} {title}")
            print(f"  {'':18} evidence: {evidence}")

    if overclaim_rate > args.max_overclaim:
        print("\nOver-claim rate above threshold. This must not inform a verdict.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
