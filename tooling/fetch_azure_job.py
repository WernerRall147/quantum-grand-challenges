"""Download a finished Azure Quantum job into a problem folder: input, output, metadata.

`submit_one_kernel.py` prints a histogram and exits. That is enough to know a run
worked and useless afterwards - the evidence lives only in the terminal scrollback.
This fetches the durable record so a run can be shown and explained later:

  job.json        what was asked for - entry point, shots, target profile, timings, cost
  input.qir.ll    the exact QIR that was submitted
  output.json     the exact payload Azure returned - histogram and every shot

    python tooling/fetch_azure_job.py <job-id> --dest problems/archived/15_database_search/azure_runs/<name>

SAS TOKENS ARE STRIPPED. `az quantum job show` returns `containerUri`, `inputDataUri`
and `outputDataUri` with a live `sig=` query string that grants read access to the
job's blob container for several days. This repo is public. The URIs are kept for
provenance with the query string replaced by `?<sas-stripped>`, so the record stays
readable without publishing a credential.

The histogram is checked against the shot count, because a job can reach "Succeeded"
and still return a payload that does not describe the run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

DEFAULT_RESOURCE_GROUP = "qgc-af-demo-rg"
DEFAULT_WORKSPACE = "qgc-af-demo"

SAS_FIELDS = ("containerUri", "inputDataUri", "outputDataUri")


def strip_sas(url: str) -> str:
    """Drop the query string, which is where the signature lives."""
    return url.split("?", 1)[0] + "?<sas-stripped>" if "?" in url else url


def az_job_show(job_id: str, resource_group: str, workspace: str) -> dict:
    result = subprocess.run(
        ["az", "quantum", "job", "show", "-g", resource_group, "-w", workspace,
         "-j", job_id, "-o", "json", "--only-show-errors"],
        capture_output=True, text=True, shell=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"FAIL: az quantum job show returned {result.returncode}\n{result.stderr[:400]}")
    return json.loads(result.stdout)


def fetch(url: str, dest: Path) -> int:
    with urllib.request.urlopen(url, timeout=120) as response:
        payload = response.read()
    dest.write_bytes(payload)
    return len(payload)


def check_histogram(output: dict, expected_shots: int) -> tuple[str, int]:
    """Assert the payload describes the run, and return the top outcome.

    A Succeeded job whose histogram does not add up to the shots requested is not
    evidence of anything, so this fails rather than writing a misleading artifact.
    """
    try:
        histogram = output["Results"][0]["Histogram"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"FAIL: no histogram in the output payload ({exc})")

    total = sum(row["Count"] for row in histogram)
    if total != expected_shots:
        raise SystemExit(
            f"FAIL: histogram sums to {total} but the job requested {expected_shots} shots"
        )
    top = max(histogram, key=lambda row: row["Count"])
    return top["Display"], top["Count"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("job_id")
    parser.add_argument("--dest", required=True,
                        help="folder to write job.json, input.qir.ll and output.json into")
    parser.add_argument("--resource-group", default=DEFAULT_RESOURCE_GROUP)
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE)
    parser.add_argument("--expect", default="",
                        help="outcome that must dominate, e.g. '[0, 1, 1, 1]'")
    args = parser.parse_args()

    job = az_job_show(args.job_id, args.resource_group, args.workspace)
    if job.get("status") != "Succeeded":
        raise SystemExit(f"FAIL: job status is {job.get('status')!r}, refusing to record it as evidence")

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    input_bytes = fetch(job["inputDataUri"], dest / "input.qir.ll")
    output_bytes = fetch(job["outputDataUri"], dest / "output.json")
    output = json.loads((dest / "output.json").read_text(encoding="utf-8"))

    shots = job.get("inputParams", {}).get("shots")
    top, count = check_histogram(output, shots)
    if args.expect and args.expect != top:
        raise SystemExit(f"FAIL: expected {args.expect!r} to dominate, got {top!r}")

    for field in SAS_FIELDS:
        if job.get(field):
            job[field] = strip_sas(job[field])
    (dest / "job.json").write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")

    # Re-read what was written; a credential left on disk is the failure that matters.
    written = (dest / "job.json").read_text(encoding="utf-8")
    if "sig=" in written:
        raise SystemExit("FAIL: a SAS signature survived stripping - not committing this")

    print(f"job     : {job['name']} ({job['id']})")
    print(f"target  : {job['target']}  {shots} shots  {job['inputParams'].get('target_profile')}")
    print(f"input   : input.qir.ll   {input_bytes:,} bytes")
    print(f"output  : output.json    {output_bytes:,} bytes")
    print(f"top     : {top} at {count}/{shots} ({count / shots:.0%})")
    print(f"written : {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
