"""Every hardware kernel must compile to QIR for the Adaptive_RI profile Azure Quantum submissions use.

The repository described all kernels as syntax-checked for Azure, but that check dated from an
earlier QDK. Under the pinned qdk 1.31.0, problem 03's kernel crashed the QIR compiler (a
PostArgPromote invariant panic on partially applied callables inside controlled operations),
and once that was avoided, the profile's compile-time evaluation could not fold the complex
power behind its log-normal weights. Nothing ran the compiler, so nothing noticed.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from qdk import qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
KERNELS = sorted(REPO_ROOT.glob("problems/*/qsharp/HardwareKernel.qs")) + sorted(
    REPO_ROOT.glob("problems/archived/*/qsharp/HardwareKernel.qs")
)
ENTRY = re.compile(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)")


def test_every_problem_has_a_kernel():
    assert len(KERNELS) == 20


@pytest.mark.parametrize("kernel", KERNELS, ids=[k.parts[-3] for k in KERNELS])
def test_the_kernel_compiles_to_adaptive_qir(kernel: Path):
    source = kernel.read_text(encoding="utf-8-sig")
    entry = ENTRY.search(source)
    assert entry, f"{kernel} has no @EntryPoint operation"
    qsharp.init(target_profile=qsharp.TargetProfile.Adaptive_RI)
    qsharp.eval(source)
    try:
        qir = qsharp.compile(f"{entry.group(1)}()")
    except BaseException as error:  # the compiler reports some failures as Rust panics
        pytest.fail(f"{kernel.parts[-3]}: {str(error).splitlines()[0]}")
    assert "__quantum__qis__" in str(qir)
