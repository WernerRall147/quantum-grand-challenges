"""Generate Stage D advantage claim contracts for candidate problems."""

import json
from datetime import datetime, timezone
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

STAGE_D_CANDIDATES = {
    "03_qae_risk": {
        "claim_category": "theoretical",
        "problem_class": "Tail risk estimation: P(Loss > threshold) for continuous loss distributions",
        "instance_regime": "Log-normal(0,1) distribution, threshold=2.5, 4-qubit amplitude encoding",
        "baseline_algorithm": "Classical Monte Carlo with 10,000 samples (±0.39% at 95% CI)",
        "fairness_rationale": "MC is the standard industry method for tail risk; variance-reduced MC included for comparison",
        "quantum_resource_scaling": "QAE achieves O(1/ε) vs classical MC O(1/ε²)  quadratic speedup in precision",
        "data_loading_assumptions": "Amplitude encoding via multiplex rotations; exponential circuit depth O(2^n) for n-qubit encoding",
        "noise_model_assumptions": "Noiseless simulator; real hardware would require error correction for 40+ logical qubits",
        "confidence_method": "20-run calibration ensemble with 95% Clopper-Pearson confidence intervals",
        "residual_risks": [
            "Amplitude encoding circuit depth scales exponentially  practical advantage requires efficient state preparation",
            "293k physical qubits required  beyond current NISQ devices",
            "No noise model applied; fault-tolerant execution assumed",
            "Classical importance sampling may close the gap for structured distributions",
        ],
        "physical_qubits": 293120,
        "logical_qubits": 40,
        "t_gates": 15,
    },
    "05_qaoa_maxcut": {
        "claim_category": "theoretical",
        "problem_class": "Maximum cut in weighted graphs (NP-hard combinatorial optimization)",
        "instance_regime": "Triangle graph (3 vertices, 3 edges), depth-1 QAOA",
        "baseline_algorithm": "Brute-force enumeration (optimal for n≤20); Goemans-Williamson SDP (0.878-approx for large n)",
        "fairness_rationale": "At n=3, brute-force trivially finds optimal; GW guarantee only relevant at n>30",
        "quantum_resource_scaling": "QAOA expected ratio approaches optimal as depth p→∞; constant-depth advantage unproven for MaxCut",
        "data_loading_assumptions": "Graph encoded directly as ZZ interactions; no data loading overhead",
        "noise_model_assumptions": "Noiseless simulator; real QAOA at depth>1 highly sensitive to gate noise",
        "confidence_method": "20-run calibration ensemble; deterministic optimal found (ratio=1.0) on all runs",
        "residual_risks": [
            "No proven quantum advantage for MaxCut QAOA at any constant depth",
            "Classical GW algorithm achieves 0.878-approximation in polynomial time",
            "Instance is trivially small (n=3)  advantage claims meaningless at this scale",
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


def main():
    for pid, contract in STAGE_D_CANDIDATES.items():
        out_dir = PROBLEMS_DIR / pid / "estimates"
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
    main()
