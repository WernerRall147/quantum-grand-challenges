"""Live Azure pricing helpers for the cost model.

Two pricing surfaces:
  1. Azure Retail Prices API (public, no auth)  used for compute SKUs.
  2. Static provider rates digested from the Azure Quantum pricing page,
     because quantum-provider economics are formula-driven (HQC, AQT, time)
     and the retail-prices API does not yet model them with the right shape.

Cached locally with a 24h TTL to avoid hammering the API.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import urllib.request
    import urllib.parse
except ImportError:  # pragma: no cover - stdlib always present
    urllib = None  # type: ignore


CACHE_DIR = Path(os.environ.get("QGC_PRICING_CACHE", str(Path.home() / ".cache" / "qgc")))
CACHE_FILE = CACHE_DIR / "azure_pricing.json"
CACHE_TTL_SECONDS = 24 * 3600

RETAIL_PRICES_API = "https://prices.azure.com/api/retail/prices"

# --- Quantum provider rates (from learn.microsoft.com/azure/quantum/pricing) ---
# These are formula-driven and not exposed in the retail-prices API.
# Sourced May 2026; refresh when Azure updates the pricing page.

QUANTINUUM_H2 = {
    "name": "Quantinuum H2-1",
    "qubits": 56,
    "profile": "Adaptive_RI",
    # HQC formula: HQC = 5 + C * (N1q + 10*N2q + 5*Nm) / 5000
    # where C = number of shots
    "hqc_base": 5,
    "hqc_per_circuit_factor": 1.0 / 5000,
    "weight_1q": 1,
    "weight_2q": 10,
    "weight_measurement": 5,
    # Standard subscription: $125k/mo, 50k HQC/mo => $2.50 per HQC
    # Premium subscription: $175k/mo, 100k HQC/mo => $1.75 per HQC
    # Pay-as-you-go (informational): typically billed against subscription pool.
    "usd_per_hqc_standard": 2.50,
    "usd_per_hqc_premium": 1.75,
    "min_cost_usd": 0.0,  # billing is HQC-based, no per-job floor
    "notes": "HQC = 5 + C*(N1q + 10*N2q + 5*Nm)/5000; Standard $2.50/HQC, Premium $1.75/HQC.",
}

IONQ_ARIA = {
    "name": "IonQ Aria 1",
    "qubits": 25,
    "profile": "Base / Adaptive_RI",
    # AQT-style billing: per-shot, weighted by gate type.
    "usd_per_1q_gate_shot": 0.000220,
    "usd_per_2q_gate_shot": 0.000975,
    # Minimum-job floors
    "min_cost_usd_with_mitigation": 97.50,
    "min_cost_usd_no_mitigation": 12.4166,
    "notes": (
        "Per-shot pricing: $0.000220 (1q), $0.000975 (2q). "
        "Min job $97.50 with debiasing/mitigation, $12.42 without."
    ),
}

IONQ_FORTE = {
    "name": "IonQ Forte 1",
    "qubits": 36,
    "profile": "Base / Adaptive_RI",
    "usd_per_1q_gate_shot": 0.0001645,
    "usd_per_2q_gate_shot": 0.001121,
    "min_cost_usd_with_mitigation": 168.195,
    "min_cost_usd_no_mitigation": 21.273,
    "notes": (
        "Per-shot pricing: $0.0001645 (1q), $0.001121 (2q). "
        "Min job $168.20 with debiasing/mitigation."
    ),
}

RIGETTI_CEPHEUS = {
    "name": "Rigetti Cepheus-1-108Q",
    "qubits": 108,
    "profile": "Base",
    # Time-based billing: $0.02 per 10ms = $2.00 per second of wall time.
    "usd_per_second": 2.00,
    "min_cost_usd": 0.0,
    "notes": "Time-based: $0.02 per 10ms execution window.",
}

PASQAL_FRESNEL = {
    "name": "Pasqal Fresnel-1",
    "qubits": 100,
    "profile": "neutral atom analog",
    # Pasqal pricing on Azure is subscription-only; expose null so callers
    # surface the right caveat instead of a fake number.
    "usd_per_second": None,
    "min_cost_usd": None,
    "notes": "Subscription pricing only  contact Azure for quote.",
}


QUANTUM_PROVIDER_RATES: Dict[str, Dict[str, Any]] = {
    "quantinuum_h2": QUANTINUUM_H2,
    "ionq_aria": IONQ_ARIA,
    "ionq_forte": IONQ_FORTE,
    "rigetti_cepheus": RIGETTI_CEPHEUS,
    "pasqal_fresnel": PASQAL_FRESNEL,
}


# --- Azure HPC / GPU SKU fallback rates (East US, Pay-as-you-go, USD/hr) ---
# Refreshed via fetch_azure_compute_rates(); these are the offline fallback.
_AZURE_COMPUTE_FALLBACK: Dict[str, Dict[str, Any]] = {
    "Standard_HB176rs_v4": {"usd_per_hour": 7.20, "vcpus": 176, "family": "HPC AMD EPYC"},
    "Standard_HB120rs_v3": {"usd_per_hour": 3.60, "vcpus": 120, "family": "HPC AMD EPYC"},
    "Standard_HC44rs": {"usd_per_hour": 2.20, "vcpus": 44, "family": "HPC Intel Xeon Platinum"},
    "Standard_ND96amsr_A100_v4": {"usd_per_hour": 27.197, "vcpus": 96, "family": "8x A100 80GB"},
    "Standard_ND96isr_H100_v5": {"usd_per_hour": 98.32, "vcpus": 96, "family": "8x H100 NVLink"},
    "Standard_ND96asr_v4": {"usd_per_hour": 27.20, "vcpus": 96, "family": "8x A100 40GB"},
}

DEFAULT_HPC_SKU = "Standard_HB176rs_v4"
DEFAULT_GPU_SKU = "Standard_ND96amsr_A100_v4"
DEFAULT_REGION = "eastus"


# --- Cache helpers ---


def _load_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {}
    try:
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if time.time() - cache.get("fetched_at", 0) > CACHE_TTL_SECONDS:
        return {}
    return cache


def _write_cache(payload: Dict[str, Any]) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        pass  # caching is best-effort


def _fetch_retail_prices(filter_query: str, timeout: float = 8.0) -> List[Dict[str, Any]]:
    """Query the Azure Retail Prices OData endpoint. Returns [] on any failure."""
    if urllib is None:
        return []
    safe_chars = "()/=, '"
    encoded = urllib.parse.quote(filter_query, safe=safe_chars)
    url = f"{RETAIL_PRICES_API}?$filter={encoded}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "qgc-evaluator/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - public read-only API
            payload = json.loads(resp.read().decode("utf-8"))
        return payload.get("Items", []) or []
    except Exception:
        return []


def fetch_azure_compute_rates(
    skus: Optional[List[str]] = None,
    region: str = DEFAULT_REGION,
    use_cache: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """Return {sku: {usd_per_hour, vcpus, family, source}} for the given SKUs.

    Falls back to hardcoded constants on network failure or partial coverage.
    """
    skus = skus or [DEFAULT_HPC_SKU, DEFAULT_GPU_SKU, "Standard_HB120rs_v3", "Standard_ND96isr_H100_v5"]

    if use_cache:
        cached = _load_cache()
        cached_rates = cached.get("compute_rates", {}).get(region, {})
        if all(s in cached_rates for s in skus):
            return {s: cached_rates[s] for s in skus}

    out: Dict[str, Dict[str, Any]] = {}
    for sku in skus:
        # Filter: ARM SKU + region + Pay-as-you-go (no reservation/spot)
        flt = (
            f"armSkuName eq '{sku}' and armRegionName eq '{region}' "
            f"and priceType eq 'Consumption' and contains(tolower(skuName), 'low priority') eq false "
            f"and contains(tolower(skuName), 'spot') eq false"
        )
        items = _fetch_retail_prices(flt)
        if items:
            # Pick the lowest hourly Linux on-demand entry
            linux_items = [
                i for i in items
                if "windows" not in str(i.get("productName", "")).lower()
                and i.get("unitOfMeasure", "").startswith("1 Hour")
            ]
            chosen = min(linux_items or items, key=lambda i: i.get("retailPrice", 1e9))
            fallback = _AZURE_COMPUTE_FALLBACK.get(sku, {})
            out[sku] = {
                "usd_per_hour": float(chosen.get("retailPrice") or fallback.get("usd_per_hour") or 0.0),
                "vcpus": fallback.get("vcpus"),
                "family": fallback.get("family", chosen.get("productName", "")),
                "source": "azure_retail_prices_api",
                "region": region,
            }
        else:
            fallback = _AZURE_COMPUTE_FALLBACK.get(sku)
            if fallback:
                out[sku] = {**fallback, "source": "static_fallback", "region": region}

    if out:
        cached = _load_cache() or {"fetched_at": 0, "compute_rates": {}}
        cached["fetched_at"] = time.time()
        cached.setdefault("compute_rates", {}).setdefault(region, {}).update(out)
        _write_cache(cached)

    return out


# --- Quantum provider cost formulas ---


def estimate_quantinuum_hqc_cost(
    n_1q_gates: int,
    n_2q_gates: int,
    n_measurements: int,
    shots: int = 100,
    tier: str = "standard",
) -> Dict[str, Any]:
    """Compute Quantinuum H2 cost via the official HQC formula.

    HQC = 5 + C * (N1q + 10*N2q + 5*Nm) / 5000
    where C is the shot count (called 'circuit repeats' in pricing docs).
    """
    rates = QUANTINUUM_H2
    weighted = (
        rates["weight_1q"] * n_1q_gates
        + rates["weight_2q"] * n_2q_gates
        + rates["weight_measurement"] * n_measurements
    )
    hqcs = rates["hqc_base"] + shots * weighted * rates["hqc_per_circuit_factor"]
    usd_per_hqc = (
        rates["usd_per_hqc_premium"] if tier.lower() == "premium" else rates["usd_per_hqc_standard"]
    )
    return {
        "provider": rates["name"],
        "hqcs": round(hqcs, 2),
        "usd_per_hqc": usd_per_hqc,
        "tier": tier,
        "estimated_cost_usd": round(hqcs * usd_per_hqc, 2),
        "shots": shots,
        "formula": "HQC = 5 + C*(N1q + 10*N2q + 5*Nm)/5000",
        "notes": rates["notes"],
    }


def estimate_ionq_cost(
    n_1q_gates: int,
    n_2q_gates: int,
    shots: int = 100,
    target: str = "aria",
    error_mitigation: bool = True,
) -> Dict[str, Any]:
    """Compute IonQ Aria/Forte cost via per-shot AQT-style billing."""
    rates = IONQ_FORTE if target.lower() == "forte" else IONQ_ARIA
    raw_cost = shots * (
        n_1q_gates * rates["usd_per_1q_gate_shot"]
        + n_2q_gates * rates["usd_per_2q_gate_shot"]
    )
    floor = (
        rates["min_cost_usd_with_mitigation"]
        if error_mitigation
        else rates["min_cost_usd_no_mitigation"]
    )
    final_cost = max(floor, raw_cost)
    return {
        "provider": rates["name"],
        "raw_cost_usd": round(raw_cost, 2),
        "min_cost_floor_usd": floor,
        "estimated_cost_usd": round(final_cost, 2),
        "shots": shots,
        "error_mitigation": error_mitigation,
        "notes": rates["notes"],
    }


def estimate_rigetti_cost(
    runtime_seconds: float,
    shots: int = 1000,
) -> Dict[str, Any]:
    """Compute Rigetti time-based cost. Multi-shot wall time scales near-linearly."""
    rates = RIGETTI_CEPHEUS
    # Wall time per shot is ~10ms minimum; effective runtime is roughly shots * runtime_seconds
    # but for short circuits Rigetti batches shots  use the larger of (per-shot, total) heuristic.
    effective_seconds = max(runtime_seconds, shots * 0.01)
    cost = effective_seconds * rates["usd_per_second"]
    return {
        "provider": rates["name"],
        "effective_runtime_seconds": round(effective_seconds, 3),
        "estimated_cost_usd": round(cost, 2),
        "shots": shots,
        "rate": "$0.02 per 10ms",
        "notes": rates["notes"],
    }


def estimate_hpc_compute_cost(
    compute_hours: float,
    sku: str = DEFAULT_HPC_SKU,
    region: str = DEFAULT_REGION,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """Cost of running on Azure HPC/GPU. Pulls live retail price when available."""
    rates_map = fetch_azure_compute_rates([sku], region=region, use_cache=use_cache)
    rate = rates_map.get(sku) or _AZURE_COMPUTE_FALLBACK.get(sku, {"usd_per_hour": 0.0})
    cost = compute_hours * rate["usd_per_hour"]
    return {
        "platform": f"azure_hpc_{sku.lower()}",
        "sku": sku,
        "region": region,
        "estimated_cost_usd": round(cost, 2),
        "compute_hours": round(compute_hours, 3),
        "usd_per_hour": rate["usd_per_hour"],
        "vcpus": rate.get("vcpus"),
        "family": rate.get("family", ""),
        "source": rate.get("source", "static_fallback"),
    }


# --- Algorithm-class-aware default targets ---

ALGORITHM_TO_TARGET = {
    "QPE": "quantinuum_h2",
    "Shor": "quantinuum_h2",
    "Trotter": "quantinuum_h2",
    "Quantum Walk": "quantinuum_h2",
    "QEC": "quantinuum_h2",
    "VQE": "ionq_aria",
    "QAOA": "ionq_aria",
    "Swap Test": "ionq_aria",
    "Grover": "ionq_aria",
    "QAE": "ionq_aria",
    "HHL": "rigetti_cepheus",
}


def recommended_quantum_target(algorithm: str) -> str:
    """Pick a representative quantum provider for the algorithm class."""
    if not algorithm:
        return "quantinuum_h2"
    for key, target in ALGORITHM_TO_TARGET.items():
        if key.lower() in algorithm.lower():
            return target
    return "quantinuum_h2"


def estimate_quantum_cost_for_target(
    target: str,
    physical_qubits: int,
    runtime_ns: int,
    logical_depth: Optional[int] = None,
    shots: int = 100,
) -> Dict[str, Any]:
    """Convert resource-estimator output into provider-specific cost.

    Maps abstract resource counts onto the provider's billing formula:
      - Quantinuum: derive 1q/2q/measurement counts from logical depth
      - IonQ:       same gate counts, but billed per-shot AQT-style
      - Rigetti:    convert runtime_ns → wall-seconds, billed by time
    """
    # Heuristic: physical_qubits gives circuit width; logical_depth gives gate-layer count.
    # Assume each layer is ~half 1q + half 2q gates with ~1 measurement per qubit.
    depth = logical_depth or max(1, int(runtime_ns / 1_000_000))
    n_1q = max(1, physical_qubits * depth // 2)
    n_2q = max(1, physical_qubits * depth // 2)
    n_meas = max(1, physical_qubits)

    if target.startswith("quantinuum"):
        return estimate_quantinuum_hqc_cost(n_1q, n_2q, n_meas, shots=shots)
    if target == "ionq_aria":
        return estimate_ionq_cost(n_1q, n_2q, shots=shots, target="aria")
    if target == "ionq_forte":
        return estimate_ionq_cost(n_1q, n_2q, shots=shots, target="forte")
    if target == "rigetti_cepheus":
        return estimate_rigetti_cost(runtime_seconds=runtime_ns / 1e9, shots=shots)
    if target == "pasqal_fresnel":
        return {
            "provider": PASQAL_FRESNEL["name"],
            "estimated_cost_usd": None,
            "notes": PASQAL_FRESNEL["notes"],
        }
    return {"provider": target, "estimated_cost_usd": None, "notes": "unknown target"}


__all__ = [
    "QUANTUM_PROVIDER_RATES",
    "QUANTINUUM_H2",
    "IONQ_ARIA",
    "IONQ_FORTE",
    "RIGETTI_CEPHEUS",
    "PASQAL_FRESNEL",
    "DEFAULT_HPC_SKU",
    "DEFAULT_GPU_SKU",
    "DEFAULT_REGION",
    "fetch_azure_compute_rates",
    "estimate_quantinuum_hqc_cost",
    "estimate_ionq_cost",
    "estimate_rigetti_cost",
    "estimate_hpc_compute_cost",
    "estimate_quantum_cost_for_target",
    "recommended_quantum_target",
]
