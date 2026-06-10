"""Tests for the Bicep workspace code generator  offline, no Azure required."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agents.code_generator.bicep_generator import (
    BicepWorkspaceGenerator,
    REFERENCE_TEMPLATES,
    HPC_REFERENCE,
    AI_ML_REFERENCE,
    QUANTUM_REFERENCE,
)


class TestReferenceTemplates:
    """Verify reference templates are well-formed Bicep."""

    def test_three_platforms_supported(self):
        assert "HPC" in REFERENCE_TEMPLATES
        assert "AI_ML" in REFERENCE_TEMPLATES
        assert "QUANTUM" in REFERENCE_TEMPLATES

    def test_hpc_has_compute_sku(self):
        assert "computeVmSku" in HPC_REFERENCE
        assert "Standard_HB" in HPC_REFERENCE  # MPI-class compute
        assert "Standard_ND" in HPC_REFERENCE  # GPU
        assert "vnet" in HPC_REFERENCE.lower()

    def test_ai_ml_has_foundry_hub(self):
        assert "Microsoft.MachineLearningServices/workspaces" in AI_ML_REFERENCE
        assert "kind: 'Hub'" in AI_ML_REFERENCE
        assert "kind: 'Project'" in AI_ML_REFERENCE
        assert "Microsoft.CognitiveServices/accounts" in AI_ML_REFERENCE

    def test_quantum_has_workspace_and_providers(self):
        assert "Microsoft.Quantum/workspaces" in QUANTUM_REFERENCE
        assert "quantinuum" in QUANTUM_REFERENCE
        assert "ionq" in QUANTUM_REFERENCE
        assert "rigetti" in QUANTUM_REFERENCE

    def test_all_templates_use_modern_api_versions(self):
        """All API versions should be 2024+ for stable, 2025+ for preview.

        Exception: Microsoft.Insights/components is GA at 2020-02-02 (no newer
        version published yet).
        """
        for platform, ref in REFERENCE_TEMPLATES.items():
            template = ref["reference"]
            import re
            # Find resource declarations: 'Provider/Type@apiVersion'
            resources = re.findall(r"'(Microsoft\.[A-Za-z]+/[A-Za-z/]+)@(20\d{2}-\d{2}-\d{2}(?:-preview)?)'", template)
            assert len(resources) > 0, f"{platform} has no API versions"
            for provider_type, version in resources:
                year = int(version.split("-")[0])
                # Application Insights stable GA is 2020-02-02
                if provider_type.startswith("Microsoft.Insights/"):
                    continue
                assert year >= 2024, f"{platform} {provider_type} uses outdated API {version}"

    def test_all_templates_have_security_practices(self):
        """No public blob access, TLS 1.2+ where applicable."""
        for platform in ("HPC", "AI_ML", "QUANTUM"):
            template = REFERENCE_TEMPLATES[platform]["reference"]
            if "Microsoft.Storage/storageAccounts" in template:
                assert "minimumTlsVersion" in template, f"{platform} storage missing TLS config"
                assert "allowBlobPublicAccess: false" in template, f"{platform} storage allows public access"

    def test_all_templates_have_metadata(self):
        for platform, ref in REFERENCE_TEMPLATES.items():
            assert ref.get("description"), f"{platform} missing description"
            assert ref.get("deploy_commands"), f"{platform} missing deploy commands"
            assert ref.get("post_deploy_note"), f"{platform} missing post-deploy note"


class TestBicepGeneratorBasics:
    """Test the generator class without invoking Azure OpenAI."""

    def test_get_reference_returns_metadata(self):
        ref = BicepWorkspaceGenerator.get_reference("AI_ML")
        assert ref is not None
        assert "reference" in ref
        assert "description" in ref

    def test_get_reference_unknown_returns_none(self):
        assert BicepWorkspaceGenerator.get_reference("UNKNOWN") is None

    def test_get_reference_case_insensitive(self):
        assert BicepWorkspaceGenerator.get_reference("ai_ml") is not None
        assert BicepWorkspaceGenerator.get_reference("hpc") is not None
        assert BicepWorkspaceGenerator.get_reference("quantum") is not None

    def test_strip_fences_removes_markdown(self):
        gen = BicepWorkspaceGenerator.__new__(BicepWorkspaceGenerator)
        wrapped = "```bicep\nparam foo string\n```"
        assert gen._strip_fences(wrapped) == "param foo string"

    def test_strip_fences_passthrough(self):
        gen = BicepWorkspaceGenerator.__new__(BicepWorkspaceGenerator)
        plain = "// Hello\nparam foo string = 'bar'"
        assert gen._strip_fences(plain) == plain

    def test_generate_no_customize_returns_reference(self):
        """customize=False should return the reference template unchanged (no LLM call)."""
        gen = BicepWorkspaceGenerator.__new__(BicepWorkspaceGenerator)
        out = gen.generate("any problem", "AI_ML", customize=False)
        assert out == AI_ML_REFERENCE

    def test_generate_unknown_platform_raises(self):
        gen = BicepWorkspaceGenerator.__new__(BicepWorkspaceGenerator)
        with pytest.raises(ValueError):
            gen.generate("problem", "UNKNOWN", customize=False)


class TestBicepValidation:
    """Test the validation harness (gracefully skips when az CLI missing)."""

    def test_validate_skips_without_az_cli(self):
        """If az CLI is not installed, validation should skip gracefully (not crash)."""
        gen = BicepWorkspaceGenerator.__new__(BicepWorkspaceGenerator)
        result = gen.validate_bicep("// test")
        # Either validated successfully or skipped  never crashes
        assert "validated" in result
        if not result["validated"]:
            assert "skipped" in result or "error" in result


class TestAPIBicepIntegration:
    """Verify API model includes new Bicep fields."""

    def test_api_response_has_bicep_fields(self):
        try:
            from agents.api.main import EvaluateResponse, BicepRequest
        except ImportError:
            pytest.skip("FastAPI not installed")

        fields = EvaluateResponse.model_fields
        assert "bicep_template" in fields
        assert "bicep_validation" in fields
        assert "bicep_deploy_commands" in fields
        assert "bicep_post_deploy_note" in fields

        # BicepRequest exists with platform field
        req = BicepRequest(problem="test", platform="HPC")
        assert req.platform == "HPC"
