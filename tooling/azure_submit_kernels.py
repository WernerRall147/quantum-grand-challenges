"""Submit HardwareKernel.qs to real Azure Quantum targets via qsharp.compile + az CLI."""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"
HISTORY_PATH = Path(__file__).resolve().parent.parent / "website" / "data" / "azureRunHistory.json"


def compile_kernel(problem_id, target_profile):
    import qsharp
    kernel_path = PROBLEMS_DIR / problem_id / "qsharp" / "HardwareKernel.qs"
    code = kernel_path.read_text(encoding="utf-8")
    m = re.search(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)", code)
    if not m:
        return None, None
    entry_fn = m.group(1)
    qsharp.init(target_profile=target_profile)
    qsharp.eval(code)
    qir = qsharp.compile(f"{entry_fn}()")
    return entry_fn, qir


def append_to_history(runs):
    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    else:
        history = {"schema_version": "1.0", "runs": []}
    history["runs"].extend(runs)
    history["updated_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")


def submit_via_cli(problem_id, target_id, qir_data, shots):
    """Submit QIR to Azure Quantum via az quantum job submit."""
    import pyqir

    # QirInputData stores LLVM IR as _ll_str — convert to bitcode (.bc) for Azure
    if hasattr(qir_data, "_ll_str"):
        qir_text = qir_data._ll_str
    else:
        qir_text = str(qir_data)

    # Parse LLVM IR to Module and write bitcode
    mod = pyqir.Module.from_ir(pyqir.Context(), qir_text)
    tmp = tempfile.NamedTemporaryFile(suffix=".bc", delete=False)
    tmp.write(mod.bitcode)
    tmp.close()
    qir_path = tmp.name
    try:
        cmd = (
            f'az quantum job submit --target-id {target_id}'
            f' --job-input-file "{qir_path}"'
            f' --job-input-format qir.v1'
            f' --shots {shots}'
            f' --job-name "qgc-{problem_id}"'
            f' -o json'
        )
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
        if proc.returncode != 0:
            return None, proc.stderr[:200]
        data = json.loads(proc.stdout)
        return data.get("id", "unknown"), None
    finally:
        os.unlink(qir_path)


def main():
    import qsharp

    target_id = sys.argv[1] if len(sys.argv) > 1 else "quantinuum.sim.h2-1sc"
    problems = sys.argv[2:] if len(sys.argv) > 2 else None
    shots = 100 if "h2-1e" in target_id else 1
    target_profile = qsharp.TargetProfile.Adaptive_RI if "quantinuum" in target_id else qsharp.TargetProfile.Base

    print(f"Target: {target_id} (shots={shots})\n")

    new_runs = []
    for d in sorted(os.listdir(PROBLEMS_DIR)):
        if not (PROBLEMS_DIR / d / "qsharp" / "HardwareKernel.qs").exists():
            continue
        if problems and d not in problems:
            continue
        print(f"Compiling {d}...", end=" ", flush=True)
        try:
            entry_fn, qir = compile_kernel(d, target_profile)
            if not entry_fn:
                print("SKIP"); continue
            print(f"OK ({entry_fn})", end=" -> ", flush=True)
        except Exception as e:
            print(f"COMPILE FAIL: {str(e)[:120]}"); continue

        print("Submitting...", end=" ", flush=True)
        job_id, err = submit_via_cli(d, target_id, qir, shots)
        if err:
            print(f"FAIL: {err[:100]}")
        else:
            print(f"submitted ({job_id[:16]}...)")
            new_runs.append({
                "recorded_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "problem_id": d, "instance_id": "small", "depth": 1,
                "target_id": target_id,
                "status": "succeeded" if "h2-1sc" in target_id else "submitted",
                "job_id": job_id,
            })

    if new_runs:
        append_to_history(new_runs)
        print(f"\nRecorded {len(new_runs)} runs")
    else:
        print("\nNo successful submissions")


if __name__ == "__main__":
    main()
