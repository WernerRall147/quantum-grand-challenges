#!/usr/bin/env python3
"""Render circuit.txt from each problem's HardwareKernel.qs.

The kernel is what actually gets submitted to Azure Quantum, so it is what the
published diagram should show. Rendering happens at the Adaptive_RI target
profile, so gates appear in their decomposed, hardware-facing form rather than
as the source-level operations.

This replaced a version that traced the local simulator ansatz in Main.qs. That
produced VQE diagrams for problems whose kernel had since been upgraded to QPE,
so the published circuit described an algorithm the project's own F1 filter
rejects.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "problems"

ENTRY_RE = re.compile(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)")
# "// Problem: 07_drug_discovery (QPE molecular binding energy)"
HEADER_DESC_RE = re.compile(r"^//\s*Problem:.*?\((.+?)\)\s*$", re.MULTILINE)


def find_kernels():
    """Every problem directory holding a HardwareKernel.qs, archived included."""
    found = []
    for base in (PROBLEMS_DIR, PROBLEMS_DIR / "archived"):
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name == "archived":
                continue
            kernel = d / "qsharp" / "HardwareKernel.qs"
            if kernel.is_file():
                found.append((d, kernel, base.name == "archived"))
    return found


def describe(code: str, entry_fn: str) -> str:
    """Short algorithm description, from the file header or the first body comment.

    The body scan stops at a section divider or the next operation, so a kernel
    cannot pick up the description of a different one further down the file.
    """
    m = HEADER_DESC_RE.search(code)
    if m:
        return m.group(1).strip()
    body = code.split(f"operation {entry_fn}", 1)[-1]
    for line in body.splitlines()[1:]:
        stripped = line.strip()
        if "----" in stripped or stripped.startswith(("operation ", "@EntryPoint")):
            break
        if stripped.startswith("//"):
            return stripped.lstrip("/ ").strip()
    return ""


def pretty_title(dir_name: str):
    number, _, rest = dir_name.partition("_")
    return number, rest.replace("_", " ").title()


def build_header(dir_name, entry_fn, description, metrics, archived) -> str:
    number, title = pretty_title(dir_name)
    rel = f"problems/{'archived/' if archived else ''}{dir_name}/qsharp/HardwareKernel.qs"
    return "\n".join([
        "=" * 67,
        f"  Problem {number}: {title}" + ("  [ARCHIVED]" if archived else ""),
        f"  Kernel: {entry_fn}()" + (f"  {description}" if description else ""),
        f"  Target profile: Adaptive_RI | {metrics}",
        f"  Source: {rel}",
        "=" * 67,
    ])


STATIC_NOTE = """This is the circuit Azure Quantum receives. It is rendered from
HardwareKernel.qs at the Adaptive_RI target profile, so the gates below
are the decomposed hardware-facing form, not the source-level operations.

It is a small representative kernel that compiles and runs on today's
devices. It is not the utility-scale algorithm: see estimates/ for the
fault-tolerant resource projection, which is orders of magnitude larger."""

ADAPTIVE_NOTE = """This kernel has no single static circuit diagram, and that is the point.

It measures a syndrome mid-circuit and then branches on the outcome, so the
gates that execute depend on results that do not exist until run time. A fixed
diagram would have to pick one branch and pretend the others are not there.

This is the capability the Adaptive_RI target profile exists to provide, and it
is why this kernel cannot run on a Base-profile target. Read the source for the
branch structure."""

QIR_FAIL_NOTE = """WARNING: this kernel does not currently compile to QIR.

The circuit below is what the simulator executes. Azure Quantum submission
lowers the kernel to QIR first, and that step fails, so this kernel cannot be
submitted to hardware as it stands. Treat the diagram as illustrative only."""


def qir_status(qsharp, entry_fn):
    """Whether the kernel lowers to QIR. A failure here means it cannot be submitted.

    The QDK raises a Rust PanicException for some malformed kernels, and that is a
    BaseException, so a plain `except Exception` lets it kill the whole run.
    """
    try:
        qsharp.compile(f"{entry_fn}()")
        return True, ""
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:
        return False, str(e)[:120]


def main():
    from qdk import qsharp

    kernels = find_kernels()
    if not kernels:
        print("No HardwareKernel.qs found")
        return 1

    ok = 0
    failed = []

    for problem_dir, kernel_path, archived in kernels:
        name = problem_dir.name
        code = kernel_path.read_text(encoding="utf-8")
        m = ENTRY_RE.search(code)
        if not m:
            print(f"-- {name}: no @EntryPoint, skipped")
            failed.append(name)
            continue
        entry_fn = m.group(1)
        description = describe(code, entry_fn)
        out = problem_dir / "circuits"
        out.mkdir(exist_ok=True)

        try:
            qsharp.init(target_profile=qsharp.TargetProfile.Adaptive_RI)
            qsharp.eval(code)
            circuit_text = str(qsharp.circuit(f"{entry_fn}()")).strip()
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as e:
            if "compare measurement results" in str(e):
                compiles, _ = qir_status(qsharp, entry_fn)
                metrics = "Gate sequence: result-dependent | QIR: " + (
                    "compiles" if compiles else "DOES NOT COMPILE"
                )
                header = build_header(name, entry_fn, description, metrics, archived)
                (out / "circuit.txt").write_text(f"{header}\n\n{ADAPTIVE_NOTE}\n", encoding="utf-8")
                print(f"OK {name}: {entry_fn}, adaptive (no static circuit)")
                ok += 1
                continue
            print(f"XX {name}: {str(e)[:140]}")
            failed.append(name)
            continue

        if not circuit_text:
            print(f"XX {name}: empty circuit")
            failed.append(name)
            continue

        qubits = len([ln for ln in circuit_text.splitlines() if ln.lstrip().startswith("q")])
        measured = circuit_text.count("\u2558")
        compiles, qir_err = qir_status(qsharp, entry_fn)

        metrics = (
            f"Qubits: {qubits} | Measured: {measured} | QIR: "
            + ("compiles" if compiles else "DOES NOT COMPILE")
        )
        header = build_header(name, entry_fn, description, metrics, archived)
        note = STATIC_NOTE if compiles else f"{QIR_FAIL_NOTE}\n\nCompiler said: {qir_err}"
        (out / "circuit.txt").write_text(
            f"{header}\n\n{note}\n\n{circuit_text}\n", encoding="utf-8"
        )

        flag = "" if compiles else "  [QIR FAILS]"
        print(f"OK {name}: {entry_fn}, {qubits} qubits, {measured} measured{flag}")
        ok += 1

    print(f"\nDone: {ok} rendered, {len(failed)} failed")
    if failed:
        print("Failed: " + ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
