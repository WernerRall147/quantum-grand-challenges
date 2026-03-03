"""Prepare QAOA estimator parameter payloads from instance + quantum baseline artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


def load_instance(instance_path: Path) -> Dict[str, object]:
    payload = yaml.safe_load(instance_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid instance payload in {instance_path}")
    return payload


def build_weight_matrix(nodes: List[str], edges: List[Tuple[str, str, float]]) -> List[List[float]]:
    index = {name: i for i, name in enumerate(nodes)}
    n = len(nodes)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for u, v, w in edges:
        i = index[u]
        j = index[v]
        matrix[i][j] = float(w)
        matrix[j][i] = float(w)
    return matrix


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate estimator input parameters for QAOA Max-Cut.")
    parser.add_argument("--instance", default="small", help="Instance id (small/medium/large).")
    parser.add_argument("--depth", type=int, default=1, help="QAOA depth used for the quantum baseline artifact.")
    parser.add_argument(
        "--quantum-file",
        default=None,
        help="Optional explicit path to quantum baseline JSON. Defaults to estimates/quantum_baseline_<instance>_d<depth>.json",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output path. Defaults to estimates/estimator_params_<instance>_d<depth>.json",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    instance_path = root / "instances" / f"{args.instance}.yaml"
    if not instance_path.exists():
        raise FileNotFoundError(f"Instance file not found: {instance_path}")

    instance_payload = load_instance(instance_path)
    nodes = [str(v) for v in instance_payload.get("nodes", [])]
    if not nodes:
        raise ValueError(f"No nodes defined in {instance_path}")

    raw_edges = instance_payload.get("edges", [])
    edges: List[Tuple[str, str, float]] = []
    for item in raw_edges:
        if not isinstance(item, list) or len(item) != 3:
            raise ValueError(f"Invalid edge item in {instance_path}: {item}")
        u, v, w = item
        edges.append((str(u), str(v), float(w)))

    weights = build_weight_matrix(nodes, edges)

    if args.quantum_file:
        quantum_path = Path(args.quantum_file).resolve()
    else:
        quantum_path = root / "estimates" / f"quantum_baseline_{args.instance}_d{args.depth}.json"

    if not quantum_path.exists():
        raise FileNotFoundError(
            f"Quantum baseline artifact not found: {quantum_path}. Run QAOA first to generate it."
        )

    quantum_payload = json.loads(quantum_path.read_text(encoding="utf-8"))
    best_trial = quantum_payload.get("best_trial", {}) if isinstance(quantum_payload, dict) else {}

    out_path = (
        Path(args.out).resolve()
        if args.out
        else root / "estimates" / f"estimator_params_{args.instance}_d{args.depth}.json"
    )

    estimator_payload = {
        "weights": weights,
        "depth": int(quantum_payload.get("depth", args.depth)),
        "coarseShots": int(quantum_payload.get("coarse_shots", 24)),
        "refinedShots": int(quantum_payload.get("refined_shots", 96)),
        # Metadata fields can be used by wrappers even if the estimator ignores them.
        "bestBeta": float(best_trial.get("BestBeta", 0.0)) if isinstance(best_trial, dict) else 0.0,
        "bestGamma": float(best_trial.get("BestGamma", 0.0)) if isinstance(best_trial, dict) else 0.0,
        "instance": str(args.instance),
        "sourceQuantumArtifact": str(quantum_path.relative_to(root)),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(estimator_payload, indent=2) + "\n", encoding="utf-8")

    try:
        rel = out_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel = out_path
    print(f"Wrote estimator params: {rel}")


if __name__ == "__main__":
    main()
