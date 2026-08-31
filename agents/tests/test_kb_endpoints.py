"""The knowledge base has to be repointable, or nobody but its author can run it.

SEARCH_ENDPOINT and OPENAI_ENDPOINT were module-level literals naming one tenant's
resources. The README told readers to run the CLI evaluator with nothing but `az login`,
which was never true for anyone outside that tenant: there was no override short of
editing the source. The Container App had been setting SEARCH_ENDPOINT and
AZURE_OPENAI_ENDPOINT the whole time and no code read either.
"""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

MODULE = "knowledge.search.kb_client"


def _reload(monkeypatch, **env):
    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    return importlib.reload(importlib.import_module(MODULE))


@pytest.fixture(autouse=True)
def _restore_module_defaults():
    """Leave the module as it was found, or later tests inherit a fake endpoint."""
    yield
    for key in ("SEARCH_ENDPOINT", "AZURE_OPENAI_ENDPOINT", "QGC_EMBEDDING_DEPLOYMENT"):
        __import__("os").environ.pop(key, None)
    importlib.reload(importlib.import_module(MODULE))


class TestEndpointsAreOverridable:
    def test_search_endpoint_follows_the_environment(self, monkeypatch):
        kb = _reload(monkeypatch, SEARCH_ENDPOINT="https://someone-else.search.windows.net")

        assert kb.SEARCH_ENDPOINT == "https://someone-else.search.windows.net"

    def test_openai_endpoint_follows_the_environment(self, monkeypatch):
        kb = _reload(monkeypatch, AZURE_OPENAI_ENDPOINT="https://someone-else.openai.azure.com/")

        assert kb.OPENAI_ENDPOINT == "https://someone-else.openai.azure.com/"

    def test_embedding_deployment_follows_the_environment(self, monkeypatch):
        kb = _reload(monkeypatch, QGC_EMBEDDING_DEPLOYMENT="my-embeddings")

        assert kb.EMBEDDING_DEPLOYMENT == "my-embeddings"

    def test_defaults_are_unchanged_when_nothing_is_set(self, monkeypatch):
        kb = _reload(
            monkeypatch,
            SEARCH_ENDPOINT=None,
            AZURE_OPENAI_ENDPOINT=None,
            QGC_EMBEDDING_DEPLOYMENT=None,
        )

        assert kb.SEARCH_ENDPOINT == "https://qgcsearcheval.search.windows.net"
        assert kb.OPENAI_ENDPOINT == "https://qgc-openai.openai.azure.com/"
        assert kb.EMBEDDING_DEPLOYMENT == "text-embedding-3-large"

    def test_no_endpoint_literal_is_left_hardcoded(self, monkeypatch):
        """Both search clients read the module constant, so an override must reach both.

        Asserting on the source rather than on a client instance, because building one
        needs Azure credentials this test deliberately does not have.
        """
        source = (ROOT / "knowledge" / "search" / "kb_client.py").read_text(encoding="utf-8")
        literal_assignments = [
            line for line in source.splitlines()
            if line.startswith(("SEARCH_ENDPOINT =", "OPENAI_ENDPOINT ="))
            and "os.environ.get" not in line
        ]

        assert not literal_assignments, (
            f"endpoint pinned to one tenant: {literal_assignments}"
        )


class TestSeederIsSelfHostable:
    """Populating the index is the other half of running this yourself.

    The seeder is the only documented way to fill the index, and it hardcoded three
    endpoints and connected to Cosmos unconditionally - a store the evaluator stopped
    reading in #156. So the reader being repointable was not enough to self-host.
    """

    SOURCE = ROOT / "knowledge" / "seed_knowledge_base.py"

    def test_seeder_endpoints_are_not_hardcoded(self):
        literals = [
            line for line in self.SOURCE.read_text(encoding="utf-8").splitlines()
            if line.startswith(("COSMOS_ENDPOINT =", "SEARCH_ENDPOINT =", "OPENAI_ENDPOINT ="))
            and "os.environ.get" not in line
        ]

        assert not literals, f"seeder endpoint pinned to one tenant: {literals}"

    def test_seeder_imports_without_the_cosmos_package(self):
        """azure-cosmos is only pinned because this module imported it at import time."""
        source = self.SOURCE.read_text(encoding="utf-8")
        module_level = [
            line for line in source.splitlines()
            if line.startswith("from azure.cosmos") or line.startswith("import azure.cosmos")
        ]

        assert not module_level, (
            f"Cosmos imported at module level, so the seeder cannot run without it: {module_level}"
        )

    def test_cosmos_seeding_is_off_unless_asked_for(self, monkeypatch):
        monkeypatch.delenv("QGC_SEED_COSMOS", raising=False)
        seeder = importlib.reload(importlib.import_module("knowledge.seed_knowledge_base"))

        assert seeder.SEED_COSMOS is False

        monkeypatch.setenv("QGC_SEED_COSMOS", "1")
        seeder = importlib.reload(importlib.import_module("knowledge.seed_knowledge_base"))

        assert seeder.SEED_COSMOS is True
