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

from qdk import qsharp

import evidence_hashes
from estimator_config import ENTRY_POINTS, SHOTS_CALIBRATION

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"
WEBSITE_CALIBRATION = PROBLEMS_DIR.parent / "website" / "data" / "calibrationData.json"

# Per-problem calibration metadata: result interpretation + display blurb.
# Entry expressions are sourced from estimator_config.ENTRY_POINTS so the
# kernel signatures stay in sync across estimator / calibration / circuit
# tooling. ``entry_override`` is only set where calibration needs a kernel
# variant that differs from the estimator default (e.g., a wider clock
# register for HHL stability runs).
CALIBRATION_META: dict[str, dict] = {
    # The five QPE problems estimate at 10 phase bits; 20 calibration runs of that would take
    # hours on a simulator, so calibration samples the same programs at 8 bits.
    "01_hubbard": {
        "type": "numeric",
        "description": "QPE ground-state energy, two-site Hubbard model (t=1, U=4), 8 phase bits, mode of 8 runs",
        "entry_override": "Main.HubbardQPE(1.0, 4.0, 8, 8)",
    },
    "02_catalysis": {
        "type": "numeric",
        "description": "QPE total ground-state energy of H2, 8 phase bits, mode of 8 runs",
        "entry_override": "Main.MolecularQPE(8, 8)",
    },
    "03_qae_risk": {
        "type": "numeric",
        "description": "Canonical QAE, 6 phase bits: per-run estimate sin²(πy/64), register read most significant bit first (exact expectation 0.1686 for a = 0.1614)",
        "metric": "qae_amplitude",
    },
    "04_linear_solvers": {
        "type": "result",
        "description": "HHL on [[4,-1],[-1,3]] x = [15,10], 4-bit clock: post-selected system bit, whose mean estimates the second component of the normalized solution (exactly 0.5 for A^-1 b proportional to [5, 5])",
        # Calibration uses a 4-bit clock register for sharper eigenphase
        # resolution; the estimator path uses 3 to keep depth manageable.
        "entry_override": "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 4)",
    },
    "05_qaoa_maxcut": {"type": "numeric", "description": "Optimized p=1 QAOA MaxCut triangle graph; repository gamma convention has gamma_std=-2 gamma"},
    "06_high_frequency_trading": {"type": "numeric", "description": "Loss probability sampled directly from a 2-qubit state, no amplitude estimation (exact 0.9675)"},
    "07_drug_discovery": {
        "type": "numeric",
        "description": "QPE ground-state energy of the illustrative binding Hamiltonian, 8 phase bits, mode of 8 runs",
        "entry_override": "Main.BindingQPE(8, 8)",
    },
    "08_protein_folding": {"type": "numeric", "description": "Optimized p=1 QAOA on a four-variable toy Ising/QUBO energy, not a protein-folding model"},
    "09_factorization": {"type": "numeric", "description": "Shor period finding for a=7 mod 15: the 4-bit phase register reads 0, 4, 8 or 12"},
    "10_post_quantum_cryptography": {"type": "numeric", "description": "Grover key search: successful searches out of 50"},
    "11_quantum_machine_learning": {"type": "numeric", "description": "Swap test P(ancilla = 0) = (1 + |<a|b>|^2)/2 for the estimator vectors (exact 0.9175)"},
    "12_quantum_optimization": {"type": "numeric", "description": "Optimized p=1 QAOA on a four-job toy same-machine penalty QUBO"},
    "13_climate_modeling": {"type": "numeric", "description": "HHL on the 2x2 diffusion matrix [[2,-1],[-1,2]], 3-bit clock: fraction of shots heralding success (exact 5/9)"},
    "14_materials_discovery": {
        "type": "numeric",
        "description": "QPE band gap of the tight-binding dimer, 8 phase bits, mode of 8 runs per level",
        "entry_override": "Main.BandGapQPE(1.0, -0.5, 0.8, 0.3, 8, 8)",
    },
    "15_database_search": {"type": "numeric", "description": "Grover search for target=7 in 4-qubit space"},
    "16_error_correction": {
        "type": "result",
        "description": "3-qubit repetition code cycle: whether the decoded state matched",
        "tuple_index": 1,
    },
    "17_nuclear_physics": {
        "type": "numeric",
        "description": "QPE deuteron ground-state energy, 8 phase bits, mode of 8 runs",
        "entry_override": "Main.NuclearQPE(8, 8)",
    },
    "18_photovoltaics": {
        "type": "numeric",
        "description": "Quantum walk exciton transport: mean final site over 50 walks",
        "metric": "mean_index",
    },
    "19_quantum_chromodynamics": {"type": "numeric", "description": "Trotterized transverse-field Ising chain, 2 sites: mean Z-parity"},
    "20_space_mission_planning": {"type": "numeric", "description": "Optimized p=1 QAOA on the four-leg toy mission QUBO from RunMissionOptimization"},
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
        "tuple_index": meta.get("tuple_index", 0),
        "metric": meta.get("metric"),
    }
    for pid, meta in CALIBRATION_META.items()
}


def source_hashes(qsharp_dir: Path) -> dict[str, str]:
    """sha256 of every Q# source the ensemble ran, so stale evidence can be detected."""
    return evidence_hashes.source_hashes(qsharp_dir, PROBLEMS_DIR.parent)


def _as_number(value) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if str(value) in ("One", "Zero"):
        return 1.0 if str(value) == "One" else 0.0
    return None


def run_value(raw, config: dict) -> float | None:
    """The number one calibration run contributes, or None.

    qsharp.run(..., shots=1) returns a one-element list. The previous parser treated that
    list as the result itself, so every tuple- or list-valued kernel recorded 0 and every
    Result-valued one recorded nothing.
    """
    value = raw[0] if isinstance(raw, list) and len(raw) == 1 else raw
    if isinstance(value, tuple):
        value = value[config.get("tuple_index", 0)]
    number = _as_number(value)
    if number is not None:
        return number
    if isinstance(value, list) and value:
        if all(str(v) in ("One", "Zero") for v in value):
            if config.get("metric") == "qae_amplitude":
                # A QPE phase register, returned most significant bit first; outcome y estimates
                # the amplitude as sin^2(pi y / 2^m) (Brassard et al. 2002).
                y = sum(1 << (len(value) - 1 - i) for i, v in enumerate(value) if str(v) == "One")
                return math.sin(math.pi * y / (1 << len(value))) ** 2
            return float(sum(1 << i for i, v in enumerate(value) if str(v) == "One"))
        if config.get("metric") == "mean_index" and all(isinstance(v, int) for v in value) and sum(value):
            return sum(i * v for i, v in enumerate(value)) / sum(value)
    return None


def problem_dir(problem_id: str) -> Path:
    """Active problems live in problems/, archived ones in problems/archived/."""
    active = PROBLEMS_DIR / problem_id
    return active if active.is_dir() else PROBLEMS_DIR / "archived" / problem_id


def run_ensemble(problem_id: str, config: dict, num_runs: int) -> dict:
    """Run Q# kernel num_runs times and collect statistics."""
    qsharp_dir = problem_dir(problem_id) / "qsharp"
    qsharp.init(project_root=str(qsharp_dir))

    results = []
    raw_values = []
    for i in range(num_runs):
        t0 = time.time()
        raw = qsharp.run(config["entry"], shots=1)
        elapsed = time.time() - t0
        raw_values.append(raw)
        results.append({
            "run": i + 1,
            "raw_result": str(raw),
            "elapsed_s": round(elapsed, 4),
        })

    # Compute statistics
    elapsed_times = [r["elapsed_s"] for r in results]
    mean_time = sum(elapsed_times) / len(elapsed_times)
    std_time = math.sqrt(sum((t - mean_time) ** 2 for t in elapsed_times) / max(len(elapsed_times) - 1, 1))

    numeric_values = [v for v in (run_value(raw, config) for raw in raw_values) if v is not None]

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
        "sources": source_hashes(qsharp_dir),
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

    website = json.loads(WEBSITE_CALIBRATION.read_text(encoding="utf-8")) if WEBSITE_CALIBRATION.exists() else {}
    for pid in problems:
        config = CALIBRATION_TARGETS[pid]
        print(f"Running {num_runs} calibration runs for {pid}...")

        ensemble = run_ensemble(pid, config, num_runs)

        out_dir = problem_dir(pid) / "estimates"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "quantum_calibration_ensemble.json"
        out_path.write_text(json.dumps(ensemble, indent=2), encoding="utf-8")

        stats = ensemble["statistics"]
        mean_t = stats["mean_elapsed_s"]
        if "mean_value" in stats:
            print(f"  OK {pid}: mean={stats['mean_value']} ± {stats.get('ci95_half_width', '?')} (95% CI), {mean_t:.3f}s avg runtime")
        else:
            print(f"  OK {pid}: {num_runs} runs completed, {mean_t:.3f}s avg runtime")
        website[pid] = stats

    # The dashboard reads the same statistics; this script is the file's only writer, and
    # it merges by problem id so a partial run leaves the other problems untouched.
    WEBSITE_CALIBRATION.write_text(json.dumps(website, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
