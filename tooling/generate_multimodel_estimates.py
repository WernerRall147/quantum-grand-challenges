#!/usr/bin/env python3
"""Generate multi-model resource estimates for all 20 problems.

Runs qsharp.estimate() across 6 qubit models × 2 QEC schemes (surface_code +
floquet_code where applicable), inspired by Dr. Matthias Troyer's
"Building the Modern Quantum Architecture" lecture series.

Qubit models (from Azure Quantum Resource Estimator):
  - qubit_gate_ns_e3: Superconducting/spin, ns gates, 1e-3 error (realistic)
  - qubit_gate_ns_e4: Superconducting/spin, ns gates, 1e-4 error (optimistic)
  - qubit_gate_us_e3: Trapped ion, μs gates, 1e-3 error (realistic)
  - qubit_gate_us_e4: Trapped ion, μs gates, 1e-4 error (optimistic)
  - qubit_maj_ns_e4:  Majorana, ns gates, 1e-4 error (realistic)
  - qubit_maj_ns_e6:  Majorana, ns gates, 1e-6 error (optimistic)

QEC schemes:
  - surface_code: Works with all qubit types
  - floquet_code: Only works with Majorana qubits

Output: website/data/multiModelEstimates.json
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "website" / "data" / "multiModelEstimates.json"

ENTRY_POINTS = {
    "01_hubbard": "Main.EstimateHubbardEnergy(0.5, 2.0, 1.0, 0.5, 0.3, 1)",
    "02_catalysis": "Main.EstimateMolecularEnergy(1.0, 0.5, 0.3, 1)",
    "03_qae_risk": "Main.QAEKernel()",
    "04_linear_solvers": "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)",
    "05_qaoa_maxcut": "Main.EvaluateQaoa([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]], [0.5], [0.5], 1)",
    "06_high_frequency_trading": "Main.EstimateLossProbability([0.05, -0.03, 0.02], 1, 1)",
    "07_drug_discovery": "Main.EstimateBindingEnergy(1.0, 0.5, 0.3, 1)",
    "08_protein_folding": "Main.EvaluateFoldingQaoa([[0.0,1.0],[1.0,0.0]], 0.5, 0.5, 1)",
    "09_factorization": "Main.ShorPeriodFinding(3, 4)",
    "10_post_quantum_cryptography": "Main.GroverKeySearch(3, 5, 1)",
    "11_quantum_machine_learning": "Main.SwapTest([1.0, 0.5, 0.3, 0.2], [0.8, 0.2, 0.6, 0.1], 1)",
    "12_quantum_optimization": "Main.EvaluateQaoa([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], 0.5, 0.5, 1, 1)",
    "13_climate_modeling": "Main.RunHHLClimate(3, 1)",
    "14_materials_discovery": "Main.EstimateBandGap(1.0, -0.5, 0.8, 0.3, 1)",
    "15_database_search": "Main.GroverSearch([7], 4, 3)",
    "16_error_correction": "Main.RunRepetitionCodeCycle(false, 0)",
    "17_nuclear_physics": "Main.EstimateNuclearEnergy(1.0, 0.5, 0.3, 1)",
    "18_photovoltaics": "Main.RunExcitonWalk(10, 0.5, 1)",
    "19_quantum_chromodynamics": "Main.SimulateLatticeGauge(2, 1.0, 0.5, 3, 1)",
    "20_space_mission_planning": "Main.EvaluateQaoaMission([[0.0,1.0,0.5],[1.0,0.0,0.8],[0.5,0.8,0.0]], 0.5, 0.5, 1, 1)",
}

# All qubit models with their QEC compatibility
QUBIT_MODELS = [
    {"name": "qubit_gate_ns_e3", "label": "Superconducting (ns, 1e-3)", "qec": ["surface_code"], "family": "gate_based", "speed": "ns"},
    {"name": "qubit_gate_ns_e4", "label": "Superconducting (ns, 1e-4)", "qec": ["surface_code"], "family": "gate_based", "speed": "ns"},
    {"name": "qubit_gate_us_e3", "label": "Trapped Ion (μs, 1e-3)", "qec": ["surface_code"], "family": "gate_based", "speed": "us"},
    {"name": "qubit_gate_us_e4", "label": "Trapped Ion (μs, 1e-4)", "qec": ["surface_code"], "family": "gate_based", "speed": "us"},
    {"name": "qubit_maj_ns_e4", "label": "Majorana (ns, 1e-4)", "qec": ["surface_code", "floquet_code"], "family": "majorana", "speed": "ns"},
    {"name": "qubit_maj_ns_e6", "label": "Majorana (ns, 1e-6)", "qec": ["surface_code", "floquet_code"], "family": "majorana", "speed": "ns"},
]


def extract_summary(estimate):
    """Extract key metrics from a qsharp.estimate() result."""
    pc = estimate.get("physicalCounts", {})
    lc = estimate.get("logicalCounts", {})
    bd = pc.get("breakdown", {})
    return {
        "physicalQubits": pc.get("physicalQubits"),
        "runtime": pc.get("runtime"),
        "rqops": pc.get("rqops"),
        "logicalQubits": bd.get("algorithmicLogicalQubits"),
        "logicalDepth": lc.get("logicalDepth"),
        "tCount": lc.get("tCount"),
        "rotationCount": lc.get("rotationCount"),
        "codeDistance": bd.get("logicalPatch", {}).get("codeDistance") if isinstance(bd.get("logicalPatch"), dict) else None,
    }


def main():
    import qsharp

    results = {}
    total_estimates = 0
    total_failures = 0
    start = time.time()

    problem_dirs = sorted(
        [d for d in PROBLEMS_DIR.iterdir() if d.is_dir() and d.name[:2].isdigit()],
        key=lambda d: d.name,
    )

    for pd in problem_dirs:
        name = pd.name
        qsharp_dir = pd / "qsharp"

        if not (qsharp_dir / "qsharp.json").exists():
            continue

        entry = ENTRY_POINTS.get(name)
        if not entry:
            continue

        try:
            qsharp.init(project_root=str(qsharp_dir))
        except Exception as e:
            print(f"XX {name}: compile error — {str(e)[:100]}")
            total_failures += 1
            continue

        problem_results = {"models": {}}

        for model in QUBIT_MODELS:
            for qec in model["qec"]:
                config_key = f"{model['name']}+{qec}"
                try:
                    estimate = qsharp.estimate(
                        entry,
                        params={
                            "qubitParams": {"name": model["name"]},
                            "qecScheme": {"name": qec},
                        },
                    )
                    summary = extract_summary(estimate)
                    summary["qubitModel"] = model["name"]
                    summary["qubitLabel"] = model["label"]
                    summary["qecScheme"] = qec
                    summary["family"] = model["family"]
                    summary["speed"] = model["speed"]
                    problem_results["models"][config_key] = summary
                    total_estimates += 1

                    pq = summary.get("physicalQubits", "?")
                    print(f"  OK {name} [{config_key}]: {pq} physical qubits")

                except Exception as e:
                    err = str(e)[:120]
                    print(f"  XX {name} [{config_key}]: {err}")
                    total_failures += 1

        if problem_results["models"]:
            results[name] = problem_results

    elapsed = time.time() - start

    output = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "qubit_models": [{"name": m["name"], "label": m["label"], "family": m["family"], "speed": m["speed"], "qec_schemes": m["qec"]} for m in QUBIT_MODELS],
        "total_estimates": total_estimates,
        "total_failures": total_failures,
        "elapsed_seconds": round(elapsed, 1),
        "problems": results,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"\nDone: {total_estimates} estimates, {total_failures} failures in {elapsed:.1f}s")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    sys.exit(main() or 0)
