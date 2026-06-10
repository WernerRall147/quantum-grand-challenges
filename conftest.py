"""Root conftest.py  auto-discovers test_baseline.py files and registers them as pytest tests."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_PROBLEMS_DIR = Path(__file__).parent / "problems"
_ARCHIVED_DIR = _PROBLEMS_DIR / "archived"


def _discover_baseline_tests():
    """Yield (problem_name, script_path) for every test_baseline.py."""
    for problem_dir in sorted(_PROBLEMS_DIR.iterdir()):
        script = problem_dir / "python" / "test_baseline.py"
        if script.is_file():
            yield problem_dir.name, script
    if _ARCHIVED_DIR.is_dir():
        for problem_dir in sorted(_ARCHIVED_DIR.iterdir()):
            script = problem_dir / "python" / "test_baseline.py"
            if script.is_file():
                yield problem_dir.name, script


_BASELINE_TESTS = list(_discover_baseline_tests())


@pytest.fixture(params=[name for name, _ in _BASELINE_TESTS], ids=[name for name, _ in _BASELINE_TESTS])
def baseline_test_script(request):
    """Return the path to a test_baseline.py script."""
    return dict(_BASELINE_TESTS)[request.param]


def test_baseline(baseline_test_script):
    """Run a problem's test_baseline.py as a subprocess and assert it exits 0."""
    result = subprocess.run(
        [sys.executable, str(baseline_test_script)],
        capture_output=True,
        text=True,
        timeout=60,
        env={**__import__("os").environ, "PYTHONUTF8": "1", "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, (
        f"test_baseline.py failed for {baseline_test_script.parent.parent.name}:\n"
        f"STDOUT: {result.stdout[-500:] if result.stdout else ''}\n"
        f"STDERR: {result.stderr[-500:] if result.stderr else ''}"
    )
