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


ARXIV_API = "http://export.arxiv.org/api/query"
CATEGORIES = ["cs.QC", "quant-ph"]
MAX_RESULTS_PER_CATEGORY = 50


def fetch_arxiv_papers(category: str, days_back: int = 1, max_results: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent papers from arxiv API."""
    import urllib.request
    import xml.etree.ElementTree as ET

    # arxiv API date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)

    query = f"cat:{category}"
    url = f"{ARXIV_API}?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"

    req = urllib.request.Request(url, headers={"User-Agent": "QuantumGrandChallenges/2.0"})
    response = urllib.request.urlopen(req, timeout=30)
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


def generate_embeddings(papers: List[Dict], api_key: str, endpoint: str) -> List[Dict]:
    """Generate vector embeddings for paper abstracts using Azure OpenAI."""
    # Placeholder — will use Azure OpenAI text-embedding-3-large
    # from openai import AzureOpenAI
    # client = AzureOpenAI(api_key=api_key, azure_endpoint=endpoint, api_version="2024-10-21")
    for p in papers:
        # p["embedding"] = client.embeddings.create(input=p["abstract"], model="text-embedding-3-large").data[0].embedding
        p["embedding"] = None  # Placeholder until Azure OpenAI is provisioned
    return papers


def upsert_to_cosmos(papers: List[Dict], connection_string: str, database: str = "quantum_kb", container: str = "scientific_papers"):
    """Upsert papers into Cosmos DB."""
    # Placeholder — will use azure.cosmos.CosmosClient
    print(f"Would upsert {len(papers)} papers to Cosmos DB {database}/{container}")


def upsert_to_search_index(papers: List[Dict], endpoint: str, api_key: str, index_name: str = "quantum-papers"):
    """Upsert papers into Azure AI Search index."""
    # Placeholder — will use azure.search.documents.SearchClient
    print(f"Would upsert {len(papers)} papers to AI Search index {index_name}")


def main():
    """Daily ingestion pipeline."""
    print(f"Starting arxiv ingestion at {datetime.now(timezone.utc).isoformat()}")

    all_papers = []
    for cat in CATEGORIES:
        papers = fetch_arxiv_papers(cat, days_back=1, max_results=MAX_RESULTS_PER_CATEGORY)
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

    # Generate embeddings (when Azure OpenAI is provisioned)
    # relevant = generate_embeddings(relevant, api_key=os.environ["AZURE_OPENAI_KEY"], endpoint=os.environ["AZURE_OPENAI_ENDPOINT"])

    # Upsert to Cosmos DB (when provisioned)
    # upsert_to_cosmos(relevant, connection_string=os.environ["COSMOS_CONNECTION_STRING"])

    # Upsert to AI Search (when provisioned)
    # upsert_to_search_index(relevant, endpoint=os.environ["SEARCH_ENDPOINT"], api_key=os.environ["SEARCH_KEY"])

    # For now, save to local file
    output_path = "knowledge/data/latest_papers.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"ingested_utc": datetime.now(timezone.utc).isoformat(), "count": len(relevant), "papers": relevant}, f, indent=2)
    print(f"Saved {len(relevant)} papers to {output_path}")


if __name__ == "__main__":
    main()
