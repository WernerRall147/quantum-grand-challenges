"""Troyer Cost Model — Framework for Part 6 of the Architecture Series.

"Balancing the Cost of Utility-Scale Quantum Computing"

This module will integrate Troyer's cost model once Part 6 is published.
Until then, it provides a placeholder cost assessment based on
resource estimation data and known hardware pricing.

The cost model answers: "Even if quantum advantage exists, is the
engineering and economic cost justified?"
"""

from typing import Dict, Any, Optional


# Approximate costs per logical qubit-second for current hardware platforms
# These are order-of-magnitude estimates — will be refined with Part 6 data
PLATFORM_COST_RATES = {
    "azure_quantum_quantinuum_h2": {
        "cost_per_circuit_shot": 0.01,  # HQC-based pricing
        "min_cost_per_job": 1.0,
        "notes": "Quantinuum H2: ~$0.01 per HQC. Real cost depends on circuit depth and qubit count.",
    },
    "azure_quantum_ionq_aria": {
        "cost_per_gate": 0.00022,  # Gate-based pricing
        "min_cost_per_job": 1.0,
        "notes": "IonQ Aria: gate-based pricing. 1-qubit gate ~$0.00015, 2-qubit ~$0.00098.",
    },
    "azure_hpc_nd96amsr_a100": {
        "cost_per_hour": 27.20,
        "notes": "NDv4 (8x A100 80GB): $27.20/hr on-demand, ~$16/hr spot.",
    },
    "azure_hpc_hbv4": {
        "cost_per_hour": 3.60,
        "notes": "HBv4 (176 AMD cores): $3.60/hr. Good for MPI-parallel workloads.",
    },
    "azure_ai_foundry": {
        "cost_per_1k_tokens_gpt4": 0.03,
        "cost_per_1k_tokens_embedding": 0.00002,
        "notes": "Azure AI Foundry: model-dependent. GPT-4.1 ~$0.03/1k tokens.",
    },
}

# Troyer Part 6 will provide a formal framework for these tradeoffs
# For now, we use a simplified model based on resource estimation outputs
COST_MODEL_STATUS = "placeholder"
TROYER_PART_6_STATUS = "coming_soon"
TROYER_PART_6_URL = None  # Will be filled when Part 6 is published


def estimate_quantum_cost(
    physical_qubits: int,
    runtime_ns: int,
    target_platform: str = "azure_quantum_quantinuum_h2",
    shots: int = 100,
) -> Dict[str, Any]:
    """Estimate the cost of running a quantum computation.

    This is a PLACEHOLDER — will be replaced with Troyer's formal cost model.
    Currently uses rough estimates based on known Azure Quantum pricing.
    """
    rates = PLATFORM_COST_RATES.get(target_platform, {})

    if "cost_per_circuit_shot" in rates:
        # HQC-style pricing (Quantinuum)
        # Rough: HQC ~ num_qubits * circuit_depth_factor
        depth_factor = max(1, runtime_ns / 1_000_000)  # Normalize to ~ms
        hqc_per_shot = physical_qubits * depth_factor * 0.001
        estimated_cost = max(rates.get("min_cost_per_job", 1.0), hqc_per_shot * shots)
    elif "cost_per_gate" in rates:
        # Gate-based pricing (IonQ)
        # Rough: assume 10 gates per qubit per layer, ~sqrt(runtime) layers
        est_gates = physical_qubits * 10 * max(1, (runtime_ns / 1_000_000) ** 0.5)
        estimated_cost = max(rates.get("min_cost_per_job", 1.0), est_gates * rates["cost_per_gate"] * shots)
    else:
        estimated_cost = None

    return {
        "platform": target_platform,
        "estimated_cost_usd": round(estimated_cost, 2) if estimated_cost else None,
        "shots": shots,
        "cost_model": COST_MODEL_STATUS,
        "notes": rates.get("notes", ""),
        "troyer_part_6": TROYER_PART_6_STATUS,
        "caveat": "Placeholder estimate. Troyer Part 6 will provide formal cost-advantage analysis.",
    }


def estimate_hpc_cost(
    compute_hours: float,
    platform: str = "azure_hpc_nd96amsr_a100",
) -> Dict[str, Any]:
    """Estimate the cost of solving the same problem on Azure HPC."""
    rates = PLATFORM_COST_RATES.get(platform, {})
    cost_per_hour = rates.get("cost_per_hour", 0)
    estimated_cost = compute_hours * cost_per_hour

    return {
        "platform": platform,
        "estimated_cost_usd": round(estimated_cost, 2),
        "compute_hours": compute_hours,
        "notes": rates.get("notes", ""),
    }


def cost_advantage_ratio(
    quantum_cost: Dict[str, Any],
    hpc_cost: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare quantum vs HPC costs. Ratio > 1 means HPC is cheaper.

    Troyer's Part 6 framework will formalize when the quantum cost
    premium is justified by speedup class and problem scale.
    """
    q = quantum_cost.get("estimated_cost_usd")
    h = hpc_cost.get("estimated_cost_usd")

    if q is None or h is None or h == 0:
        return {"ratio": None, "verdict": "INSUFFICIENT_DATA"}

    ratio = q / h

    if ratio > 100:
        verdict = "HPC_STRONGLY_PREFERRED"
    elif ratio > 10:
        verdict = "HPC_PREFERRED_ON_COST"
    elif ratio > 1:
        verdict = "HPC_SLIGHTLY_CHEAPER"
    elif ratio > 0.1:
        verdict = "QUANTUM_SLIGHTLY_CHEAPER"
    else:
        verdict = "QUANTUM_STRONGLY_PREFERRED"

    return {
        "quantum_cost_usd": q,
        "hpc_cost_usd": h,
        "ratio": round(ratio, 3),
        "verdict": verdict,
        "note": "Cost alone does not determine advantage. Speedup class and problem scale matter. See Troyer Part 6.",
    }
