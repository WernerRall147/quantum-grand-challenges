"""Vendor Q# samples from microsoft/qdk, keeping only the ones that actually compile.

The generator had five reference implementations and returned nothing for every other
algorithm, so VQE and Grover requests reached the model with no compiling example in
front of it. Upstream has those samples; this brings them in.

Three things this refuses to do, each because the alternative has already bitten:

  - Track `main`. We compile with qsharp 1.31.0, so samples come from v1.31.0. A sample
    using syntax newer than the deployed compiler would reintroduce exactly the class of
    bug this is meant to prevent.
  - Trust the rendered page. The GitHub HTML view of Std/Arrays.qs elided `Repeated`
    from the export list; acting on that reading would have broken a correct rule. Files
    are fetched raw and then compiled.
  - Keep a sample that does not define `Main`. The estimator invokes `Main.Main()` by
    name. A reference that demonstrates some other entry point teaches the model to
    produce something unestimatable, which fails quietly - the code compiles and the
    Pareto rows come back empty.

    python tooling/vendor_qdk_samples.py
    python tooling/vendor_qdk_samples.py --check   # verify, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from importlib import metadata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEST = REPO / "libs" / "qdk_samples"
PROVENANCE = DEST / "provenance.json"

TAG = "v1.31.0"
RAW = "https://raw.githubusercontent.com/microsoft/qdk/{tag}/{path}"

# Algorithm names the orchestrator emits, mapped to upstream samples. Names not in this
# map fall back to DEFAULT_REFERENCE in generate.py.
SAMPLES = {
    "VQE": "samples/algorithms/SimpleVQE.qs",
    "Grover": "samples/algorithms/Grover.qs",
    "Bernstein-Vazirani": "samples/algorithms/BernsteinVazirani.qs",
    "Deutsch-Jozsa": "samples/algorithms/DeutschJozsa.qs",
    "Hidden Shift": "samples/algorithms/HiddenShift.qs",
    "Phase Estimation": "samples/algorithms/PhaseEstimation.qs",
    "Teleportation": "samples/algorithms/Teleportation.qs",
    "QRNG": "samples/algorithms/QRNG.qs",
    "Repetition Code": "samples/algorithms/ThreeQubitRepetitionCode.qs",
    "Superdense Coding": "samples/algorithms/SuperdenseCoding.qs",
}

_MAIN = re.compile(r"^\s*operation\s+Main\s*\(", re.M)


def installed_qsharp_version() -> str:
    return metadata.version("qsharp")


def fetch(path: str) -> str:
    url = RAW.format(tag=TAG, path=path)
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read().decode("utf-8")


def compiles(source: str) -> tuple[bool, str]:
    """Compile in a throwaway project. Reports the compiler's message, not just a bool."""
    from qdk import qsharp

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        (root / "qsharp.json").write_text("{}", encoding="utf-8")
        (root / "src" / "Main.qs").write_text(source, encoding="utf-8")
        try:
            qsharp.init(project_root=str(root))
            return True, ""
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)[:400]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="verify the vendored copies without writing")
    args = parser.parse_args()

    version = installed_qsharp_version()
    if TAG != f"v{version}":
        print(f"FAIL: pinned to {TAG} but qsharp {version} is installed. "
              f"Samples must match the compiler they are meant to demonstrate.")
        return 1

    records: dict[str, dict[str, str]] = {}
    kept, rejected = 0, 0

    for algorithm, path in sorted(SAMPLES.items()):
        name = Path(path).name
        try:
            source = fetch(path)
        except urllib.error.HTTPError as exc:
            print(f"  SKIP {name:<28} HTTP {exc.code}")
            rejected += 1
            continue

        ok, error = compiles(source)
        if not ok:
            print(f"  SKIP {name:<28} does not compile: {error.splitlines()[0][:70]}")
            rejected += 1
            continue
        if not _MAIN.search(source):
            print(f"  SKIP {name:<28} defines no Main operation")
            rejected += 1
            continue

        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
        target = DEST / name
        if args.check:
            if not target.exists():
                print(f"  MISS {name:<28} not vendored")
                rejected += 1
                continue
            current = hashlib.sha256(target.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            if current != digest:
                print(f"  DRIFT {name:<27} vendored copy differs from {TAG}")
                rejected += 1
                continue
        else:
            DEST.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")

        records[algorithm] = {
            "file": name,
            "source": RAW.format(tag=TAG, path=path),
            "sha256": digest,
        }
        print(f"  OK   {name:<28} {len(source):>5} chars")
        kept += 1

    if not args.check:
        PROVENANCE.write_text(
            json.dumps({"tag": TAG, "qsharp_version": version, "samples": records},
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(f"\n{kept} kept, {rejected} rejected, pinned to {TAG} (qsharp {version})")
    return 0 if kept and not rejected else 1


if __name__ == "__main__":
    sys.exit(main())
