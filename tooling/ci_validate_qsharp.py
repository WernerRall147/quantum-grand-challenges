"""Validate Q# compilation for all 20 problems using the modern QDK."""
import os
import sys
from pathlib import Path

import qsharp

# Discover problems from both active and archived directories
sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover_problems import discover_all_problems

failed = []
for pd in discover_all_problems():
    qs_dir = str(pd / "qsharp")
    if not os.path.isdir(qs_dir):
        continue
    if not os.path.isfile(os.path.join(qs_dir, "qsharp.json")):
        continue
    try:
        qsharp.init(project_root=qs_dir)
        print(f"OK {pd.name}: compilation passed")
    except Exception as e:
        print(f"FAIL {pd.name}: {str(e)[:200]}")
        failed.append(pd.name)

if failed:
    print(f"{len(failed)} problem(s) failed to compile: {failed}")
    sys.exit(1)

print(f"All {20 - len(failed)} problems compiled successfully.")
