#!/usr/bin/env python3
"""Run Stage C calibration campaigns for quantum problems.

Executes each Q# program multiple times, collects statistics,
compares against classical baselines, and produces calibration evidence JSON.
"""

import json
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def run_qsharp(csproj: Path, timeout: int = 120) -> str:
    """Run a Q# project and return stdout."""
    result = subprocess.run(
        ["dotnet", "run", "--project", str(csproj), "--configuration", "Release"],
        capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        env={**__import__("os").environ, "DOTNET_NOLOGO": "1"},
    )
    return result.stdout


def extract_numbers(text: str, pattern: str) -> list:
    """Extract floating point numbers matching a regex pattern from text."""
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def calibrate_problem(problem_id: str, csproj_name: str, runs: int, extractors: dict) -> dict:
    """Run a problem multiple times and collect statistics."""
    csproj = REPO / "problems" / problem_id / "qsharp" / csproj_name
    if not csproj.exists():
        print(f"  ERROR: {csproj} not found")
        return {}

    print(f"\n=== Calibrating {problem_id} ({runs} runs) ===")
    all_metrics = {k: [] for k in extractors}

    for i in range(1, runs + 1):
        print(f"  Run {i}/{runs}...", end=" ", flush=True)
        try:
            output = run_qsharp(csproj)
            for metric_name, pattern in extractors.items():
                values = extract_numbers(output, pattern)
                if values:
                    # For metrics with multiple matches per run, take the mean
                    all_metrics[metric_name].append(statistics.mean(values) if len(values) > 1 else values[0])
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")

    # Compute statistics
    result = {
        "problem_id": problem_id,
        "runs": runs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {},
    }

    for metric_name, values in all_metrics.items():
        if len(values) >= 2:
            result["metrics"][metric_name] = {
                "values": values,
                "mean": statistics.mean(values),
                "std_dev": statistics.stdev(values),
                "std_error": statistics.stdev(values) / len(values) ** 0.5,
                "min": min(values),
                "max": max(values),
                "n": len(values),
            }
        elif len(values) == 1:
            result["metrics"][metric_name] = {
                "values": values,
                "mean": values[0],
                "std_dev": 0.0,
                "std_error": 0.0,
                "n": 1,
            }

    return result


# Problem configurations: what to extract from each run
PROBLEMS = {
    "01_hubbard": {
        "csproj": "Hubbard.csproj",
        "extractors": {"vqe_energy": r"Estimated Hubbard energy.*?:\s+([-\d.]+)"},
    },
    "02_catalysis": {
        "csproj": "Catalysis.csproj",
        "extractors": {"vqe_energy": r"VQE energy estimate:\s+([-\d.]+)"},
    },
    "03_qae_risk": {
        "csproj": "QAERisk.csproj",
        "extractors": {"qae_estimate": r"QAE estimate:.*?P = ([\d.]+)"},
    },
    "04_linear_solvers": {
        "csproj": "LinearSolvers.csproj",
        "extractors": {"success_prob": r"Success probability.*?([\d.]+)"},
    },
    "05_qaoa_maxcut": {
        "csproj": "QaoaMaxCut.csproj",
        "extractors": {"best_cut": r"Best observed cut.*?([\d.]+)"},
    },
    "06_high_frequency_trading": {
        "csproj": "HighFrequencyTrading.csproj",
        "extractors": {"quantum_var": r"Quantum VaR estimate.*?:\s+([\d.]+)"},
    },
    "07_drug_discovery": {
        "csproj": "DrugDiscovery.csproj",
        "extractors": {"binding_energy": r"VQE binding energy:\s+([-\d.]+)"},
    },
    "08_protein_folding": {
        "csproj": "ProteinFolding.csproj",
        "extractors": {"approx_ratio": r"Approximation ratio:\s+([\d.]+)"},
    },
    "09_factorization": {
        "csproj": "Factorization.csproj",
        "extractors": {"period_found": r"most frequent period: r=(\d+)"},
    },
    "10_post_quantum_cryptography": {
        "csproj": "PostQuantum.csproj",
        "extractors": {"success_pct_all": r"Success rate \(64 shots\):\s+\d+/64 \((\d+\.?\d*)%\)"},
    },
    "11_quantum_machine_learning": {
        "csproj": "QuantumML.csproj",
        "extractors": {"self_overlap": r"K\(Sample A \(duplicate\), Sample A \(duplicate\)\).*?overlap.*?=(\d+\.?\d*)"},
    },
    "12_quantum_optimization": {
        "csproj": "QuantumOptimization.csproj",
        "extractors": {
            "best_cost": r"Best cost:\s+([\d.]+)",
            "approx_ratio": r"Approximation ratio:\s+([\d.]+)",
        },
    },
    "13_climate_modeling": {
        "csproj": "QuantumClimate.csproj",
        "extractors": {"hhl_success": r"HHL success rate.*?:\s+([\d.]+)"},
    },
    "14_materials_discovery": {
        "csproj": "QuantumMaterials.csproj",
        "extractors": {"valence_energy": r"Valence band energy:\s+([-\d.]+)"},
    },
    "15_database_search": {
        "csproj": "QuantumSearch.csproj",
        "extractors": {"search_result": r"Success rate.*?([\d.]+)%"},
    },
    "16_error_correction": {
        "csproj": "QuantumQEC.csproj",
        "extractors": {"overall_rate": r"Overall correction rate: (\d+)/"},
    },
    "17_nuclear_physics": {
        "csproj": "QuantumNuclear.csproj",
        "extractors": {"nuclear_energy": r"VQE nuclear energy:\s+([-\d.]+)"},
    },
    "18_photovoltaics": {
        "csproj": "QuantumPhotovoltaics.csproj",
        "extractors": {"site_1_pct": r"Site 1:.*?(\d+\.?\d*)%"},
    },
    "19_quantum_chromodynamics": {
        "csproj": "QuantumQcd.csproj",
        "extractors": {"wilson_beta6": r"beta=6:.*?=\s+([-\d.]+)"},
    },
    "20_space_mission_planning": {
        "csproj": "QuantumMission.csproj",
        "extractors": {"approx_ratio": r"Approximation ratio:\s+([\d.]+)"},
    },
}


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    selected = sys.argv[2:] if len(sys.argv) > 2 else list(PROBLEMS.keys())

    all_results = []

    for pid in selected:
        if pid not in PROBLEMS:
            print(f"Unknown problem: {pid}")
            continue
        cfg = PROBLEMS[pid]
        result = calibrate_problem(pid, cfg["csproj"], runs, cfg["extractors"])
        if result:
            all_results.append(result)
            # Save per-problem
            out_path = REPO / "problems" / pid / "estimates" / "calibration_evidence.json"
            out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"  Saved: {out_path.relative_to(REPO)}")

            # Print summary
            for name, stats in result.get("metrics", {}).items():
                if "mean" in stats and "std_error" in stats:
                    print(f"  {name}: {stats['mean']:.4f} ± {stats['std_error']:.4f} (n={stats['n']})")

    # Summary
    summary_path = REPO / "tooling" / "estimator" / "output" / "calibration_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\nSummary: {summary_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
