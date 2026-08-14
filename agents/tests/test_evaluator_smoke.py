"""Smoke tests for the Quantum Advantage Evaluator  offline, no Azure needed.

Tests the deterministic routing layer (platform_router) and the API schema.
These run in CI without Azure credentials.
"""

import json
import sys
from pathlib import Path

import pytest

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agents.classifier.platform_router import route_platform


# --- Deterministic routing tests ---

class TestPlatformRouter:
    """Test the deterministic pre-classification layer."""

    def test_quantum_chemistry_routes_quantum(self):
        result = route_platform(
            "Simulate the ground state energy of a 50-atom catalyst using quantum phase estimation",
            [], 0.0,
        )
        assert result["platform"] == "QUANTUM"

    def test_neural_network_routes_ai_ml(self):
        result = route_platform(
            "Train a neural network on 10 million images for medical diagnosis",
            [], 0.0,
        )
        assert result["platform"] == "AI_ML"
        assert result["confidence"] >= 0.7

    def test_cfd_routes_hpc(self):
        result = route_platform(
            "Simulate turbulent flow around an aircraft wing using Navier-Stokes equations",
            [], 0.0,
        )
        assert result["platform"] == "HPC"

    def test_factoring_routes_quantum(self):
        result = route_platform(
            "Factor a 2048-bit RSA public key to test cryptographic security",
            [], 0.0,
        )
        assert result["platform"] == "QUANTUM"

    def test_qcd_routes_quantum(self):
        result = route_platform(
            "Simulate real-time quark-gluon plasma dynamics on a lattice",
            [], 0.0,
        )
        assert result["platform"] == "QUANTUM"

    def test_llm_finetuning_routes_ai_ml(self):
        result = route_platform(
            "Fine-tune a large language model for customer support chatbot",
            [], 0.0,
        )
        assert result["platform"] == "AI_ML"

    def test_molecular_dynamics_routes_hpc(self):
        result = route_platform(
            "Run classical molecular dynamics simulation of protein folding with force fields",
            [], 0.0,
        )
        assert result["platform"] == "HPC"

    def test_generic_optimization_inconclusive(self):
        result = route_platform(
            "Optimize a vehicle routing problem with 500 delivery stops and time windows",
            [], 0.0,
        )
        # Could be QAOA (no proven advantage) or classical  INCONCLUSIVE is honest
        assert result["verdict"] in ("INCONCLUSIVE", "HPC_PREFERRED", "AI_ML_PREFERRED")

    def test_result_schema(self):
        """Verify routing result has all required fields."""
        result = route_platform("test problem", [], 0.0)
        assert "platform" in result
        assert "verdict" in result
        assert "confidence" in result
        assert "reason" in result
        assert "evidence" in result
        assert "keyword_scores" in result["evidence"]
        assert "troyer_filters" in result["evidence"]

    def test_confidence_bounds(self):
        """Confidence should always be between 0 and 1."""
        for problem in [
            "quantum simulation of Hubbard model",
            "train a CNN for image classification",
            "solve Navier-Stokes for aerodynamics",
            "random unrelated text about cooking",
        ]:
            result = route_platform(problem, [], 0.0)
            assert 0.0 <= result["confidence"] <= 1.0, f"Bad confidence {result['confidence']} for: {problem}"


def _kb_match(name, speedup="superpolynomial", verdict="QUANTUM_ADVANTAGE"):
    """A knowledge base hit of the kind AI Search actually returns."""
    return {
        "name": name,
        "category": "simulation",
        "speedup_class": speedup,
        "troyer_verdict": verdict,
        "io_bottleneck": False,
        "naturally_quantum": True,
        "score": 0.03,
    }


class TestRetrievalRelevance:
    """Rule 1 must not fire on an irrelevant knowledge base match.

    Every other router test passes an empty kb_matches list, so Rule 1 - the
    branch that actually runs in production - was never exercised. It turned out
    to accept any top match as proof of quantum advantage. Retrieval always
    returns a top match, and the algorithm zoo is almost entirely strong-speedup
    quantum algorithms, so this fired on nearly everything.

    These are the two cases observed against the live API.
    """

    def test_portfolio_optimisation_is_not_quantum(self):
        result = route_platform(
            "Optimize a portfolio of 500 assets using mean-variance optimisation",
            [_kb_match("Probabilistic Sampling (Quantum Supremacy)")],
            0.03,
        )
        assert result["verdict"] != "QUANTUM_ADVANTAGE"
        assert result["platform"] != "QUANTUM"

    def test_image_classification_is_not_quantum(self):
        result = route_platform(
            "Train an image classifier on 10 million medical photos",
            [_kb_match("Coupled Classical Oscillators Simulation")],
            0.03,
        )
        assert result["verdict"] != "QUANTUM_ADVANTAGE"
        assert result["platform"] == "AI_ML"

    def test_cfd_is_not_quantum_despite_a_strong_match(self):
        result = route_platform(
            "Simulate turbulent airflow over an aircraft wing using CFD",
            [_kb_match("Quantum Simulation of Hamiltonian Dynamics")],
            0.03,
        )
        assert result["verdict"] != "QUANTUM_ADVANTAGE"
        assert result["platform"] == "HPC"

    def test_a_genuinely_quantum_problem_still_routes_quantum(self):
        """The gate must not cost us the true positives."""
        result = route_platform(
            "Find the ground state energy of the FeMoco nitrogenase cofactor",
            [_kb_match("Preparing Eigenstates and Thermal States")],
            0.03,
        )
        assert result["verdict"] == "QUANTUM_ADVANTAGE"
        assert result["platform"] == "QUANTUM"
        assert result["confidence"] == 0.9

    def test_factoring_still_routes_quantum(self):
        """Shor has structural advantage, not natural quantumness."""
        result = route_platform(
            "Factor a 2048-bit RSA integer to test post-quantum readiness",
            [
                {
                    "name": "Shor's Factoring Algorithm",
                    "category": "cryptography",
                    "speedup_class": "superpolynomial",
                    "troyer_verdict": "QUANTUM_ADVANTAGE",
                    "io_bottleneck": False,
                    "naturally_quantum": False,
                    "score": 0.03,
                }
            ],
            0.03,
        )
        assert result["verdict"] == "QUANTUM_ADVANTAGE"
        assert result["platform"] == "QUANTUM"

    def test_rejected_match_is_named_in_the_reason(self):
        """An unexplained INCONCLUSIVE is not good enough - say what was rejected."""
        result = route_platform(
            "Rebalance a portfolio subject to a turnover budget",
            [_kb_match("Probabilistic Sampling (Quantum Supremacy)")],
            0.03,
        )
        if result["verdict"] == "INCONCLUSIVE":
            assert "Probabilistic Sampling" in result["reason"]

    def test_corroboration_is_recorded_as_evidence(self):
        result = route_platform(
            "Optimize a portfolio of 500 assets using mean-variance optimisation",
            [_kb_match("Probabilistic Sampling (Quantum Supremacy)")],
            0.03,
        )
        assert result["evidence"]["quantum_corroborated"] is False


# --- API response model tests ---

try:
    from agents.api.main import EvaluateResponse
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


@pytest.mark.skipif(not _HAS_FASTAPI, reason="FastAPI not installed (API deployment dependency)")
class TestAPIResponseModel:
    """Test that the API response model accepts all expected fields."""

    def test_response_model_imports(self):
        from agents.api.main import EvaluateResponse
        # Verify new fields exist in the model
        fields = EvaluateResponse.model_fields
        assert "workspace_guidance" in fields
        assert "divincenzo_assessment" in fields
        assert "error_correction_codes" in fields
        assert "troyer_filters" in fields
        assert "recommended_platform" in fields

    def test_response_model_defaults(self):
        from agents.api.main import EvaluateResponse
        # Minimal valid response
        resp = EvaluateResponse(
            verdict="QUANTUM_ADVANTAGE",
            confidence=0.85,
            advantage_class="exponential",
            recommended_algorithm="QPE",
            troyer_filters={"F1_proven_speedup": True},
            red_flags=[],
            hpc_alternative="Azure HBv4 cluster",
            explanation="Test explanation",
            similar_problems=[],
            references=[],
        )
        assert resp.workspace_guidance == {}
        assert resp.divincenzo_assessment == {}
        assert resp.error_correction_codes == []

    def test_response_model_with_new_fields(self):
        from agents.api.main import EvaluateResponse
        resp = EvaluateResponse(
            verdict="QUANTUM_ADVANTAGE",
            confidence=0.85,
            advantage_class="exponential",
            recommended_algorithm="QPE",
            troyer_filters={"F1_proven_speedup": True},
            red_flags=[],
            hpc_alternative="",
            explanation="Test",
            similar_problems=[],
            references=[],
            workspace_guidance={
                "platform": "Azure Quantum",
                "setup_steps": ["Create workspace", "Select Quantinuum target"],
            },
            divincenzo_assessment={
                "scalable_qubits": "partial",
                "initialization": "met",
                "summary": "Hardware partially ready",
            },
            error_correction_codes=["surface_code", "color_code"],
        )
        assert resp.workspace_guidance["platform"] == "Azure Quantum"
        assert len(resp.error_correction_codes) == 2


# --- Troyer assessment data tests ---

class TestTroyerAssessmentData:
    """Validate the troyerAssessment.json data integrity."""

    @pytest.fixture
    def troyer_data(self):
        path = ROOT / "website" / "data" / "troyerAssessment.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_has_three_categories(self, troyer_data):
        cats = troyer_data["categories"]
        assert "proven_speedup" in cats
        assert "heuristic_potential" in cats
        assert "simulation_native" in cats

    def test_summary_counts(self, troyer_data):
        s = troyer_data["summary"]
        assert s["proven_speedup_count"] == 5
        assert s["active_count"] == 9
        assert s["archived_count"] == 11

    def test_vqe_upgrades_tracked(self, troyer_data):
        upgrades = troyer_data["summary"]["vqe_to_qpe_upgrades"]
        assert "01_hubbard" in upgrades
        assert "02_catalysis" in upgrades
        assert len(upgrades) == 5

    def test_lecture_series_has_6_parts(self, troyer_data):
        lectures = troyer_data["lecture_series"]
        assert len(lectures) == 6
        assert lectures[4]["title"] == "Scalable quantum architecture"
        assert lectures[5]["title"] == "Balancing the Cost of Utility-Scale Quantum Computing"

    def test_error_correction_zoo_in_sources(self, troyer_data):
        sources = troyer_data["external_knowledge_sources"]
        names = [s["name"] for s in sources]
        assert "Error Correction Zoo" in names

    def test_divincenzo_framework_present(self, troyer_data):
        frameworks = troyer_data["additional_frameworks"]
        assert "divincenzo_criteria" in frameworks
        criteria = frameworks["divincenzo_criteria"]["criteria"]
        assert len(criteria) >= 5

    def test_industry_developments_present(self, troyer_data):
        devs = troyer_data["industry_developments"]
        assert len(devs) >= 2
        sources = [d["source"] for d in devs]
        assert "Google Quantum AI" in sources


# --- Verdict authority ---

class _StubKB:
    """Knowledge base stub so evaluate() runs without Azure."""

    def classify_problem(self, description):
        return {
            "verdict": "QUANTUM_ADVANTAGE",
            "best_algorithm": "Quantum Phase Estimation",
            "speedup_class": "superpolynomial",
            "filters": {},
            "matches": [],
        }

    def find_similar_problems(self, description):
        return []


def _evaluator_returning(payload):
    """Evaluator whose LLM call returns ``payload``, with Azure bypassed."""
    from agents.orchestrator.evaluate import QuantumEvaluator

    evaluator = object.__new__(QuantumEvaluator)
    evaluator.kb = _StubKB()

    class _Message:
        content = json.dumps(payload)

    class _Choice:
        message = _Message()
        finish_reason = "stop"

    class _Usage:
        total_tokens = 42

    class _Response:
        choices = [_Choice()]
        model = "stub-model"
        usage = _Usage()

    class _Completions:
        def create(self, **kwargs):
            return _Response()

    class _Chat:
        completions = _Completions()

    class _Client:
        chat = _Chat()

    evaluator._get_chat_client = lambda: _Client()
    evaluator._get_deployment = lambda: "stub-deployment"
    return evaluator


QUANTUM_PROBLEM = "Simulate the ground state energy of a 50-atom catalyst using quantum phase estimation"


class TestVerdictAuthority:
    """The deterministic router owns the verdict; the model only explains it.

    A model that disagreed used to silently rewrite the published verdict, so
    identical inputs returned different answers between runs.
    """

    def test_router_verdict_survives_a_disagreeing_model(self):
        expected = route_platform(QUANTUM_PROBLEM, [], 0.0)
        evaluator = _evaluator_returning({
            "verdict": "HPC_PREFERRED",
            "recommended_platform": "HPC",
            "explanation": "the model argues for classical",
        })

        result = evaluator.evaluate(QUANTUM_PROBLEM)

        assert result["verdict"] == expected["verdict"]
        assert result["recommended_platform"] == expected["platform"]

    def test_disagreement_is_recorded_not_discarded(self):
        evaluator = _evaluator_returning({
            "verdict": "HPC_PREFERRED",
            "recommended_platform": "HPC",
            "explanation": "the model argues for classical",
        })

        dissent = evaluator.evaluate(QUANTUM_PROBLEM)["model_dissent"]

        assert dissent["verdict"] == "HPC_PREFERRED"
        assert dissent["recommended_platform"] == "HPC"

    def test_agreement_records_no_dissent(self):
        expected = route_platform(QUANTUM_PROBLEM, [], 0.0)
        evaluator = _evaluator_returning({
            "verdict": expected["verdict"],
            "recommended_platform": expected["platform"],
            "explanation": "the model agrees",
        })

        assert evaluator.evaluate(QUANTUM_PROBLEM)["model_dissent"] == {}

    def test_model_still_supplies_the_narrative(self):
        evaluator = _evaluator_returning({
            "verdict": "HPC_PREFERRED",
            "explanation": "a specific explanation",
            "red_flags": ["a specific red flag"],
        })

        result = evaluator.evaluate(QUANTUM_PROBLEM)

        assert result["explanation"] == "a specific explanation"
        assert result["red_flags"] == ["a specific red flag"]

    def test_identical_input_gives_identical_verdict(self):
        """Whatever the model says, repeated calls must agree."""
        verdicts = set()
        for model_verdict in ("HPC_PREFERRED", "QUANTUM_ADVANTAGE", "INCONCLUSIVE"):
            evaluator = _evaluator_returning({"verdict": model_verdict, "explanation": ""})
            verdicts.add(evaluator.evaluate(QUANTUM_PROBLEM)["verdict"])

        assert len(verdicts) == 1


# --- Assessment parsing ---

def _evaluator_returning_raw(text, finish_reason="stop"):
    """Evaluator whose LLM call returns ``text`` verbatim, not JSON-encoded."""
    evaluator = _evaluator_returning({})

    class _Message:
        content = text

    class _Choice:
        message = _Message()

    _Choice.finish_reason = finish_reason

    class _Usage:
        total_tokens = 42

    class _Response:
        choices = [_Choice()]
        model = "stub-model"
        usage = _Usage()

    class _Completions:
        def create(self, **kwargs):
            return _Response()

    class _Chat:
        completions = _Completions()

    class _Client:
        chat = _Chat()

    evaluator._get_chat_client = lambda: _Client()
    return evaluator


class TestAssessmentParsing:
    """A good answer wrapped in a fence is still a good answer.

    The chat path pins response_format to json_object; the agent path cannot,
    and it intermittently returns fenced or prose-wrapped JSON. A bare
    json.loads then fell through to a handler that put the model's entire raw
    output into `explanation` - once 17,243 characters of it, where the website
    renders the assessment.
    """

    PAYLOAD = {
        "explanation": "a real assessment",
        "references": ["arXiv:1234.5678", "errorcorrectionzoo.org/c/surface"],
        "red_flags": ["a real concern"],
    }

    def test_plain_json_still_parses(self):
        from agents.orchestrator.evaluate import parse_assessment

        assert parse_assessment(json.dumps(self.PAYLOAD)) == self.PAYLOAD

    def test_fenced_json_parses(self):
        from agents.orchestrator.evaluate import parse_assessment

        fenced = "```json\n" + json.dumps(self.PAYLOAD) + "\n```"
        assert parse_assessment(fenced) == self.PAYLOAD

    def test_json_with_surrounding_prose_parses(self):
        from agents.orchestrator.evaluate import parse_assessment

        wrapped = "Here is my assessment:\n" + json.dumps(self.PAYLOAD) + "\nHope that helps."
        assert parse_assessment(wrapped) == self.PAYLOAD

    def test_unparseable_returns_none(self):
        from agents.orchestrator.evaluate import parse_assessment

        assert parse_assessment("no json here at all") is None
        assert parse_assessment("") is None

    def test_fenced_response_keeps_its_references(self):
        """The end-to-end symptom: fenced JSON used to yield zero references."""
        fenced = "```json\n" + json.dumps(self.PAYLOAD) + "\n```"
        result = _evaluator_returning_raw(fenced).evaluate(QUANTUM_PROBLEM)

        assert result["references"] == self.PAYLOAD["references"]
        assert result["explanation"] == "a real assessment"

    def test_unreadable_response_does_not_dump_raw_output(self):
        raw = "sorry, I cannot comply. " + "x" * 17000
        result = _evaluator_returning_raw(raw).evaluate(QUANTUM_PROBLEM)

        assert raw not in result["explanation"]
        assert len(result["explanation"]) < 500

    def test_truncated_response_says_so(self):
        result = _evaluator_returning_raw(
            '{"explanation": "half a sen', finish_reason="length"
        ).evaluate(QUANTUM_PROBLEM)

        assert "cut off" in result["explanation"]

    def test_verdict_survives_an_unreadable_response(self):
        expected = route_platform(QUANTUM_PROBLEM, [], 0.0)
        result = _evaluator_returning_raw("not json").evaluate(QUANTUM_PROBLEM)

        assert result["verdict"] == expected["verdict"]
