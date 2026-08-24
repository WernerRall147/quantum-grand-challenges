"""Ingest the Quantum Algorithm Zoo's references - the foundational corpus we lack.

The arXiv sweep only reaches back to when ingestion started in 2026, so the papers the
verdicts actually rest on are absent: Reiher et al. on FeMoco, Shor on factoring. The
Zoo cites 550 references covering 463 distinct arXiv papers, curated by a domain expert
and, unlike our sweep, already balanced - a paper cited by an algorithm whose speedup is
"Polynomial" is evidence that the win is only quadratic, which is the side our corpus
has none of.

Each reference is also tied to the algorithm citing it, so a paper arrives with a
speedup class attached rather than as an unlabelled abstract. That mapping is written to
knowledge/data/zoo_references.json and is the grounded half of the paper classifier that
does not otherwise exist.

    python tooling/ingest_zoo_references.py            # parse and report, writes the map
    python tooling/ingest_zoo_references.py --ingest   # also fetch abstracts and index

Dry by default. Indexing is opt-in because it writes to a live search index.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_PATH = REPO / "knowledge" / "data" / "zoo_references.json"
ZOO_URL = ("https://raw.githubusercontent.com/stephenjordan/"
           "stephenjordan.github.io/master/index.html")
ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}

# arXiv accepts a batched id_list. 50 matches the page size the daily job has used
# successfully for months; the delay is not optional, two back-to-back calls earn a 429.
BATCH_SIZE = 50
BATCH_DELAY = 20

ARXIV_ID = r"(?:[0-9]{4}\.[0-9]{4,5}|[a-z-]+/[0-9]{7})"

# Entries vary: <b>Algorithm:</b>, <b id="x">Algorithm:</b>, and <b>Algorithm: </b>.
# Matching only the bare form finds 60 of the 74 and silently loses fourteen.
ALGORITHM_MARKER = re.compile(r"<b[^>]*>Algorithm:\s*</b>", re.I)
SPEEDUP = re.compile(r"<b[^>]*>Speedup:\s*</b>\s*([^<]+)", re.I)
CITATION = re.compile(r'href="#([^"]+)"')
BIB_ENTRY = re.compile(r'<dt id="([^"]+)">.*?</dt>\s*<dd>(.*?)</dd>', re.I | re.S)
BIB_ARXIV = re.compile(rf"arxiv\.org/abs/({ARXIV_ID})", re.I)

KNOWN_SPEEDUPS = {
    "superpolynomial", "exponential", "polynomial", "varies", "various",
    "constant factor", "unknown",
}


def normalise_speedup(raw: str) -> tuple[str, str]:
    """Return (class, verbatim). Prose is left unclassified rather than forced.

    The Zoo's Speedup field is usually a single class word, but not always. Adiabatic
    Algorithms carries a whole sentence, and Bernstein-Vazirani reads "Polynomial
    Directly, Superpolynomial Recursively". Coercing those into a class would invent a
    judgement the source does not make, and 28 citations would inherit it.
    """
    cleaned = " ".join(raw.split()).rstrip(".").strip()
    if cleaned.lower() in KNOWN_SPEEDUPS:
        return cleaned, cleaned
    return "unclassified", cleaned


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "quantum-grand-challenges"})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_bibliography(html: str) -> dict[str, dict]:
    """anchor -> {arxiv_id, citation}. Entries without an arXiv link are skipped."""
    bibliography = {}
    for anchor, body in BIB_ENTRY.findall(html):
        match = BIB_ARXIV.search(body)
        if not match:
            continue
        text = re.sub(r"<[^>]+>", " ", body)
        bibliography[anchor] = {
            "arxiv_id": match.group(1),
            "citation": " ".join(text.split())[:300],
        }
    return bibliography


def parse_algorithms(html: str) -> list[dict]:
    """Algorithm entries with the anchors they cite. Stops before the bibliography."""
    body = html.split("<dt id=", 1)[0]
    entries = []
    for block in ALGORITHM_MARKER.split(body)[1:]:
        name = re.match(r"\s*([^<]+)", block)
        speedup = SPEEDUP.search(block)
        speedup_class, speedup_raw = normalise_speedup(
            speedup.group(1) if speedup else "unknown")
        entries.append({
            "name": name.group(1).strip() if name else "?",
            "speedup": speedup_class,
            "speedup_raw": speedup_raw,
            "cites": sorted(set(CITATION.findall(block))),
        })
    return entries


def fetch_abstracts(arxiv_ids: list[str]) -> list[dict]:
    papers = []
    for start in range(0, len(arxiv_ids), BATCH_SIZE):
        batch = arxiv_ids[start:start + BATCH_SIZE]
        url = f"{ARXIV_API}?id_list={','.join(batch)}&max_results={len(batch)}"
        print(f"  fetching {start + 1}-{start + len(batch)} of {len(arxiv_ids)}")
        root = ET.fromstring(fetch(url))
        for entry in root.findall("atom:entry", NS):
            raw_id = entry.find("atom:id", NS).text
            papers.append({
                "arxiv_id": raw_id.rsplit("/abs/", 1)[-1].split("v")[0],
                "title": " ".join(entry.find("atom:title", NS).text.split()),
                "abstract": " ".join(entry.find("atom:summary", NS).text.split()),
                "published": entry.find("atom:published", NS).text,
                # A list, not a joined string: upsert_to_search_index does
                # ", ".join(p["authors"][:5]), which would splice a string per character.
                "authors": [a.find("atom:name", NS).text
                            for a in entry.findall("atom:author", NS)],
                "categories": ["zoo-reference"],
            })
        if start + BATCH_SIZE < len(arxiv_ids):
            time.sleep(BATCH_DELAY)
    return papers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ingest", action="store_true",
                        help="fetch abstracts and write them to the search index")
    parser.add_argument("--limit", type=int, default=0,
                        help="only process the first N references (for a smoke test)")
    args = parser.parse_args()

    html = fetch(ZOO_URL)
    bibliography = parse_bibliography(html)
    algorithms = parse_algorithms(html)

    # A reference can be cited by several algorithms; keep every citing algorithm so a
    # later classifier can see when the same paper backs both a strong and a weak claim.
    references: dict[str, dict] = {}
    for algorithm in algorithms:
        for anchor in algorithm["cites"]:
            entry = bibliography.get(anchor)
            if not entry:
                continue
            record = references.setdefault(entry["arxiv_id"], {
                "arxiv_id": entry["arxiv_id"],
                "citation": entry["citation"],
                "cited_by": [],
            })
            record["cited_by"].append({"algorithm": algorithm["name"],
                                       "speedup": algorithm["speedup"]})

    print(f"algorithms parsed        : {len(algorithms)}")
    print(f"bibliography with arXiv  : {len(bibliography)}")
    print(f"references cited by an algorithm: {len(references)}")

    speedups: dict[str, int] = {}
    for record in references.values():
        for citation in record["cited_by"]:
            speedups[citation["speedup"]] = speedups.get(citation["speedup"], 0) + 1
    print("\ncitations by the speedup class of the citing algorithm:")
    for speedup, count in sorted(speedups.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>5}  {speedup}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "source": ZOO_URL,
        "algorithms": algorithms,
        "references": sorted(references.values(), key=lambda r: r["arxiv_id"]),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT_PATH.relative_to(REPO)}")

    if not args.ingest:
        print("\ndry run. pass --ingest to fetch abstracts and write to the search index.")
        return 0

    arxiv_ids = sorted(references)
    if args.limit:
        arxiv_ids = arxiv_ids[:args.limit]
    print(f"\nfetching {len(arxiv_ids)} abstracts from arXiv")
    papers = fetch_abstracts(arxiv_ids)
    print(f"  got {len(papers)} of {len(arxiv_ids)}")

    sys.path.insert(0, str(REPO / "knowledge" / "ingest"))
    from arxiv_ingester import generate_embeddings, upsert_to_search_index

    papers = generate_embeddings(papers)
    if not upsert_to_search_index(papers):
        print("FAIL: not every document landed in the index")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
