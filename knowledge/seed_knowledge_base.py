"""Seed the Quantum Advantage Evaluator knowledge base.

Seeds Cosmos DB with:
1. Algorithm Zoo (curated quantum algorithms with Troyer verdicts)
2. Reference problems (our 9 active + 11 archived)

Creates AI Search index with vector schema for hybrid search.

Generates embeddings via Azure OpenAI text-embedding-3-large.

Usage:
    python knowledge/seed_knowledge_base.py
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchIndex,
)
from azure.search.documents import SearchClient
from openai import AzureOpenAI

# Config
COSMOS_ENDPOINT = "https://qgccosmoseval.documents.azure.com:443/"
COSMOS_DATABASE = "quantum_kb"
SEARCH_ENDPOINT = "https://qgcsearcheval.search.windows.net"
OPENAI_ENDPOINT = "https://qgc-openai.openai.azure.com/"
EMBEDDING_DEPLOYMENT = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072

ROOT = Path(__file__).resolve().parent.parent


def get_credential():
    return DefaultAzureCredential()


def get_search_credential():
    """Use admin key for Search if available, otherwise DefaultAzureCredential."""
    key = os.environ.get("SEARCH_ADMIN_KEY")
    if key:
        from azure.core.credentials import AzureKeyCredential
        return AzureKeyCredential(key)
    return DefaultAzureCredential()


def get_cosmos_client():
    """Use key for Cosmos if available, otherwise DefaultAzureCredential."""
    key = os.environ.get("COSMOS_KEY")
    if key:
        return CosmosClient(COSMOS_ENDPOINT, credential=key)
    return CosmosClient(COSMOS_ENDPOINT, credential=DefaultAzureCredential())


def get_openai_client(credential):
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return AzureOpenAI(
        azure_ad_token=token.token,
        azure_endpoint=OPENAI_ENDPOINT,
        api_version="2024-10-21",
    )


def embed_text(client, text):
    """Generate embedding vector for text."""
    r = client.embeddings.create(input=text, model=EMBEDDING_DEPLOYMENT)
    return r.data[0].embedding


def seed_algorithm_zoo(cosmos_client, openai_client):
    """Seed algorithm_zoo container from curated data."""
    db = cosmos_client.get_database_client(COSMOS_DATABASE)
    container = db.get_container_client("algorithm_zoo")

    algo_path = ROOT / "knowledge" / "data" / "algorithm_zoo_index.json"
    data = json.loads(algo_path.read_text(encoding="utf-8"))
    algorithms = data.get("algorithms", [])

    print(f"Seeding {len(algorithms)} algorithms into Cosmos DB...")
    for algo in algorithms:
        import re
        doc_id = re.sub(r'[^a-z0-9_]', '', algo["name"].lower().replace(" ", "_").replace("'", "").replace("/", "_"))
        text_for_embedding = f"{algo['name']}: {algo['category']}. {algo.get('notes', '')}"

        try:
            embedding = embed_text(openai_client, text_for_embedding)
        except Exception as e:
            print(f"  Embedding failed for {algo['name']}: {e}")
            embedding = None

        doc = {
            "id": doc_id,
            "name": algo["name"],
            "category": algo["category"],
            "speedup_class": algo["speedup_class"],
            "quantum_complexity": algo["quantum_complexity"],
            "classical_best": algo["classical_best"],
            "io_bottleneck": algo["io_bottleneck"],
            "oracle_polynomial": algo["oracle_polynomial"],
            "naturally_quantum": algo["naturally_quantum"],
            "troyer_verdict": algo["troyer_verdict"],
            "notes": algo.get("notes", ""),
            "reference": algo.get("reference", ""),
            "embedding": embedding,
            "seeded_utc": datetime.now(timezone.utc).isoformat(),
        }

        container.upsert_item(doc)
        print(f"  OK: {algo['name']} ({algo['speedup_class']})")

    print(f"Algorithm zoo: {len(algorithms)} algorithms seeded")


def seed_reference_problems(cosmos_client, openai_client):
    """Seed problem_history container with our reference implementations."""
    db = cosmos_client.get_database_client(COSMOS_DATABASE)
    container = db.get_container_client("problem_history")

    ref_path = ROOT / "problems" / "reference_index.json"
    data = json.loads(ref_path.read_text(encoding="utf-8"))

    active = data.get("active_problems", [])
    archived = data.get("archived_problems", [])

    print(f"\nSeeding {len(active)} active + {len(archived)} archived problems...")

    for prob in active:
        text = f"{prob['id']}: {prob['algorithm_class']}. {prob['notes']}"
        try:
            embedding = embed_text(openai_client, text)
        except Exception:
            embedding = None

        doc = {
            "id": f"ref_{prob['id']}",
            "user_id": "system_reference",
            "problem_id": prob["id"],
            "algorithm": prob["algorithm"],
            "algorithm_class": prob["algorithm_class"],
            "speedup_class": prob["speedup_class"],
            "naturally_quantum": prob["naturally_quantum"],
            "troyer_verdict": prob["troyer_verdict"],
            "notes": prob["notes"],
            "status": "active",
            "embedding": embedding,
            "seeded_utc": datetime.now(timezone.utc).isoformat(),
        }
        container.upsert_item(doc)
        print(f"  OK: {prob['id']} (active, {prob['algorithm']})")

    for prob in archived:
        doc = {
            "id": f"ref_{prob['id']}",
            "user_id": "system_reference",
            "problem_id": prob["id"],
            "algorithm": prob["algorithm"],
            "reason": prob["reason"],
            "status": "archived",
            "seeded_utc": datetime.now(timezone.utc).isoformat(),
        }
        container.upsert_item(doc)
        print(f"  OK: {prob['id']} (archived: {prob['reason'][:40]}...)")

    print(f"Reference problems: {len(active)} active + {len(archived)} archived")


def create_search_index(search_credential):
    """Create AI Search index with vector fields for hybrid search."""
    index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=search_credential)

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="name", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="speedup_class", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchableField(name="troyer_verdict", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="io_bottleneck", type=SearchFieldDataType.Boolean, filterable=True),
        SimpleField(name="naturally_quantum", type=SearchFieldDataType.Boolean, filterable=True),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="default-vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
        profiles=[VectorSearchProfile(name="default-vector-profile", algorithm_configuration_name="default-hnsw")],
    )

    index = SearchIndex(name="quantum-algorithms", fields=fields, vector_search=vector_search)

    result = index_client.create_or_update_index(index)
    print(f"\nAI Search index created: {result.name} ({len(fields)} fields, vector-enabled)")
    return result.name


def create_papers_search_index(search_credential):
    """Create AI Search index for arxiv papers with vector fields."""
    index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=search_credential)

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="arxiv_id", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, sortable=True),
        SearchableField(name="abstract", type=SearchFieldDataType.String),
        SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="published", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SearchableField(name="authors", type=SearchFieldDataType.String),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="default-vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
        profiles=[VectorSearchProfile(name="default-vector-profile", algorithm_configuration_name="default-hnsw")],
    )

    index = SearchIndex(name="quantum-papers", fields=fields, vector_search=vector_search)

    result = index_client.create_or_update_index(index)
    print(f"AI Search papers index created: {result.name} ({len(fields)} fields, vector-enabled)")
    return result.name


def index_algorithms_in_search(search_credential, openai_client):
    """Push algorithm data into AI Search for hybrid queries."""
    search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name="quantum-algorithms", credential=search_credential)

    algo_path = ROOT / "knowledge" / "data" / "algorithm_zoo_index.json"
    data = json.loads(algo_path.read_text(encoding="utf-8"))
    algorithms = data.get("algorithms", [])

    docs = []
    for algo in algorithms:
        import re
        doc_id = re.sub(r'[^a-z0-9_]', '', algo["name"].lower().replace(" ", "_").replace("'", "").replace("/", "_"))
        content = f"{algo['name']}: {algo['category']}. Speedup: {algo['speedup_class']}. {algo.get('notes', '')} Classical: {algo['classical_best']}"

        try:
            embedding = embed_text(openai_client, content)
        except Exception:
            embedding = [0.0] * EMBEDDING_DIMENSIONS

        docs.append({
            "id": doc_id,
            "name": algo["name"],
            "category": algo["category"],
            "speedup_class": algo["speedup_class"],
            "content": content,
            "troyer_verdict": algo["troyer_verdict"],
            "io_bottleneck": algo["io_bottleneck"],
            "naturally_quantum": algo["naturally_quantum"],
            "embedding": embedding,
        })

    result = search_client.upload_documents(documents=docs)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"AI Search: indexed {succeeded}/{len(docs)} algorithms")


def main():
    print("=== Quantum Advantage Evaluator — Knowledge Base Seeder ===\n")

    credential = get_credential()
    search_credential = get_search_credential()

    # 1. Create AI Search indexes
    print("Step 1: Creating AI Search indexes...")
    create_search_index(search_credential)
    create_papers_search_index(search_credential)

    # 2. Initialize clients
    print("\nStep 2: Connecting to Azure services...")
    cosmos_client = get_cosmos_client()
    openai_client = get_openai_client(credential)
    print("  Cosmos DB: connected")
    print("  OpenAI: connected")

    # 3. Seed algorithm zoo
    print("\nStep 3: Seeding algorithm zoo...")
    seed_algorithm_zoo(cosmos_client, openai_client)

    # 4. Seed reference problems
    print("\nStep 4: Seeding reference problems...")
    seed_reference_problems(cosmos_client, openai_client)

    # 5. Index in AI Search
    print("\nStep 5: Indexing in AI Search...")
    index_algorithms_in_search(search_credential, openai_client)

    print("\n=== Knowledge base seeded successfully ===")


if __name__ == "__main__":
    main()
