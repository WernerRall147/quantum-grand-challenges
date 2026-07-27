"""Runs every problem's test_baseline.py as a subprocess (fixture lives in conftest.py)."""


def test_baseline(baseline_test_script):
    import subprocess
    import sys
    import os

    result = subprocess.run(
        [sys.executable, str(baseline_test_script)],
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "PYTHONUTF8": "1", "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, (
        f"test_baseline.py failed for {baseline_test_script.parent.parent.name}:\n"
        f"STDOUT: {result.stdout[-500:] if result.stdout else ''}\n"
        f"STDERR: {result.stderr[-500:] if result.stderr else ''}"
    )
