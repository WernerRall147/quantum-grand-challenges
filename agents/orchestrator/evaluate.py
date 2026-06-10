"""Quantum Advantage Evaluator  Orchestrator Agent API.

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
# Default to the Azure AI Foundry model-router (cost-optimized, auto-failover).
# RBAC is in place on the router for all evaluator identities; set QGC_USE_ROUTER=0
# to fall back to the direct CHAT_DEPLOYMENT on qgc-openai.
USE_ROUTER = os.environ.get("QGC_USE_ROUTER", "1") == "1"

# Output budget for the assessment. The model-router selects gpt-5.4, a reasoning
# model whose internal reasoning tokens count against this budget, so it must
# cover BOTH the reasoning and the full JSON answer. The old value of 1000 was
# exhausted by reasoning alone, which silently truncated the explanation and
# references. Tunable via QGC_MAX_COMPLETION_TOKENS.
MAX_COMPLETION_TOKENS = int(os.environ.get("QGC_MAX_COMPLETION_TOKENS", "4000"))

SYSTEM_PROMPT = """You are the Quantum Advantage Evaluator  an expert AI assistant that helps scientists and engineers determine whether their computational problem is better solved on a quantum computer, classical AI/ML, or Azure HPC, and then guides them to build the right Azure workspace.

You have access to a knowledge base of quantum algorithms with Troyer utility-scale classifications. For each user problem, you must:

1. CLASSIFY the problem by matching it to known quantum algorithms
2. APPLY Troyer's 5 utility-scale filters:
   - F1: Is there a mathematically proven quantum speedup?
   - F2: Does the speedup survive data loading (I/O) costs?
   - F3: Does the speedup survive quantum error correction overhead?
   - F4: Is the problem naturally quantum (Feynman criterion)?
   - F5: Is there a realistic crossover point where quantum wins?
3. ASSESS DiVincenzo criteria for quantum recommendations:
   - Scalable physical qubits available for this problem size?
   - Initialization and state preparation feasible?
   - Coherence times sufficient for required circuit depth?
   - Universal gate set with acceptable fidelity?
   - Qubit-specific measurement without crosstalk?
4. COMPARE with Azure HPC and AI/ML alternatives honestly
5. RECOMMEND the best platform AND Azure workspace setup
6. PROVIDE a clear verdict with confidence level

PLATFORM RECOMMENDATION RULES:
- If all 5 Troyer filters pass AND DiVincenzo criteria are met/partial → recommend QUANTUM with specific algorithm + Azure Quantum workspace setup guidance
- If the problem involves pattern recognition, classification, prediction, NLP, computer vision, generative modeling, or optimization over unstructured data → recommend AI_ML with specific approach (e.g., "GPT-5 fine-tuning", "Azure ML + PyTorch", "Azure AI Foundry agents", "transformer architecture") + Azure AI Foundry workspace setup
- If the problem involves large-scale numerical simulation, fluid dynamics, molecular dynamics, finite element analysis, linear algebra at scale, or embarrassingly parallel computation → recommend HPC with specific Azure HPC stack (e.g., "Azure HBv4 + MPI", "Azure NDv6 GPU cluster + CUDA", "Azure CycleCloud + SLURM") + workspace sizing guidance
- For hybrid approaches (e.g., quantum-classical variational), be specific about what runs where

WORKSPACE GUIDANCE:
- QUANTUM: Azure Quantum workspace setup, target hardware selection (Quantinuum, IonQ, Rigetti), resource estimation parameters, QEC code selection (reference errorcorrectionzoo.org for code taxonomy  surface, color, QLDPC codes)
- AI_ML: Azure AI Foundry project, model selection, compute sizing, training pipeline
- HPC: Azure CycleCloud cluster, VM family selection, SLURM configuration, MPI/GPU framework

INDUSTRY CONTEXT:
- Google is pursuing dual-modality QC (superconducting + neutral atoms as of Mar 2026)
- Google set a 2029 PQC migration timeline, implying CRQC expected end of decade
- For factorization problems, note that PQC transition is already underway (NIST standards)
- DiVincenzo gaps (limited qubits, short coherence, high error rates) remain the primary barrier to utility-scale quantum advantage

HONESTY REQUIREMENTS:
- NEVER overstate quantum advantage
- If QAOA or VQE is the only quantum approach → warn: "at most quadratic or no proven advantage"
- Flag I/O bottlenecks (data loading negates speedup for many problems)
- Flag oracle costs (millions of T-gates for real implementations)
- Flag DiVincenzo gaps that make quantum infeasible today
- Always mention the best classical/HPC/AI alternative
- Reference specific algorithms, papers, and error correction codes for all claims

OUTPUT FORMAT (JSON):
{
  "verdict": "QUANTUM_ADVANTAGE" | "HPC_PREFERRED" | "AI_ML_PREFERRED" | "INCONCLUSIVE",
  "confidence": 0.0-1.0,
  "advantage_class": "exponential" | "superpolynomial" | "quadratic" | "none",
  "recommended_algorithm": "QPE / Shor / Grover / QAOA / VQE / HHL / ...",
  "recommended_platform": "QUANTUM" | "AI_ML" | "HPC" | "HYBRID",
  "platform_reason": "2-3 sentences explaining WHY this specific compute type (quantum, AI/ML, or HPC) is the best-tuned fit for THIS problem, grounded in the problem's structure (e.g. a naturally-quantum Hamiltonian, an I/O-bound dataset, an embarrassingly-parallel simulation, or a pattern-recognition task)",
  "workspace_guidance": {
    "platform": "Azure Quantum | Azure AI Foundry | Azure CycleCloud",
    "setup_steps": ["Step 1...", "Step 2..."],
    "recommended_resources": "Specific VM/hardware/model recommendations"
  },
  "troyer_filters": {
    "F1_proven_speedup": true/false,
    "F2_io_survives": true/false,
    "F3_qec_survives": true/false,
    "F4_naturally_quantum": true/false,
    "F5_crossover_feasible": true/false
  },
  "divincenzo_assessment": {
    "scalable_qubits": "met | partial | not_yet",
    "initialization": "met | partial | not_yet",
    "coherence": "met | partial | not_yet",
    "universal_gates": "met | partial | not_yet",
    "measurement": "met | partial | not_yet",
    "summary": "1-sentence hardware readiness assessment"
  },
  "red_flags": ["list of concerns"],
  "hpc_alternative": "description of what Azure HPC can do today",
  "ai_alternative": "description of what AI/ML can do today (e.g., foundation models, Azure AI services, ML frameworks)",
  "explanation": "2-3 paragraph honest assessment that walks through the REASONING: why the recommended compute type wins for this problem, how the quantum vs AI/ML vs HPC trade-offs compare, and what would change the verdict. Cite the specific evidence behind each claim.",
  "similar_problems": ["reference problem IDs"],
  "references": ["at least 2 concrete sources backing the recommendation: arXiv IDs, named algorithms/theorems, errorcorrectionzoo.org codes, or learn.microsoft.com pages"],
  "error_correction_codes": ["relevant QEC codes from errorcorrectionzoo.org if quantum recommended"]
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

        # Step 1b: Deterministic platform routing
        from agents.classifier.platform_router import route_platform
        kb_matches = kb_result.get("matches", [])
        search_score = kb_matches[0].get("score", 0) if kb_matches else 0
        routing = route_platform(problem_description, kb_matches, search_score)

        # Step 2: Find similar reference problems
        similar = self.kb.find_similar_problems(problem_description)
        similar_ids = [s.get("problem_id", "?") for s in similar]

        # Step 3: Build context for LLM
        kb_context = json.dumps({
            "deterministic_routing": {
                "platform": routing["platform"],
                "verdict": routing["verdict"],
                "confidence": routing["confidence"],
                "reason": routing["reason"],
                "keyword_scores": routing["evidence"]["keyword_scores"],
                "troyer_filters": routing["evidence"]["troyer_filters"],
            },
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

DETERMINISTIC PRE-CLASSIFICATION:
Platform: {routing['platform']} | Verdict: {routing['verdict']} | Confidence: {routing['confidence']}
Reason: {routing['reason']}
Troyer filters (from KB data): {json.dumps(routing['evidence']['troyer_filters'])}
Domain keyword scores: {json.dumps(routing['evidence']['keyword_scores'])}

IMPORTANT: The deterministic routing above is computed from the algorithm database and keyword analysis.
You MUST agree with the verdict unless you have a specific, well-reasoned scientific argument to override it.
If the routing says AI_ML_PREFERRED or HPC_PREFERRED, do NOT recommend quantum unless you can cite a specific
algorithm with proven superpolynomial speedup for this exact problem class.

KNOWLEDGE BASE RESULTS:
{kb_context}

Provide your evaluation as JSON following the output format specified in your instructions. Be honest about limitations."""},
            ],
            max_completion_tokens=MAX_COMPLETION_TOKENS,
            response_format={"type": "json_object"},
        )

        # Step 5: Parse LLM response
        choice = response.choices[0] if response.choices else None
        raw_content = (choice.message.content if choice else "") or ""
        finish_reason = getattr(choice, "finish_reason", None)
        try:
            llm_result = json.loads(raw_content)
        except (json.JSONDecodeError, TypeError):
            # An empty or truncated (finish_reason == "length") completion lands
            # here. Keep the deterministic verdict and surface whatever text we
            # got so the explanation is not silently dropped.
            truncated_note = (
                "The assessment was cut off before the model finished writing it. "
                "Raise QGC_MAX_COMPLETION_TOKENS to get the full explanation and sources."
            )
            llm_result = {
                "verdict": kb_result["verdict"],
                "confidence": kb_result.get("confidence", 0.5),
                "explanation": raw_content or (truncated_note if finish_reason == "length" else "Error parsing assessment response."),
            }

        # Step 6: Merge KB + routing + LLM results
        # Deterministic routing provides troyer_filters and platform;
        # LLM provides explanation, red_flags, and alternatives.
        deterministic_filters = routing["evidence"].get("troyer_filters", {})

        # Step 7: Compute cost-advantage analysis (Troyer Part 6 placeholder).
        # Heuristic order-of-magnitude estimates from agents/classifier/cost_model.py.
        cost_analysis = self._compute_cost_analysis(
            platform=llm_result.get("recommended_platform", routing["platform"]),
            algorithm=llm_result.get("recommended_algorithm", kb_result.get("best_algorithm", "")),
            kb_match=(kb_result.get("matches") or [{}])[0],
        )

        result = {
            "problem": problem_description,
            "verdict": llm_result.get("verdict", routing["verdict"]),
            "confidence": llm_result.get("confidence", routing["confidence"]),
            "advantage_class": llm_result.get("advantage_class", kb_result.get("speedup_class", "unknown")),
            "recommended_algorithm": llm_result.get("recommended_algorithm", kb_result.get("best_algorithm", "Unknown")),
            "recommended_platform": llm_result.get("recommended_platform", routing["platform"]),
            "platform_reason": llm_result.get("platform_reason", routing["reason"]),
            "troyer_filters": deterministic_filters if deterministic_filters else llm_result.get("troyer_filters", {}),
            "red_flags": llm_result.get("red_flags", []),
            "hpc_alternative": llm_result.get("hpc_alternative", ""),
            "ai_alternative": llm_result.get("ai_alternative", ""),
            "explanation": llm_result.get("explanation", ""),
            "similar_problems": llm_result.get("similar_problems", similar_ids),
            "references": llm_result.get("references", []),
            "cost_analysis": cost_analysis,
            "routing_evidence": routing["evidence"],
            "evaluated_utc": datetime.now(timezone.utc).isoformat(),
            "model_used": response.model if response else CHAT_DEPLOYMENT,
            "tokens_used": response.usage.total_tokens if response and response.usage else 0,
        }

        return result

    @staticmethod
    def _compute_cost_analysis(platform: str, algorithm: str, kb_match: Dict[str, Any]) -> Dict[str, Any]:
        """Compute an order-of-magnitude cost comparison across Quantum, AI/ML, and HPC.

        Uses live Azure list pricing (Retail Prices API for compute, official
        provider formulas for quantum). Quantum per-shot cost is grounded to the
        device's real qubit width so fault-tolerant projections do not produce
        physically impossible headline figures.
        """
        try:
            from agents.classifier.cost_model import (
                estimate_quantum_cost,
                estimate_hpc_cost,
                estimate_aml_cost,
                cost_advantage_ratio,
                quantum_hardware_feasibility,
                COST_MODEL_STATUS,
                TROYER_PART_6_STATUS,
            )
        except ImportError:
            return {"status": "cost_model_unavailable"}

        # Conservative default shot count. The provider per-shot formulas scale
        # linearly with shots, so a sane default keeps estimates realistic rather
        # than alarming. 256 shots is a typical sampling run.
        default_shots = 256

        # Pull resource estimate hints from the matched KB algorithm record.
        # Typical fields: physical_qubits, runtime_ns, t_count.
        physical_qubits = int(kb_match.get("physical_qubits") or 100_000)
        runtime_ns = int(kb_match.get("runtime_ns") or 10_000_000_000)  # 10 s default

        # Quantum-only path: pick a representative target by algorithm class.
        # Quantinuum H2 for QPE/Shor (chemistry/factoring). IonQ Aria for variational.
        target = "azure_quantum_quantinuum_h2"
        if algorithm and any(a in algorithm.upper() for a in ("VQE", "QAOA", "SWAP")):
            target = "azure_quantum_ionq_aria"

        # Ground the per-shot cost to what the device can actually run. A
        # fault-tolerant estimate of 10^5-10^6 physical qubits and a very deep
        # circuit cannot be submitted to a 56-qubit device, so price a
        # hardware-grounded representative circuit (width and depth capped) and
        # report feasibility separately.
        derived_depth = max(1, runtime_ns // 1_000_000)  # ~1 layer per microsecond
        feasibility = quantum_hardware_feasibility(
            physical_qubits, target_platform=target, logical_depth=derived_depth
        )
        priced_qubits = feasibility["priced_circuit_qubits"]
        priced_depth = feasibility["priced_circuit_depth"]

        quantum = estimate_quantum_cost(
            physical_qubits=priced_qubits,
            runtime_ns=runtime_ns,
            target_platform=target,
            shots=default_shots,
            logical_depth=priced_depth,
        )
        quantum["feasible_today"] = feasibility["feasible_today"]
        quantum["feasibility_note"] = feasibility["note"]

        # Classical alternatives share the same wall-time assumption: an HPC/AI
        # alternative would solve the problem in O(seconds-to-minutes) on a
        # cluster (an over-optimistic comparison favouring classical compute).
        compute_hours = max(0.1, runtime_ns / 3.6e12)  # ns -> hours
        hpc = estimate_hpc_cost(compute_hours=compute_hours, platform="azure_hpc_nd96amsr_a100")

        # AI/ML alternative on Azure Machine Learning. Size the instance by the
        # routed platform: AI/ML problems default to a GPU instance, others to a
        # lighter one for an order-of-magnitude reference point.
        aml_instance = "large" if (platform or "").upper() == "AI_ML" else "medium"
        ai_ml = estimate_aml_cost(compute_hours=compute_hours, instance_size=aml_instance)

        ratio = cost_advantage_ratio(quantum, hpc)

        # Pick the cheapest option that is actually runnable today.
        candidates = [
            ("quantum", quantum.get("estimated_cost_usd") if feasibility["feasible_today"] else None),
            ("ai_ml", ai_ml.get("estimated_cost_usd")),
            ("hpc", hpc.get("estimated_cost_usd")),
        ]
        priced = [(name, cost) for name, cost in candidates if isinstance(cost, (int, float))]
        cheapest = min(priced, key=lambda c: c[1])[0] if priced else None

        return {
            "status": COST_MODEL_STATUS,
            "troyer_part_6": TROYER_PART_6_STATUS,
            "recommended_quantum_target": target,
            "quantum_estimate": quantum,
            "ai_ml_estimate": ai_ml,
            "hpc_estimate": hpc,
            "comparison": ratio,
            "feasibility": feasibility,
            "cheapest_runnable": cheapest,
            "caveat": (
                "Order-of-magnitude estimate at Azure list pricing "
                f"({default_shots} shots, hardware-grounded). Quantum figures are "
                "capped to current device width; fault-tolerant hardware at the "
                "projected scale is not yet available. Validate with the Azure "
                "pricing API and the full Resource Estimator before budgeting."
            ),
        }


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
