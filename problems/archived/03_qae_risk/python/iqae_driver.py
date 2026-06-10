#!/usr/bin/env python3
"""
Adaptive IQAE (Iterative Quantum Amplitude Estimation) Python driver.

Implements the full IQAE algorithm from Grinko et al. (arXiv:1912.05559):
  - Confidence-interval narrowing with Clopper-Pearson bounds
  - Adaptive Grover power scheduling
  - Quadratic speedup: O(1/ε) oracle queries vs O(1/ε²) for classical MC

The Q# IQAERound operation provides the quantum kernel; this module
handles the classical outer loop.
"""

from __future__ import annotations

import math
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from scipy import stats


@dataclass
class IQAEParams:
    """Parameters for the IQAE algorithm."""
    epsilon: float = 0.01         # Target additive precision
    alpha: float = 0.05           # Failure probability (1 - confidence)
    max_iterations: int = 100     # Max number of adaptive rounds
    min_shots: int = 100          # Minimum shots per round
    max_grover_power: int = 64    # Maximum k for G^k


@dataclass
class IQAERoundResult:
    """Result of a single IQAE round."""
    k: int               # Grover power used
    shots: int            # Number of shots
    ones_count: int       # Number of 'One' outcomes
    measured_prob: float  # ones_count / shots
    ci_lower: float       # Clopper-Pearson lower bound
    ci_upper: float       # Clopper-Pearson upper bound
    oracle_queries: int   # Total oracle calls this round = shots * (2k+1)


@dataclass
class IQAEResult:
    """Full IQAE estimation result."""
    estimate: float
    confidence_interval: tuple[float, float]
    epsilon_achieved: float
    total_oracle_queries: int
    total_shots: int
    rounds: list[IQAERoundResult] = field(default_factory=list)
    runtime_seconds: float = 0.0
    converged: bool = False


def clopper_pearson(ones: int, total: int, alpha: float) -> tuple[float, float]:
    """Clopper-Pearson exact confidence interval for binomial proportion.

    Returns (lower, upper) at confidence level 1-alpha.
    """
    if total == 0:
        return (0.0, 1.0)
    if ones == 0:
        lo = 0.0
    else:
        lo = stats.beta.ppf(alpha / 2, ones, total - ones + 1)
    if ones == total:
        hi = 1.0
    else:
        hi = stats.beta.ppf(1 - alpha / 2, ones + 1, total - ones)
    return (float(lo), float(hi))


def _theta_from_prob(p: float) -> float:
    """Convert measurement probability to θ: p = sin²(θ) → θ = arcsin(√p)."""
    p_clipped = max(0.0, min(1.0, p))
    return math.asin(math.sqrt(p_clipped))


def _amplitude_ci_from_round(
    k: int,
    ci_lower: float,
    ci_upper: float,
) -> list[tuple[float, float]]:
    """Convert a confidence interval on P(One|k) to intervals on the amplitude a.

    For Grover power k:  P(One|k) = sin²((2k+1)θ), with a = sin²(θ).
    The mapping from P → θ → a has multiple branches due to sin² periodicity.
    Returns a list of candidate (a_lo, a_hi) intervals.
    """
    factor = 2 * k + 1
    # θ_lo and θ_hi from the CI on P(One)
    theta_lo_direct = _theta_from_prob(ci_lower) / factor
    theta_hi_direct = _theta_from_prob(ci_upper) / factor

    candidates = []
    # Consider branches: θ could be in [j*π/factor, (j+1)*π/factor] for various j
    # For practical IQAE, the first few branches suffice
    for j in range(factor):
        # Branch j: θ = (j*π ± arcsin(√p)) / factor
        for sign in [1, -1]:
            theta_lo = (j * math.pi + sign * _theta_from_prob(ci_lower)) / factor
            theta_hi = (j * math.pi + sign * _theta_from_prob(ci_upper)) / factor
            if theta_lo > theta_hi:
                theta_lo, theta_hi = theta_hi, theta_lo
            # θ must be in [0, π/2] for a ∈ [0, 1]
            theta_lo = max(0.0, min(math.pi / 2, theta_lo))
            theta_hi = max(0.0, min(math.pi / 2, theta_hi))
            if theta_hi > theta_lo:
                a_lo = math.sin(theta_lo) ** 2
                a_hi = math.sin(theta_hi) ** 2
                if a_lo > a_hi:
                    a_lo, a_hi = a_hi, a_lo
                candidates.append((a_lo, a_hi))

    # De-duplicate and merge overlapping intervals
    if not candidates:
        return [(0.0, 1.0)]

    candidates.sort()
    merged = [candidates[0]]
    for lo, hi in candidates[1:]:
        if lo <= merged[-1][1] + 1e-12:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))

    return merged


def _intersect_intervals(
    current: list[tuple[float, float]],
    new: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Intersect two lists of intervals on [0, 1]."""
    result = []
    for a_lo, a_hi in current:
        for b_lo, b_hi in new:
            lo = max(a_lo, b_lo)
            hi = min(a_hi, b_hi)
            if hi > lo + 1e-15:
                result.append((lo, hi))
    return result if result else [(0.0, 1.0)]


def _pick_next_k(
    current_intervals: list[tuple[float, float]],
    prev_k: int,
    max_k: int,
) -> int:
    """Pick the next Grover power k that best disambiguates the current interval.

    Strategy: double k (exponential schedule), capped at max.
    More sophisticated: pick k so that (2k+1)*θ rotates the interval
    away from the sin² extrema.
    """
    # Simple exponential schedule (matches arXiv:1912.05559 Section III.A)
    next_k = max(1, prev_k * 2)
    return min(next_k, max_k)


def _shots_for_round(k: int, alpha_round: float, epsilon: float) -> int:
    """Determine number of shots for a round to achieve target resolution.

    Uses the Clopper-Pearson interval width heuristic:
    width ≈ 2 * z_{α/2} * √(p(1-p)/N)
    For worst case p=0.5: N ≈ (z / w)² where w is target width.
    """
    z = stats.norm.ppf(1 - alpha_round / 2)
    # Target: interval width on P(One) should map to ≤ ε on amplitude
    factor = 2 * k + 1
    target_width = epsilon * factor * 2  # rough: δa ≈ δP / (2k+1)
    target_width = min(target_width, 0.5)  # don't go wider than 0.5
    n = max(50, int(math.ceil((z / target_width) ** 2 * 0.25)))
    return min(n, 10000)  # cap per-round shots


class AdaptiveIQAE:
    """Full adaptive IQAE algorithm with confidence-interval narrowing.

    Usage with local qsharp simulator:
        iqae = AdaptiveIQAE(params)
        result = iqae.run_local(loss_qubits=4, threshold=2.5, mean=0.0, std_dev=1.0)

    Usage with Azure Quantum (future):
        iqae = AdaptiveIQAE(params)
        result = iqae.run_azure(workspace, target, ...)
    """

    def __init__(self, params: Optional[IQAEParams] = None):
        self.params = params or IQAEParams()

    def run_local(
        self,
        loss_qubits: int = 4,
        threshold: float = 2.5,
        mean: float = 0.0,
        std_dev: float = 1.0,
        verbose: bool = True,
    ) -> IQAEResult:
        """Run IQAE using the local qsharp sparse-state simulator."""
        import qsharp

        start = time.time()
        p = self.params

        # ---- Build the Q# expression template ----
        prob_expr = f"Main.LogNormalProbabilities({loss_qubits}, {mean}, {std_dev})"
        def run_round(k: int, shots: int) -> tuple[int, int]:
            """Execute IQAERound shots times, return (ones_count, total)."""
            expr = f"Main.IQAERound({prob_expr}, {threshold}, {loss_qubits}, {k})"
            results = qsharp.run(expr, shots)
            ones = sum(1 for r in results if str(r) == "One")
            return ones, shots

        # ---- Adaptive loop ----
        rounds: list[IQAERoundResult] = []
        total_oracle_queries = 0
        total_shots = 0

        # Current confidence interval on the amplitude a ∈ [0, 1]
        current_ci: list[tuple[float, float]] = [(0.0, 1.0)]
        k = 0
        alpha_used = 0.0
        max_rounds = p.max_iterations

        for round_idx in range(max_rounds):
            # Allocate failure probability budget for this round
            alpha_round = p.alpha / (2 * max_rounds)
            alpha_used += alpha_round

            # Determine shots
            shots = max(p.min_shots, _shots_for_round(k, alpha_round, p.epsilon))

            # Run quantum round
            ones, total = run_round(k, shots)
            measured_prob = ones / total
            ci_lo, ci_hi = clopper_pearson(ones, total, alpha_round)

            oracle_queries = total * (2 * k + 1)
            total_oracle_queries += oracle_queries
            total_shots += total

            rr = IQAERoundResult(
                k=k, shots=total, ones_count=ones,
                measured_prob=measured_prob,
                ci_lower=ci_lo, ci_upper=ci_hi,
                oracle_queries=oracle_queries,
            )
            rounds.append(rr)

            # Map CI on P(One|k) to CI on amplitude a
            a_intervals = _amplitude_ci_from_round(k, ci_lo, ci_hi)
            current_ci = _intersect_intervals(current_ci, a_intervals)

            # Best estimate = midpoint of tightest interval
            best_interval = min(current_ci, key=lambda iv: iv[1] - iv[0])
            estimate = (best_interval[0] + best_interval[1]) / 2
            half_width = (best_interval[1] - best_interval[0]) / 2

            if verbose:
                print(
                    f"  Round {round_idx + 1}: k={k}, shots={total}, "
                    f"P(1)={measured_prob:.4f} [{ci_lo:.4f}, {ci_hi:.4f}], "
                    f"a ∈ [{best_interval[0]:.6f}, {best_interval[1]:.6f}], "
                    f"est={estimate:.6f} ± {half_width:.6f}"
                )

            # Check convergence
            if half_width <= p.epsilon:
                runtime = time.time() - start
                return IQAEResult(
                    estimate=estimate,
                    confidence_interval=(best_interval[0], best_interval[1]),
                    epsilon_achieved=half_width,
                    total_oracle_queries=total_oracle_queries,
                    total_shots=total_shots,
                    rounds=rounds,
                    runtime_seconds=runtime,
                    converged=True,
                )

            # Pick next k
            k = _pick_next_k(current_ci, k, p.max_grover_power)

        # Did not converge  return best so far
        runtime = time.time() - start
        best_interval = min(current_ci, key=lambda iv: iv[1] - iv[0])
        estimate = (best_interval[0] + best_interval[1]) / 2
        half_width = (best_interval[1] - best_interval[0]) / 2

        return IQAEResult(
            estimate=estimate,
            confidence_interval=(best_interval[0], best_interval[1]),
            epsilon_achieved=half_width,
            total_oracle_queries=total_oracle_queries,
            total_shots=total_shots,
            rounds=rounds,
            runtime_seconds=runtime,
            converged=False,
        )


def run_variance_reduced_mc(
    mean: float,
    std_dev: float,
    threshold: float,
    n_samples: int = 100_000,
    use_antithetic: bool = True,
    use_control_variate: bool = True,
) -> dict:
    """Variance-reduced Monte Carlo baseline (per QAEUpdates2026 benchmarking rules).

    Implements:
      - Antithetic variates: pair each Z with -Z to reduce variance
      - Control variate: use E[X] of the log-normal as a control

    Returns dict with estimate, standard_error, samples, runtime, method details.
    """
    start = time.time()
    rng = np.random.default_rng()

    if use_antithetic:
        half = n_samples // 2
        z = rng.normal(mean, std_dev, half)
        losses = np.concatenate([np.exp(z), np.exp(2 * mean - z)])  # antithetic pairs
    else:
        losses = rng.lognormal(mean, std_dev, n_samples)

    tail_indicators = (losses > threshold).astype(float)
    p_hat = tail_indicators.mean()

    if use_control_variate:
        # Control variate: use the loss values themselves
        # E[X] for log-normal is exp(mu + sigma^2/2)
        expected_loss = math.exp(mean + std_dev**2 / 2)
        cov = np.cov(tail_indicators, losses)[0, 1]
        var_loss = np.var(losses)
        if var_loss > 0:
            c_star = -cov / var_loss
            p_hat_cv = p_hat + c_star * (losses.mean() - expected_loss)
            p_hat_cv = max(0.0, min(1.0, p_hat_cv))
            se_cv = float(np.std(tail_indicators + c_star * (losses - expected_loss)) / math.sqrt(len(losses)))
        else:
            p_hat_cv = p_hat
            se_cv = float(np.std(tail_indicators) / math.sqrt(len(losses)))
    else:
        p_hat_cv = p_hat
        se_cv = float(np.std(tail_indicators) / math.sqrt(len(losses)))

    plain_se = float(np.sqrt(p_hat * (1 - p_hat) / len(losses)))
    runtime = time.time() - start

    return {
        "estimate": float(p_hat_cv),
        "standard_error": se_cv,
        "plain_mc_estimate": float(p_hat),
        "plain_mc_se": plain_se,
        "variance_reduction_factor": plain_se / se_cv if se_cv > 0 else float("inf"),
        "samples": len(losses),
        "runtime_seconds": runtime,
        "methods": {
            "antithetic": use_antithetic,
            "control_variate": use_control_variate,
        },
    }


def run_cvar_bisection(
    mean: float,
    std_dev: float,
    confidence_level: float = 0.95,
    loss_qubits: int = 4,
    n_bisection_steps: int = 20,
    mc_samples: int = 100_000,
) -> dict:
    """Estimate VaR and CVaR via bisection search over thresholds.

    Per QAEUpdates2026: VaR = bisection_search_over_thresholds (max n steps).
    CVaR = bounded expectation reformulation.

    Uses classical MC for now; the Q# IQAERound kernel can replace
    the inner tail-probability oracle when running on quantum hardware.

    Returns dict with var_estimate, cvar_estimate, threshold_grid, tail_curve.
    """
    start = time.time()
    rng = np.random.default_rng()
    losses = rng.lognormal(mean, std_dev, mc_samples)

    alpha = 1.0 - confidence_level  # e.g. 0.05 for 95% VaR

    # --- VaR via bisection ---
    lo, hi = 0.0, float(np.percentile(losses, 99.9))
    threshold_grid = []
    tail_curve = []

    for step in range(n_bisection_steps):
        mid = (lo + hi) / 2.0
        tail_prob = float(np.mean(losses > mid))
        threshold_grid.append(mid)
        tail_curve.append(tail_prob)

        if tail_prob > alpha:
            lo = mid
        else:
            hi = mid

    var_estimate = (lo + hi) / 2.0

    # --- CVaR = E[L | L > VaR] ---
    tail_losses = losses[losses > var_estimate]
    cvar_estimate = float(tail_losses.mean()) if len(tail_losses) > 0 else var_estimate

    # --- Also compute theoretical values for log-normal ---
    from scipy.stats import lognorm
    dist = lognorm(s=std_dev, scale=math.exp(mean))
    var_theoretical = float(dist.ppf(confidence_level))
    # CVaR theoretical = E[X | X > VaR] = E[X * 1(X>VaR)] / P(X > VaR)
    # For log-normal: E[X * 1(X>q)] = exp(μ + σ²/2) * Φ((μ + σ² - ln(q))/σ)
    phi_arg = (mean + std_dev**2 - math.log(var_theoretical)) / std_dev
    cvar_theoretical = float(
        math.exp(mean + std_dev**2 / 2)
        * stats.norm.cdf(phi_arg)
        / alpha
    )

    runtime = time.time() - start

    return {
        "confidence_level": confidence_level,
        "alpha": alpha,
        "var_estimate": var_estimate,
        "var_theoretical": var_theoretical,
        "var_error": abs(var_estimate - var_theoretical),
        "cvar_estimate": cvar_estimate,
        "cvar_theoretical": cvar_theoretical,
        "cvar_error": abs(cvar_estimate - cvar_theoretical),
        "bisection_steps": n_bisection_steps,
        "threshold_grid": threshold_grid,
        "tail_probability_curve": tail_curve,
        "mc_samples": mc_samples,
        "runtime_seconds": runtime,
    }


def main() -> int:
    """Run the full IQAE analysis pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Adaptive IQAE driver")
    parser.add_argument("--loss-qubits", type=int, default=4)
    parser.add_argument("--threshold", type=float, default=2.5)
    parser.add_argument("--mean", type=float, default=0.0)
    parser.add_argument("--std-dev", type=float, default=1.0)
    parser.add_argument("--epsilon", type=float, default=0.05,
                        help="Target precision (default: 0.05)")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="Failure probability (default: 0.05)")
    parser.add_argument("--max-power", type=int, default=16)
    parser.add_argument("--min-shots", type=int, default=100)
    parser.add_argument("--skip-quantum", action="store_true",
                        help="Skip quantum IQAE, only run classical baselines")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file path")
    args = parser.parse_args()

    problem_dir = Path(__file__).resolve().parent.parent
    estimates_dir = problem_dir / "estimates"
    estimates_dir.mkdir(exist_ok=True)

    results: dict = {
        "parameters": {
            "loss_qubits": args.loss_qubits,
            "threshold": args.threshold,
            "mean": args.mean,
            "std_dev": args.std_dev,
        }
    }

    # ---- Theoretical baseline ----
    from scipy.stats import lognorm
    dist = lognorm(s=args.std_dev, scale=math.exp(args.mean))
    theoretical = 1.0 - dist.cdf(args.threshold)
    print(f"Theoretical tail probability P(L > {args.threshold}): {theoretical:.6f}")
    results["theoretical_tail_probability"] = theoretical

    # ---- Variance-reduced MC ----
    print("\n--- Variance-Reduced Monte Carlo ---")
    mc_result = run_variance_reduced_mc(
        args.mean, args.std_dev, args.threshold, n_samples=100_000
    )
    print(f"  Plain MC:    {mc_result['plain_mc_estimate']:.6f} ± {mc_result['plain_mc_se']:.6f}")
    print(f"  VR MC:       {mc_result['estimate']:.6f} ± {mc_result['standard_error']:.6f}")
    print(f"  VR factor:   {mc_result['variance_reduction_factor']:.2f}x")
    print(f"  Samples:     {mc_result['samples']}")
    print(f"  Runtime:     {mc_result['runtime_seconds']:.4f}s")
    results["variance_reduced_mc"] = mc_result

    # ---- CVaR/VaR ----
    print("\n--- VaR / CVaR (bisection search) ---")
    cvar_result = run_cvar_bisection(args.mean, args.std_dev, confidence_level=0.95)
    print(f"  VaR(95%):    {cvar_result['var_estimate']:.4f}  (theoretical: {cvar_result['var_theoretical']:.4f})")
    print(f"  CVaR(95%):   {cvar_result['cvar_estimate']:.4f}  (theoretical: {cvar_result['cvar_theoretical']:.4f})")
    print(f"  Bisection:   {cvar_result['bisection_steps']} steps")
    results["cvar_var"] = cvar_result

    # ---- Adaptive IQAE ----
    if not args.skip_quantum:
        print(f"\n--- Adaptive IQAE (ε={args.epsilon}, α={args.alpha}) ---")
        try:
            import qsharp
            qsharp.init(project_root=str(problem_dir / "qsharp"))

            params = IQAEParams(
                epsilon=args.epsilon,
                alpha=args.alpha,
                max_grover_power=args.max_power,
                min_shots=args.min_shots,
            )
            iqae = AdaptiveIQAE(params)
            iqae_result = iqae.run_local(
                loss_qubits=args.loss_qubits,
                threshold=args.threshold,
                mean=args.mean,
                std_dev=args.std_dev,
            )
            print(f"\n  IQAE estimate:    {iqae_result.estimate:.6f}")
            print(f"  CI:               [{iqae_result.confidence_interval[0]:.6f}, {iqae_result.confidence_interval[1]:.6f}]")
            print(f"  ε achieved:       {iqae_result.epsilon_achieved:.6f}")
            print(f"  Oracle queries:   {iqae_result.total_oracle_queries}")
            print(f"  Total shots:      {iqae_result.total_shots}")
            print(f"  Converged:        {iqae_result.converged}")
            print(f"  Runtime:          {iqae_result.runtime_seconds:.2f}s")
            print(f"  Qubits used:      {args.loss_qubits + 1} (no precision register)")

            results["iqae"] = {
                "estimate": iqae_result.estimate,
                "confidence_interval": list(iqae_result.confidence_interval),
                "epsilon_achieved": iqae_result.epsilon_achieved,
                "total_oracle_queries": iqae_result.total_oracle_queries,
                "total_shots": iqae_result.total_shots,
                "converged": iqae_result.converged,
                "runtime_seconds": iqae_result.runtime_seconds,
                "qubits": args.loss_qubits + 1,
                "rounds": [
                    {
                        "k": r.k, "shots": r.shots, "ones": r.ones_count,
                        "measured_prob": r.measured_prob,
                        "ci": [r.ci_lower, r.ci_upper],
                        "oracle_queries": r.oracle_queries,
                    }
                    for r in iqae_result.rounds
                ],
            }

            # ---- Comparison summary ----
            print("\n--- Comparison Summary ---")
            print(f"  Theoretical:  {theoretical:.6f}")
            print(f"  IQAE:         {iqae_result.estimate:.6f} ± {iqae_result.epsilon_achieved:.6f}  ({iqae_result.total_oracle_queries} queries, {args.loss_qubits + 1} qubits)")
            print(f"  VR MC:        {mc_result['estimate']:.6f} ± {mc_result['standard_error']:.6f}  ({mc_result['samples']} samples)")
            if iqae_result.total_oracle_queries > 0 and mc_result['samples'] > 0:
                query_ratio = mc_result['samples'] / iqae_result.total_oracle_queries
                print(f"  Query ratio:  MC/IQAE = {query_ratio:.1f}x")

        except ImportError:
            print("  [Skipped  qsharp package not available]")
        except Exception as e:
            print(f"  [Error: {e}]")
            results["iqae"] = {"error": str(e)}

    # ---- Save results ----
    out_path = Path(args.output) if args.output else estimates_dir / "iqae_analysis.json"
    # Convert numpy types for JSON serialization
    def _convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Not serializable: {type(obj)}")

    out_path.write_text(json.dumps(results, indent=2, default=_convert), encoding="utf-8")
    print(f"\nResults saved to {out_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
