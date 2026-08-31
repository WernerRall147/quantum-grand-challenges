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
    os.environ.pop("QGC_CODEGEN_DEPLOYMENT", None)
    os.environ.pop("QGC_CHAT_DEPLOYMENT", None)
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

    assert gen._deployment() == generate.CODEGEN_DEPLOYMENT
    assert gen._deployment() != generate.ROUTER_DEPLOYMENT


@pytest.mark.parametrize("module", GENERATORS)
def test_generation_does_not_borrow_the_verdict_models_deployment(module, monkeypatch):
    """The verdict model is not a code model.

    Pointing generation at CHAT_DEPLOYMENT produced Q# that never compiled: the
    deployment named gpt-54-mini serves gpt-4.1-mini from April 2025, which emits
    `import Std.Math::*` and imports without semicolons no matter what the system prompt
    says. Three attempts, three parse errors, compiled=false, no resource estimate - and
    the response still carried 5,380 characters, so a length check called it healthy.
    """
    monkeypatch.delenv("QGC_CODEGEN_USE_ROUTER", raising=False)
    monkeypatch.delenv("QGC_CODEGEN_DEPLOYMENT", raising=False)
    monkeypatch.setenv("QGC_CHAT_DEPLOYMENT", "some-chat-model")
    mod = importlib.reload(importlib.import_module(module))

    assert mod.CODEGEN_DEPLOYMENT != mod.CHAT_DEPLOYMENT
    assert mod.CODEGEN_DEPLOYMENT == "qgc-codegen"


@pytest.mark.parametrize("module", GENERATORS)
def test_codegen_deployment_is_overridable(module, monkeypatch):
    monkeypatch.setenv("QGC_CODEGEN_DEPLOYMENT", "my-code-model")
    mod = importlib.reload(importlib.import_module(module))

    assert mod.CODEGEN_DEPLOYMENT == "my-code-model"


def test_generator_reports_which_model_answered(monkeypatch):
    """A response that cannot say which model wrote it cannot be diagnosed.

    Three models failed three different ways on 2026-08-31 and none of the responses
    named the one used, so every diagnosis restarted from the beginning.
    """
    monkeypatch.delenv("QGC_CODEGEN_USE_ROUTER", raising=False)
    generate = importlib.reload(importlib.import_module("agents.code_generator.generate"))

    gen = generate.QSharpCodeGenerator.__new__(generate.QSharpCodeGenerator)
    gen.last_model_used = "gpt-5.4-mini-2026-03-17"
    gen.generate = lambda *a, **k: "import Std.Arrays.*;"
    gen.compile_and_estimate = lambda code, multi_profile=False: {"compiled": True}

    est = gen.generate_with_estimate("any problem", algorithm="QPE")["estimation"]

    assert est["codegen_model"] == "gpt-5.4-mini-2026-03-17"
    assert est["codegen_deployment"] == generate.CODEGEN_DEPLOYMENT
