#!/usr/bin/env python3
"""Run the QAE Risk Analysis Q# program using the modern QDK Python API.

Replaces the old `dotnet run` invocation.  The qdk package compiles and
simulates the Q# project in-process.  Message() output goes to stdout so
the existing analyze.py parser can consume it unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from qdk import qsharp
except ImportError:
    print(
        "Error: the 'qdk' package is not installed.\n"
        "Install with:  pip install qdk",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> int:
    qsharp_dir = Path(__file__).resolve().parent.parent / "qsharp"
    if not (qsharp_dir / "qsharp.json").exists():
        print(f"Error: qsharp.json not found in {qsharp_dir}", file=sys.stderr)
        return 1

    qsharp.init(project_root=str(qsharp_dir))
    qsharp.run("Main.RunQAERiskAnalysis()", 1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
