"""Generate Stage D advantage claim contracts for candidate problems."""

import json
from datetime import datetime, timezone
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

STAGE_D_CANDIDATES = {
    "03_qae_risk": {
        "claim_category": "theoretical",
        "problem_class": "Tail risk estimation: P(Loss > threshold) for a loss distribution loaded on a discrete grid",
        "instance_regime": "Log-normal(0,1) evaluated on 16 levels, threshold 2.5 (tail probability a = 0.1614), 4 loss qubits",
        "baseline_algorithm": "Plain Monte Carlo on the same 16-level distribution, compared with IQAE at equal interval half-width and confidence (python/iqae_driver.py)",
        "fairness_rationale": "Monte Carlo is the standard method when a distribution is available only by sampling, and here it estimates the same quantity as the circuit; both sides count applications of the state preparation. Variance-reduced Monte Carlo is reported on the continuous model, a different quantity",
        "quantum_resource_scaling": "IQAE's query count grows as 1/ε and Monte Carlo's sample count as 1/ε² (measured: 42,715 applications of A against 3.2 million samples at half-width 0.0004), before loading and error-correction costs",
        "data_loading_assumptions": "Amplitude encoding via multiplex rotations; exponential circuit depth O(2^n) for n-qubit encoding",
        "noise_model_assumptions": "Noiseless simulator; real hardware would require error correction for 40+ logical qubits",
        "confidence_method": "IQAE intervals at confidence 1 - α (Clopper-Pearson per round at level α/T), coverage checked over 300 repetitions; 20-run calibration ensemble with normal-approximation 95% intervals",
        "residual_risks": [
            "Amplitude encoding circuit depth scales exponentially, so practical advantage requires efficient state preparation",
            "369k physical qubits required for the 16-level instance, beyond current NISQ devices",
            "No noise model applied; fault-tolerant execution assumed",
            "Classical importance sampling may close the gap for structured distributions",
            "Before 2026-09-27 the canonical kernel's Grover iterate was wrong; ensembles from that kernel are superseded",
        ],
        "physical_qubits": 369400,
        "logical_qubits": 40,
        "t_gates": 15,
    },
    "05_qaoa_maxcut": {
        "claim_category": "theoretical",
        "problem_class": "Maximum cut in weighted graphs (NP-hard combinatorial optimization)",
        "instance_regime": "Triangle graph (3 vertices, 3 edges), depth-1 QAOA at grid-searched angles, with repository gamma convention gamma_std=-2 gamma",
        "baseline_algorithm": "Brute-force enumeration (optimal for n≤20); Goemans-Williamson SDP (0.878-approx for large n)",
        "fairness_rationale": "At n=3, brute-force trivially finds optimal; GW guarantee only relevant at n>30",
        "quantum_resource_scaling": "QAOA expected ratio approaches optimal as depth p→∞; constant-depth advantage unproven for MaxCut",
        "data_loading_assumptions": "Graph encoded directly as ZZ interactions; no data loading overhead",
        "noise_model_assumptions": "Noiseless simulator; real QAOA at depth>1 highly sensitive to gate noise",
        "confidence_method": "Exact state-vector expectation at the best grid point is 1.999334805117118 against optimum 2.0 (ratio 0.999667; continuous p=1 angles reach 2.0 on a triangle); finite-shot samples report the best observed bit string, not deterministic optimization",
        "residual_risks": [
            "No proven quantum advantage for MaxCut QAOA at any constant depth",
            "Classical GW algorithm achieves 0.878-approximation in polynomial time",
            "Instance is trivially small (n=3); advantage claims are meaningless at this scale",
            "131k physical qubits for a 3-vertex graph; scaling to practical graphs unknown",
        ],
        "physical_qubits": 131544,
        "logical_qubits": 12,
        "t_gates": 0,
    },
    "15_database_search": {
        "claim_category": "projected",
        "problem_class": "Unstructured search in N-element database",
        "instance_regime": "N=16 (4 qubits), single target (M=1), 3 Grover iterations",
        "baseline_algorithm": "Classical linear search O(N); expected N/2 queries on average",
        "fairness_rationale": "Linear search is optimal for unstructured search  no classical heuristic can beat O(N)",
        "quantum_resource_scaling": "Grover achieves O(√N) queries  provably optimal quadratic speedup (BBBV lower bound)",
        "data_loading_assumptions": "Oracle assumed to be a black-box function; implementation cost O(n) for n-qubit register",
        "noise_model_assumptions": "Noiseless simulator; Grover amplitude amplification degrades significantly with gate errors",
        "confidence_method": "20-run calibration ensemble; target found deterministically on all runs (search space N=16)",
        "residual_risks": [
            "Quadratic speedup offset by large constant factors in fault-tolerant implementation",
            "Oracle compilation cost not included  real oracles may require O(N) gates, eliminating speedup",
            "119k physical qubits for 4-qubit search; scaling to useful N requires millions of qubits",
            "Grover is provably optimal but constant-factor overhead may delay practical advantage to N>10^6",
        ],
        "physical_qubits": 119556,
        "logical_qubits": 18,
        "t_gates": 0,
    },
}


def problem_dir(problem_id: str) -> Path:
    """Active problems live in problems/, archived ones in problems/archived/."""
    active = PROBLEMS_DIR / problem_id
    return active if active.is_dir() else PROBLEMS_DIR / "archived" / problem_id


def main(selected: list[str] | None = None):
    for pid, contract in STAGE_D_CANDIDATES.items():
        if selected and pid not in selected:
            continue
        out_dir = problem_dir(pid) / "estimates"
        out_dir.mkdir(exist_ok=True)

        payload = {
            "problem_id": pid,
            "stage": "D",
            "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            **contract,
        }

        out_path = out_dir / "advantage_claim_contract.json"
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"OK {pid}: {contract['claim_category']} claim → {out_path.name}")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:] or None)
