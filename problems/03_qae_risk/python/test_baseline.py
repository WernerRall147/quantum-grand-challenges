"""Deterministic checks for the 03_qae_risk classical baseline."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    baseline_path = Path(__file__).resolve().parents[1] / "estimates" / "classical_baseline.json"
    payload = json.loads(baseline_path.read_text(encoding="utf-8"))

    # Baseline is keyed by threshold (e.g. "2.0", "3.0", "4.0")
    assert isinstance(payload, dict), "Expected dict keyed by threshold"
    assert len(payload) >= 1, "Expected at least one threshold entry"

    for threshold_key, data in payload.items():
        threshold = float(threshold_key)
        assert threshold > 0, f"Threshold must be positive, got {threshold}"

        precisions = data.get("target_precisions")
        assert isinstance(precisions, list) and len(precisions) >= 1, (
            f"Expected target_precisions list for threshold {threshold_key}"
        )

        estimates = data.get("estimates")
        assert isinstance(estimates, list), f"Expected estimates list for threshold {threshold_key}"
        assert len(estimates) == len(precisions), (
            f"Estimates count {len(estimates)} != precisions count {len(precisions)}"
        )

        # All estimates should be probabilities in [0, 1]
        for est in estimates:
            assert 0.0 <= float(est) <= 1.0, f"Estimate {est} out of [0,1] range"

        # Samples needed should be positive integers
        samples = data.get("samples_needed")
        assert isinstance(samples, list) and len(samples) == len(precisions), (
            f"samples_needed length mismatch for threshold {threshold_key}"
        )
        for s in samples:
            assert int(s) > 0, f"Sample count must be positive, got {s}"

    print("PASS: 03_qae_risk classical baseline checks")


if __name__ == "__main__":
    main()
