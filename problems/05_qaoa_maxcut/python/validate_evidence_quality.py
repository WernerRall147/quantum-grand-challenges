"""Validate QAOA Stage C evidence quality thresholds for depth and noise sweeps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def _load_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required evidence file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON structure in {path}")
    return payload


def validate_depth_sweep(
    path: Path,
    min_points: int,
    min_depth_gain: float,
    max_step_regression: float,
    min_trials: int,
) -> Dict[str, float]:
    payload = _load_json(path)
    instance = str(payload.get("instance_id", "unknown"))
    records = payload.get("records", [])
    if not isinstance(records, list) or len(records) < min_points:
        raise ValueError(f"{path.name}: expected at least {min_points} depth points")

    rows: List[Dict[str, float]] = []
    for row in records:
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "depth": int(row.get("depth", 0)),
                "mean": float(row.get("refined_mean", 0.0)),
                "trials": int(row.get("trials", payload.get("trials", 0))),
            }
        )

    if len(rows) < min_points:
        raise ValueError(f"{path.name}: insufficient parsed depth records")

    rows.sort(key=lambda r: r["depth"])
    depths = [int(r["depth"]) for r in rows]
    if len(set(depths)) != len(depths):
        raise ValueError(f"{path.name}: duplicate depth entries detected")

    for idx in range(1, len(rows)):
        prev = rows[idx - 1]
        cur = rows[idx]
        # Allow only bounded regression from one depth step to the next.
        if cur["mean"] + max_step_regression < prev["mean"]:
            raise ValueError(
                f"{path.name}: depth regression too large ({prev['mean']:.4f} -> {cur['mean']:.4f})"
            )

    for row in rows:
        if row["trials"] < min_trials:
            raise ValueError(
                f"{path.name}: trials {row['trials']} below required minimum {min_trials}"
            )

    gain = rows[-1]["mean"] - rows[0]["mean"]
    if gain < min_depth_gain:
        raise ValueError(
            f"{path.name}: depth gain {gain:.4f} below required minimum {min_depth_gain:.4f}"
        )

    return {"instance": instance, "points": float(len(rows)), "gain": gain}


def validate_noise_sweep(
    path: Path,
    min_points: int,
    min_degradation: float,
    max_step_increase: float,
) -> Dict[str, float]:
    payload = _load_json(path)
    instance = str(payload.get("instance_id", "unknown"))
    depth = int(payload.get("depth", 0))
    records = payload.get("records", [])
    if not isinstance(records, list) or len(records) < min_points:
        raise ValueError(f"{path.name}: expected at least {min_points} noise points")

    rows: List[Dict[str, float]] = []
    for row in records:
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "noise": float(row.get("noise", 0.0)),
                "mean": float(row.get("noisy_mean", 0.0)),
            }
        )

    if len(rows) < min_points:
        raise ValueError(f"{path.name}: insufficient parsed noise records")

    rows.sort(key=lambda r: r["noise"])
    noises = [r["noise"] for r in rows]
    if len(set(round(n, 8) for n in noises)) != len(noises):
        raise ValueError(f"{path.name}: duplicate noise entries detected")

    for idx in range(1, len(rows)):
        prev = rows[idx - 1]
        cur = rows[idx]
        # With larger noise, score should not increase beyond tolerance.
        if cur["mean"] > prev["mean"] + max_step_increase:
            raise ValueError(
                f"{path.name}: noisy mean increased too much ({prev['mean']:.4f} -> {cur['mean']:.4f})"
            )

    degradation = rows[0]["mean"] - rows[-1]["mean"]
    if degradation < min_degradation:
        raise ValueError(
            f"{path.name}: total degradation {degradation:.4f} below minimum {min_degradation:.4f}"
        )

    return {
        "instance": instance,
        "depth": float(depth),
        "points": float(len(rows)),
        "degradation": degradation,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate QAOA depth/noise evidence quality thresholds.")
    parser.add_argument("--estimates-dir", default="problems/05_qaoa_maxcut/estimates")
    parser.add_argument("--depth-instances", default="small,medium,large")
    parser.add_argument("--noise-targets", default="small:d3,medium:d2,large:d2")
    parser.add_argument("--min-depth-points", type=int, default=2)
    parser.add_argument("--min-noise-points", type=int, default=5)
    parser.add_argument("--min-depth-gain", type=float, default=0.02)
    parser.add_argument("--max-depth-step-regression", type=float, default=0.15)
    parser.add_argument("--min-noise-degradation", type=float, default=0.05)
    parser.add_argument("--max-noise-step-increase", type=float, default=0.05)
    parser.add_argument("--min-trials", type=int, default=4)
    args = parser.parse_args()

    estimates_dir = Path(args.estimates_dir)
    if not estimates_dir.is_absolute():
        candidates = [Path.cwd() / estimates_dir, Path(__file__).resolve().parents[1] / "estimates"]
        resolved = None
        for candidate in candidates:
            if candidate.exists():
                resolved = candidate.resolve()
                break
        estimates_dir = resolved if resolved else (Path.cwd() / estimates_dir).resolve()

    depth_instances = [part.strip() for part in args.depth_instances.split(",") if part.strip()]
    if not depth_instances:
        raise ValueError("No depth instances specified")

    noise_targets = [part.strip() for part in args.noise_targets.split(",") if part.strip()]
    if not noise_targets:
        raise ValueError("No noise targets specified")

    depth_results: List[Dict[str, float]] = []
    for instance in depth_instances:
        path = estimates_dir / f"depth_sweep_{instance}.json"
        depth_results.append(
            validate_depth_sweep(
                path,
                min_points=args.min_depth_points,
                min_depth_gain=args.min_depth_gain,
                max_step_regression=args.max_depth_step_regression,
                min_trials=args.min_trials,
            )
        )

    noise_results: List[Dict[str, float]] = []
    for target in noise_targets:
        if ":" not in target:
            raise ValueError(f"Invalid noise target '{target}', expected format <instance>:d<depth>")
        instance, depth_tag = target.split(":", maxsplit=1)
        depth_tag = depth_tag.strip()
        if not depth_tag.startswith("d"):
            raise ValueError(f"Invalid noise target depth tag '{depth_tag}' in '{target}'")
        depth = int(depth_tag[1:])
        path = estimates_dir / f"noise_sweep_{instance}_d{depth}.json"
        noise_results.append(
            validate_noise_sweep(
                path,
                min_points=args.min_noise_points,
                min_degradation=args.min_noise_degradation,
                max_step_increase=args.max_noise_step_increase,
            )
        )

    print("Evidence quality validation passed")
    for row in depth_results:
        print(
            f"  depth::{row['instance']}: points={int(row['points'])}, gain={row['gain']:.4f}"
        )
    for row in noise_results:
        print(
            f"  noise::{row['instance']}@d{int(row['depth'])}: points={int(row['points'])}, "
            f"degradation={row['degradation']:.4f}"
        )


if __name__ == "__main__":
    main()
