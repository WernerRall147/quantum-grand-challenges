"""Code generation must not depend on which model the router happens to pick.

Measured against production on 2026-08-31, generate_code=true returned no Q# on two of
four calls. The error named the cause each time: finish_reason=length with
completion_tokens equal to max_completion_tokens and reasoning consuming all of it, on
gpt-5.6-sol. The same prompt on gpt-5.4-mini produced 5,221 characters in 90 seconds.

Raising the budget to 12000 in production did not fix it - it let the reasoning run past
the ingress timeout, turning an empty response into a 504. So generation is pinned to a
deployment. Verdicts keep using the router, which is what the architecture doc claims.
"""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

GENERATORS = [
    "agents.code_generator.generate",
    "agents.code_generator.bicep_generator",
]


@pytest.fixture(autouse=True)
def _restore(monkeypatch):
    yield
    import os

    os.environ.pop("QGC_CODEGEN_USE_ROUTER", None)
    for name in GENERATORS:
        importlib.reload(importlib.import_module(name))


@pytest.mark.parametrize("module", GENERATORS)
def test_generation_does_not_use_the_router_by_default(module, monkeypatch):
    monkeypatch.delenv("QGC_CODEGEN_USE_ROUTER", raising=False)
    mod = importlib.reload(importlib.import_module(module))

    assert mod.USE_ROUTER is False


@pytest.mark.parametrize("module", GENERATORS)
def test_generation_is_not_steered_by_the_verdict_path_flag(module, monkeypatch):
    """QGC_USE_ROUTER=1 is set in production for verdicts and must not reach generation."""
    monkeypatch.delenv("QGC_CODEGEN_USE_ROUTER", raising=False)
    monkeypatch.setenv("QGC_USE_ROUTER", "1")
    mod = importlib.reload(importlib.import_module(module))

    assert mod.USE_ROUTER is False


@pytest.mark.parametrize("module", GENERATORS)
def test_the_router_can_still_be_opted_back_in(module, monkeypatch):
    monkeypatch.setenv("QGC_CODEGEN_USE_ROUTER", "1")
    mod = importlib.reload(importlib.import_module(module))

    assert mod.USE_ROUTER is True


def test_pinned_deployment_is_the_one_measured_to_work(monkeypatch):
    """Resolving to a deployment name, not the router, is the point of the change."""
    monkeypatch.delenv("QGC_CODEGEN_USE_ROUTER", raising=False)
    generate = importlib.reload(importlib.import_module("agents.code_generator.generate"))

    gen = generate.QSharpCodeGenerator.__new__(generate.QSharpCodeGenerator)

    assert gen._deployment() == generate.CHAT_DEPLOYMENT
    assert gen._deployment() != generate.ROUTER_DEPLOYMENT
