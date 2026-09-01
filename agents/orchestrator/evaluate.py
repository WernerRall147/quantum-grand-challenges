"""Quantum Advantage Evaluator  Orchestrator Agent API.

Accepts a problem description, runs it through the evaluation pipeline:
1. Classify via knowledge base (Troyer filters)
2. Generate detailed assessment via GPT-5.4-mini/model-router
3. Return structured verdict

Can be called from the website chat interface or CLI.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from knowledge.search.kb_client import QuantumKnowledgeBase
from agents.orchestrator.instructions import SYSTEM_PROMPT
from agents.orchestrator.citations import partition_references
from agents.observability.trace import span

# Config
OPENAI_ENDPOINT = os.environ.get("QGC_OPENAI_ENDPOINT", "https://qgc-openai.openai.azure.com/")
CHAT_DEPLOYMENT = os.environ.get("QGC_CHAT_DEPLOYMENT", "gpt-54-mini")
ROUTER_ENDPOINT = os.environ.get("QGC_ROUTER_ENDPOINT", "https://admin-mo1q7owo-eastus2.cognitiveservices.azure.com/")
ROUTER_DEPLOYMENT = os.environ.get("QGC_ROUTER_DEPLOYMENT", "model-router")
# Default to the Azure AI Foundry model-router (cost-optimized, auto-failover).
# RBAC is in place on the router for all evaluator identities; set QGC_USE_ROUTER=0
# to fall back to the direct CHAT_DEPLOYMENT on qgc-openai.
USE_ROUTER = os.environ.get("QGC_USE_ROUTER", "1") == "1"

# Foundry Agent path (opt-in). When QGC_USE_AGENT=1 the evaluator runs through the
# Foundry agent "quantum-advantage-orchestrator" (model-router + Tools) in the
# qgc-eval-proj project via the Responses API, instead of a raw chat-completions
# call.
#
# Measured 2026-08-19 on the same five cases, model_seconds median: chat 28.3s
# (23.1-31.8), agent 51.9s (41.6-78.0). Slower on every case. Note the router
# picked a different model per path (luna vs terra), so this compares the two
# paths as configured, not agent plumbing overhead in isolation.
#
# Recommendation is chat: at n=22 the agent's only quality edge was references
# 22/22 vs 21/22, and since citations are verified at the source that edge no
# longer reaches the published output. 1.8x latency for one formatting case in 22
# is not a trade worth making, and on the website that is 52s of waiting instead
# of 28s.
#
# NOTE: this default is NOT authoritative. Container App qgc-eval-api sets
# QGC_USE_AGENT as an env var, which wins over this default. Since 2026-08-19 it is
# set to 0 (chat-completions, ~38s median against ~52s for the agent path). Change it
# with `az containerapp update -n qgc-eval-api -g qgc-evaluator --set-env-vars
# QGC_USE_AGENT=...`, not by editing this line.
USE_AGENT = os.environ.get("QGC_USE_AGENT", "0") == "1"

# Recent-arXiv context, off by default and deliberately so. The quantum-papers index
# is an arXiv quant-ph sweep, so every document in it is a quantum paper and retrieval
# argues for quantum on every question. Measured 2026-08-24 across the five demo
# prompts, its most confident hits were portfolio optimisation (0.0323) and image
# classification (0.0325) - the two that must be declined - while FeMoco, which must be
# accepted, scored 0.0242. A score threshold cannot separate those, so the corpus is
# kept out of the decision path entirely and passed to the model as labelled reading.
# Turn on with QGC_USE_PAPERS=1 only after re-running tooling/verify_demo_prompts.py.
USE_PAPERS = os.environ.get("QGC_USE_PAPERS", "0") == "1"
PROJECT_ENDPOINT = os.environ.get(
    "QGC_PROJECT_ENDPOINT",
    "https://admin-mo1q7owo-eastus2.services.ai.azure.com/api/projects/qgc-eval-proj",
)
AGENT_NAME = os.environ.get("QGC_AGENT_NAME", "quantum-advantage-orchestrator")

# Output budget for the assessment. The model-router selects gpt-5.4, a reasoning
# model whose internal reasoning tokens count against this budget, so it must
# cover BOTH the reasoning and the full JSON answer. The old value of 1000 was
# exhausted by reasoning alone, which silently truncated the explanation and
# references. Tunable via QGC_MAX_COMPLETION_TOKENS.
MAX_COMPLETION_TOKENS = int(os.environ.get("QGC_MAX_COMPLETION_TOKENS", "4000"))

# The client had no timeout, so a stalled model pinned the request indefinitely.
# The model-router selects a different model per prompt and they are not equally
# fast: a typical assessment returns in about 40s, but one selection was still
# running after eight minutes. Without a bound that holds an API worker open for
# the whole time. Tunable via QGC_REQUEST_TIMEOUT.
REQUEST_TIMEOUT = float(os.environ.get("QGC_REQUEST_TIMEOUT", "180"))

# Resolving citations puts network calls in the request path. That is a real cost,
# accepted because a fabricated source is worse than a slower answer. Off in tests,
# which must stay hermetic.
VERIFY_CITATIONS = os.environ.get("QGC_VERIFY_CITATIONS", "1") == "1"

# Retries multiply the timeout: the SDK default of 2 turns a 180s bound into a
# 540s worst case. Kept at 2 so transient 429s still recover, but exposed so a
# batch caller can drop it to 0 rather than wait out three stalls per case.
MAX_RETRIES = int(os.environ.get("QGC_MAX_RETRIES", "2"))


def parse_assessment(raw: str) -> Optional[dict]:
    """Read the model's JSON, tolerating fences and surrounding prose.

    The chat path pins response_format to json_object, but the agent path cannot,
    so the agent occasionally wraps its answer in a ```json fence or adds a
    sentence around it. A bare json.loads then fails on an answer that is
    perfectly good.
    """
    if not raw:
        return None

    candidates = [raw]

    text = raw.strip()
    if text.startswith("```"):
        candidates.append(re.sub(r"\s*```$", "", re.sub(r"^```(?:json)?\s*", "", text)))

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


class QuantumEvaluator:
    """Orchestrator that evaluates quantum problems using KB + LLM."""

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.kb = QuantumKnowledgeBase()
        # Populated by evaluate(). Read by agents/evaluations/score_narrative.py,
        # which needs the model's own JSON before the merge below overwrites it.
        self.last_diagnostics: Dict[str, Any] = {}

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
            timeout=REQUEST_TIMEOUT,
            max_retries=MAX_RETRIES,
        )

    def _get_deployment(self) -> str:
        return ROUTER_DEPLOYMENT if USE_ROUTER else CHAT_DEPLOYMENT

    def _evaluate_via_agent(self, user_message: str):
        """Run the evaluation through the Foundry agent (model-router + Tools).

        Uses the Responses API with an agent reference. The agent's own
        instructions are SYSTEM_PROMPT, so only the user message is sent here.
        Returns (text, finish_reason, model_used, tokens_used).
        """
        from azure.ai.projects import AIProjectClient

        project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=self.credential)
        client = project.get_openai_client()
        # The response format cannot be set here: the API rejects `text` with
        # "Not allowed when agent is specified". It lives on the agent definition
        # instead, applied by tooling/provision_foundry_agent.py.
        response = client.responses.create(
            input=user_message,
            extra_body={"agent_reference": {"type": "agent_reference", "name": AGENT_NAME}},
        )
        text = getattr(response, "output_text", None) or ""
        model_used = getattr(response, "model", None) or AGENT_NAME
        usage = getattr(response, "usage", None)
        tokens_used = getattr(usage, "total_tokens", 0) or 0
        return text, "stop", model_used, tokens_used

    @staticmethod
    def _recent_work_block(papers: List[Dict[str, Any]]) -> str:
        """Render recent arXiv hits in their own block, marked as not-evidence.

        Kept separate from KNOWLEDGE BASE RESULTS on purpose. The corpus only contains
        quantum papers, so it supports a quantum answer for anything, and merging it
        into the evidence block would invite the model to read it as corroboration.
        """
        if not papers:
            return ""
        lines = [
            "",
            "RECENT ARXIV WORK (context only - NOT evidence for the verdict):",
            "This index contains quantum papers exclusively, so it returns quantum-adjacent",
            "results for every query, including problems that should not use quantum. It is",
            "also recent-only and does not contain the foundational references. Cite these as",
            "current related work if genuinely relevant. Do not treat them as support for the",
            "verdict, and do not let them displace canonical citations.",
        ]
        for paper in papers:
            lines.append(
                f"- {paper['title']} (arXiv:{paper['arxiv_id']}, {paper['published']})"
            )
        lines.append("")
        return "\n".join(lines)

    def evaluate(self, problem_description: str) -> Dict[str, Any]:
        """Full evaluation pipeline for a quantum problem."""

        # Step 1: KB classification (fast, no LLM needed)
        with span("1. kb.classify_problem", source="Azure AI Search over the curated corpus") as s:
            kb_result = self.kb.classify_problem(problem_description)
            _matches = kb_result.get("matches", [])
            s.set(
                match_count=len(_matches),
                top_match=(_matches[0].get("name") if _matches else None),
                top_score=(_matches[0].get("score") if _matches else None),
                kb_verdict=kb_result.get("verdict"),
                model_called=False,
            )

        # Step 1b: Deterministic platform routing
        from agents.classifier.platform_router import is_platform_refinement, route_platform
        kb_matches = kb_result.get("matches", [])
        search_score = kb_matches[0].get("score", 0) if kb_matches else 0
        # This is the span that carries the architectural claim. It closes before
        # "4. model.chat" opens, and test_trace_ordering.py asserts that against a
        # real evaluation rather than trusting the comment.
        with span("1b. route_platform  <-- VERDICT DECIDED HERE",
                  decided_by="deterministic rules over the algorithm database, no model") as s:
            routing = route_platform(problem_description, kb_matches, search_score)
            s.set(
                verdict=routing["verdict"],
                platform=routing["platform"],
                confidence=routing["confidence"],
                reason=routing["reason"],
                search_score=search_score,
                model_called=False,
            )

        # Step 2: Find similar reference problems
        with span("2. kb.find_similar_problems") as s:
            similar = self.kb.find_similar_problems(problem_description)
            similar_ids = [s2.get("problem_id", "?") for s2 in similar]
            s.set(count=len(similar_ids), problem_ids=", ".join(similar_ids[:5]) or "none")

        # Step 3: Build context for LLM
        with span("3. build_context_json",
                  note="the already-decided routing goes IN as input") as _ctx_span:
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
            _ctx_span.set(context_chars=len(kb_context),
                          carries_verdict=routing["verdict"])

        # Recent arXiv work, off by default. The corpus is an arXiv quant-ph sweep, so
        # it argues for quantum on every question - measured, its most confident hits
        # were for the two demo prompts that must be declined. It is passed to the model
        # in its own labelled block, never merged into KNOWLEDGE BASE RESULTS, and never
        # reaches route_platform(), which has already produced the verdict by this point.
        if USE_PAPERS:
            with span("3b. kb.search_papers", corpus="arXiv quant-ph") as s:
                recent_papers = self.kb.search_papers(problem_description)
                s.set(count=len(recent_papers))
        else:
            recent_papers = []

        # Step 4: LLM generates detailed assessment
        user_message = f"""Evaluate this quantum computing problem:

PROBLEM: {problem_description}

DETERMINISTIC PRE-CLASSIFICATION:
Platform: {routing['platform']} | Verdict: {routing['verdict']} | Confidence: {routing['confidence']}
Reason: {routing['reason']}
Troyer filters (from KB data): {json.dumps(routing['evidence']['troyer_filters'])}
Domain keyword scores: {json.dumps(routing['evidence']['keyword_scores'])}

IMPORTANT: The deterministic routing above is computed from the algorithm database and keyword analysis,
and it is what the published verdict will be. Your job is to explain and stress-test it, not to replace it.
Write the explanation, red flags and alternatives as though that verdict stands.
If you believe it is scientifically wrong, still return it, and put your reasoning in red_flags citing a
specific algorithm and speedup class - a disagreement is recorded and reviewed rather than silently applied.

KNOWLEDGE BASE RESULTS:
{kb_context}
{self._recent_work_block(recent_papers)}
Provide your evaluation as JSON following the output format specified in your instructions. Be honest about limitations."""

        # Timed so the cost of the agent path is a measurement rather than an
        # impression. Client construction is inside the window on both paths.
        started = time.perf_counter()
        with span("4. model call", writes="the prose; may disagree -> model_dissent") as _model_span:
            _model_span.set(path="foundry-agent" if USE_AGENT else "chat-completions",
                            verdict_already_decided=routing["verdict"])
            if USE_AGENT:
                raw_content, finish_reason, model_used, tokens_used = self._evaluate_via_agent(user_message)
            else:
                client = self._get_chat_client()
                deployment = self._get_deployment()
                response = client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    max_completion_tokens=MAX_COMPLETION_TOKENS,
                    response_format={"type": "json_object"},
                )
                choice = response.choices[0] if response.choices else None
                raw_content = (choice.message.content if choice else "") or ""
                finish_reason = getattr(choice, "finish_reason", None)
                model_used = response.model if response else CHAT_DEPLOYMENT
                tokens_used = response.usage.total_tokens if response and response.usage else 0
            _model_span.set(model_used=model_used, tokens_used=tokens_used,
                            finish_reason=finish_reason)
        model_seconds = round(time.perf_counter() - started, 2)

        # Step 5: Parse LLM response
        with span("5. parse_assessment") as _parse_span:
            llm_result = parse_assessment(raw_content)
            parse_ok = llm_result is not None
            _parse_span.set(parse_ok=parse_ok, raw_chars=len(raw_content or ""))
        if llm_result is None:
            # Never surface raw_content here. It is the model's unparsed output,
            # and a failed parse once put 17,000 characters of JSON on screen
            # where the assessment should have been.
            if finish_reason == "length":
                note = (
                    "The assessment was cut off before the model finished writing it. "
                    "Raise QGC_MAX_COMPLETION_TOKENS to get the full explanation and sources."
                )
            else:
                note = (
                    "The model's assessment could not be read. The verdict above still "
                    "stands: it comes from the deterministic router, not the model."
                )
            llm_result = {
                "verdict": kb_result["verdict"],
                "confidence": kb_result.get("confidence", 0.5),
                "explanation": note,
            }

        # Step 6: Merge KB + routing + LLM results.
        # The deterministic router owns the verdict and platform: those are the
        # claims this tool stands behind, and letting a stochastic model set them
        # made identical inputs return different answers. The LLM contributes the
        # explanation, red flags and alternatives, and any disagreement it has is
        # recorded rather than allowed to change the result.
        deterministic_filters = routing["evidence"].get("troyer_filters", {})

        verdict = routing["verdict"]
        platform = routing["platform"]
        model_verdict = llm_result.get("verdict")
        model_platform = llm_result.get("recommended_platform")

        dissent = {}
        if model_verdict and model_verdict != verdict:
            dissent["verdict"] = model_verdict
        if (model_platform and model_platform != platform
                and not is_platform_refinement(platform, model_platform)):
            dissent["recommended_platform"] = model_platform

        # Recorded as its own span because "the model disagreed and we kept the
        # router's answer anyway" is the single most important thing a reader of
        # this trace can be shown. published_verdict is always the router's.
        with span("6. merge  <-- router's verdict wins") as _merge_span:
            _merge_span.set(
                published_verdict=verdict,
                published_platform=platform,
                model_proposed_verdict=model_verdict or "(none)",
                dissent_recorded=bool(dissent),
                dissent_applied=False,
            )

        # Step 7: Compute cost-advantage analysis (Troyer Part 6 placeholder).
        # Heuristic order-of-magnitude estimates from agents/classifier/cost_model.py.
        with span("7. cost_analysis"):
            cost_analysis = self._compute_cost_analysis(
                platform=platform,
                algorithm=llm_result.get("recommended_algorithm", kb_result.get("best_algorithm", "")),
                kb_match=(kb_result.get("matches") or [{}])[0],
            )

        # Both paths fabricate a source about 1 in 22, and the agent's Learn MCP
        # did not prevent it, so a citation is only published once it resolves.
        model_refs = llm_result.get("references", [])
        with span("8. verify_citations", enabled=VERIFY_CITATIONS) as _cite_span:
            if VERIFY_CITATIONS:
                kept_refs, rejected_refs, _ = partition_references(model_refs)
            else:
                kept_refs, rejected_refs = model_refs, []
            _cite_span.set(proposed=len(model_refs), kept=len(kept_refs),
                           rejected=len(rejected_refs))

        result = {
            "problem": problem_description,
            "verdict": verdict,
            "confidence": routing["confidence"],
            "advantage_class": llm_result.get("advantage_class", kb_result.get("speedup_class", "unknown")),
            "recommended_algorithm": llm_result.get("recommended_algorithm", kb_result.get("best_algorithm", "Unknown")),
            "recommended_platform": platform,
            "platform_reason": routing["reason"],
            "troyer_filters": deterministic_filters if deterministic_filters else llm_result.get("troyer_filters", {}),
            "red_flags": llm_result.get("red_flags", []),
            "hpc_alternative": llm_result.get("hpc_alternative", ""),
            "ai_alternative": llm_result.get("ai_alternative", ""),
            "explanation": llm_result.get("explanation", ""),
            "similar_problems": llm_result.get("similar_problems", similar_ids),
            "references": kept_refs,
            "rejected_references": rejected_refs,
            "model_dissent": dissent,
            "cost_analysis": cost_analysis,
            "routing_evidence": routing["evidence"],
            "evaluated_utc": datetime.now(timezone.utc).isoformat(),
            "model_used": model_used,
            "tokens_used": tokens_used,
            "model_seconds": model_seconds,
            "used_agent": USE_AGENT,
        }

        self.last_diagnostics = {
            "parse_ok": parse_ok,
            "finish_reason": finish_reason,
            "llm_assessment": llm_result if parse_ok else None,
            "deterministic_filters": deterministic_filters,
            "router_verdict": verdict,
            "router_platform": platform,
            "model_used": model_used,
            "model_seconds": model_seconds,
            "used_agent": USE_AGENT,
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

    path_label = "agent" if result.get("used_agent") else "chat"
    print(f"\n🤖 Model: {result.get('model_used', '?')}, Tokens: {result.get('tokens_used', 0)}, "
          f"{result.get('model_seconds', 0)}s via {path_label}")

    # Save to file
    out_path = Path("agents/evaluations")
    out_path.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_path / f"eval_{ts}.json"
    out_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\n💾 Saved: {out_file}")


if __name__ == "__main__":
    main()
