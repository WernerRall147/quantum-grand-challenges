"""Classical moving-average crossover baseline for high-frequency trading instances."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import yaml


@dataclass(frozen=True)
class TradingInstance:
    instance_id: str
    description: str
    steps: int
    interval: float
    annual_trading_days: int
    short_window: int
    long_window: int
    threshold: float
    transaction_cost: float
    volatility: float
    drift: float
    seed: int


def load_instances(instances_dir: Path) -> List[TradingInstance]:
    instances: List[TradingInstance] = []
    for path in sorted(instances_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        instances.append(
            TradingInstance(
                instance_id=path.stem,
                description=str(raw.get("description", "")),
                steps=int(raw["steps"]),
                interval=float(raw["interval"]),
                annual_trading_days=int(raw.get("annual_trading_days", 252)),
                short_window=int(raw["short_window"]),
                long_window=int(raw["long_window"]),
                threshold=float(raw.get("threshold", 0.0)),
                transaction_cost=float(raw.get("transaction_cost", 0.0)),
                volatility=float(raw.get("volatility", 0.01)),
                drift=float(raw.get("drift", 0.0)),
                seed=int(raw.get("seed", 1234)),
            )
        )
    return instances


def moving_average(series: np.ndarray, window: int) -> np.ndarray:
    if window <= 0:
        raise ValueError("Window size must be positive.")
    result = np.full(series.shape, np.nan, dtype=float)
    if window > len(series):
        return result
    cumsum = np.cumsum(series, dtype=float)
    result[window - 1 :] = (
        cumsum[window - 1 :] - np.concatenate(([0.0], cumsum[:-window]))
    ) / window
    return result


def geometric_brownian_path(instance: TradingInstance) -> np.ndarray:
    rng = np.random.default_rng(instance.seed)
    dt = instance.interval / float(instance.annual_trading_days)
    increments = (
        (instance.drift - 0.5 * instance.volatility**2) * dt
        + instance.volatility * np.sqrt(dt) * rng.standard_normal(instance.steps)
    )
    log_prices = np.concatenate(([0.0], np.cumsum(increments)))
    prices = 100.0 * np.exp(log_prices)
    return prices


def build_trading_signal(prices: np.ndarray, instance: TradingInstance) -> Dict[str, np.ndarray]:
    short_ma = moving_average(prices, instance.short_window)
    long_ma = moving_average(prices, instance.long_window)
    signal = short_ma - long_ma

    positions = np.zeros(instance.steps, dtype=float)
    current_position = 0.0
    for t in range(instance.steps):
        signal_value = signal[t]
        if np.isnan(signal_value):
            positions[t] = current_position
            continue
        if signal_value > instance.threshold:
            current_position = 1.0
        elif signal_value < -instance.threshold:
            current_position = -1.0
        # Otherwise maintain the previous position.
        positions[t] = current_position

    return {
        "short_ma": short_ma,
        "long_ma": long_ma,
        "signal": signal,
        "positions": positions,
    }


def downsample(series: np.ndarray, max_points: int = 200) -> List[float]:
    if len(series) <= max_points:
        return [float(x) for x in series]
    indices = np.linspace(0, len(series) - 1, max_points, dtype=int)
    return [float(series[i]) for i in indices]


def analyze_instance(instance: TradingInstance) -> Dict[str, object]:
    prices = geometric_brownian_path(instance)
    signal_data = build_trading_signal(prices, instance)

    log_returns = np.diff(np.log(prices))
    positions = signal_data["positions"]
    position_history = np.concatenate(([0.0], positions))
    position_changes = np.diff(position_history)

    raw_returns = positions * log_returns
    trading_costs = instance.transaction_cost * np.abs(position_changes)
    net_returns = raw_returns - trading_costs

    equity_curve = np.exp(np.cumsum(net_returns))
    total_return = float(equity_curve[-1] - 1.0)

    annualization_factor = 0.0
    if instance.interval > 0:
        steps_per_day = int(round(1.0 / instance.interval))
        annualization_factor = float(steps_per_day * instance.annual_trading_days)
    sharpe_ratio = 0.0
    volatility = float(np.std(net_returns))
    if volatility > 1e-12:
        sharpe_ratio = float((np.mean(net_returns) / volatility) * np.sqrt(annualization_factor))

    win_rate = float(np.mean(net_returns > 0.0)) if len(net_returns) > 0 else 0.0
    turnover = float(np.mean(np.abs(position_changes))) if len(position_changes) > 0 else 0.0

    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = 1.0 - equity_curve / running_max
    max_drawdown = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0

    sampled_prices = downsample(prices)
    sampled_equity = downsample(equity_curve)

    return {
        "instance_id": instance.instance_id,
        "description": instance.description,
        "steps": instance.steps,
        "short_window": instance.short_window,
        "long_window": instance.long_window,
        "threshold": instance.threshold,
        "transaction_cost": instance.transaction_cost,
        "total_return": total_return,
        "sharpe_ratio": sharpe_ratio,
        "win_rate": win_rate,
        "turnover": turnover,
        "max_drawdown": max_drawdown,
        "sampled_price_path": sampled_prices,
        "sampled_equity_curve": sampled_equity,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    instances = load_instances(root / "instances")
    if not instances:
        raise RuntimeError("No HFT instances found. Add YAML files to ../instances.")

    results = [analyze_instance(instance) for instance in instances]
    payload = {
        "problem_id": "06_high_frequency_trading",
        "model": "moving_average_crossover",
        "results": results,
    }

    estimates_path = root / "estimates" / "classical_baseline.json"
    estimates_path.write_text(json.dumps(payload, indent=2))

    try:
        rel_path = estimates_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_path = estimates_path

    print(f"✅ Classical baseline written to {rel_path}")


if __name__ == "__main__":
    main()
