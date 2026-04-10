"""Validate Q# compilation for all 20 problems using the modern QDK."""
import os
import sys

import qsharp

failed = []
for d in sorted(os.listdir("problems")):
    qs_dir = os.path.join("problems", d, "qsharp")
    if not os.path.isdir(qs_dir):
        continue
    if not os.path.isfile(os.path.join(qs_dir, "qsharp.json")):
        continue
    try:
        qsharp.init(project_root=qs_dir)
        print(f"OK {d}: compilation passed")
    except Exception as e:
        print(f"FAIL {d}: {str(e)[:200]}")
        failed.append(d)

if failed:
    print(f"{len(failed)} problem(s) failed to compile: {failed}")
    sys.exit(1)

print(f"All {20 - len(failed)} problems compiled successfully.")
