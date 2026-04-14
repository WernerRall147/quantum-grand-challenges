"""Deterministic checks for the 05_qaoa_maxcut classical baseline."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    baseline_path = Path(__file__).resolve().parents[1] / "estimates" / "classical_baseline.json"
    payload = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert payload.get("problem_id") == "05_qaoa_maxcut", "Unexpected problem_id"
    assert payload.get("model") == "exhaustive_maxcut", "Unexpected model"

    results = payload.get("results")
    assert isinstance(results, list) and len(results) >= 1, "Expected at least one result"

    for row in results:
        num_nodes = int(row["num_nodes"])
        num_edges = int(row["num_edges"])
        best_cut = float(row["best_cut"])

        assert num_nodes >= 2, f"num_nodes must be >= 2, got {num_nodes}"
        assert num_edges >= 1, f"num_edges must be >= 1, got {num_edges}"
        assert best_cut >= 0, f"best_cut must be non-negative, got {best_cut}"

        # Best assignments should be binary strings of length num_nodes
        assignments = row.get("best_assignments", [])
        assert len(assignments) >= 1, f"Expected at least one best assignment for {row['instance_id']}"
        for a in assignments:
            assert len(a) == num_nodes, f"Assignment length {len(a)} != num_nodes {num_nodes}"
            assert set(a) <= {"0", "1"}, f"Assignment {a} contains non-binary characters"

        # Value histogram should have 2^num_nodes total entries
        histogram = row.get("value_histogram", {})
        total_assignments = sum(histogram.values())
        assert total_assignments == 2 ** num_nodes, (
            f"Histogram total {total_assignments} != 2^{num_nodes} = {2 ** num_nodes}"
        )

    print("PASS: 05_qaoa_maxcut classical baseline checks")


if __name__ == "__main__":
    main()
