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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover_problems import discover_all_problems
from estimator_config import (
    ENTRY_POINTS,
    QUBIT_MODELS,
    extract_summary,
    iter_model_configs,
    make_batch_estimator_params,
)


def main():
    import qsharp

    results = {}
    total_estimates = 0
    total_failures = 0
    start = time.time()

    problem_dirs = discover_all_problems()

    for pd in problem_dirs:
        name = pd.name
        qsharp_dir = pd / "qsharp"

        if not (qsharp_dir / "qsharp.json").exists():
            continue

        ep = ENTRY_POINTS.get(name)
        if ep is None:
            continue

        try:
            qsharp.init(project_root=str(qsharp_dir))
        except Exception as e:
            print(f"XX {name}: compile error -- {str(e)[:100]}")
            total_failures += 1
            continue

        # Build batched params: one estimate call evaluates every (qubit, QEC) combo.
        configs = list(iter_model_configs())  # [(model, qec, key), ...]
        params = make_batch_estimator_params([(m.name, qec) for m, qec, _ in configs])

        try:
            batch = qsharp.estimate(ep.expr(), params=params)
        except Exception as e:
            err = str(e)[:120]
            print(f"XX {name}: batch estimate failed -- {err}")
            total_failures += len(configs)
            continue

        problem_results = {"models": {}}

        for idx, (model, qec, config_key) in enumerate(configs):
            try:
                item = batch[idx]
                data = item.data() if hasattr(item, "data") else item
                summary = extract_summary(data)
                summary["qubitModel"] = model.name
                summary["qubitLabel"] = model.label
                summary["qecScheme"] = qec
                summary["family"] = model.family
                summary["speed"] = model.speed
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
        "qubit_models": [
            {
                "name": m.name,
                "label": m.label,
                "family": m.family,
                "speed": m.speed,
                "qec_schemes": list(m.qec_schemes),
            }
            for m in QUBIT_MODELS
        ],
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
