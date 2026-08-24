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
import logging
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any, Optional

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

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
        self._papers_search_client = None
        self.last_search_mode = "uninitialised"

        # AI Search  use key if available, otherwise Entra ID
        try:
            search_key = os.environ.get("SEARCH_ADMIN_KEY")
            search_cred = AzureKeyCredential(search_key) if search_key else self.credential
            self.search_client = SearchClient(
                endpoint=SEARCH_ENDPOINT,
                index_name="quantum-algorithms",
                credential=search_cred,
            )
        except Exception as exc:
            logger.warning(
                "AI Search client could not be created, algorithm search will return "
                "nothing: %s: %s", type(exc).__name__, str(exc)[:200]
            )

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

        Falls back to keyword-only search if the vector query fails, and warns when
        it does. The fallback is measurably worse: for "factor a 2048-bit RSA integer"
        it ranks Nonlinear Differential Equations above Shor's Algorithm, so a silent
        downgrade would corrupt verdicts with no visible symptom.
        """
        if not self.search_client:
            return []

        select = [
            "name", "category", "speedup_class", "content",
            "troyer_verdict", "io_bottleneck", "naturally_quantum",
        ]

        try:
            embedding = self._embed(query)
            from azure.search.documents.models import VectorizedQuery
            results = self.search_client.search(
                search_text=query,
                vector_queries=[VectorizedQuery(vector=embedding, k_nearest_neighbors=top, fields="embedding")],
                top=top,
                select=select,
            )
            self.last_search_mode = "hybrid"
        except Exception as exc:
            self.last_search_mode = "keyword-fallback"
            logger.warning(
                "Vector search failed, falling back to keyword-only ranking, "
                "which is significantly less accurate: %s: %s",
                type(exc).__name__, str(exc)[:200],
            )
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=select,
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

    # === Scientific Paper Tools ===

    def search_papers(self, query: str, top: int = 3) -> List[Dict[str, Any]]:
        """Hybrid search over the ingested arXiv papers. Recent work only.

        This corpus cannot be used as evidence for a verdict, and callers must not
        treat it that way. Every document in it came from an arXiv quant-ph sweep, so
        it holds quantum papers and nothing else, and it will therefore return
        confident quantum-flavoured support for any question at all - including the
        ones whose correct answer is "do not use a quantum computer".

        Re-measured 2026-08-24 over the five demo prompts, after the Zoo references
        landed: portfolio optimisation still tops out at 0.0323 and image classification
        at 0.0323, both of which must be declined, while FeMoco - which must be accepted -
        scores 0.0290. Score still runs against correctness, so a relevance threshold
        cannot separate them; only keeping this out of the decision path can. Ingesting
        451 curated references did not shift this, which is the point: the imbalance is
        in what the corpus is, not in how much of it there is.

        The coverage gap is closed. Reiher et al. arXiv:1605.03590 for FeMoco and Shor
        quant-ph/9508027 for factoring are both present now.

        What the corpus mostly cannot do is state a speedup. Measured across all 2,239
        documents by tooling/measure_corpus_decidability.py, only 4.6% carry a
        classifiable speedup claim - 13.5% of the curated Zoo references against 2.3% of
        the daily arXiv sweep. Over these five prompts retrieval returned 25 papers and
        none of them were decidable, which is what a 2.3% rate predicts.

        Returns [] on any failure. A missing paper list must degrade the answer, never
        break it.
        """
        client = self._papers_client()
        if not client:
            return []

        select = ["title", "arxiv_id", "abstract", "published", "authors", "category"]
        try:
            embedding = self._embed(query)
            from azure.search.documents.models import VectorizedQuery
            results = client.search(
                search_text=query,
                vector_queries=[
                    VectorizedQuery(vector=embedding, k_nearest_neighbors=top, fields="embedding")
                ],
                top=top,
                select=select,
            )
        except Exception as exc:
            logger.warning(
                "Paper search failed, continuing without recent-work context: %s: %s",
                type(exc).__name__, str(exc)[:200],
            )
            return []

        return [
            {
                "title": r["title"],
                "arxiv_id": r["arxiv_id"],
                "published": (r.get("published") or "")[:10],
                "authors": r.get("authors", ""),
                # The index stores abstract[:2000]; this second cut keeps the recent-work
                # block short in the prompt. Checked 2026-08-24 that it costs nothing
                # downstream: classifying the same 25 retrieved papers at 400 characters
                # and at full stored length decided on none of them either way.
                "abstract": (r.get("abstract") or "")[:400],
                "score": r["@search.score"],
            }
            for r in results
        ]

    def _papers_client(self) -> Optional[SearchClient]:
        """Lazily build the papers client so it costs nothing when the flag is off."""
        if self._papers_search_client is not None:
            return self._papers_search_client
        try:
            search_key = os.environ.get("SEARCH_ADMIN_KEY")
            search_cred = AzureKeyCredential(search_key) if search_key else self.credential
            self._papers_search_client = SearchClient(
                endpoint=SEARCH_ENDPOINT,
                index_name="quantum-papers",
                credential=search_cred,
            )
        except Exception as exc:
            logger.warning(
                "AI Search papers client could not be created, paper search will "
                "return nothing: %s: %s", type(exc).__name__, str(exc)[:200]
            )
            return None
        return self._papers_search_client

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
