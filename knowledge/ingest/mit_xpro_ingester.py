"""MIT xPRO course transcript ingester.

Indexes ~80 course transcripts (C1 Intro to QC, C2 Quantum Algorithms for
Cybersecurity/Chemistry/Optimization) into the existing quantum-papers AI
Search index, so the evaluator can cite authoritative course content
alongside arxiv papers.

Document IDs use the form `mit-xpro:<filename-stem>` so they don't collide
with arxiv IDs.

Run:
    python knowledge/ingest/mit_xpro_ingester.py
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent

# Course folders + metadata
COURSES = [
    {
        "code": "QCFx1",
        "label": "MIT xPRO QCFx1: Introduction to Quantum Computing",
        "folder": "C1 Intro to Quantum Computing",
        "category": "mit-xpro-c1",
    },
    {
        "code": "QCFx2",
        "label": "MIT xPRO QCFx2: Quantum Algorithms for Cybersecurity, Chemistry, and Optimization",
        "folder": "C2 Quantum Algorithms for Cybersecurity, Chemistry, and Optimization_",
        "category": "mit-xpro-c2",
    },
]

# Map common video-code -> human-readable topic hints used to title each chunk.
TOPIC_HINTS = {
    # C1 weeks
    "Q1M1": "Foundations of Quantum Computing",
    "Q1M2": "Qubit Modalities & DiVincenzo Criteria",
    "Q1M3": "Quantum Gates & Circuits",
    "Q1M4": "Algorithms & Software Stack",
    # C2 weeks
    "Q2W1": "Quantum Cryptography & Shor's Algorithm",
    "Q2W2": "Grover's Algorithm & Quantum Search",
    "Q2W3": "Quantum Chemistry & VQE",
    "Q2W4": "Quantum Optimization & QAOA",
}

# Chunk size for embedding (text-embedding-3-large supports 8192 tokens, but
# search relevance is better with smaller passages).
CHUNK_CHARS = 1800
CHUNK_OVERLAP = 200


def _topic_hint(filename: str) -> str:
    """Lookup topic hint from filename prefix (e.g. Q1M1, Q2W1)."""
    for prefix, hint in TOPIC_HINTS.items():
        if filename.startswith(prefix):
            return hint
    return "Quantum Computing Course Transcript"


def _chunk_text(text: str, chunk_chars: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split a long transcript into overlapping passages on sentence boundaries."""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= chunk_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_chars, len(text))
        # Prefer sentence boundary if we're not at end
        if end < len(text):
            tail = text[start:end]
            last_period = max(tail.rfind(". "), tail.rfind("? "), tail.rfind("! "))
            if last_period > chunk_chars * 0.5:
                end = start + last_period + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def collect_transcripts() -> List[Dict[str, Any]]:
    """Walk both course folders and produce transcript records ready to embed.

    Each record represents one chunk of one transcript. Multi-chunk transcripts
    get suffixes like ":chunk1", ":chunk2".

    Filters: only files whose names match the transcript convention (e.g.
    `Q1M1V1_REV_2026-en.txt`, `Q2W3V7a_REV_2026-en.txt`). This excludes
    `Links.txt`, `People.txt`, ad-hoc notes, and empty placeholders.
    """
    records: List[Dict[str, Any]] = []
    ingested_utc = datetime.now(timezone.utc).isoformat()

    # Filename convention: Q<course><module/week><video><suffix>_REV_<year>...
    transcript_pattern = re.compile(r"^Q\dM?W?\d+V\d+", re.IGNORECASE)

    for course in COURSES:
        course_dir = KNOWLEDGE_ROOT / course["folder"]
        if not course_dir.is_dir():
            print(f"  skip: {course_dir} (not found)")
            continue

        # Each course has W1..W4 subfolders
        txt_files = sorted(course_dir.rglob("*.txt"))
        for path in txt_files:
            # Filter: only Q*V* transcript files
            if not transcript_pattern.match(path.stem):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                print(f"  skip {path.name}: {e}")
                continue

            if len(text.strip()) < 200:
                # Likely an empty or near-empty file
                continue

            stem = path.stem  # e.g. Q2W1V1_REV_2026
            week = path.parent.name  # "W1", "W2", etc.
            topic = _topic_hint(stem)
            base_id = f"mit-xpro:{stem}"

            chunks = _chunk_text(text)
            for i, chunk in enumerate(chunks):
                doc_id = base_id if len(chunks) == 1 else f"{base_id}:chunk{i+1}"
                title_suffix = f" (part {i+1}/{len(chunks)})" if len(chunks) > 1 else ""
                records.append({
                    "doc_id": doc_id,
                    "title": f"{course['code']} {week}: {stem} — {topic}{title_suffix}",
                    "abstract": chunk[:2000],
                    "category": course["category"],
                    "published": "2026-01-01",  # course publication marker
                    "authors": "MIT xPRO Quantum Computing Fundamentals",
                    "ingested_utc": ingested_utc,
                    "source": "mit-xpro",
                    "course_code": course["code"],
                    "week": week,
                    "video_id": stem,
                })

    return records


def generate_embeddings(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate vector embeddings for transcript chunks using Azure OpenAI."""
    try:
        from azure.identity import DefaultAzureCredential
        from openai import AzureOpenAI
    except ImportError:
        print("  Embeddings: openai/azure-identity not installed; skipping")
        for r in records:
            r["embedding"] = None
        return records

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://qgc-openai.openai.azure.com/")
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        client = AzureOpenAI(
            azure_ad_token=token.token,
            azure_endpoint=endpoint,
            api_version="2024-10-21",
        )
    except Exception as e:  # noqa: BLE001
        print(f"  Embeddings: auth failed ({e}); skipping vectors")
        for r in records:
            r["embedding"] = None
        return records

    batch_size = 16
    total = len(records)
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        texts = [r["abstract"][:2000] for r in batch]
        try:
            resp = client.embeddings.create(input=texts, model="text-embedding-3-large")
            for j, emb_data in enumerate(resp.data):
                batch[j]["embedding"] = emb_data.embedding
        except Exception as e:  # noqa: BLE001
            print(f"  Embeddings: batch {i//batch_size+1} failed ({e})")
            for r in batch:
                if "embedding" not in r:
                    r["embedding"] = None
        print(f"  Embeddings: {min(i+batch_size, total)}/{total}")
    return records


_ID_SAFE_RE = re.compile(r"[^A-Za-z0-9_\-=]")


def _safe_doc_id(doc_id: str) -> str:
    """Convert a doc_id like 'mit-xpro:Q1M1V6_REV_2026-en (1):chunk1' to a key
    that AI Search accepts (only letters, digits, underscore, dash, equals)."""
    return _ID_SAFE_RE.sub("_", doc_id)


def upsert_to_search(records: List[Dict[str, Any]]) -> int:
    """Upsert into the quantum-papers AI Search index. Returns count succeeded."""
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_key = os.environ.get("SEARCH_ADMIN_KEY")
    if not search_key:
        print("  AI Search: SEARCH_ADMIN_KEY not set; skipping upsert")
        return 0

    client = SearchClient(
        endpoint="https://qgcsearcheval.search.windows.net",
        index_name="quantum-papers",
        credential=AzureKeyCredential(search_key),
    )

    docs: List[Dict[str, Any]] = []
    for r in records:
        doc = {
            "id": _safe_doc_id(r["doc_id"]),
            "arxiv_id": r["doc_id"],  # reuse arxiv_id field for the citation handle
            "title": r["title"],
            "abstract": r["abstract"],
            "category": r["category"],
            "published": r["published"],
            "authors": r["authors"],
        }
        if r.get("embedding"):
            doc["embedding"] = r["embedding"]
        docs.append(doc)

    succeeded = 0
    # Upload in batches of 100 (AI Search batch limit)
    for i in range(0, len(docs), 100):
        chunk = docs[i:i + 100]
        try:
            result = client.upload_documents(documents=chunk)
            succeeded += sum(1 for x in result if x.succeeded)
        except Exception as e:  # noqa: BLE001
            print(f"  AI Search: batch {i//100+1} failed ({e})")
    print(f"  AI Search: upserted {succeeded}/{len(docs)} chunks into quantum-papers")
    return succeeded


def main() -> None:
    print(f"Starting MIT xPRO ingestion at {datetime.now(timezone.utc).isoformat()}")
    print(f"Knowledge root: {KNOWLEDGE_ROOT}")

    records = collect_transcripts()
    print(f"Collected {len(records)} transcript chunks across {len(COURSES)} courses")

    if not records:
        print("Nothing to ingest.")
        return

    records = generate_embeddings(records)
    succeeded = upsert_to_search(records)

    # Persist a local manifest for offline reproducibility
    manifest_path = KNOWLEDGE_ROOT / "data" / "mit_xpro_ingest_manifest.json"
    import json
    manifest = {
        "ingested_utc": datetime.now(timezone.utc).isoformat(),
        "chunk_count": len(records),
        "succeeded": succeeded,
        "courses": [
            {"code": c["code"], "category": c["category"], "label": c["label"]}
            for c in COURSES
        ],
        "documents": [
            {
                "id": r["doc_id"],
                "title": r["title"],
                "category": r["category"],
                "course_code": r.get("course_code"),
                "week": r.get("week"),
                "video_id": r.get("video_id"),
                "char_count": len(r["abstract"]),
                "has_embedding": bool(r.get("embedding")),
            }
            for r in records
        ],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
