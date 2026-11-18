"""Run Azure CLI commands without depending on a platform command shell."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence


def resolve_azure_cli_command(args: Sequence[str]) -> list[str]:
    """Resolve a shell-free argv that works for the Windows MSI wrapper too."""
    executable = shutil.which("az")
    if not executable:
        raise FileNotFoundError("Azure CLI 'az' was not found on PATH")

    path = Path(executable)
    if os.name != "nt" or path.suffix.lower() not in {".bat", ".cmd"}:
        return [str(path), *args]

    python_candidates = (path.parent / "python.exe", path.parent.parent / "python.exe")
    for python in python_candidates:
        if python.is_file():
            return [str(python), "-IBm", "azure.cli", *args]

    raise FileNotFoundError(
        f"Azure CLI resolves to a Windows command wrapper ({path}), but no "
        "python.exe entry point was found beside it"
    )


def run_az(
    args: Sequence[str],
    timeout: float | None,
    *,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run Azure CLI with argument isolation and a bounded wait."""
    return subprocess.run(
        resolve_azure_cli_command(args),
        shell=False,
        capture_output=True,
        text=True,
        check=check,
        timeout=timeout,
    )
