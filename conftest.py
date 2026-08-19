"""Root conftest.py  auto-discovers test_baseline.py files and exposes them as a fixture."""

import os
from pathlib import Path

import pytest

# Citation resolution makes HTTP calls. Tests must not depend on a network, so it
# is disabled here rather than in each test that happens to reach evaluate().
os.environ.setdefault("QGC_VERIFY_CITATIONS", "0")

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
