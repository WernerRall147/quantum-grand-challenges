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
