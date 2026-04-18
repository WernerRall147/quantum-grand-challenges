"""Quantum Advantage Evaluator — Orchestrator Agent API.

Accepts a problem description, runs it through the evaluation pipeline:
1. Classify via knowledge base (Troyer filters)
2. Generate detailed assessment via GPT-5.4-mini/model-router
3. Return structured verdict

Can be called from the website chat interface or CLI.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from knowledge.search.kb_client import QuantumKnowledgeBase

# Config
OPENAI_ENDPOINT = os.environ.get("QGC_OPENAI_ENDPOINT", "https://qgc-openai.openai.azure.com/")
CHAT_DEPLOYMENT = os.environ.get("QGC_CHAT_DEPLOYMENT", "gpt-54-mini")
ROUTER_ENDPOINT = os.environ.get("QGC_ROUTER_ENDPOINT", "https://admin-mo1q7owo-eastus2.cognitiveservices.azure.com/")
ROUTER_DEPLOYMENT = os.environ.get("QGC_ROUTER_DEPLOYMENT", "model-router")
# Toggle model-router (cost-optimized): set QGC_USE_ROUTER=1 once RBAC has propagated.
USE_ROUTER = os.environ.get("QGC_USE_ROUTER", "0") == "1"

SYSTEM_PROMPT = """You are the Quantum Advantage Evaluator — an expert AI assistant that helps scientists determine whether their computational problem is better solved on a quantum computer or Azure HPC.

You have access to a knowledge base of quantum algorithms with Troyer utility-scale classifications. For each user problem, you must:

1. CLASSIFY the problem by matching it to known quantum algorithms
2. APPLY Troyer's 5 utility-scale filters:
   - F1: Is there a mathematically proven quantum speedup?
   - F2: Does the speedup survive data loading (I/O) costs?
   - F3: Does the speedup survive quantum error correction overhead?
   - F4: Is the problem naturally quantum (Feynman criterion)?
   - F5: Is there a realistic crossover point where quantum wins?
3. COMPARE with Azure HPC alternatives honestly
4. PROVIDE a clear verdict with confidence level

HONESTY REQUIREMENTS:
- NEVER overstate quantum advantage
- If QAOA or VQE is the only quantum approach → warn: "at most quadratic or no proven advantage"
- Flag I/O bottlenecks (data loading negates speedup for many problems)
- Flag oracle costs (millions of T-gates for real implementations)
- Always mention the best classical/HPC alternative
- Reference specific algorithms and papers for all claims

OUTPUT FORMAT (JSON):
{
  "verdict": "QUANTUM_ADVANTAGE" | "HPC_PREFERRED" | "INCONCLUSIVE",
  "confidence": 0.0-1.0,
  "advantage_class": "exponential" | "superpolynomial" | "quadratic" | "none",
  "recommended_algorithm": "QPE / Shor / Grover / QAOA / VQE / HHL / ...",
  "troyer_filters": {
    "F1_proven_speedup": true/false,
    "F2_io_survives": true/false,
    "F3_qec_survives": true/false,
    "F4_naturally_quantum": true/false,
    "F5_crossover_feasible": true/false
  },
  "red_flags": ["list of concerns"],
  "hpc_alternative": "description of what Azure HPC can do today",
  "explanation": "2-3 paragraph honest assessment",
  "similar_problems": ["reference problem IDs"],
  "references": ["arxiv IDs or algorithm names"]
}
"""


class QuantumEvaluator:
    """Orchestrator that evaluates quantum problems using KB + LLM."""

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.kb = QuantumKnowledgeBase()

    def _get_chat_client(self):
        """Get OpenAI chat client with fresh token.

        When QGC_USE_ROUTER=1, returns a client pointing at the model-router
        deployment (cost-optimized, auto-selects best model for the prompt).
        Otherwise falls back to the direct gpt-5.4-mini deployment.
        """
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        endpoint = ROUTER_ENDPOINT if USE_ROUTER else OPENAI_ENDPOINT
        return AzureOpenAI(
            azure_ad_token=token.token,
            azure_endpoint=endpoint,
            api_version="2024-10-21",
        )

    def _get_deployment(self) -> str:
        return ROUTER_DEPLOYMENT if USE_ROUTER else CHAT_DEPLOYMENT

    def evaluate(self, problem_description: str) -> Dict[str, Any]:
        """Full evaluation pipeline for a quantum problem."""

        # Step 1: KB classification (fast, no LLM needed)
        kb_result = self.kb.classify_problem(problem_description)

        # Step 2: Find similar reference problems
        similar = self.kb.find_similar_problems(problem_description)
        similar_ids = [s.get("problem_id", "?") for s in similar]

        # Step 3: Build context for LLM
        kb_context = json.dumps({
            "kb_classification": {
                "verdict": kb_result["verdict"],
                "best_algorithm": kb_result.get("best_algorithm", "Unknown"),
                "speedup_class": kb_result.get("speedup_class", "unknown"),
                "troyer_filters": kb_result.get("filters", {}),
            },
            "similar_reference_problems": similar_ids,
            "algorithm_matches": [
                {"name": m["name"], "speedup": m["speedup_class"], "verdict": m["troyer_verdict"]}
                for m in kb_result.get("matches", [])
            ],
        }, indent=2)

        # Step 4: LLM generates detailed assessment
        client = self._get_chat_client()
        deployment = self._get_deployment()
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""Evaluate this quantum computing problem:

PROBLEM: {problem_description}

KNOWLEDGE BASE RESULTS:
{kb_context}

Provide your evaluation as JSON following the output format specified in your instructions. Be honest about limitations."""},
            ],
            max_completion_tokens=1000,
            response_format={"type": "json_object"},
        )

        # Step 5: Parse LLM response
        try:
            llm_result = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, IndexError):
            llm_result = {
                "verdict": kb_result["verdict"],
                "confidence": kb_result.get("confidence", 0.5),
                "explanation": response.choices[0].message.content if response.choices else "Error parsing response",
            }

        # Step 6: Merge KB + LLM results
        result = {
            "problem": problem_description,
            "verdict": llm_result.get("verdict", kb_result["verdict"]),
            "confidence": llm_result.get("confidence", kb_result.get("confidence", 0.5)),
            "advantage_class": llm_result.get("advantage_class", kb_result.get("speedup_class", "unknown")),
            "recommended_algorithm": llm_result.get("recommended_algorithm", kb_result.get("best_algorithm", "Unknown")),
            "troyer_filters": llm_result.get("troyer_filters", kb_result.get("filters", {})),
            "red_flags": llm_result.get("red_flags", []),
            "hpc_alternative": llm_result.get("hpc_alternative", ""),
            "explanation": llm_result.get("explanation", ""),
            "similar_problems": llm_result.get("similar_problems", similar_ids),
            "references": llm_result.get("references", []),
            "evaluated_utc": datetime.now(timezone.utc).isoformat(),
            "model_used": response.model if response else CHAT_DEPLOYMENT,
            "tokens_used": response.usage.total_tokens if response and response.usage else 0,
        }

        return result


def main():
    """CLI interface for the evaluator."""
    if len(sys.argv) > 1:
        problem = " ".join(sys.argv[1:])
    else:
        problem = "I need to simulate the ground state energy of a 100-atom iron oxide catalyst for hydrogen fuel cell optimization"

    print(f"Evaluating: {problem}\n")
    print("=" * 60)

    evaluator = QuantumEvaluator()
    result = evaluator.evaluate(problem)

    # Pretty print
    verdict_emoji = {"QUANTUM_ADVANTAGE": "✅", "HPC_PREFERRED": "💻", "INCONCLUSIVE": "🔍"}.get(result["verdict"], "❓")
    print(f"\n{verdict_emoji} Verdict: {result['verdict']}")
    print(f"📊 Confidence: {result['confidence']:.0%}")
    print(f"⚡ Advantage class: {result['advantage_class']}")
    print(f"🔧 Algorithm: {result['recommended_algorithm']}")

    print(f"\n🔬 Troyer Filters:")
    for k, v in result.get("troyer_filters", {}).items():
        icon = "✅" if v else "❌"
        print(f"  {icon} {k}")

    if result.get("red_flags"):
        print(f"\n🚩 Red Flags:")
        for flag in result["red_flags"]:
            print(f"  - {flag}")

    if result.get("hpc_alternative"):
        print(f"\n💻 HPC Alternative: {result['hpc_alternative']}")

    if result.get("explanation"):
        print(f"\n📝 Assessment:\n{result['explanation']}")

    print(f"\n🤖 Model: {result.get('model_used', '?')}, Tokens: {result.get('tokens_used', 0)}")

    # Save to file
    out_path = Path("agents/evaluations")
    out_path.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_path / f"eval_{ts}.json"
    out_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\n💾 Saved: {out_file}")


if __name__ == "__main__":
    main()
