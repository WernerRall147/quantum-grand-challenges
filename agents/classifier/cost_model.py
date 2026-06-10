"""Cost-advantage estimation backed by live Azure provider pricing.

Uses agents/classifier/azure_pricing.py for:
  - Quantinuum HQC formula (`HQC = 5 + C*(N1q + 10*N2q + 5*Nm)/5000`)
  - IonQ Aria/Forte AQT-style per-shot billing with min-job floors
  - Rigetti time-based billing ($0.02 per 10ms)
  - Azure HPC SKU rates from the public Retail Prices API (cached 24h)

Troyer's Part 6 formal framework is layered on top via the verdict
thresholds in `cost_advantage_ratio`.
"""

from typing import Dict, Any, Optional

from agents.classifier import azure_pricing


COST_MODEL_STATUS = "live_pricing_v1"
TROYER_PART_6_STATUS = "coming_soon"
TROYER_PART_6_URL = None

# Representative max circuit depth (gate layers) a current NISQ device can run
# before decoherence dominates. Used to keep per-shot cost estimates grounded
# in a hardware-runnable circuit rather than a deep fault-tolerant projection.
REPRESENTATIVE_NISQ_DEPTH = 1000

# Map orchestrator-level platform IDs onto azure_pricing target keys.
PLATFORM_TARGET_ALIASES = {
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

PLATFORM_HPC_ALIASES = {
    "azure_hpc_nd96amsr_a100": "Standard_ND96amsr_A100_v4",
    "azure_hpc_nd96isr_h100": "Standard_ND96isr_H100_v5",
    "azure_hpc_hbv4": "Standard_HB176rs_v4",
    "azure_hpc_hbv3": "Standard_HB120rs_v3",
}


def estimate_quantum_cost(
    physical_qubits: int,
    runtime_ns: int,
    target_platform: str = "azure_quantum_quantinuum_h2",
    shots: int = 100,
    logical_depth: Optional[int] = None,
) -> Dict[str, Any]:
    """Estimate the cost of running a quantum computation on a real provider.

    Uses provider-specific billing formulas (HQC for Quantinuum, AQT for IonQ,
    time-based for Rigetti) and applies minimum-job floors where the provider
    enforces them.
    """
    target_key = PLATFORM_TARGET_ALIASES.get(target_platform, target_platform)
    detail = azure_pricing.estimate_quantum_cost_for_target(
        target=target_key,
        physical_qubits=physical_qubits,
        runtime_ns=runtime_ns,
        logical_depth=logical_depth,
        shots=shots,
    )

    return {
        "platform": target_platform,
        "provider": detail.get("provider"),
        "estimated_cost_usd": detail.get("estimated_cost_usd"),
        "shots": shots,
        "cost_model": COST_MODEL_STATUS,
        "notes": detail.get("notes", ""),
        "billing_detail": {k: v for k, v in detail.items() if k not in {"provider", "notes"}},
        "troyer_part_6": TROYER_PART_6_STATUS,
        "caveat": (
            "Provider pricing as of May 2026 from learn.microsoft.com/azure/quantum/pricing. "
            "Final billing depends on subscription tier and error-mitigation flags."
        ),
    }


def estimate_hpc_cost(
    compute_hours: float,
    platform: str = "azure_hpc_nd96amsr_a100",
) -> Dict[str, Any]:
    """Estimate the cost of solving the same problem on Azure HPC/GPU."""
    sku = PLATFORM_HPC_ALIASES.get(platform, azure_pricing.DEFAULT_HPC_SKU)
    detail = azure_pricing.estimate_hpc_compute_cost(compute_hours=compute_hours, sku=sku)
    return {
        "platform": platform,
        "sku": sku,
        "estimated_cost_usd": detail["estimated_cost_usd"],
        "compute_hours": detail["compute_hours"],
        "usd_per_hour": detail["usd_per_hour"],
        "vcpus": detail.get("vcpus"),
        "family": detail.get("family"),
        "source": detail.get("source"),
        "notes": f"{detail.get('family', '')} @ ${detail['usd_per_hour']}/hr ({detail.get('source')})",
    }


def estimate_aml_cost(
    compute_hours: float,
    instance_size: str = "medium",
) -> Dict[str, Any]:
    """Estimate the cost of solving the same problem on Azure Machine Learning.

    AI/ML alternative for problems better served by classical/deep-learning
    approaches. ``instance_size`` (small | medium | large) maps to a
    representative single-accelerator AML compute SKU.
    """
    detail = azure_pricing.estimate_aml_compute_cost(
        compute_hours=compute_hours,
        instance_size=instance_size,
    )
    return {
        "platform": "azure_ml",
        "provider": detail.get("provider"),
        "sku": detail.get("sku"),
        "instance_size": detail.get("instance_size"),
        "estimated_cost_usd": detail.get("estimated_cost_usd"),
        "compute_hours": detail.get("compute_hours"),
        "usd_per_hour": detail.get("usd_per_hour"),
        "vcpus": detail.get("vcpus"),
        "family": detail.get("family"),
        "source": detail.get("source"),
        "notes": detail.get("notes", ""),
    }


def quantum_hardware_feasibility(
    physical_qubits: int,
    target_platform: str = "azure_quantum_quantinuum_h2",
    logical_depth: Optional[int] = None,
) -> Dict[str, Any]:
    """Check whether a circuit of this width/depth can run on today's hardware.

    A fault-tolerant resource estimate (often 10^4 to 10^6 physical qubits and
    very deep circuits) cannot be submitted to a device that only exposes tens
    of qubits with limited coherence, so the per-shot dollar figure is only
    physically meaningful for a hardware-runnable circuit. Returns the device
    width plus capped width/depth to use for grounded pricing.
    """
    target_key = PLATFORM_TARGET_ALIASES.get(target_platform, target_platform)
    hardware_qubits = azure_pricing.QUANTUM_HARDWARE_QUBITS.get(target_key, 56)
    width_ok = physical_qubits <= hardware_qubits
    depth_ok = logical_depth is None or logical_depth <= REPRESENTATIVE_NISQ_DEPTH
    feasible_today = width_ok and depth_ok

    priced_depth = (
        min(logical_depth, REPRESENTATIVE_NISQ_DEPTH)
        if isinstance(logical_depth, int)
        else None
    )
    return {
        "feasible_today": feasible_today,
        "estimated_physical_qubits": physical_qubits,
        "hardware_qubits": hardware_qubits,
        "priced_circuit_qubits": min(physical_qubits, hardware_qubits),
        "priced_circuit_depth": priced_depth,
        "representative_depth_cap": REPRESENTATIVE_NISQ_DEPTH,
        "note": (
            f"Runnable today on {target_key} ({hardware_qubits} qubits)."
            if feasible_today
            else (
                f"Fault-tolerant projection needs ~{physical_qubits:,} physical qubits; "
                f"{target_key} exposes {hardware_qubits}. Cost shown is for a "
                f"hardware-grounded representative circuit (width and depth capped) "
                f"at official per-shot rates."
            )
        ),
    }


def cost_advantage_ratio(
    quantum_cost: Dict[str, Any],
    hpc_cost: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare quantum vs HPC costs. Ratio > 1 means HPC is cheaper.

    Verdict thresholds will be replaced by Troyer's formal Part 6
    framework once published.
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
