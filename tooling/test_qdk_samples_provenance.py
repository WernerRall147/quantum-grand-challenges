"""The vendored QDK samples must still compile against the compiler we actually run.

Vendoring is a snapshot, and snapshots rot. Two ways this goes wrong quietly:

  - qsharp is upgraded and the samples are not re-vendored, so the model is shown code
    the deployed compiler rejects - the exact failure #233 was fixing.
  - Someone edits a vendored file by hand, and the provenance record no longer describes
    what is on disk.

Both produce worse generated Q# without any error being raised, so these assert the
outcome: the files compile, they define the entry point estimation invokes, and their
hashes match what was recorded at vendoring time.
"""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
from importlib import metadata
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
VENDORED = REPO / "libs" / "qdk_samples"
PROVENANCE = VENDORED / "provenance.json"

_MAIN = re.compile(r"^\s*operation\s+Main\s*\(", re.M)
LEGACY_NEW_ARRAY = re.compile(r"\bnew\s+[A-Za-z_][A-Za-z0-9_]*\s*\[")


def record() -> dict:
    assert PROVENANCE.exists(), "run tooling/vendor_qdk_samples.py"
    return json.loads(PROVENANCE.read_text(encoding="utf-8"))


def sample_files() -> list[Path]:
    return sorted(VENDORED.glob("*.qs"))


def test_samples_were_actually_vendored():
    """A glob that matches nothing passes every other test in this file forever."""
    assert len(sample_files()) >= 10, f"only {len(sample_files())} vendored samples found"


def test_pin_matches_the_installed_compiler():
    data = record()
    assert data["tag"] == f"v{metadata.version('qsharp')}", (
        f"samples pinned to {data['tag']} but qsharp {metadata.version('qsharp')} is "
        f"installed. Re-run tooling/vendor_qdk_samples.py."
    )


@pytest.mark.parametrize("path", sample_files(), ids=lambda p: p.name)
def test_vendored_file_matches_its_recorded_hash(path):
    by_file = {entry["file"]: entry for entry in record()["samples"].values()}
    assert path.name in by_file, f"{path.name} is on disk but not in provenance.json"
    source = path.read_text(encoding="utf-8")
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    assert digest == by_file[path.name]["sha256"], f"{path.name} differs from the vendored copy"


@pytest.mark.parametrize("path", sample_files(), ids=lambda p: p.name)
def test_vendored_file_defines_main(path):
    """Estimation invokes Main by name; a sample without one teaches an unestimatable shape."""
    assert _MAIN.search(path.read_text(encoding="utf-8")), f"{path.name} defines no Main"


@pytest.mark.parametrize("path", sample_files(), ids=lambda p: p.name)
def test_vendored_file_has_no_legacy_array_syntax(path):
    source = path.read_text(encoding="utf-8")
    assert not LEGACY_NEW_ARRAY.search(source), f"{path.name} contains legacy `new T[...]`"
    assert "ConstantArray" not in source


@pytest.mark.parametrize("path", sample_files(), ids=lambda p: p.name)
def test_vendored_file_still_compiles(path):
    from qdk import qsharp

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        (root / "qsharp.json").write_text("{}", encoding="utf-8")
        (root / "src" / "Main.qs").write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        qsharp.init(project_root=str(root))


def test_every_referenced_sample_is_vendored():
    from agents.code_generator.generate import REFERENCE_IMPLEMENTATIONS

    referenced = [rel for rel in REFERENCE_IMPLEMENTATIONS.values()
                  if rel.startswith("libs/qdk_samples/")]
    missing = [rel for rel in referenced if not (REPO / rel).exists()]
    assert not missing, f"generate.py points at samples that are not vendored: {missing}"
