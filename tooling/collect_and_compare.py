"""Collect all emulator results and optionally submit to Rigetti QVM."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"
HISTORY_PATH = Path(__file__).resolve().parent.parent / "website" / "data" / "azureRunHistory.json"


def collect_emulator_results():
    """Collect all H2-1E emulator results."""
    proc = subprocess.run(
        'az quantum job list --query "[?status==\'Succeeded\' && target==\'quantinuum.sim.h2-1e\'].{name:name, id:id}" -o json',
        capture_output=True, text=True, shell=True, timeout=30
    )
    jobs = json.loads(proc.stdout)
    seen = {}
    for j in jobs:
        seen[j["name"]] = j["id"]

    results = {}
    for name, jid in sorted(seen.items()):
        p = subprocess.run(f"az quantum job output --job-id {jid} -o json", capture_output=True, text=True, shell=True, timeout=30)
        if p.returncode != 0:
            print(f"  {name}: ERROR fetching output")
            continue
        data = json.loads(p.stdout)
        histogram = data.get("Results", [{}])[0].get("Histogram", [])
        histogram.sort(key=lambda x: x.get("Count", 0), reverse=True)
        total = sum(h["Count"] for h in histogram)
        top = histogram[0] if histogram else {}
        pid = name.replace("qgc-", "")
        pct = round(top.get("Count", 0) / max(total, 1) * 100)
        print(f"  {pid:35s} {str(top.get('Display', '?')):15s} {top.get('Count', 0):3d}/{total}  ({pct}%)")
        results[pid] = {
            "target": "quantinuum.sim.h2-1e",
            "shots": total,
            "histogram": [{"outcome": h["Display"], "count": h["Count"], "probability": round(h["Count"] / total, 4)} for h in histogram],
        }
    return results


def submit_rigetti(problems=None):
    """Submit all kernels to Rigetti QVM via SDK and collect results."""
    import qsharp
    from azure.identity import AzureCliCredential
    from qdk.azure import Workspace

    RESOURCE_ID = "/subscriptions/82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3/resourceGroups/Quantum-Grand-Challenges/providers/Microsoft.Quantum/Workspaces/Quantum-Grand-Challenges"
    credential = AzureCliCredential(tenant_id="dc692f3e-104b-4247-b52c-23692694684a")
    workspace = Workspace(resource_id=RESOURCE_ID, location="eastus", credential=credential)
    target = workspace.get_targets("rigetti.sim.qvm")

    results = {}
    new_runs = []

    for d in sorted(os.listdir(PROBLEMS_DIR)):
        kernel_path = PROBLEMS_DIR / d / "qsharp" / "HardwareKernel.qs"
        if not kernel_path.exists():
            # Check archived directory
            archived_path = PROBLEMS_DIR / "archived" / d / "qsharp" / "HardwareKernel.qs"
            if archived_path.exists():
                kernel_path = archived_path
            else:
                continue
        if problems and d not in problems:
            continue

        code = kernel_path.read_text(encoding="utf-8")
        m = re.search(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)", code)
        if not m:
            continue
        entry_fn = m.group(1)

        print(f"  {d} ({entry_fn})...", end=" ", flush=True)
        try:
            qsharp.init(target_profile=qsharp.TargetProfile.Base)
            qsharp.eval(code)
            qir = qsharp.compile(f"{entry_fn}()")
            job = target.submit(qir, f"qgc-rigetti-{d}", shots=100)
            job.wait_until_completed(timeout_secs=120)
            raw = job.get_results()

            # Parse results into histogram
            counts = {}
            if isinstance(raw, dict):
                counts = raw
            elif isinstance(raw, list):
                for r in raw:
                    k = str(r)
                    counts[k] = counts.get(k, 0) + 1

            total = sum(counts.values())
            histogram = sorted(
                [{"outcome": k, "count": v, "probability": round(v / max(total, 1), 4)} for k, v in counts.items()],
                key=lambda x: -x["count"]
            )
            top = histogram[0] if histogram else {}
            pct = round(top.get("count", 0) / max(total, 1) * 100)
            print(f"OK  {str(top.get('outcome', '?')):15s} {top.get('count', 0):3d}/{total}  ({pct}%)")

            results[d] = {"target": "rigetti.sim.qvm", "shots": total, "histogram": histogram}
            new_runs.append({
                "recorded_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "problem_id": d, "instance_id": "small", "depth": 1,
                "target_id": "rigetti.sim.qvm", "status": "succeeded",
            })
        except Exception as e:
            print(f"FAIL: {str(e)[:100]}")

    if new_runs:
        if HISTORY_PATH.exists():
            history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        else:
            history = {"schema_version": "1.0", "runs": []}
        history["runs"].extend(new_runs)
        history["updated_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")

    return results


def main():
    out_path = Path("website/data/emulatorResults.json")

    print("=== Collecting Quantinuum H2-1E emulator results ===")
    h2_results = collect_emulator_results()
    print(f"\nCollected {len(h2_results)} H2-1E results")

    print("\n=== Submitting to Rigetti QVM (100 shots) ===")
    rigetti_results = submit_rigetti()
    print(f"\nCollected {len(rigetti_results)} Rigetti results")

    output = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "quantinuum_h2_1e": h2_results,
        "rigetti_qvm": rigetti_results,
    }
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
