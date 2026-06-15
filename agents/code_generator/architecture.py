"""Solution architecture diagrams (Mermaid) for a recommended platform.

After the evaluator picks a platform and the code generator produces code +
resource estimates, this renders a deployable Azure architecture as a Mermaid
flowchart, grounded in the actual recommendation (target quantum hardware +
qubit width, or HPC/AI-ML compute SKUs). Paired with ``price_solution`` it
answers "what would I build, and what would it cost to run?".

This is the deterministic baseline (Increment 1). Roadmap is tracked in
docs/initiatives/architecture-pricing.md: Increment 2 lets the Foundry agent
enrich the diagram from Azure Architecture Center via the Microsoft Learn MCP.
"""

from typing import Any, Dict, Optional

from agents.classifier import azure_pricing

# Map orchestrator quantum-target ids onto azure_pricing provider keys.
_QTARGET_ALIASES = {
    "azure_quantum_quantinuum_h2": "quantinuum_h2",
    "quantinuum_h2": "quantinuum_h2",
    "azure_quantum_ionq_aria": "ionq_aria",
    "ionq_aria": "ionq_aria",
    "azure_quantum_ionq_forte": "ionq_forte",
    "ionq_forte": "ionq_forte",
    "azure_quantum_rigetti": "rigetti_cepheus",
    "rigetti_cepheus": "rigetti_cepheus",
    "azure_quantum_pasqal": "pasqal_fresnel",
    "pasqal_fresnel": "pasqal_fresnel",
}


def _hardware(target: Optional[str]):
    """Return (display_name, qubits) for a quantum target id."""
    key = _QTARGET_ALIASES.get(target or "", target or "quantinuum_h2")
    rec = azure_pricing.QUANTUM_PROVIDER_RATES.get(key, azure_pricing.QUANTINUUM_H2)
    return rec.get("name", "Quantinuum H2-1"), int(rec.get("qubits", 56))


def _quantum_mermaid(algorithm: str, hw_name: str, hw_qubits: int) -> str:
    algo = algorithm or "QPE"
    return "\n".join(
        [
            "flowchart LR",
            '    user["Researcher / client"] --> api["Azure Container App<br/>Evaluator API"]',
            f'    api --> orch["Classical orchestrator<br/>{algo} driver (Python + QDK)"]',
            '    orch --> aqw["Azure Quantum workspace"]',
            f'    aqw --> hw["{hw_name}<br/>{hw_qubits} qubits (QPU)"]',
            '    orch --> est["Azure Quantum<br/>Resource Estimator"]',
            '    aqw --> store["Azure Storage<br/>job results"]',
            '    api --> kv["Key Vault<br/>secrets"]',
            '    orch --> mon["Azure Monitor<br/>+ App Insights"]',
        ]
    )


def _hpc_mermaid(sku_label: str) -> str:
    return "\n".join(
        [
            "flowchart LR",
            '    user["Researcher / client"] --> cc["Azure CycleCloud"]',
            '    cc --> sched["Slurm scheduler"]',
            f'    sched --> nodes["{sku_label}<br/>MPI / GPU cluster"]',
            '    nodes --> lustre["Azure Managed Lustre<br/>scratch"]',
            '    nodes --> blob["Blob Storage<br/>datasets + results"]',
            '    cc --> mon["Azure Monitor"]',
        ]
    )


def _aiml_mermaid(sku_label: str) -> str:
    return "\n".join(
        [
            "flowchart LR",
            '    user["Researcher / client"] --> foundry["Azure AI Foundry<br/>project"]',
            f'    foundry --> compute["{sku_label}<br/>training / inference compute"]',
            '    compute --> pipe["ML pipeline<br/>(PyTorch / fine-tune)"]',
            '    foundry --> data["Azure Data Lake<br/>training data"]',
            '    foundry --> reg["Model registry"]',
            '    foundry --> mon["Azure Monitor<br/>+ App Insights"]',
        ]
    )


def build_architecture(
    platform: str,
    algorithm: str = "",
    estimation: Optional[Dict[str, Any]] = None,
    quantum_target: Optional[str] = None,
    confidence: float = 0.0,
    hpc_sku_label: str = "HBv4 / ND A100 v4 nodes",
    aiml_sku_label: str = "NC A100 v4 GPU compute",
) -> Dict[str, Any]:
    """Build a grounded Mermaid architecture for the recommended platform.

    Returns ``{platform, mermaid, components, narrative, confidence}``. The
    diagram is deterministic and tied to the recommendation so it pairs 1:1 with
    the run-cost estimate from ``cost_model.price_solution``.
    """
    platform = (platform or "").upper()
    estimation = estimation or {}

    if platform in ("QUANTUM", "HYBRID") or quantum_target:
        hw_name, hw_qubits = _hardware(quantum_target)
        mermaid = _quantum_mermaid(algorithm, hw_name, hw_qubits)
        components = [
            "Azure Container App (evaluator API entry point)",
            f"Classical orchestrator running the {algorithm or 'QPE'} driver (QDK)",
            "Azure Quantum workspace",
            f"{hw_name} QPU target ({hw_qubits} qubits)",
            "Azure Quantum Resource Estimator",
            "Azure Storage for job results, Key Vault for secrets, Azure Monitor",
        ]
        narrative = (
            f"Hybrid quantum-classical solution: a classical orchestrator drives the "
            f"{algorithm or 'QPE'} circuit and submits jobs to the {hw_name} QPU "
            f"({hw_qubits} qubits) through an Azure Quantum workspace. The Resource "
            f"Estimator sizes the fault-tolerant requirement; results land in Storage."
        )
    elif platform == "HPC":
        mermaid = _hpc_mermaid(hpc_sku_label)
        components = [
            "Azure CycleCloud orchestration",
            "Slurm scheduler",
            f"{hpc_sku_label} compute cluster",
            "Azure Managed Lustre scratch + Blob Storage",
            "Azure Monitor",
        ]
        narrative = (
            f"Classical HPC solution: Azure CycleCloud provisions a Slurm-scheduled "
            f"{hpc_sku_label} cluster for MPI/GPU compute, with Managed Lustre scratch "
            f"and Blob Storage for datasets and results."
        )
    else:  # AI_ML and anything else
        platform = platform or "AI_ML"
        mermaid = _aiml_mermaid(aiml_sku_label)
        components = [
            "Azure AI Foundry project",
            f"{aiml_sku_label}",
            "ML training / inference pipeline",
            "Azure Data Lake + Model registry",
            "Azure Monitor",
        ]
        narrative = (
            f"AI/ML solution: an Azure AI Foundry project orchestrates training and "
            f"inference on {aiml_sku_label}, with a Data Lake for training data and a "
            f"model registry for versioning."
        )

    return {
        "platform": platform,
        "mermaid": mermaid,
        "components": components,
        "narrative": narrative,
        "confidence": round(float(confidence or 0.0), 3),
    }
