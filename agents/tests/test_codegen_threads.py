"""Concurrent generations must not share, or cross threads with, one qsharp interpreter.

The interpreter is a thread-bound object: used from another thread it panics ("Interpreter
is unsendable, but sent to another thread"). The API serves requests on a thread pool, so
two generations at once crashed in 6 of 6 trials on 2026-09-25, each program compiled by
one thread and estimated by the other. Uses only the public API, so it runs unchanged
against older versions of the generator.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

pytest.importorskip("qdk.qsharp")

from agents.code_generator.generate import QSharpCodeGenerator  # noqa: E402


def _program(width: int) -> str:
    return f"""import Std.Math.*;
operation Main() : Result[] {{
    use qs = Qubit[{width}];
    for _ in 1..300 {{
        for q in qs {{
            Rz(0.1, q);
            H(q);
        }}
    }}
    return MResetEachZ(qs);
}}
"""


def test_two_generations_at_once_each_estimate_their_own_program():
    gen = QSharpCodeGenerator.__new__(QSharpCodeGenerator)
    programs = {"narrow": _program(3), "wide": _program(9)}
    alone = {name: gen.compile_and_estimate(src)["physical_qubits"] for name, src in programs.items()}
    assert alone["narrow"] != alone["wide"]

    for _ in range(3):
        results: dict[str, dict] = {}

        def run(name: str) -> None:
            try:
                results[name] = gen.compile_and_estimate(programs[name], multi_profile=True)
            except BaseException as e:  # noqa: BLE001 - a Rust panic arrives as BaseException
                results[name] = {"crash": f"{type(e).__name__}: {str(e)[:120]}"}

        threads = [threading.Thread(target=run, args=(name,)) for name in programs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for name in programs:
            result = results[name]
            assert "crash" not in result, result
            assert result["physical_qubits"] == alone[name], (name, result.get("physical_qubits"))
            assert not [row["error"] for row in result["pareto_table"] if row.get("error")]
