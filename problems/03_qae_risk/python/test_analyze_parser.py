import json
from pathlib import Path

from analyze import QAERiskAnalyzer


class _Completed:
    def __init__(self, stdout: str = "", stderr: str = ""):
        self.stdout = stdout
        self.stderr = stderr


def test_run_quantum_estimation_parses_current_console_format(monkeypatch, tmp_path: Path):
    problem_dir = tmp_path / "problem"
    qsharp_dir = problem_dir / "qsharp"
    estimates_dir = problem_dir / "estimates"
    plots_dir = problem_dir / "plots"
    qsharp_dir.mkdir(parents=True)
    estimates_dir.mkdir(parents=True)
    plots_dir.mkdir(parents=True)

    quantum_stdout = """
TestQaeUniformHalf mean=0,5000000000000001
=== Quantum Amplitude Estimation for Tail Risk Analysis ===

Risk Model Configuration:
  Loss distribution qubits: 4 (2^4 = 16 discrete levels)
  Loss threshold: 2,5
  Distribution: Log-normal(μ=0, σ=1)
  Theoretical tail probability P(Loss > 2,5): 0,18977381200856933

QAE Algorithm Parameters:
  Precision qubits: 6 (phase resolution: π/64)
  Repetitions: 120
  Total qubits: 11 (loss + precision + marker)

=== Canonical QAE Results (precision=6 bits, runs=120) ===
Phase measurement histogram (top 10):
  Phase 0/64 (θ=0, P≈0): 98 times
  Phase 32/64 (θ=1,5707963267948966, P≈1): 22 times
Most frequent outcome: phase=0/64, θ=0, P≈0
Mean amplitude estimate: 0,18333333333333332 ± 0,035322587464470735
Theoretical tail probability: 0,18977381200856933
Relative error: 3,3937657715097083%

=== Classical Baseline Comparison ===
Monte Carlo (10000 samples): 0,18977381200856933 ± 0,0039212206299098435
""".strip()

    calls = {"count": 0}

    def _fake_run(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return _Completed(stdout="build ok", stderr="")
        return _Completed(stdout=quantum_stdout, stderr="")

    monkeypatch.setattr("subprocess.run", _fake_run)

    analyzer = QAERiskAnalyzer(problem_dir=str(problem_dir), show_plots=False)
    payload = analyzer.run_quantum_estimation(skip_build=False)

    assert payload is not None
    metrics = payload["metrics"]
    params = payload["instance"]["parameters"]

    assert payload["estimator_target"] == "TailRisk > 2.5"
    assert params["phase_bits"] == 6
    assert params["repetitions"] == 120
    assert params["shots"] == 120
    assert params["threshold"] == 2.5
    assert params["loss_qubits"] == 4

    assert abs(metrics["quantum_estimate"] - 0.18333333333333332) < 1e-12
    assert abs(metrics["quantum_std_error"] - 0.035322587464470735) < 1e-12
    assert abs(metrics["analytic_probability"] - 0.18977381200856933) < 1e-12
    assert metrics["logical_qubits"] == 7
    assert metrics["t_count"] == 2880

    assert payload["histogram_counts"] == {0: 98, 32: 22}

    saved = json.loads((estimates_dir / "quantum_estimate.json").read_text(encoding="utf-8"))
    assert saved["estimator_target"] == "TailRisk > 2.5"
