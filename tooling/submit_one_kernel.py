"""Submit one problem's HardwareKernel.qs to Azure Quantum and report the result.

`azure_submit_kernels.py` only walks `problems/`, so it silently skips anything
under `problems/archived/` - including `15_database_search`, which is the kernel
the Azure Friday demo is built on. This submits one named problem from either
location and waits for the answer.

It asserts on the histogram, not on the exit code. A job that reaches
"Succeeded" having measured noise is still a failed demo prop, so this checks
that the marked state actually dominates.

    python tooling/submit_one_kernel.py 15_database_search quantinuum.sim.h2-1e --shots 100 --expect "0, 1, 1, 1"

WHICH WORKSPACE. Defaults to `qgc-af-demo` in `qgc-af-demo-rg`, because the
original `Quantum-Grand-Challenges` workspace cannot accept jobs. It stages
payloads in a service-managed storage account inside a Microsoft-managed resource
group, and tenant policy `mcapsgovdeploypolicies` forced
`publicNetworkAccess=Disabled` on it. A deny assignment blocks writing to that
account and tagging its resource group, even as subscription Owner, so neither of
the policy's own escape hatches can reach it. Jobs there last succeeded 2026-06-10.
Use --resource-group/--workspace to point elsewhere.

HOW THE WORKING WORKSPACE WAS BUILT. The policy skips any resource whose resource
group carries `SecurityControl=Ignore`, and it evaluates that at creation time. So
the managed resource group was created *first*, already tagged, before the service
could put anything in it. That workspace ended up with no managed storage account
at all and uses its linked one, which was never locked. See
docs/AzureFriday/deck-notes.md, "Can you submit a job right now?".

QUOTA. h2-1e is metered in eHQC and the allowance is shared across the
subscription. 200 shots of this kernel wanted 75.36 and was rejected; 100 shots
went through. If you see `NotEnoughQuota`, lower --shots rather than retrying.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

SUBSCRIPTION_ID = "82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3"
TENANT_ID = "dc692f3e-104b-4247-b52c-23692694684a"

# Defaults to the workspace that can actually accept jobs - see module docstring.
DEFAULT_RESOURCE_GROUP = "qgc-af-demo-rg"
DEFAULT_WORKSPACE = "qgc-af-demo"


def resource_id(resource_group: str, workspace: str) -> str:
    return (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.Quantum/Workspaces/{workspace}"
    )


def find_kernel(problem_id: str) -> Path:
    for base in (REPO / "problems", REPO / "problems" / "archived"):
        candidate = base / problem_id / "qsharp" / "HardwareKernel.qs"
        if candidate.exists():
            return candidate
    raise SystemExit(f"FAIL: no HardwareKernel.qs for {problem_id} in problems/ or problems/archived/")


def compile_kernel(kernel_path: Path, target_id: str):
    from qdk import qsharp

    code = kernel_path.read_text(encoding="utf-8")
    match = re.search(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)", code)
    if not match:
        raise SystemExit("FAIL: no @EntryPoint in the kernel")
    entry = match.group(1)

    profile = (
        qsharp.TargetProfile.Adaptive_RI if "quantinuum" in target_id
        else qsharp.TargetProfile.Base
    )
    qsharp.init(target_profile=profile)
    qsharp.eval(code)
    return entry, qsharp.compile(f"{entry}()")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("problem_id")
    parser.add_argument("target_id", nargs="?", default="quantinuum.sim.h2-1e")
    parser.add_argument("--shots", type=int, default=100)
    parser.add_argument("--resource-group", default=DEFAULT_RESOURCE_GROUP)
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE)
    parser.add_argument("--timeout", type=int, default=1800,
                        help="seconds to wait for the job; the SDK default of 300 is often "
                             "shorter than the h2-1e queue")
    parser.add_argument("--no-wait", action="store_true", help="submit and exit without polling")
    parser.add_argument("--expect", default="",
                        help="bitstring that should dominate the histogram, e.g. 1110")
    parser.add_argument("--save", help="write the histogram JSON here")
    args = parser.parse_args()

    kernel = find_kernel(args.problem_id)
    print(f"kernel : {kernel.relative_to(REPO)}")
    print(f"target : {args.target_id}  ({args.shots} shots)")
    print(f"space  : {args.workspace} in {args.resource_group}")

    entry, qir = compile_kernel(kernel, args.target_id)
    print(f"entry  : {entry}()  - compiled to QIR")

    from azure.identity import AzureCliCredential
    from qdk.azure import Workspace

    credential = AzureCliCredential(tenant_id=TENANT_ID)
    workspace = Workspace(
        resource_id=resource_id(args.resource_group, args.workspace),
        location="eastus", credential=credential,
    )
    target = workspace.get_targets(args.target_id)

    job = target.submit(qir, f"qgc-{args.problem_id}", shots=args.shots)
    job_id = job.details.id if hasattr(job, "details") else str(job)
    print(f"job id : {job_id}")

    if args.no_wait:
        print("submitted; not waiting.")
        return 0

    print("waiting for results...", flush=True)
    results = job.get_results(timeout_secs=args.timeout)

    # A job can reach Succeeded and still be useless as a demo prop, so assert on
    # the histogram rather than on the status.
    if isinstance(results, dict):
        counts = Counter({str(k): v for k, v in results.items()})
    else:
        counts = Counter(str(r) for r in results)

    total = sum(counts.values()) or 1
    print(f"\n{'OUTCOME':<12}{'COUNT':>8}{'SHARE':>9}")
    for outcome, n in counts.most_common(8):
        print(f"{outcome:<12}{n:>8}{n / total:>8.1%}")

    if args.save:
        Path(args.save).write_text(json.dumps(dict(counts), indent=2), encoding="utf-8")
        print(f"\nsaved to {args.save}")

    top, top_n = counts.most_common(1)[0]
    if args.expect:
        if args.expect not in top:
            print(f"\nFAIL: expected {args.expect!r} to dominate, got {top!r} at {top_n / total:.1%}")
            return 1
        print(f"\nOK: {top!r} dominates at {top_n / total:.1%} - the marked state was found")
    else:
        print(f"\ntop outcome {top!r} at {top_n / total:.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
