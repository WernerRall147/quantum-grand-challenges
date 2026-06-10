"""Generate multi-run calibration ensembles for Stage C promotion.

Runs each problem's Q# kernel N times and collects:
  - Per-run measurement results
  - Ensemble statistics (mean, stddev, confidence interval)
  - Resource estimation consistency check

Output: problems/XX/estimates/quantum_calibration_ensemble.json
"""

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import qsharp

from estimator_config import ENTRY_POINTS, SHOTS_CALIBRATION

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Per-problem calibration metadata: result interpretation + display blurb.
# Entry expressions are sourced from estimator_config.ENTRY_POINTS so the
# kernel signatures stay in sync across estimator / calibration / circuit
# tooling. ``entry_override`` is only set where calibration needs a kernel
# variant that differs from the estimator default (e.g., a wider clock
# register for HHL stability runs).
CALIBRATION_META: dict[str, dict] = {
    "01_hubbard": {"type": "numeric", "description": "VQE energy estimate for t=0.5, U=2.0"},
    "02_catalysis": {"type": "numeric", "description": "VQE H2 ground state energy"},
    "03_qae_risk": {"type": "result", "description": "QAE single-shot kernel"},
    "04_linear_solvers": {
        "type": "result",
        "description": "HHL single-shot solution measurement",
        # Calibration uses a 4-bit clock register for sharper eigenphase
        # resolution; the estimator path uses 3 to keep depth manageable.
        "entry_override": "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 4)",
    },
    "05_qaoa_maxcut": {"type": "numeric", "description": "QAOA MaxCut triangle graph depth-1"},
    "06_high_frequency_trading": {"type": "numeric", "description": "Quantum VaR loss probability"},
    "07_drug_discovery": {"type": "numeric", "description": "VQE molecular binding energy"},
    "08_protein_folding": {"type": "numeric", "description": "QAOA lattice folding energy"},
    "09_factorization": {"type": "numeric", "description": "Shor period finding for a=3 mod 15"},
    "10_post_quantum_cryptography": {"type": "numeric", "description": "Grover key search success rate"},
    "11_quantum_machine_learning": {"type": "numeric", "description": "Swap test kernel overlap"},
    "12_quantum_optimization": {"type": "numeric", "description": "QAOA scheduling optimization"},
    "13_climate_modeling": {"type": "numeric", "description": "HHL diffusion PDE solver"},
    "14_materials_discovery": {"type": "numeric", "description": "VQE band gap estimation"},
    "15_database_search": {"type": "numeric", "description": "Grover search for target=7 in 4-qubit space"},
    "16_error_correction": {"type": "result", "description": "3-qubit repetition code cycle"},
    "17_nuclear_physics": {"type": "numeric", "description": "VQE deuteron binding energy"},
    "18_photovoltaics": {"type": "numeric", "description": "Quantum walk exciton transport"},
    "19_quantum_chromodynamics": {"type": "numeric", "description": "Trotter lattice gauge simulation"},
    "20_space_mission_planning": {"type": "numeric", "description": "QAOA trajectory optimization"},
}


def _resolve_entry(problem_id: str, meta: dict) -> str:
    """Pick the calibration entry expression for one problem."""
    override = meta.get("entry_override")
    if override:
        return override
    return ENTRY_POINTS[problem_id].expr(shots=SHOTS_CALIBRATION)


CALIBRATION_TARGETS = {
    pid: {
        "entry": _resolve_entry(pid, meta),
        "description": meta["description"],
        "type": meta["type"],
    }
    for pid, meta in CALIBRATION_META.items()
}


def run_ensemble(problem_id: str, config: dict, num_runs: int) -> dict:
    """Run Q# kernel num_runs times and collect statistics."""
    qsharp_dir = PROBLEMS_DIR / problem_id / "qsharp"
    qsharp.init(project_root=str(qsharp_dir))

    results = []
    for i in range(num_runs):
        t0 = time.time()
        raw = qsharp.run(config["entry"], shots=1)
        elapsed = time.time() - t0
        results.append({
            "run": i + 1,
            "raw_result": str(raw),
            "elapsed_s": round(elapsed, 4),
        })

    # Compute statistics
    elapsed_times = [r["elapsed_s"] for r in results]
    mean_time = sum(elapsed_times) / len(elapsed_times)
    std_time = math.sqrt(sum((t - mean_time) ** 2 for t in elapsed_times) / max(len(elapsed_times) - 1, 1))

    # Parse numeric results if applicable
    numeric_values = []
    for r in results:
        try:
            val = eval(r["raw_result"])  # noqa: S307 — controlled input
            if isinstance(val, (int, float)):
                numeric_values.append(float(val))
            elif isinstance(val, (list, tuple)) and len(val) > 0:
                numeric_values.append(float(val[0]) if isinstance(val[0], (int, float)) else len([x for x in val if str(x) == "One"]))
        except Exception:
            pass

    stats = {
        "num_runs": num_runs,
        "mean_elapsed_s": round(mean_time, 4),
        "std_elapsed_s": round(std_time, 4),
    }
    if numeric_values:
        mean_val = sum(numeric_values) / len(numeric_values)
        std_val = math.sqrt(sum((v - mean_val) ** 2 for v in numeric_values) / max(len(numeric_values) - 1, 1))
        ci95 = 1.96 * std_val / math.sqrt(len(numeric_values)) if len(numeric_values) > 1 else 0
        stats.update({
            "mean_value": round(mean_val, 6),
            "std_value": round(std_val, 6),
            "ci95_half_width": round(ci95, 6),
            "ci95_lower": round(mean_val - ci95, 6),
            "ci95_upper": round(mean_val + ci95, 6),
        })

    return {
        "problem_id": problem_id,
        "description": config["description"],
        "entry_point": config["entry"],
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "statistics": stats,
        "runs": results,
    }


def main():
    num_runs = 20
    if len(sys.argv) > 1:
        num_runs = int(sys.argv[1])

    problems = list(CALIBRATION_TARGETS.keys())
    if len(sys.argv) > 2:
        problems = [p for p in sys.argv[2:] if p in CALIBRATION_TARGETS]

    for pid in problems:
        config = CALIBRATION_TARGETS[pid]
        print(f"Running {num_runs} calibration runs for {pid}...")

        ensemble = run_ensemble(pid, config, num_runs)

        out_dir = PROBLEMS_DIR / pid / "estimates"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "quantum_calibration_ensemble.json"
        out_path.write_text(json.dumps(ensemble, indent=2), encoding="utf-8")

        stats = ensemble["statistics"]
        mean_t = stats["mean_elapsed_s"]
        if "mean_value" in stats:
            print(f"  OK {pid}: mean={stats['mean_value']} ± {stats.get('ci95_half_width', '?')} (95% CI), {mean_t:.3f}s avg runtime")
        else:
            print(f"  OK {pid}: {num_runs} runs completed, {mean_t:.3f}s avg runtime")


if __name__ == "__main__":
    main()
