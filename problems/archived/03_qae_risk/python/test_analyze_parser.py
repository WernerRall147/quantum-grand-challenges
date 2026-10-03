import json
from argparse import Namespace
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import analyze as analyze_module
finally:
    sys.path.pop(0)

QAERiskAnalyzer = analyze_module.QAERiskAnalyzer


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

    quantum_events = [{"messages": quantum_stdout.splitlines()}]
    calls = {"init": None, "run": None}

    def _fake_init(**kwargs):
        calls["init"] = kwargs

    def _fake_run(*args, **kwargs):
        calls["run"] = (args, kwargs)
        return quantum_events

    monkeypatch.setattr(analyze_module.qsharp, "init", _fake_init)
    monkeypatch.setattr(analyze_module.qsharp, "run", _fake_run)
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: _Completed())

    analyzer = QAERiskAnalyzer(problem_dir=str(problem_dir), show_plots=False)
    payload = analyzer.run_quantum_estimation(skip_build=False)

    assert calls["init"] == {"project_root": str(qsharp_dir)}
    assert calls["run"] == (
        ("Main.RunQAERiskAnalysis()",),
        {"shots": 1, "save_events": True},
    )
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
    assert metrics["logical_qubits"] == 11
    assert metrics["t_count"] == 2880

    assert payload["histogram_counts"] == {0: 98, 32: 22}

    saved = json.loads((estimates_dir / "quantum_estimate.json").read_text(encoding="utf-8"))
    assert saved["estimator_target"] == "TailRisk > 2.5"


def test_main_exits_without_generating_outputs_when_qsharp_fails(
    monkeypatch,
    tmp_path: Path,
    capsys,
):
    (tmp_path / "qsharp").mkdir()
    (tmp_path / "python").mkdir()
    original_analyzer = QAERiskAnalyzer
    monkeypatch.setattr(
        analyze_module,
        "QAERiskAnalyzer",
        lambda **kwargs: original_analyzer(problem_dir=str(tmp_path), **kwargs),
    )
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: _Completed())
    monkeypatch.setattr(analyze_module.qsharp, "init", lambda **kwargs: None)

    def _fail_run(*args, **kwargs):
        raise RuntimeError("simulator failed")

    monkeypatch.setattr(analyze_module.qsharp, "run", _fail_run)
    args = Namespace(
        show_plots=False,
        build_timeout_seconds=180,
        run_timeout_seconds=180,
        instance_file=str(tmp_path / "missing.yaml"),
        loss_qubits=None,
        threshold=None,
        mean=None,
        std_dev=None,
        precision_bits=None,
        repetitions=None,
        run_sanity_check=None,
        ensemble_runs=1,
        skip_build=False,
    )

    with pytest.raises(SystemExit) as exc_info:
        analyze_module.main(args)

    assert "Failed to run Q# estimation: simulator failed" in capsys.readouterr().err
    assert exc_info.value.code != 0
    assert not (tmp_path / "plots" / "analysis_report.md").exists()
    assert not list((tmp_path / "estimates").glob("quantum*.json"))


def test_legacy_execution_flags_still_parse(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "analyze.py",
            "--skip-build",
            "--build-timeout-seconds",
            "12",
            "--run-timeout-seconds",
            "34",
        ],
    )

    args = analyze_module.parse_args()

    assert args.skip_build is True
    assert args.build_timeout_seconds == 12
    assert args.run_timeout_seconds == 34
