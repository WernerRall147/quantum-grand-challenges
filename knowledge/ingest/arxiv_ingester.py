"""Daily arxiv paper ingestion for the Quantum Advantage Evaluator.

Fetches every paper submitted in the window that matches any configured source,
filters for relevance, generates embeddings, and indexes into Azure AI Search.

Designed to run as an Azure Container Apps Job on a daily schedule.
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

# Will use these when Azure resources are provisioned:
# from azure.cosmos import CosmosClient
# from azure.search.documents import SearchClient
# from openai import AzureOpenAI


ARXIV_API = "https://export.arxiv.org/api/query"

# (label for logs, URL-ready search_query fragment).
#
# cs.QC was listed here and returned 0 papers on every run for months. It is not an
# arXiv category: https://arxiv.org/archive/cs lists 40 CS categories and cs.QC is
# not among them, and `cat:cs.QC` reports 0 total results. quant-ph is the canonical
# home (184,786 papers); cs.ET explicitly covers quantum technologies.
#
# Quantum work also appears in cs.LG, cs.CR and cs.CC. Those categories are swept by
# abstract terms rather than wholesale, so a machine-learning paper only arrives if it
# actually mentions quantum computing. Sources overlap; main() deduplicates by arxiv_id.
SOURCES = [
    ("cat:quant-ph", "cat:quant-ph"),
    ("cat:cs.ET", "cat:cs.ET"),
    ('abs:"quantum computing"', "abs:%22quantum+computing%22"),
    ('abs:"quantum algorithm"', "abs:%22quantum+algorithm%22"),
    ('abs:"quantum advantage"', "abs:%22quantum+advantage%22"),
    ('abs:"post-quantum"', "abs:%22post-quantum%22"),
]

# arXiv caps a single response, so results are paged. Neither number is arbitrary:
# 100-per-page timed out on every retry when measured, while 50 is the size this
# job has fetched successfully every day for months. The delay is not optional
# either - two back-to-back requests earned a 429.
ARXIV_PAGE_SIZE = 50
ARXIV_PAGE_DELAY = 4
ARXIV_MAX_PAGES = 40

# arXiv rate-limits with 429 and drops slow reads, so fetches are retried.
ARXIV_MAX_ATTEMPTS = 4
ARXIV_BACKOFF_SECONDS = 5


def _retry_delay(attempt: int, error: Exception) -> int:
    """Exponential backoff, widened to honour a 429 Retry-After when present."""
    import urllib.error

    delay = ARXIV_BACKOFF_SECONDS * (3 ** (attempt - 1))
    if isinstance(error, urllib.error.HTTPError):
        retry_after = error.headers.get("Retry-After") if error.headers else None
        if retry_after:
            try:
                delay = max(delay, int(float(retry_after)))
            except ValueError:
                pass
    return delay


def _open_arxiv(req, timeout: int):
    """Single arXiv request, falling back to an unverified context only for TLS faults."""
    import ssl
    import urllib.error
    import urllib.request

    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError:
        # An HTTP status is a real answer; retrying it unverified changes nothing.
        raise
    except (ssl.SSLCertVerificationError, urllib.error.URLError):
        ctx = ssl._create_unverified_context()
        return urllib.request.urlopen(req, timeout=timeout, context=ctx)


def _open_arxiv_with_retry(req, timeout: int = 30):
    import urllib.error

    last_error: Exception | None = None
    for attempt in range(ARXIV_MAX_ATTEMPTS):
        if attempt:
            delay = _retry_delay(attempt, last_error)
            print(f"    retry {attempt}/{ARXIV_MAX_ATTEMPTS - 1} in {delay}s after {type(last_error).__name__}: {last_error}")
            time.sleep(delay)
        try:
            return _open_arxiv(req, timeout)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_error = e
    raise last_error


def _parse_entries(root, ns) -> List[Dict[str, Any]]:
    papers = []
    for entry in root.findall("atom:entry", ns):
        arxiv_id = entry.find("atom:id", ns).text.split("/abs/")[-1]
        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
        abstract = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
        published = entry.find("atom:published", ns).text
        authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
        categories = [c.get("term") for c in entry.findall("atom:category", ns)]

        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": abstract,
            "authors": authors[:10],  # Cap at 10 authors
            "categories": categories,
            "published": published,
            "ingested_utc": datetime.now(timezone.utc).isoformat(),
            "source": "arxiv",
        })
    return papers


def fetch_arxiv_papers(query: str, days_back: int = 1,
                       max_pages: int = ARXIV_MAX_PAGES) -> List[Dict[str, Any]]:
    """Fetch every paper matching `query` submitted within the window.

    The date window used to be computed and then left out of the request, so this
    returned the newest max_results papers regardless of days_back - and with a cap
    of 50 against a category that publishes more than that daily, the corpus was
    silently truncated every run.
    """
    import urllib.request
    import xml.etree.ElementTree as ET

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)
    window = f"[{start_date.strftime('%Y%m%d%H%M')}+TO+{end_date.strftime('%Y%m%d%H%M')}]"
    search_query = f"{query}+AND+submittedDate:{window}"

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    papers: List[Dict[str, Any]] = []

    for page in range(max_pages):
        if page:
            time.sleep(ARXIV_PAGE_DELAY)
        url = (f"{ARXIV_API}?search_query={search_query}"
               f"&sortBy=submittedDate&sortOrder=descending"
               f"&start={page * ARXIV_PAGE_SIZE}&max_results={ARXIV_PAGE_SIZE}")
        req = urllib.request.Request(url, headers={"User-Agent": "QuantumGrandChallenges/2.0"})
        response = _open_arxiv_with_retry(req, timeout=60)
        batch = _parse_entries(ET.fromstring(response.read().decode("utf-8")), ns)
        papers.extend(batch)
        if len(batch) < ARXIV_PAGE_SIZE:
            return papers

    print(f"    WARNING: hit the {max_pages}-page cap; this window is truncated")
    return papers


def filter_quantum_computing_relevance(papers: List[Dict]) -> List[Dict]:
    """Filter papers for quantum computing relevance."""
    keywords = [
        "quantum advantage", "quantum speedup", "quantum algorithm",
        "quantum error correction", "quantum simulation", "QPE",
        "quantum phase estimation", "grover", "shor", "VQE", "QAOA",
        "resource estimation", "fault-tolerant", "logical qubit",
        "quantum chemistry", "hamiltonian simulation", "quantum supremacy",
        "quantum utility", "quantum computing", "qubit",
    ]
    relevant = []
    for p in papers:
        text = (p["title"] + " " + p["abstract"]).lower()
        if any(kw in text for kw in keywords):
            relevant.append(p)
    return relevant


def generate_embeddings(papers: List[Dict]) -> List[Dict]:
    """Generate vector embeddings for paper abstracts using Azure OpenAI."""
    try:
        from azure.identity import DefaultAzureCredential
        from openai import AzureOpenAI

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://qgc-openai.openai.azure.com/")
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        client = AzureOpenAI(
            azure_ad_token=token.token,
            azure_endpoint=endpoint,
            api_version="2024-10-21",
        )
        # Batch in groups of 16 to stay under token limits
        batch_size = 16
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            texts = [p["abstract"][:2000] for p in batch]
            resp = client.embeddings.create(input=texts, model="text-embedding-3-large")
            for j, emb_data in enumerate(resp.data):
                batch[j]["embedding"] = emb_data.embedding
        print(f"  Embeddings: generated for {len(papers)} papers")
    except Exception as e:
        print(f"  Embeddings failed ({e}), papers will have no vectors")
        for p in papers:
            if "embedding" not in p:
                p["embedding"] = None
    return papers



def upsert_to_search_index(papers: List[Dict]) -> bool:
    """Upsert papers into Azure AI Search quantum-papers index."""
    from azure.search.documents import SearchClient

    search_key = os.environ.get("SEARCH_ADMIN_KEY")
    if search_key:
        from azure.core.credentials import AzureKeyCredential
        credential = AzureKeyCredential(search_key)
    else:
        from azure.identity import DefaultAzureCredential
        credential = DefaultAzureCredential()

    try:
        client = SearchClient(
            endpoint="https://qgcsearcheval.search.windows.net",
            index_name="quantum-papers",
            credential=credential,
        )
        docs = []
        for p in papers:
            doc = {
                "id": p["arxiv_id"].replace("/", "_").replace(".", "_"),
                "arxiv_id": p["arxiv_id"],
                "title": p["title"],
                "abstract": p["abstract"][:2000],
                "category": p["categories"][0] if p["categories"] else "unknown",
                "published": p["published"],
                "authors": ", ".join(p["authors"][:5]),
            }
            if p.get("embedding"):
                doc["embedding"] = p["embedding"]
            docs.append(doc)
        result = client.upload_documents(documents=docs)
        succeeded = sum(1 for r in result if r.succeeded)
        print(f"  AI Search: indexed {succeeded}/{len(docs)} papers")
        # Every document must land. Accepting a partial write here is how a
        # data-loss bug reports success.
        return succeeded == len(docs)
    except Exception as e:
        print(f"  AI Search upsert failed: {e}")
        return False


def main():
    """Daily ingestion pipeline."""
    print(f"Starting arxiv ingestion at {datetime.now(timezone.utc).isoformat()}")

    all_papers = []
    failed_categories = []
    for label, query in SOURCES:
        try:
            papers = fetch_arxiv_papers(query, days_back=3)
        except Exception as e:  # one bad source must not lose the whole run
            failed_categories.append(label)
            print(f"  {label}: FAILED after {ARXIV_MAX_ATTEMPTS} attempts -- {type(e).__name__}: {e}")
            continue
        print(f"  {label}: fetched {len(papers)} papers")
        all_papers.extend(papers)

    if failed_categories and len(failed_categories) == len(SOURCES):
        raise SystemExit(
            f"Ingestion failed: every arXiv source failed ({', '.join(failed_categories)})"
        )

    # Deduplicate by arxiv_id
    seen = set()
    unique = []
    for p in all_papers:
        if p["arxiv_id"] not in seen:
            seen.add(p["arxiv_id"])
            unique.append(p)

    print(f"Total unique papers: {len(unique)}")

    # Filter for quantum computing relevance
    relevant = filter_quantum_computing_relevance(unique)
    print(f"Relevant to quantum computing: {len(relevant)}")

    # Generate embeddings
    if relevant:
        relevant = generate_embeddings(relevant)

    # AI Search is the query path for papers. Any rejection fails the job: a
    # partial write is a silent data-loss bug, not a success.
    failed_sinks = []
    if relevant:
        if not upsert_to_search_index(relevant):
            failed_sinks.append("AI Search")

    # Save to local file as backup
    output_path = "knowledge/data/latest_papers.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"ingested_utc": datetime.now(timezone.utc).isoformat(), "count": len(relevant), "papers": relevant}, f, indent=2)
    print(f"Saved {len(relevant)} papers to {output_path}")

    if failed_categories:
        print(f"WARNING: arXiv categories that failed: {', '.join(failed_categories)}")

    if failed_sinks:
        raise SystemExit(
            f"Ingestion incomplete: {', '.join(failed_sinks)} rejected the papers"
        )


if __name__ == "__main__":
    main()
