"""Run noisy simulation study: compare ideal vs depolarizing noise for all 20 problems.

Produces website/data/noisySimResults.json with:
  - Ideal results (noiseless)
  - Noisy results at error rates 0.001, 0.01, 0.05
  - Fidelity comparison
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import qsharp

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"
SHOTS = 100


def get_kernel_entry(problem_id):
    """Extract entry point name from HardwareKernel.qs."""
    kernel_path = PROBLEMS_DIR / problem_id / "qsharp" / "HardwareKernel.qs"
    if not kernel_path.exists():
        return None
    code = kernel_path.read_text(encoding="utf-8")
    m = re.search(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)", code)
    return m.group(1) if m else None


def run_kernel(problem_id, entry_fn, noise=None):
    """Run a kernel and return histogram of outcomes."""
    kernel_path = PROBLEMS_DIR / problem_id / "qsharp" / "HardwareKernel.qs"
    code = kernel_path.read_text(encoding="utf-8")
    qsharp.init()
    qsharp.eval(code)

    if noise:
        results = qsharp.run(f"{entry_fn}()", shots=SHOTS, noise=noise)
    else:
        results = qsharp.run(f"{entry_fn}()", shots=SHOTS)

    # Build histogram
    counts = {}
    for r in results:
        key = str(r)
        counts[key] = counts.get(key, 0) + 1

    # Sort by count
    histogram = [{"outcome": k, "count": v, "probability": round(v / SHOTS, 4)}
                 for k, v in sorted(counts.items(), key=lambda x: -x[1])]
    return histogram


def compute_fidelity(ideal, noisy):
    """Compute classical fidelity between two histograms."""
    ideal_map = {h["outcome"]: h["probability"] for h in ideal}
    noisy_map = {h["outcome"]: h["probability"] for h in noisy}
    all_keys = set(ideal_map) | set(noisy_map)
    fid = sum(
        (ideal_map.get(k, 0) * noisy_map.get(k, 0)) ** 0.5
        for k in all_keys
    )
    return round(fid ** 2, 4)


def main():
    noise_rates = [0.001, 0.01, 0.05]
    results = {}

    for d in sorted(os.listdir(PROBLEMS_DIR)):
        entry_fn = get_kernel_entry(d)
        if not entry_fn:
            continue

        print(f"{d} ({entry_fn}):", end=" ", flush=True)
        problem_data = {"entry_point": entry_fn}

        # Ideal run
        try:
            ideal = run_kernel(d, entry_fn, noise=None)
            problem_data["ideal"] = ideal
            top = ideal[0]["outcome"] if ideal else "?"
            print(f"ideal={top}({ideal[0]['count']})", end="", flush=True)
        except Exception as e:
            print(f"IDEAL FAIL: {str(e)[:80]}")
            continue

        # Noisy runs
        noisy_results = {}
        for rate in noise_rates:
            try:
                noise = qsharp.DepolarizingNoise(rate)
                noisy = run_kernel(d, entry_fn, noise=noise)
                fid = compute_fidelity(ideal, noisy)
                noisy_results[str(rate)] = {
                    "error_rate": rate,
                    "histogram": noisy,
                    "fidelity_vs_ideal": fid,
                }
                print(f" | p={rate}→fid={fid}", end="", flush=True)
            except Exception as e:
                noisy_results[str(rate)] = {"error_rate": rate, "error": str(e)[:80]}
                print(f" | p={rate}→ERR", end="", flush=True)

        problem_data["noisy"] = noisy_results
        results[d] = problem_data
        print()

    output = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "shots": SHOTS,
        "noise_model": "DepolarizingNoise",
        "noise_rates": noise_rates,
        "problems": results,
    }

    out_path = Path(__file__).resolve().parent.parent / "website" / "data" / "noisySimResults.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nSaved {len(results)} problems to {out_path.name}")

    # Summary
    print("\n=== Fidelity Summary ===")
    print(f"{'Problem':<35s} {'p=0.001':>8s} {'p=0.01':>8s} {'p=0.05':>8s}")
    for pid, data in results.items():
        noisy = data.get("noisy", {})
        f1 = noisy.get("0.001", {}).get("fidelity_vs_ideal", "?")
        f2 = noisy.get("0.01", {}).get("fidelity_vs_ideal", "?")
        f3 = noisy.get("0.05", {}).get("fidelity_vs_ideal", "?")
        print(f"{pid:<35s} {f1:>8} {f2:>8} {f3:>8}")


if __name__ == "__main__":
    main()
