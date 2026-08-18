#!/usr/bin/env python3
"""Run every HardwareKernel across the Azure Quantum simulators and emulators.

Two modes:

  --local   Run the bundled sparse simulator and record shot histograms. This is
            the noise-free reference the hardware emulators are compared against,
            and it works without an Azure connection.

  (default) Compile per target profile and submit to Azure Quantum, then record
            the returned histograms alongside the real job id.

Every record carries `execution` set to "local-simulator" or "azure-quantum" and,
for Azure runs, the job id. A previous script printed "Submitting to <target>",
executed locally, and wrote the target name into azureRunHistory.json with no job
id, so local results were indistinguishable from hardware results after the fact.
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = REPO / "problems"
MATRIX_PATH = REPO / "website" / "data" / "simulatorMatrix.json"

RESOURCE_ID = (
    "/subscriptions/82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3"
    "/resourceGroups/Quantum-Grand-Challenges"
    "/providers/Microsoft.Quantum/Workspaces/Quantum-Grand-Challenges"
)
TENANT_ID = "dc692f3e-104b-4247-b52c-23692694684a"
LOCATION = "eastus"

# Profiles verified by compiling every kernel at both Base and Adaptive_RI.
TARGETS = {
    "quantinuum.sim.h2-1sc": {
        "profile": "Adaptive_RI",
        "shots": 20,
        "billed": False,
        "note": "Syntax checker. Validates QIR then returns all zeros by design, "
                "so its histogram is not a physics result.",
    },
    "quantinuum.sim.h2-1e": {
        "profile": "Adaptive_RI",
        "shots": 200,
        "billed": True,
        "note": "Noise model of H2-1. Consumes eHQC quota.",
    },
    "rigetti.sim.qvm": {
        "profile": "Base",
        "shots": 200,
        "billed": False,
        "note": "Base profile only, so kernels needing mid-circuit branching are skipped.",
    },
    "ionq.simulator": {
        "profile": "Base",
        "shots": 200,
        "billed": False,
        "note": "Base profile only, so kernels needing mid-circuit branching are skipped.",
    },
}

# pasqal.sim.emu-free is deliberately absent. Its input format is pasqal.pulser.v1,
# an analog neutral-atom pulse sequence. Our kernels are gate-model QIR, so the
# target cannot accept them at all. Supporting it means writing Pulser sequences
# per problem, which is a separate piece of work rather than a configuration change.
EXCLUDED_TARGETS = {
    "pasqal.sim.emu-free": "input format pasqal.pulser.v1 (analog), not gate-model QIR",
}

ENTRY_RE = re.compile(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)")


def discover_kernels():
    out = []
    for d in sorted(PROBLEMS_DIR.iterdir()):
        if not (d.is_dir() and d.name[:2].isdigit()):
            continue
        kernel = d / "qsharp" / "HardwareKernel.qs"
        if not kernel.exists():
            continue
        code = kernel.read_text(encoding="utf-8")
        m = ENTRY_RE.search(code)
        if m:
            out.append((d.name, m.group(1), code))
    return out


def histogram(results, shots):
    counts = Counter(str(r) for r in results)
    return {
        "shots": shots,
        "distinct_outcomes": len(counts),
        "counts": dict(counts.most_common(16)),
    }


def run_local(qsharp, entry_fn, code, shots):
    qsharp.init(target_profile=qsharp.TargetProfile.Adaptive_RI)
    qsharp.eval(code)
    return histogram(qsharp.run(f"{entry_fn}()", shots=shots), shots)


def compile_for(qsharp, entry_fn, code, profile_name):
    profile = getattr(qsharp.TargetProfile, profile_name)
    qsharp.init(target_profile=profile)
    qsharp.eval(code)
    return qsharp.compile(f"{entry_fn}()")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true",
                    help="run the local simulator baseline instead of submitting")
    ap.add_argument("--targets", nargs="*", default=sorted(TARGETS),
                    help="subset of targets to submit to")
    ap.add_argument("--problems", nargs="*", default=None,
                    help="subset of problem directory names")
    args = ap.parse_args()

    from qdk import qsharp

    kernels = discover_kernels()
    if args.problems:
        kernels = [k for k in kernels if k[0] in args.problems]
    print(f"{len(kernels)} kernels discovered\n")

    records = []

    if args.local:
        for name, entry_fn, code in kernels:
            print(f"{name:<30} {entry_fn:<28}", end=" ", flush=True)
            try:
                hist = run_local(qsharp, entry_fn, code, 200)
                print(f"ok  {hist['distinct_outcomes']} outcomes")
                records.append({
                    "problem_id": name,
                    "entry_point": entry_fn,
                    "execution": "local-simulator",
                    "target_id": None,
                    "profile": "Adaptive_RI",
                    "status": "succeeded",
                    "histogram": hist,
                })
            except BaseException as e:  # QDK raises Rust panics as BaseException
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                print(f"FAILED  {str(e).splitlines()[0][:60]}")
                records.append({
                    "problem_id": name,
                    "entry_point": entry_fn,
                    "execution": "local-simulator",
                    "target_id": None,
                    "status": "failed",
                    "error": str(e).splitlines()[0][:200],
                })
    else:
        from azure.identity import AzureCliCredential
        from qdk.azure import Workspace

        ws = Workspace(resource_id=RESOURCE_ID, location=LOCATION,
                       credential=AzureCliCredential(tenant_id=TENANT_ID))

        for target_id in args.targets:
            cfg = TARGETS[target_id]
            print(f"\n=== {target_id}  ({cfg['profile']}, {cfg['shots']} shots"
                  f"{', billed' if cfg['billed'] else ''}) ===")
            target = ws.get_targets(target_id)

            for name, entry_fn, code in kernels:
                print(f"  {name:<30}", end=" ", flush=True)
                try:
                    qir = compile_for(qsharp, entry_fn, code, cfg["profile"])
                except BaseException as e:
                    if isinstance(e, (KeyboardInterrupt, SystemExit)):
                        raise
                    print(f"skipped (will not compile at {cfg['profile']})")
                    records.append({
                        "problem_id": name, "entry_point": entry_fn,
                        "execution": "azure-quantum", "target_id": target_id,
                        "profile": cfg["profile"], "status": "incompatible",
                        "reason": f"does not compile at {cfg['profile']}",
                    })
                    continue

                try:
                    job = target.submit(qir, f"qgc-{name}", shots=cfg["shots"])
                    job.wait_until_completed(timeout_secs=900)
                    res = job.get_results()
                    print(f"ok  job={job.details.id[:8]}")
                    records.append({
                        "problem_id": name, "entry_point": entry_fn,
                        "execution": "azure-quantum", "target_id": target_id,
                        "profile": cfg["profile"], "status": "succeeded",
                        "job_id": job.details.id,
                        "shots": cfg["shots"],
                        "results": res,
                    })
                except Exception as e:
                    print(f"FAILED  {str(e).splitlines()[0][:70]}")
                    records.append({
                        "problem_id": name, "entry_point": entry_fn,
                        "execution": "azure-quantum", "target_id": target_id,
                        "profile": cfg["profile"], "status": "failed",
                        "error": str(e).splitlines()[0][:300],
                    })

    payload = {
        "schema_version": "1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "targets": TARGETS,
        "excluded_targets": EXCLUDED_TARGETS,
        "records": records,
    }
    MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MATRIX_PATH.exists():
        prev = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        keep = [r for r in prev.get("records", [])
                if (r.get("execution"), r.get("target_id")) not in
                {(x.get("execution"), x.get("target_id")) for x in records}]
        payload["records"] = keep + records

    MATRIX_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    ok = sum(1 for r in records if r["status"] == "succeeded")
    print(f"\n{ok}/{len(records)} succeeded -> {MATRIX_PATH.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
