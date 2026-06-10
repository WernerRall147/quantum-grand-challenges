"""Unit tests for ``tooling.estimator_config`` helpers.

Covers the typed ``EstimatorParams`` factories and ``extract_summary`` 
the building blocks that replaced ad-hoc raw-dict construction across the
estimation tooling and the code-generator agent.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tooling.estimator_config import (  # noqa: E402
    QUBIT_MODELS,
    extract_summary,
    iter_model_configs,
    make_batch_estimator_params,
    make_estimator_params,
)


class TestMakeEstimatorParams:
    def test_single_item_sets_qubit_and_qec(self):
        p = make_estimator_params("qubit_gate_ns_e3", "surface_code")
        assert p.qubit_params.name == "qubit_gate_ns_e3"
        assert p.qec_scheme.name == "surface_code"

    def test_optional_error_budget(self):
        p = make_estimator_params("qubit_maj_ns_e6", "floquet_code", error_budget=1e-4)
        assert p.error_budget == pytest.approx(1e-4)

    def test_error_budget_omitted_by_default(self):
        # Just ensure construction succeeds; default EstimatorParams.error_budget
        # is whatever the SDK chooses, we only assert ours-isn't-set behavior
        # via the absence of an exception and a callable EstimatorParams.
        p = make_estimator_params("qubit_gate_us_e4", "surface_code")
        assert p is not None


class TestMakeBatchEstimatorParams:
    def test_num_items_matches_configs(self):
        configs = [("qubit_gate_ns_e3", "surface_code"), ("qubit_maj_ns_e6", "floquet_code")]
        p = make_batch_estimator_params(configs)
        # ``items`` should expose len == num_items
        assert len(p.items) == 2

    def test_preserves_order(self):
        configs = [
            ("qubit_gate_ns_e3", "surface_code"),
            ("qubit_gate_us_e4", "surface_code"),
            ("qubit_maj_ns_e6", "floquet_code"),
        ]
        p = make_batch_estimator_params(configs)
        for i, (q, qec) in enumerate(configs):
            assert p.items[i].qubit_params.name == q
            assert p.items[i].qec_scheme.name == qec

    def test_per_item_error_budget(self):
        configs = [("qubit_gate_ns_e3", "surface_code"), ("qubit_maj_ns_e4", "floquet_code")]
        p = make_batch_estimator_params(configs, error_budget=5e-4)
        for i in range(len(configs)):
            assert p.items[i].error_budget == pytest.approx(5e-4)

    def test_full_pareto_matrix_builds(self):
        """Sanity: every (model, qec) from iter_model_configs round-trips."""
        configs = [(m.name, qec) for m, qec, _ in iter_model_configs()]
        # 4 gate-based × surface_code (4) + 2 majorana × 2 schemes (4) = 8
        assert len(configs) == 8
        assert len(QUBIT_MODELS) == 6
        p = make_batch_estimator_params(configs, error_budget=1e-3)
        assert len(p.items) == 8


class TestExtractSummary:
    def _sample(self) -> dict:
        return {
            "physicalCounts": {
                "physicalQubits": 1200,
                "runtime": 8400,
                "rqops": 1.5e6,
                "breakdown": {
                    "algorithmicLogicalQubits": 17,
                    "physicalQubitsForTfactories": 300,
                    "logicalPatch": {"codeDistance": 9},
                },
            },
            "logicalCounts": {
                "logicalDepth": 42,
                "tCount": 17,
                "rotationCount": 3,
                "cczCount": 0,
                "measurementCount": 5,
                "numQubits": 8,
            },
        }

    def test_extracts_core_keys(self):
        out = extract_summary(self._sample())
        assert out["physicalQubits"] == 1200
        assert out["runtime"] == 8400
        assert out["logicalQubits"] == 17
        assert out["logicalDepth"] == 42
        assert out["tCount"] == 17
        assert out["codeDistance"] == 9

    def test_computes_t_factory_fraction(self):
        out = extract_summary(self._sample())
        # 300 / 1200 = 0.25
        assert out["tFactoryFraction"] == pytest.approx(0.25)

    def test_handles_missing_fields(self):
        out = extract_summary({"physicalCounts": {}, "logicalCounts": {}})
        for key in ("physicalQubits", "runtime", "tCount", "codeDistance"):
            assert out[key] is None
        assert out["tFactoryFraction"] is None

    def test_handles_non_dict_input(self):
        assert extract_summary(None) == {}
        assert extract_summary("not a dict") == {}
        assert extract_summary(42) == {}

    def test_handles_missing_logical_patch(self):
        data = self._sample()
        del data["physicalCounts"]["breakdown"]["logicalPatch"]
        out = extract_summary(data)
        assert out["codeDistance"] is None
