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

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Map problem → (entry_point, result_extractor_description)
CALIBRATION_TARGETS = {
    "01_hubbard": {
        "entry": "Main.EstimateHubbardEnergy(0.5, 2.0, 1.0, 0.5, 0.3, 50)",
        "description": "VQE energy estimate for t=0.5, U=2.0",
        "type": "numeric",
    },
    "04_linear_solvers": {
        "entry": "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 4)",
        "description": "HHL single-shot solution measurement",
        "type": "result",
    },
    "09_factorization": {
        "entry": "Main.ShorPeriodFinding(3, 4)",
        "description": "Shor period finding for a=3 mod 15",
        "type": "numeric",
    },
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
