#!/usr/bin/env python3
"""
Iterative Quantum Amplitude Estimation (IQAE) driver for problem 03.

Implements Algorithm 1 of Grinko, Gacon, Zoufal and Woerner, "Iterative quantum amplitude
estimation", npj Quantum Information 7, 52 (2021), arXiv:1912.05559:
  - FindNextK (their Algorithm 2) picks the largest Grover power whose scaled interval stays
    in one half-circle, so each measurement inverts to a single interval on theta
  - Clopper-Pearson intervals at level alpha / T, with T the bound on the number of rounds,
    so the final interval contains a with probability at least 1 - alpha
  - Rounds that reuse a Grover power are pooled

The Q# IQAERound operation provides the quantum kernel; this module runs the classical loop.
Query counts are applications of A or its inverse (a Q^k A|0> shot costs 2k + 1), the unit in
which a classical Monte Carlo sample costs one.
"""

from __future__ import annotations

import math
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from scipy import stats


@dataclass
class IQAEParams:
    """Parameters for IQAE."""
    epsilon: float = 0.01         # Target half-width of the confidence interval on a
    alpha: float = 0.05           # The interval misses a with probability at most alpha
    shots_per_round: int = 100    # N_shots in Grinko et al.
    min_ratio: float = 2.0        # r in FindNextK: a new K is at least r times the last
    max_rounds: int = 1000        # Safety stop; the analysis in the paper needs far fewer


@dataclass
class IQAERoundResult:
    """Result of a single IQAE round."""
    k: int               # Grover power used
    shots: int            # Number of shots
    ones_count: int       # Number of 'One' outcomes
    measured_prob: float  # ones_count / shots
    ci_lower: float       # Clopper-Pearson bound on P(One|k), pooled over rounds with this k
    ci_upper: float
    oracle_queries: int   # Applications of A or its inverse this round = shots * (2k+1)
    upper_half_circle: bool = True


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


def max_rounds(epsilon: float, min_ratio: float = 2.0) -> int:
    """T in Grinko et al.: a bound on the number of rounds, over which alpha is split."""
    return int(math.log(min_ratio * math.pi / 8 / epsilon) / math.log(min_ratio)) + 1


def find_next_k(
    k: int,
    upper_half_circle: bool,
    theta_interval: tuple[float, float],
    min_ratio: float = 2.0,
) -> tuple[int, bool]:
    """FindNextK, Algorithm 2 of Grinko et al.

    theta is measured in turns: a = sin^2(2 pi theta) with theta in [0, 1/4], and
    P(One|k) = sin^2((2k+1) 2 pi theta) = (1 - cos(2 pi K theta)) / 2 with K = 4k + 2.
    Returns the largest k, with K at least `min_ratio` times the current K, for which K times
    the current interval lies inside one half-circle, where arccos inverts P uniquely; or the
    current k if there is none.
    """
    theta_l, theta_u = theta_interval
    old_scaling = 4 * k + 2
    max_scaling = int(1 / (2 * (theta_u - theta_l)))
    scaling = max_scaling - (max_scaling - 2) % 4
    while scaling >= min_ratio * old_scaling:
        theta_min = scaling * theta_l - int(scaling * theta_l)
        theta_max = scaling * theta_u - int(scaling * theta_u)
        if theta_min <= theta_max <= 0.5:
            return (scaling - 2) // 4, True
        if 0.5 <= theta_min <= theta_max:
            return (scaling - 2) // 4, False
        scaling -= 4
    return k, upper_half_circle


def iterative_amplitude_estimation(
    sample: Callable[[int, int], int],
    params: IQAEParams,
) -> IQAEResult:
    """Algorithm 1 of Grinko et al. with Clopper-Pearson intervals at level alpha / T.

    `sample(k, shots)` returns how many of `shots` measurements of Q^k A|0> gave One. The
    returned interval contains a with probability at least 1 - alpha.
    """
    start = time.time()
    alpha_round = params.alpha / max_rounds(params.epsilon, params.min_ratio)
    theta_l, theta_u = 0.0, 0.25
    k, upper = 0, True
    pooled_ones = pooled_shots = 0
    a_lo, a_hi = 0.0, 1.0
    rounds: list[IQAERoundResult] = []
    total_queries = total_shots = 0

    while theta_u - theta_l > params.epsilon / math.pi and len(rounds) < params.max_rounds:
        next_k, upper = find_next_k(k, upper, (theta_l, theta_u), params.min_ratio)
        if next_k != k or not rounds:
            pooled_ones = pooled_shots = 0
        k = next_k
        shots = params.shots_per_round
        ones = int(sample(k, shots))
        pooled_ones += ones
        pooled_shots += shots
        total_shots += shots
        total_queries += shots * (2 * k + 1)

        p_lo, p_hi = clopper_pearson(pooled_ones, pooled_shots, alpha_round)
        if upper:
            turn_lo = math.acos(1 - 2 * p_lo) / (2 * math.pi)
            turn_hi = math.acos(1 - 2 * p_hi) / (2 * math.pi)
        else:
            turn_lo = 1 - math.acos(1 - 2 * p_hi) / (2 * math.pi)
            turn_hi = 1 - math.acos(1 - 2 * p_lo) / (2 * math.pi)
        scaling = 4 * k + 2
        # Both ends share one half-circle, so take the whole turns from the lower end: the upper
        # end can sit exactly on the next whole turn when the interval on P reaches 0.
        whole_turns = int(scaling * theta_l)
        theta_l = (whole_turns + turn_lo) / scaling
        theta_u = (whole_turns + turn_hi) / scaling
        a_lo = math.sin(2 * math.pi * theta_l) ** 2
        a_hi = math.sin(2 * math.pi * theta_u) ** 2

        rounds.append(IQAERoundResult(
            k=k, shots=shots, ones_count=ones, measured_prob=ones / shots,
            ci_lower=p_lo, ci_upper=p_hi, oracle_queries=shots * (2 * k + 1),
            upper_half_circle=upper,
        ))

    return IQAEResult(
        estimate=(a_lo + a_hi) / 2,
        confidence_interval=(a_lo, a_hi),
        epsilon_achieved=(a_hi - a_lo) / 2,
        total_oracle_queries=total_queries,
        total_shots=total_shots,
        rounds=rounds,
        runtime_seconds=time.time() - start,
        converged=theta_u - theta_l <= params.epsilon / math.pi,
    )


def exact_sampler(a: float, rng: np.random.Generator) -> Callable[[int, int], int]:
    """A sampler that draws from the ideal P(One|k) = sin^2((2k+1) theta), sin^2(theta) = a."""
    theta = math.asin(math.sqrt(a))

    def sample(k: int, shots: int) -> int:
        return int(rng.binomial(shots, math.sin((2 * k + 1) * theta) ** 2))

    return sample


def discrete_loss_distribution(loss_qubits: int, mean: float, std_dev: float) -> tuple[list[float], list[float]]:
    """The distribution the circuit loads: Main.LogNormalProbabilities and LossValueFromIndex."""
    levels = 1 << loss_qubits
    values = [(i + 1) / levels * 10.0 for i in range(levels)]
    sigma = max(std_dev, 0.01)
    pdf = [math.exp(-((math.log(x) - mean) ** 2) / (2 * sigma * sigma)) / (x * sigma * math.sqrt(2 * math.pi)) for x in values]
    total = sum(pdf)
    return [p / total for p in pdf], values


def discrete_tail_probability(loss_qubits: int, threshold: float, mean: float, std_dev: float) -> float:
    """a, the amplitude the circuit encodes: P(loss > threshold) on the 2^n-level grid."""
    probabilities, values = discrete_loss_distribution(loss_qubits, mean, std_dev)
    return sum(p for p, x in zip(probabilities, values) if x > threshold)


def monte_carlo_samples_for(a: float, half_width: float, alpha: float) -> int:
    """Samples plain Monte Carlo needs for a normal-approximation interval of this half-width."""
    z = stats.norm.ppf(1 - alpha / 2)
    return int(math.ceil(z * z * a * (1 - a) / (half_width * half_width)))


class AdaptiveIQAE:
    """IQAE against the Q# kernel or an exact sampler.

    Usage with the local qsharp simulator:
        iqae = AdaptiveIQAE(params)
        result = iqae.run_local(loss_qubits=4, threshold=2.5, mean=0.0, std_dev=1.0)
    """

    def __init__(self, params: Optional[IQAEParams] = None):
        self.params = params or IQAEParams()

    def run(self, sample: Callable[[int, int], int], verbose: bool = False) -> IQAEResult:
        result = iterative_amplitude_estimation(sample, self.params)
        if verbose:
            for index, r in enumerate(result.rounds, start=1):
                half = "upper" if r.upper_half_circle else "lower"
                print(
                    f"  Round {index}: k={r.k}, shots={r.shots}, P(1)={r.measured_prob:.4f} "
                    f"pooled CI [{r.ci_lower:.4f}, {r.ci_upper:.4f}] ({half} half-circle)"
                )
        return result

    def run_local(
        self,
        loss_qubits: int = 4,
        threshold: float = 2.5,
        mean: float = 0.0,
        std_dev: float = 1.0,
        verbose: bool = True,
    ) -> IQAEResult:
        """Run IQAE with Main.IQAERound on the local qsharp simulator."""
        from qdk import qsharp

        prob_expr = f"Main.LogNormalProbabilities({loss_qubits}, {mean}, {std_dev})"

        def sample(k: int, shots: int) -> int:
            expr = f"Main.IQAERound({prob_expr}, {threshold}, {loss_qubits}, {k})"
            return sum(1 for r in qsharp.run(expr, shots) if str(r) == "One")

        return self.run(sample, verbose=verbose)


def run_variance_reduced_mc(
    mean: float,
    std_dev: float,
    threshold: float,
    n_samples: int = 100_000,
    use_antithetic: bool = True,
    use_control_variate: bool = True,
) -> dict:
    """Variance-reduced Monte Carlo on the continuous log-normal model (not the discrete grid).

    Implements:
      - Antithetic variates: pair each Z with -Z to reduce variance
      - Control variate: use E[X] of the log-normal as a control

    The standard error treats the antithetic pairs as independent draws, so it overstates the
    error of the paired estimator; the variance-reduction factor is correspondingly low.

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


def run_discrete_mc(
    loss_qubits: int,
    threshold: float,
    mean: float,
    std_dev: float,
    n_samples: int,
    rng: np.random.Generator,
) -> dict:
    """Plain Monte Carlo on the distribution the circuit loads, so it estimates the same a."""
    probabilities, values = discrete_loss_distribution(loss_qubits, mean, std_dev)
    draws = rng.choice(len(values), size=n_samples, p=probabilities)
    tail = np.array([values[i] > threshold for i in draws], dtype=float)
    p_hat = float(tail.mean())
    return {
        "estimate": p_hat,
        "standard_error": float(math.sqrt(p_hat * (1 - p_hat) / n_samples)),
        "samples": n_samples,
    }


def query_scaling(
    a: float,
    epsilons: list[float],
    alpha: float,
    shots_per_round: int,
    repeats: int,
    seed: int = 7,
) -> list[dict]:
    """IQAE query counts against plain Monte Carlo at the same interval half-width.

    IQAE runs against the exact sampler, whose P(One|k) the Q# kernel reproduces (see
    tooling/test_qae_kernel.py); query counts do not depend on which simulator drew the shots.
    Both sides count applications of A or its inverse, and ignore error correction.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for epsilon in epsilons:
        params = IQAEParams(epsilon=epsilon, alpha=alpha, shots_per_round=shots_per_round)
        runs = [iterative_amplitude_estimation(exact_sampler(a, rng), params) for _ in range(repeats)]
        half_widths = [r.epsilon_achieved for r in runs]
        queries = [r.total_oracle_queries for r in runs]
        mean_half_width = float(np.mean(half_widths))
        rows.append({
            "epsilon_target": epsilon,
            "iqae_mean_half_width": mean_half_width,
            "iqae_mean_queries": float(np.mean(queries)),
            "iqae_interval_misses": sum(1 for r in runs if not r.confidence_interval[0] <= a <= r.confidence_interval[1]),
            "runs": repeats,
            "mc_samples_same_half_width": monte_carlo_samples_for(a, mean_half_width, alpha),
        })
    return rows


def main() -> int:
    """Run the IQAE analysis against like-for-like classical baselines."""
    import argparse

    parser = argparse.ArgumentParser(description="IQAE driver (Grinko et al. 2021)")
    parser.add_argument("--loss-qubits", type=int, default=4)
    parser.add_argument("--threshold", type=float, default=2.5)
    parser.add_argument("--mean", type=float, default=0.0)
    parser.add_argument("--std-dev", type=float, default=1.0)
    parser.add_argument("--epsilon", type=float, default=0.05,
                        help="Target half-width of the interval on a (default: 0.05)")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="The interval misses a with probability at most alpha (default: 0.05)")
    parser.add_argument("--shots", type=int, default=100, help="Shots per round (default: 100)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Seed the classical sampling. The Q# simulator is left unseeded: "
                             "qsharp.set_quantum_seed repeats one outcome in every shot of a run")
    parser.add_argument("--skip-quantum", action="store_true",
                        help="Skip quantum IQAE, only run classical baselines")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file path")
    args = parser.parse_args()

    problem_dir = Path(__file__).resolve().parent.parent
    estimates_dir = problem_dir / "estimates"
    estimates_dir.mkdir(exist_ok=True)
    rng = np.random.default_rng(args.seed)

    results: dict = {
        "parameters": {
            "loss_qubits": args.loss_qubits,
            "threshold": args.threshold,
            "mean": args.mean,
            "std_dev": args.std_dev,
            "epsilon": args.epsilon,
            "alpha": args.alpha,
            "shots_per_round": args.shots,
        }
    }

    # ---- The quantity the circuit encodes, and the model it approximates ----
    from scipy.stats import lognorm
    discrete = discrete_tail_probability(args.loss_qubits, args.threshold, args.mean, args.std_dev)
    continuous = float(1.0 - lognorm(s=args.std_dev, scale=math.exp(args.mean)).cdf(args.threshold))
    print(f"Discrete tail probability on the {1 << args.loss_qubits}-level grid (what the circuit encodes): {discrete:.6f}")
    print(f"Continuous log-normal tail P(L > {args.threshold}) (what the grid approximates): {continuous:.6f}")
    results["discrete_tail_probability"] = discrete
    results["continuous_tail_probability"] = continuous

    # ---- Plain MC on the same discrete distribution ----
    mc_discrete = run_discrete_mc(args.loss_qubits, args.threshold, args.mean, args.std_dev, 100_000, rng)
    print(f"\n--- Plain Monte Carlo on the same {1 << args.loss_qubits}-level distribution ---")
    print(f"  {mc_discrete['estimate']:.6f} ± {mc_discrete['standard_error']:.6f} ({mc_discrete['samples']} samples)")
    results["discrete_mc"] = mc_discrete

    # ---- Variance-reduced MC on the continuous model ----
    print("\n--- Variance-reduced Monte Carlo on the continuous log-normal model ---")
    mc_result = run_variance_reduced_mc(
        args.mean, args.std_dev, args.threshold, n_samples=100_000
    )
    print(f"  Plain MC:    {mc_result['plain_mc_estimate']:.6f} ± {mc_result['plain_mc_se']:.6f}")
    print(f"  VR MC:       {mc_result['estimate']:.6f} ± {mc_result['standard_error']:.6f}")
    print(f"  VR factor:   {mc_result['variance_reduction_factor']:.2f}x")
    print(f"  This estimates the continuous tail ({continuous:.4f}), not the discrete a ({discrete:.4f}).")
    results["variance_reduced_mc_continuous_model"] = mc_result

    # ---- CVaR/VaR ----
    print("\n--- VaR / CVaR (classical bisection on the continuous model) ---")
    cvar_result = run_cvar_bisection(args.mean, args.std_dev, confidence_level=0.95)
    print(f"  VaR(95%):    {cvar_result['var_estimate']:.4f}  (theoretical: {cvar_result['var_theoretical']:.4f})")
    print(f"  CVaR(95%):   {cvar_result['cvar_estimate']:.4f}  (theoretical: {cvar_result['cvar_theoretical']:.4f})")
    results["cvar_var"] = cvar_result

    # ---- IQAE against the Q# kernel ----
    params = IQAEParams(epsilon=args.epsilon, alpha=args.alpha, shots_per_round=args.shots)
    if not args.skip_quantum:
        print(f"\n--- IQAE on the Q# kernel (ε={args.epsilon}, α={args.alpha}, {args.shots} shots per round) ---")
        try:
            from qdk import qsharp
            qsharp.init(project_root=str(problem_dir / "qsharp"))
            iqae_result = AdaptiveIQAE(params).run_local(
                loss_qubits=args.loss_qubits,
                threshold=args.threshold,
                mean=args.mean,
                std_dev=args.std_dev,
            )
            lo, hi = iqae_result.confidence_interval
            mc_needed = monte_carlo_samples_for(discrete, iqae_result.epsilon_achieved, args.alpha)
            print(f"\n  IQAE estimate:    {iqae_result.estimate:.6f}")
            print(f"  Interval:         [{lo:.6f}, {hi:.6f}] (contains a = {discrete:.6f}: {lo <= discrete <= hi})")
            print(f"  Half-width:       {iqae_result.epsilon_achieved:.6f}")
            print(f"  Queries:          {iqae_result.total_oracle_queries} applications of A or its inverse")
            print(f"  Plain MC needs:   {mc_needed} samples for the same half-width at the same confidence")
            print(f"  Qubits used:      {args.loss_qubits + 1} (no precision register)")

            results["iqae"] = {
                "estimate": iqae_result.estimate,
                "confidence_interval": [lo, hi],
                "contains_discrete_tail": lo <= discrete <= hi,
                "epsilon_achieved": iqae_result.epsilon_achieved,
                "total_oracle_queries": iqae_result.total_oracle_queries,
                "mc_samples_same_half_width": mc_needed,
                "total_shots": iqae_result.total_shots,
                "converged": iqae_result.converged,
                "runtime_seconds": iqae_result.runtime_seconds,
                "qubits": args.loss_qubits + 1,
                "rounds": [
                    {
                        "k": r.k, "shots": r.shots, "ones": r.ones_count,
                        "measured_prob": r.measured_prob,
                        "pooled_ci": [r.ci_lower, r.ci_upper],
                        "upper_half_circle": r.upper_half_circle,
                        "oracle_queries": r.oracle_queries,
                    }
                    for r in iqae_result.rounds
                ],
            }
        except ImportError:
            print("  [Skipped  qsharp package not available]")

    # ---- Query counts against plain MC at equal precision ----
    print("\n--- Queries at equal half-width (exact sampler, 20 runs per ε) ---")
    scaling = query_scaling(discrete, [0.05, 0.02, 0.01, 0.005, 0.002, 0.001], args.alpha, args.shots, repeats=20)
    for row in scaling:
        print(
            f"  ε={row['epsilon_target']:<6} IQAE {row['iqae_mean_queries']:>9.0f} queries "
            f"(half-width {row['iqae_mean_half_width']:.5f}, misses {row['iqae_interval_misses']}/{row['runs']})  "
            f"plain MC {row['mc_samples_same_half_width']:>9} samples"
        )
    fewer = [row["epsilon_target"] for row in scaling if row["iqae_mean_queries"] < row["mc_samples_same_half_width"]]
    if len(fewer) == len(scaling):
        print(f"  IQAE needs fewer queries than plain MC at every ε tested ({scaling[0]['epsilon_target']} to {scaling[-1]['epsilon_target']}).")
    elif fewer:
        print(f"  IQAE needs fewer queries than plain MC only at ε in {fewer}.")
    else:
        print("  IQAE never needs fewer queries than plain MC in this range.")
    print("  These are noiseless query counts; error correction makes each quantum query far slower than a sample.")
    results["query_scaling"] = {"rows": scaling, "iqae_fewer_queries_at_epsilon": fewer}

    # ---- Save results ----
    from datetime import datetime, timezone
    results["generated_utc"] = datetime.now(timezone.utc).isoformat()
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
