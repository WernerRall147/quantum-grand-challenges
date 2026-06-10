"""Quantum Advantage Evaluator  FastAPI backend.

Exposes the orchestrator as an HTTP API for the website chat interface.
Deployed as an Azure Container App.

Usage:
    uvicorn agents.api.main:app --host 0.0.0.0 --port 8000
"""

import json
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

app = FastAPI(
    title="Quantum Advantage Evaluator API",
    description="Evaluates whether a scientific problem is better solved on quantum or HPC",
    version="1.0.0",
)

# CORS  allow the GitHub Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wernerrall147.github.io",
        "https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluateRequest(BaseModel):
    problem: str
    generate_code: bool = False


class EvaluateResponse(BaseModel):
    verdict: str
    confidence: float
    advantage_class: str
    recommended_algorithm: str
    recommended_platform: str = ""
    platform_reason: str = ""
    workspace_guidance: dict = {}
    troyer_filters: dict
    divincenzo_assessment: dict = {}
    red_flags: list
    hpc_alternative: str
    ai_alternative: str = ""
    explanation: str
    similar_problems: list
    references: list
    error_correction_codes: list = []
    model_used: str = ""
    tokens_used: int = 0
    qsharp_code: str = ""
    estimation: dict = {}
    resource_estimate_pareto: list = []
    bicep_template: str = ""
    bicep_validation: dict = {}
    bicep_deploy_commands: str = ""
    bicep_post_deploy_note: str = ""
    cost_analysis: dict = {}


class CodeRequest(BaseModel):
    problem: str
    algorithm: str = "QPE"


class BicepRequest(BaseModel):
    problem: str
    platform: str = "AI_ML"  # HPC | AI_ML | QUANTUM


# Lazy-load the evaluator to avoid import overhead on cold start
_evaluator = None
_codegen = None
_bicepgen = None


def get_evaluator():
    global _evaluator
    if _evaluator is None:
        from agents.orchestrator.evaluate import QuantumEvaluator
        _evaluator = QuantumEvaluator()
    return _evaluator


def get_codegen():
    global _codegen
    if _codegen is None:
        from agents.code_generator.generate import QSharpCodeGenerator
        _codegen = QSharpCodeGenerator()
    return _codegen


def get_bicepgen():
    global _bicepgen
    if _bicepgen is None:
        from agents.code_generator.bicep_generator import BicepWorkspaceGenerator
        _bicepgen = BicepWorkspaceGenerator()
    return _bicepgen


@app.get("/")
def health():
    return {"status": "ok", "service": "quantum-advantage-evaluator"}


@app.post("/api/evaluate", response_model=EvaluateResponse)
def evaluate(request: EvaluateRequest):
    if not request.problem.strip():
        raise HTTPException(status_code=400, detail="Problem description is required")

    if len(request.problem) > 5000:
        raise HTTPException(status_code=400, detail="Problem description too long (max 5000 chars)")

    try:
        evaluator = get_evaluator()
        result = evaluator.evaluate(request.problem.strip())
        if request.generate_code:
            verdict = result.get("verdict", "").upper()
            platform = result.get("recommended_platform", "").upper()
            # Quantum verdicts → generate Q# code
            if verdict == "QUANTUM_ADVANTAGE" or platform == "QUANTUM":
                try:
                    codegen = get_codegen()
                    code_out = codegen.generate_with_estimate(
                        request.problem.strip(),
                        algorithm=result.get("recommended_algorithm", "QPE"),
                        multi_profile=True,
                    )
                    result["qsharp_code"] = code_out.get("qsharp_code", "")
                    estimation = code_out.get("estimation", {})
                    result["estimation"] = estimation
                    result["resource_estimate_pareto"] = estimation.get("pareto_table", [])
                except Exception as e:  # noqa: BLE001
                    result["qsharp_code"] = ""
                    result["estimation"] = {"error": str(e)[:200]}
                    result["resource_estimate_pareto"] = []
            # Non-quantum verdicts → generate Bicep workspace template
            elif platform in ("HPC", "AI_ML"):
                try:
                    bicepgen = get_bicepgen()
                    bicep_out = bicepgen.generate_with_validation(
                        request.problem.strip(), platform=platform,
                    )
                    result["bicep_template"] = bicep_out.get("bicep_template", "")
                    result["bicep_validation"] = bicep_out.get("validation", {})
                    result["bicep_deploy_commands"] = bicep_out.get("deploy_commands", "")
                    result["bicep_post_deploy_note"] = bicep_out.get("post_deploy_note", "")
                except Exception as e:  # noqa: BLE001
                    result["bicep_template"] = ""
                    result["bicep_validation"] = {"error": str(e)[:200]}
        return EvaluateResponse(**{k: result.get(k, EvaluateResponse.model_fields[k].default)
                                   for k in EvaluateResponse.model_fields})
    except Exception as e:
        import traceback, sys
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {type(e).__name__}: {str(e)[:400]}")


@app.post("/api/generate-code")
def generate_code(request: CodeRequest):
    """Generate Q# code for a problem + algorithm, compile, and estimate resources."""
    if not request.problem.strip():
        raise HTTPException(status_code=400, detail="Problem description is required")
    try:
        codegen = get_codegen()
        return codegen.generate_with_estimate(request.problem.strip(), request.algorithm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)[:200]}")


@app.post("/api/generate-bicep")
def generate_bicep(request: BicepRequest):
    """Generate a Bicep workspace template for HPC, AI/ML, or Quantum platforms.

    Use this for problems that don't pass Troyer quantum filters but need
    Azure infrastructure provisioning.
    """
    if not request.problem.strip():
        raise HTTPException(status_code=400, detail="Problem description is required")
    platform = request.platform.upper()
    if platform not in ("HPC", "AI_ML", "QUANTUM"):
        raise HTTPException(status_code=400, detail="platform must be HPC | AI_ML | QUANTUM")
    try:
        bicepgen = get_bicepgen()
        return bicepgen.generate_with_validation(request.problem.strip(), platform=platform)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bicep generation failed: {str(e)[:200]}")


@app.get("/api/algorithms")
def list_algorithms():
    """List all algorithms in the knowledge base."""
    try:
        evaluator = get_evaluator()
        algos = evaluator.kb.search_algorithms("quantum algorithm", top=20)
        return {"algorithms": algos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)[:200])


@app.get("/api/reference-problems")
def list_reference_problems():
    """List active reference problems."""
    try:
        evaluator = get_evaluator()
        active = evaluator.kb.get_reference_problems("active")
        archived = evaluator.kb.get_reference_problems("archived")
        return {"active": active, "archived": archived}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)[:200])
