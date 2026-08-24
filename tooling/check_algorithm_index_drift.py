"""Fail when the deployed algorithm index and its source file disagree.

The verdict every evaluation publishes comes from the quantum-algorithms search
index, which is seeded from knowledge/data/algorithm_zoo_index.json. Nothing kept
the two in step. On 2026-08-24 the index held 48 documents against 47 in the file:
an id-scheme change had left `lattice_gauge_theory_real-time` orphaned alongside
`lattice_gauge_theory_realtime`, and the duplicate was taking two of the three
evidence slots the router sees whenever that algorithm ranked. It had been there
for months without anything noticing.

Comparing name sets alone would not have caught it, because both documents carried
the same name. So this compares three things: the count, the set of names, and the
number of documents per name.

    python tooling/check_algorithm_index_drift.py

Exit 0 only when the index matches the file.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

REPO = Path(__file__).resolve().parents[1]
ZOO_PATH = REPO / "knowledge" / "data" / "algorithm_zoo_index.json"
SEARCH_ENDPOINT = "https://qgcsearcheval.search.windows.net"
INDEX_NAME = "quantum-algorithms"


def find_drift(
    file_names: list[str],
    declared: object,
    index_docs: list[dict],
    reported_count: int,
) -> list[str]:
    """Return every disagreement between the file and the index. Pure, so it is tested."""
    problems: list[str] = []

    # The file is the source of truth, so check it is self-consistent first.
    # A wrong total_algorithms would otherwise be reported as index drift.
    if declared != len(file_names):
        problems.append(
            f"{ZOO_PATH.name} says total_algorithms={declared} but lists {len(file_names)}"
        )
    file_dupes = [n for n, c in Counter(file_names).items() if c > 1]
    if file_dupes:
        problems.append(f"{ZOO_PATH.name} has duplicate names: {file_dupes}")

    index_names = [d["name"] for d in index_docs]

    if reported_count != len(index_docs):
        problems.append(
            f"index reports {reported_count} documents but the query returned "
            f"{len(index_docs)}; raise the page size in this script"
        )
    if len(index_docs) != len(file_names):
        problems.append(f"index has {len(index_docs)} documents, file has {len(file_names)}")

    # Name-set comparison alone misses same-name duplicates, which is the drift that
    # actually occurred, so count documents per name too.
    for name, count in Counter(index_names).items():
        if count > 1:
            ids = sorted(d["id"] for d in index_docs if d["name"] == name)
            problems.append(f"index has {count} documents named {name!r}: {ids}")

    missing = sorted(set(file_names) - set(index_names))
    extra = sorted(set(index_names) - set(file_names))
    if missing:
        problems.append(f"in the file but not indexed: {missing}")
    if extra:
        problems.append(f"indexed but not in the file: {extra}")

    return problems


def main() -> int:
    zoo = json.loads(ZOO_PATH.read_text(encoding="utf-8"))
    file_names = [a["name"] for a in zoo["algorithms"]]

    key = os.environ.get("SEARCH_ADMIN_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()
    client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, credential)

    docs = list(client.search(search_text="*", top=1000, select=["id", "name"]))
    if not docs:
        # Retrieving nothing is a failure, not a clean run. A check that silently
        # compares an empty index against the file would pass forever.
        print(f"FAIL: {INDEX_NAME} returned no documents. Cannot verify anything.")
        return 1

    problems = find_drift(file_names, zoo.get("total_algorithms"), docs,
                          client.get_document_count())

    print(f"file : {len(file_names)} algorithms ({len(set(file_names))} distinct names)")
    print(f"index: {len(docs)} documents ({len({d['name'] for d in docs})} distinct names)")

    if problems:
        print("\nDRIFT:")
        for problem in problems:
            print(f"  - {problem}")
        print(
            "\nThe verdicts rest on this index. Reconcile it against the file before "
            "trusting an evaluation."
        )
        return 1

    print("\nindex matches the file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
