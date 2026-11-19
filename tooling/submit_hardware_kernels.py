"""SUPERSEDED by tooling/run_simulator_matrix.py.

Despite the name and its "Submitting <problem> to <target>" output, this script
never contacted Azure Quantum. submit_kernel() calls qsharp.run(), which executes
on the local simulator, and the result was then written to azureRunHistory.json
carrying the requested target_id and no job id. Local results were therefore
indistinguishable from real hardware results once recorded.

It now prints the local results and refuses to write run history. Use
run_simulator_matrix.py, which labels every record with `execution` and stores the
Azure job id for anything that really was submitted.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__:
    from .discover_problems import discover_all_problems, resolve_problem_dir
else:
    from discover_problems import discover_all_problems, resolve_problem_dir

HISTORY_PATH = Path(__file__).resolve().parent.parent / "website" / "data" / "azureRunHistory.json"


def submit_kernel(problem_id: str, target_id: str) -> dict:
    """Compile and submit a HardwareKernel.qs to Azure Quantum."""
    from qdk import qsharp

    try:
        kernel_path = (
            resolve_problem_dir(problem_id) / "qsharp" / "HardwareKernel.qs"
        )
    except FileNotFoundError:
        return {"status": "skipped", "reason": "problem directory not found"}
    if not kernel_path.exists():
        return {"status": "skipped", "reason": "no HardwareKernel.qs"}

    code = kernel_path.read_text(encoding="utf-8")

    # Extract entry point name
    m = re.search(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)", code)
    if not m:
        return {"status": "skipped", "reason": "no @EntryPoint found"}

    entry_fn = m.group(1)

    try:
        qsharp.init()
        qsharp.eval(code)

        # For syntax checker, just compile - it validates QIR compatibility
        if "h2-1sc" in target_id:
            # Syntax check only - verify it compiles to QIR
            result = qsharp.run(f"{entry_fn}()", shots=1)
            return {
                "status": "succeeded",
                "target_id": target_id,
                "entry_point": entry_fn,
                "result": str(result),
            }
        else:
            # For simulators, run and get results
            result = qsharp.run(f"{entry_fn}()", shots=10)
            return {
                "status": "succeeded",
                "target_id": target_id,
                "entry_point": entry_fn,
                "result": str(result),
                "shots": 10,
            }
    except Exception as e:
        return {"status": "failed", "error": str(e)[:200]}


def append_to_history(runs: list):
    """Append new runs to the Azure run history."""
    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    else:
        history = {"schema_version": "1.0", "runs": []}

    history["runs"].extend(runs)
    history["updated_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "quantinuum.sim.h2-1sc"
    problems = sys.argv[2:] if len(sys.argv) > 2 else None

    new_runs = []
    for problem_dir in discover_all_problems():
        problem_id = problem_dir.name
        if not (problem_dir / "qsharp" / "HardwareKernel.qs").exists():
            continue
        if problems and problem_id not in problems:
            continue

        print(f"Submitting {problem_id} to {target}...", end=" ", flush=True)
        result = submit_kernel(problem_id, target)
        print(result["status"])

        if result["status"] == "succeeded":
            new_runs.append({
                "recorded_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "problem_id": problem_id,
                "instance_id": "small",
                "depth": 1,
                "target_id": target,
                "status": "succeeded",
            })

    if new_runs:
        print(f"\n{len(new_runs)} kernels ran on the LOCAL simulator.")
        print("Not recording to run history: these are not Azure Quantum runs.")
        print("Use 'python tooling/run_simulator_matrix.py' to submit and record real jobs.")
    else:
        print("\nNo successful runs")


if __name__ == "__main__":
    main()
