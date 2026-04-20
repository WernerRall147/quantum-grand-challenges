"""Daily arxiv paper ingestion for the Quantum Advantage Evaluator.

Fetches new papers from arxiv categories cs.QC and quant-ph,
filters for relevance, generates embeddings, and indexes into
Cosmos DB + Azure AI Search.

Designed to run as an Azure Function with a timer trigger (daily).
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
CATEGORIES = ["cs.QC", "quant-ph"]
MAX_RESULTS_PER_CATEGORY = 50


def fetch_arxiv_papers(category: str, days_back: int = 1, max_results: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent papers from arxiv API."""
    import urllib.request
    import ssl
    import xml.etree.ElementTree as ET

    # arxiv API date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)

    query = f"cat:{category}"
    url = f"{ARXIV_API}?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"

    req = urllib.request.Request(url, headers={"User-Agent": "QuantumGrandChallenges/2.0"})
    # Handle corporate proxies / SSL cert issues
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except (ssl.SSLCertVerificationError, urllib.error.URLError):
        ctx = ssl._create_unverified_context()
        response = urllib.request.urlopen(req, timeout=30, context=ctx)
    xml_data = response.read().decode("utf-8")

    root = ET.fromstring(xml_data)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

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


def upsert_to_cosmos(papers: List[Dict]):
    """Upsert papers into Cosmos DB. Uses key if COSMOS_KEY set, otherwise Entra ID."""
    from azure.cosmos import CosmosClient

    endpoint = "https://qgccosmoseval.documents.azure.com:443/"
    try:
        cosmos_key = os.environ.get("COSMOS_KEY")
        if cosmos_key:
            client = CosmosClient(endpoint, credential=cosmos_key)
        else:
            from azure.identity import DefaultAzureCredential
            client = CosmosClient(endpoint, credential=DefaultAzureCredential())
        container = client.get_database_client("quantum_kb").get_container_client("scientific_papers")
        for p in papers:
            doc = {
                "id": p["arxiv_id"].replace("/", "_").replace(".", "_"),
                "arxiv_id": p["arxiv_id"],
                "title": p["title"],
                "abstract": p["abstract"][:2000],
                "authors": p["authors"],
                "categories": p["categories"],
                "published": p["published"],
                "category": p["categories"][0] if p["categories"] else "unknown",
                "ingested_utc": p["ingested_utc"],
                "source": "arxiv",
            }
            container.upsert_item(doc)
        print(f"  Cosmos DB: upserted {len(papers)} papers")
    except Exception as e:
        print(f"  Cosmos DB upsert failed: {e}")


def upsert_to_search_index(papers: List[Dict]):
    """Upsert papers into Azure AI Search quantum-papers index."""
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_key = os.environ.get("SEARCH_ADMIN_KEY")
    if not search_key:
        print("  AI Search: SEARCH_ADMIN_KEY not set, skipping")
        return

    try:
        client = SearchClient(
            endpoint="https://qgcsearcheval.search.windows.net",
            index_name="quantum-papers",
            credential=AzureKeyCredential(search_key),
        )
        docs = []
        for p in papers:
            docs.append({
                "id": p["arxiv_id"].replace("/", "_").replace(".", "_"),
                "arxiv_id": p["arxiv_id"],
                "title": p["title"],
                "abstract": p["abstract"][:2000],
                "category": p["categories"][0] if p["categories"] else "unknown",
                "published": p["published"],
                "authors": ", ".join(p["authors"][:5]),
            })
        result = client.upload_documents(documents=docs)
        succeeded = sum(1 for r in result if r.succeeded)
        print(f"  AI Search: indexed {succeeded}/{len(docs)} papers")
    except Exception as e:
        print(f"  AI Search upsert failed: {e}")


def main():
    """Daily ingestion pipeline."""
    print(f"Starting arxiv ingestion at {datetime.now(timezone.utc).isoformat()}")

    all_papers = []
    for cat in CATEGORIES:
        papers = fetch_arxiv_papers(cat, days_back=3, max_results=MAX_RESULTS_PER_CATEGORY)
        print(f"  {cat}: fetched {len(papers)} papers")
        all_papers.extend(papers)

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

    # Upsert to Cosmos DB
    if relevant:
        upsert_to_cosmos(relevant)
        upsert_to_search_index(relevant)

    # Save to local file as backup
    output_path = "knowledge/data/latest_papers.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"ingested_utc": datetime.now(timezone.utc).isoformat(), "count": len(relevant), "papers": relevant}, f, indent=2)
    print(f"Saved {len(relevant)} papers to {output_path}")


if __name__ == "__main__":
    main()
