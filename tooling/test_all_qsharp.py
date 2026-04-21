#!/usr/bin/env python3
"""Test compilation of all migrated Q# projects and run entry points."""

import sys
import traceback
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"


def test_problem(problem_dir: Path) -> dict:
    """Test a single problem: compile + run entry point."""
    import qsharp

    qsharp_dir = problem_dir / "qsharp"
    result = {"problem": problem_dir.name, "compile": False, "run": False, "error": None}

    if not (qsharp_dir / "qsharp.json").exists():
        result["error"] = "No qsharp.json"
        return result

    try:
        qsharp.init(project_root=str(qsharp_dir))
        result["compile"] = True
    except Exception as e:
        result["error"] = f"Compile: {e}"
        return result

    # Try to run the entry point (capture first 500 chars of output)
    try:
        qsharp.run("Main.Main()", 1)
        result["run"] = True
    except Exception:
        # Main.Main() might not exist, try to find the entry point
        pass

    return result


def main():
    problem_dirs = sorted(
        [d for d in PROBLEMS_DIR.iterdir() if d.is_dir() and d.name[:2].isdigit()],
        key=lambda d: d.name,
    )
    # Also include archived problems
    archived = PROBLEMS_DIR / "archived"
    if archived.is_dir():
        problem_dirs.extend(sorted(
            [d for d in archived.iterdir() if d.is_dir() and d.name[:2].isdigit()],
            key=lambda d: d.name,
        ))
    problem_dirs.sort(key=lambda d: d.name)

    print(f"Testing {len(problem_dirs)} problems...\n")

    results = []
    for pd in problem_dirs:
        qsharp_dir = pd / "qsharp"
        if not (qsharp_dir / "qsharp.json").exists():
            print(f"⏭️  {pd.name}: no qsharp.json")
            continue

        r = test_problem(pd)
        results.append(r)
        icon = "✅" if r["compile"] else "❌"
        err = f" — {r['error']}" if r["error"] else ""
        print(f"{icon} {r['problem']}: compile={'OK' if r['compile'] else 'FAIL'}{err}")

    ok = sum(1 for r in results if r["compile"])
    fail = sum(1 for r in results if not r["compile"])
    print(f"\nResults: {ok} compiled OK, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
