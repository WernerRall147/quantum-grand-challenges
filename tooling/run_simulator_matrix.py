#!/usr/bin/env python3
"""Run every HardwareKernel across the Azure Quantum simulators and emulators.

Two modes:

  --local   Run the bundled sparse simulator and record shot histograms. This is
            the noise-free reference the hardware emulators are compared against,
            and it works without an Azure connection.

  (default) Compile per target profile and submit to Azure Quantum, then record
            the returned histograms alongside the real job id.

Every public record carries `execution` set to "local-simulator" or
"azure-quantum" plus source, QIR, target, and SDK provenance. Azure job IDs stay in
the gitignored `.azure/job-provenance.json` file. A previous script printed
"Submitting to <target>", executed locally, and wrote the target name into
azureRunHistory.json with no job ID, so local results were indistinguishable from
hardware results after the fact.
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

if __package__:
    from .discover_problems import discover_all_problems
    from .quantum_provenance import build_run_provenance
else:
    from discover_problems import discover_all_problems
    from quantum_provenance import build_run_provenance

REPO = Path(__file__).resolve().parent.parent
MATRIX_PATH = REPO / "website" / "data" / "simulatorMatrix.json"

# Job ids are sensitive per tooling/reporting/validate_website_data_schema.py and the
# repo is public, so they never enter website/data. They go here instead, under the
# gitignored .azure/ directory, which keeps runs traceable without publishing them.
PROVENANCE_PATH = REPO / ".azure" / "job-provenance.json"

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
    for d in discover_all_problems():
        kernel = d / "qsharp" / "HardwareKernel.qs"
        if not kernel.exists():
            continue
        code = kernel.read_text(encoding="utf-8")
        m = ENTRY_RE.search(code)
        if m:
            out.append((d.name, m.group(1), kernel, code))
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
    qir = qsharp.compile(f"{entry_fn}()")
    return histogram(qsharp.run(f"{entry_fn}()", shots=shots), shots), qir


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
    provenance = []

    if args.local:
        for name, entry_fn, kernel_path, code in kernels:
            print(f"{name:<30} {entry_fn:<28}", end=" ", flush=True)
            try:
                hist, qir = run_local(qsharp, entry_fn, code, 200)
                print(f"ok  {hist['distinct_outcomes']} outcomes")
                record = build_run_provenance(
                    repo_root=REPO,
                    problem_id=name,
                    entry_point=entry_fn,
                    source_paths=[kernel_path],
                    execution_mode="local-simulator",
                    target_id=None,
                    target_profile="Adaptive_RI",
                    shots=200,
                    status="succeeded",
                    qir=qir,
                )
                records.append(record | {
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
                record = build_run_provenance(
                    repo_root=REPO,
                    problem_id=name,
                    entry_point=entry_fn,
                    source_paths=[kernel_path],
                    execution_mode="local-simulator",
                    target_id=None,
                    target_profile="Adaptive_RI",
                    shots=200,
                    status="failed",
                )
                records.append(record | {
                    "execution": "local-simulator",
                    "profile": "Adaptive_RI",
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

            for name, entry_fn, kernel_path, code in kernels:
                print(f"  {name:<30}", end=" ", flush=True)
                try:
                    qir = compile_for(qsharp, entry_fn, code, cfg["profile"])
                except BaseException as e:
                    if isinstance(e, (KeyboardInterrupt, SystemExit)):
                        raise
                    print(f"skipped (will not compile at {cfg['profile']})")
                    record = build_run_provenance(
                        repo_root=REPO,
                        problem_id=name,
                        entry_point=entry_fn,
                        source_paths=[kernel_path],
                        execution_mode="azure-quantum",
                        target_id=target_id,
                        target_profile=cfg["profile"],
                        shots=cfg["shots"],
                        status="incompatible",
                    )
                    records.append(record | {
                        "execution": "azure-quantum",
                        "profile": cfg["profile"], "status": "incompatible",
                        "reason": f"does not compile at {cfg['profile']}",
                    })
                    continue

                try:
                    job = target.submit(qir, f"qgc-{name}", shots=cfg["shots"])
                    job.wait_until_completed(timeout_secs=900)
                    res = job.get_results()
                    print(f"ok  job={job.details.id[:8]}")
                    record = build_run_provenance(
                        repo_root=REPO,
                        problem_id=name,
                        entry_point=entry_fn,
                        source_paths=[kernel_path],
                        execution_mode="azure-quantum",
                        target_id=target_id,
                        target_profile=cfg["profile"],
                        shots=cfg["shots"],
                        status="succeeded",
                        qir=qir,
                    )
                    provenance.append(record | {"job_id": job.details.id})
                    records.append(record | {
                        "execution": "azure-quantum",
                        "profile": cfg["profile"], "status": "succeeded",
                        "shots": cfg["shots"],
                        "results": res,
                    })
                except Exception as e:
                    print(f"FAILED  {str(e).splitlines()[0][:70]}")
                    record = build_run_provenance(
                        repo_root=REPO,
                        problem_id=name,
                        entry_point=entry_fn,
                        source_paths=[kernel_path],
                        execution_mode="azure-quantum",
                        target_id=target_id,
                        target_profile=cfg["profile"],
                        shots=cfg["shots"],
                        status="failed",
                        qir=qir,
                    )
                    records.append(record | {
                        "execution": "azure-quantum",
                        "profile": cfg["profile"],
                        "error": str(e).splitlines()[0][:300],
                    })

    payload = {
        "schema_version": "2.0",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "targets": TARGETS,
        "excluded_targets": EXCLUDED_TARGETS,
        "records": records,
    }
    MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MATRIX_PATH.exists():
        prev = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        # Keyed by problem as well as target: keyed by target alone, re-running a subset
        # of problems deleted every other problem's record for that target.
        rerun = {(x.get("problem_id"), x.get("execution"), x.get("target_id")) for x in records}
        keep = [r for r in prev.get("records", [])
                if (r.get("problem_id"), r.get("execution"), r.get("target_id")) not in rerun]
        payload["records"] = keep + records

    MATRIX_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if provenance:
        PROVENANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing = []
        if PROVENANCE_PATH.exists():
            existing = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8")).get("jobs", [])
        PROVENANCE_PATH.write_text(
            json.dumps({"jobs": existing + provenance}, indent=2), encoding="utf-8"
        )
        print(f"{len(provenance)} job ids -> {PROVENANCE_PATH.relative_to(REPO)} (gitignored)")

    ok = sum(1 for r in records if r["status"] == "succeeded")
    print(f"\n{ok}/{len(records)} succeeded -> {MATRIX_PATH.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
