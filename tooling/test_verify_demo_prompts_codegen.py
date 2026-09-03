"""Code generation must report, not block.

`verify_demo_prompts.py` is the pre-flight gate. It used to return 1 when Q#
generation failed, which made a recording look unsafe over a path that is never on
camera: beat 1 says "leave Generate code unticked" and beat 3 is the local Grover
run. Generation is also genuinely flaky - on 2026-09-02 it failed with an
`IndexOutOfRange` in the generated source and then succeeded minutes later with no
change - so a blocking check there is a coin flip that teaches you to ignore red.

These tests pin both halves: generation problems warn and return 0, and a real
verdict mismatch still fails.
"""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tooling"))

import verify_demo_prompts as vdp  # noqa: E402

BROKEN_PAYLOADS = {
    "no Q# at all": {"qsharp_code": "", "estimation": {"error": "generator returned nothing"}},
    "compiler error": {
        "qsharp_code": "operation Main() : Unit {}",
        "estimation": {"estimate_error": "index out of range: 1", "physical_qubits": None},
    },
    "no qubit count": {
        "qsharp_code": "operation Main() : Unit {}",
        "estimation": {"entry_expression": "Main.Main()", "physical_qubits": None},
    },
    "broken pareto rows": {
        "qsharp_code": "operation Main() : Unit {}",
        "estimation": {"entry_expression": "Main.Main()", "physical_qubits": 99602},
        "resource_estimate_pareto": [{"error": "R1Frac type error"}, {"physical_qubits": 5}],
    },
}


@pytest.mark.parametrize("label", sorted(BROKEN_PAYLOADS))
def test_broken_generation_warns_and_does_not_block(monkeypatch, label):
    monkeypatch.setattr(vdp, "evaluate", lambda *a, **k: (BROKEN_PAYLOADS[label], 12.3))
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vdp.check_codegen("http://example.invalid", "some prompt", 60)
    out = buf.getvalue()
    assert rc == 0, f"{label!r} must not block the recording"
    assert "WARN" in out, f"{label!r} must still be reported, not swallowed"
    assert "not tick" in out.lower(), "the warning must say what to do on camera"


def test_request_failure_warns_and_does_not_block(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("connection reset")

    monkeypatch.setattr(vdp, "evaluate", boom)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vdp.check_codegen("http://example.invalid", "some prompt", 60)
    assert rc == 0
    assert "WARN" in buf.getvalue()


def test_working_generation_reports_ok(monkeypatch):
    monkeypatch.setattr(vdp, "evaluate", lambda *a, **k: (
        {"qsharp_code": "x" * 3753,
         "estimation": {"entry_expression": "Main.Main()", "physical_qubits": 99602},
         "resource_estimate_pareto": [{"physical_qubits": 5}]}, 39.5))
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vdp.check_codegen("http://example.invalid", "some prompt", 60)
    out = buf.getvalue()
    assert rc == 0
    assert "OK" in out and "WARN" not in out


def test_codegen_never_contributes_to_the_exit_code():
    """The gate must key on verdicts only.

    Guards against a future edit reintroducing `failures += check_codegen(...)`.
    """
    source = (REPO / "tooling" / "verify_demo_prompts.py").read_text(encoding="utf-8")
    assert "failures += check_codegen" not in source, (
        "code generation is not a demo beat and must not block the recording"
    )
