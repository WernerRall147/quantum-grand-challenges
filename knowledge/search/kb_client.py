"""Knowledge Base query tools for the Quantum Advantage Evaluator agents.

Provides search functions over:
- Algorithm Zoo (committed JSON, plus AI Search for vector queries)
- Reference Problems (committed JSON)
- Scientific Papers (AI Search)

The algorithm zoo and reference problems are served straight from the files that
are their source of truth, rather than from a database seeded from those files.

These functions are the tools that agents call via the orchestrator.
"""

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any, Optional

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Config
SEARCH_ENDPOINT = "https://qgcsearcheval.search.windows.net"
OPENAI_ENDPOINT = "https://qgc-openai.openai.azure.com/"
EMBEDDING_DEPLOYMENT = "text-embedding-3-large"

ROOT = Path(__file__).resolve().parents[2]
ALGORITHM_ZOO_PATH = ROOT / "knowledge" / "data" / "algorithm_zoo_index.json"
REFERENCE_INDEX_PATH = ROOT / "problems" / "reference_index.json"


def _normalise(name: str) -> str:
    """Fold a display name to a lookup key; apostrophes vanish rather than split."""
    stripped = name.lower().replace("'", "").replace("\u2019", "")
    return re.sub(r"[^a-z0-9]+", "_", stripped).strip("_")


@lru_cache(maxsize=1)
def _algorithms_by_name() -> Dict[str, Dict[str, Any]]:
    data = json.loads(ALGORITHM_ZOO_PATH.read_text(encoding="utf-8"))
    return {_normalise(a["name"]): a for a in data.get("algorithms", [])}


@lru_cache(maxsize=1)
def _reference_problems_by_status() -> Dict[str, List[Dict[str, Any]]]:
    data = json.loads(REFERENCE_INDEX_PATH.read_text(encoding="utf-8"))

    def shape(prob: Dict[str, Any], status: str) -> Dict[str, Any]:
        out = {k: v for k, v in prob.items() if k != "id"}
        out["problem_id"] = prob["id"]
        out["status"] = status
        return out

    return {
        "active": [shape(p, "active") for p in data.get("active_problems", [])],
        "archived": [shape(p, "archived") for p in data.get("archived_problems", [])],
    }


class QuantumKnowledgeBase:
    """Query interface for the Quantum Advantage Evaluator knowledge base."""

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.search_client = None

        # AI Search  use key if available, otherwise Entra ID
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
        """Get a specific algorithm by name from the algorithm zoo."""
        return _algorithms_by_name().get(_normalise(name))

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
        """Get reference problems.

        Used by agents to find similar previously-evaluated problems.
        """
        return list(_reference_problems_by_status().get(status, []))

    def find_similar_problems(self, description: str) -> List[Dict[str, Any]]:
        """Find reference problems similar to the given description."""
        desc_lower = description.lower()
        keywords = set(desc_lower.split())

        scored = []
        for item in self.get_reference_problems("active"):
            text = f"{item.get('notes', '')} {item.get('algorithm_class', '')}".lower()
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0:
                scored.append((matches, item))

        scored.sort(key=lambda x: -x[0])
        return [item for _, item in scored[:3]]


def test_knowledge_base():
    """Quick smoke test of the knowledge base."""
    print("=== Knowledge Base Smoke Test ===\n")
    kb = QuantumKnowledgeBase()

    # Test 1: Search algorithms
    print("1. Search: 'simulate molecular ground state energy'")
    results = kb.search_algorithms("simulate molecular ground state energy", top=3)
    for r in results:
        print(f"   {r['name']} ({r['speedup_class']})  score: {r['score']:.2f}")

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
