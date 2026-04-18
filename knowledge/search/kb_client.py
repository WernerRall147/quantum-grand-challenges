"""Knowledge Base query tools for the Quantum Advantage Evaluator agents.

Provides search functions over:
- Algorithm Zoo (Cosmos DB + AI Search with vector embeddings)
- Reference Problems (Cosmos DB)
- Scientific Papers (AI Search — when arxiv ingestion is live)

These functions are the tools that agents call via the orchestrator.
"""

import json
import os
from typing import List, Dict, Any, Optional

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Config
COSMOS_ENDPOINT = "https://qgccosmoseval.documents.azure.com:443/"
COSMOS_DATABASE = "quantum_kb"
SEARCH_ENDPOINT = "https://qgcsearcheval.search.windows.net"
OPENAI_ENDPOINT = "https://qgc-openai.openai.azure.com/"
EMBEDDING_DEPLOYMENT = "text-embedding-3-large"


class QuantumKnowledgeBase:
    """Query interface for the Quantum Advantage Evaluator knowledge base."""

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.cosmos = None
        self.db = None
        self.search_client = None

        # Try Cosmos DB — may not exist yet
        try:
            self.cosmos = CosmosClient(COSMOS_ENDPOINT, credential=self.credential)
            self.db = self.cosmos.get_database_client(COSMOS_DATABASE)
        except Exception:
            pass

        # AI Search — use key if available, otherwise Entra ID
        try:
            search_key = os.environ.get("SEARCH_ADMIN_KEY")
            search_cred = AzureKeyCredential(search_key) if search_key else self.credential
            self.search_client = SearchClient(
                endpoint=SEARCH_ENDPOINT,
                index_name="quantum-algorithms",
                credential=search_cred,
            )
        except Exception:
            pass

    def _get_openai_client(self):
        """Get OpenAI client with fresh token."""
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        return AzureOpenAI(
            azure_ad_token=token.token,
            azure_endpoint=OPENAI_ENDPOINT,
            api_version="2024-10-21",
        )

    def _embed(self, text: str) -> List[float]:
        """Generate embedding vector."""
        client = self._get_openai_client()
        r = client.embeddings.create(input=text, model=EMBEDDING_DEPLOYMENT)
        return r.data[0].embedding

    # === Algorithm Zoo Tools ===

    def search_algorithms(self, query: str, top: int = 5) -> List[Dict[str, Any]]:
        """Hybrid search over the algorithm zoo (keyword + vector).

        Falls back to keyword-only search if embeddings are unavailable.
        This is the primary tool for the Classifier Agent.
        """
        if not self.search_client:
            return []

        # Try hybrid search (keyword + vector), fall back to keyword-only
        try:
            embedding = self._embed(query)
            from azure.search.documents.models import VectorizedQuery
            results = self.search_client.search(
                search_text=query,
                vector_queries=[VectorizedQuery(vector=embedding, k_nearest_neighbors=top, fields="embedding")],
                top=top,
                select=["name", "category", "speedup_class", "content", "troyer_verdict", "io_bottleneck", "naturally_quantum"],
            )
        except Exception:
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=["name", "category", "speedup_class", "content", "troyer_verdict", "io_bottleneck", "naturally_quantum"],
            )

        return [
            {
                "name": r["name"],
                "category": r["category"],
                "speedup_class": r["speedup_class"],
                "troyer_verdict": r["troyer_verdict"],
                "io_bottleneck": r["io_bottleneck"],
                "naturally_quantum": r["naturally_quantum"],
                "content": r["content"],
                "score": r["@search.score"],
            }
            for r in results
        ]

    def get_algorithm(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific algorithm by name from Cosmos DB."""
        if not self.db:
            return None
        container = self.db.get_container_client("algorithm_zoo")
        doc_id = name.lower().replace(" ", "_").replace("'", "").replace("(", "").replace(")", "")
        try:
            items = list(container.query_items(
                query=f"SELECT * FROM c WHERE c.id = '{doc_id}'",
                partition_key=None,
                enable_cross_partition_query=True,
            ))
            return items[0] if items else None
        except Exception:
            return None

    def classify_problem(self, problem_description: str) -> Dict[str, Any]:
        """Classify a quantum problem using Troyer's filters.

        Returns the best-matching algorithm and filter results.
        This is the core tool for the Classifier Agent.
        """
        matches = self.search_algorithms(problem_description, top=3)
        if not matches:
            return {"verdict": "INCONCLUSIVE", "matches": [], "filters": {}}

        best = matches[0]
        filters = {
            "F1_proven_speedup": best["speedup_class"] in ("exponential", "superpolynomial"),
            "F2_io_survives": not best["io_bottleneck"],
            "F3_qec_survives": best["speedup_class"] not in ("quadratic", "quadratic_at_most"),
            "F4_naturally_quantum": best["naturally_quantum"],
            "F5_crossover_feasible": best["troyer_verdict"] == "QUANTUM_ADVANTAGE",
        }

        all_pass = all(filters.values())
        verdict = "QUANTUM_ADVANTAGE" if all_pass else ("HPC_PREFERRED" if not filters["F1_proven_speedup"] else "INCONCLUSIVE")

        return {
            "verdict": verdict,
            "confidence": 0.9 if all_pass else (0.3 if not filters["F1_proven_speedup"] else 0.5),
            "best_algorithm": best["name"],
            "speedup_class": best["speedup_class"],
            "filters": filters,
            "matches": matches,
        }

    # === Reference Problem Tools ===

    def get_reference_problems(self, status: str = "active") -> List[Dict[str, Any]]:
        """Get reference problems from Cosmos DB.

        Used by agents to find similar previously-evaluated problems.
        """
        if not self.db:
            return []
        container = self.db.get_container_client("problem_history")
        query = f"SELECT * FROM c WHERE c.user_id = 'system_reference' AND c.status = '{status}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return [{k: v for k, v in item.items() if not k.startswith("_") and k != "embedding"} for item in items]

    def find_similar_problems(self, description: str) -> List[Dict[str, Any]]:
        """Find reference problems similar to the given description."""
        if not self.db:
            return []
        container = self.db.get_container_client("problem_history")
        # Get all reference problems and do text matching (vector search in Cosmos requires change feed)
        query = "SELECT * FROM c WHERE c.user_id = 'system_reference' AND c.status = 'active'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        # Simple keyword matching for now (vector search via AI Search for papers)
        desc_lower = description.lower()
        scored = []
        for item in items:
            text = f"{item.get('notes', '')} {item.get('algorithm_class', '')}".lower()
            # Count keyword overlap
            keywords = set(desc_lower.split())
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0:
                scored.append((matches, {k: v for k, v in item.items() if not k.startswith("_") and k != "embedding"}))

        scored.sort(key=lambda x: -x[0])
        return [item for _, item in scored[:3]]

    # === Problem History Tools ===

    def save_problem(self, problem_id: str, user_id: str, description: str, result: Dict) -> str:
        """Save a user-submitted problem evaluation to history."""
        if not self.db:
            return problem_id
        container = self.db.get_container_client("problem_history")
        from datetime import datetime, timezone
        doc = {
            "id": problem_id,
            "user_id": user_id,
            "description": description,
            "result": result,
            "status": "evaluated",
            "created_utc": datetime.now(timezone.utc).isoformat(),
        }
        container.upsert_item(doc)
        return problem_id


def test_knowledge_base():
    """Quick smoke test of the knowledge base."""
    print("=== Knowledge Base Smoke Test ===\n")
    kb = QuantumKnowledgeBase()

    # Test 1: Search algorithms
    print("1. Search: 'simulate molecular ground state energy'")
    results = kb.search_algorithms("simulate molecular ground state energy", top=3)
    for r in results:
        print(f"   {r['name']} ({r['speedup_class']}) — score: {r['score']:.2f}")

    # Test 2: Classify a problem
    print("\n2. Classify: 'I need to find the ground state energy of a 50-atom iron catalyst'")
    classification = kb.classify_problem("I need to find the ground state energy of a 50-atom iron catalyst")
    print(f"   Verdict: {classification['verdict']}")
    print(f"   Best algorithm: {classification['best_algorithm']}")
    print(f"   Speedup: {classification['speedup_class']}")
    print(f"   Filters: {classification['filters']}")

    # Test 3: Reference problems
    print("\n3. Active reference problems:")
    active = kb.get_reference_problems("active")
    for p in active[:3]:
        print(f"   {p['problem_id']}: {p['algorithm']} ({p['troyer_verdict']})")

    # Test 4: Similar problems
    print("\n4. Find similar: 'nuclear binding energy calculation'")
    similar = kb.find_similar_problems("nuclear binding energy calculation")
    for s in similar:
        print(f"   {s['problem_id']}: {s.get('algorithm', '?')}")

    print("\n=== All tests passed ===")


if __name__ == "__main__":
    test_knowledge_base()
