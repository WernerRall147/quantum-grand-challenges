#!/usr/bin/env python3
"""Update website data with today's Azure job results and project status changes."""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WEB_DATA = REPO / "website" / "data"


def update_run_history():
    path = WEB_DATA / "azureRunHistory.json"
    d = json.loads(path.read_text(encoding="utf-8-sig"))

    new_runs = [
        {
            "recorded_utc": "2026-03-24T13:03:10Z",
            "problem_id": "01_hubbard",
            "instance_id": "small",
            "depth": 1,
            "target_id": "quantinuum.sim.h2-1sc",
            "status": "succeeded",
            "runtime_seconds": 0.0001,
            "queue_seconds": 8.5,
            "duration_seconds": 8.5,
            "cost_usd": 0.0,
            "metrics_status": "available",
        },
        {
            "recorded_utc": "2026-03-24T13:03:22Z",
            "problem_id": "01_hubbard",
            "instance_id": "small",
            "depth": 1,
            "target_id": "quantinuum.sim.h2-1sc",
            "status": "succeeded",
            "runtime_seconds": 0.0001,
            "queue_seconds": 3.1,
            "duration_seconds": 3.1,
            "cost_usd": 0.0,
            "metrics_status": "available",
        },
        {
            "recorded_utc": "2026-03-24T13:03:39Z",
            "problem_id": "05_qaoa_maxcut",
            "instance_id": "small",
            "depth": 1,
            "target_id": "quantinuum.sim.h2-1sc",
            "status": "succeeded",
            "runtime_seconds": 0.0001,
            "queue_seconds": 4.5,
            "duration_seconds": 4.5,
            "cost_usd": 0.0,
            "metrics_status": "available",
        },
        {
            "recorded_utc": "2026-03-24T13:03:56Z",
            "problem_id": "15_database_search",
            "instance_id": "small",
            "depth": 1,
            "target_id": "quantinuum.sim.h2-1sc",
            "status": "succeeded",
            "runtime_seconds": 0.0001,
            "queue_seconds": 6.6,
            "duration_seconds": 6.6,
            "cost_usd": 0.0,
            "metrics_status": "available",
        },
    ]

    # Avoid duplicates
    existing_ids = {(r["recorded_utc"], r["problem_id"], r["target_id"]) for r in d["runs"]}
    added = 0
    for run in new_runs:
        key = (run["recorded_utc"], run["problem_id"], run["target_id"])
        if key not in existing_ids:
            d["runs"].append(run)
            added += 1

    d["updated_utc"] = "2026-03-24T13:10:00Z"
    path.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
    print(f"Azure run history: {len(d['runs'])} total runs (+{added} new)")


if __name__ == "__main__":
    update_run_history()
