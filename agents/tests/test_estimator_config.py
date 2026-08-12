"""Unit tests for ``tooling.estimator_config`` helpers.

Covers the QRE v3 architecture/ISA factories, the Pareto-point selection rule
and ``extract_summary`` - the building blocks shared by the estimation tooling
and the code-generator agent.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from qdk.qre.models import GateBased  # noqa: E402
from qdk.qre.property_keys import (  # noqa: E402
    LOGICAL_COMPUTE_QUBITS,
    LOGICAL_MEMORY_QUBITS,
    PHYSICAL_FACTORY_QUBITS,
)

from tooling.estimator_config import (  # noqa: E402
    DEFAULT_QEC_SCHEME,
    DEFAULT_QUBIT_MODEL,
    QUBIT_MODELS,
    extract_summary,
    iter_model_configs,
    make_architecture,
    make_isa_query,
    select_entry,
)


class _FakeEntry:
    """Stands in for a QRE v3 ``EstimationTableEntry``."""

    def __init__(self, qubits, runtime, error=1e-4, properties=None, source=""):
        self.qubits = qubits
        self.runtime = runtime
        self.error = error
        self.properties = properties or {}
        self.source = source


class TestMakeArchitecture:
    def test_gate_based_carries_physical_parameters(self):
        arch = make_architecture("qubit_gate_ns_e3")
        assert isinstance(arch, GateBased)
        assert arch.error_rate == pytest.approx(1e-3)

    def test_error_rate_distinguishes_profiles(self):
        assert make_architecture("qubit_gate_ns_e4").error_rate == pytest.approx(1e-4)

    def test_microsecond_profile_is_slower_than_nanosecond(self):
        ns = make_architecture("qubit_gate_ns_e3")
        us = make_architecture("qubit_gate_us_e3")
        assert us.gate_time > ns.gate_time

    def test_unknown_model_raises(self):
        with pytest.raises(KeyError):
            make_architecture("qubit_does_not_exist")


class TestMakeIsaQuery:
    def test_surface_code_query_builds(self):
        assert make_isa_query("surface_code") is not None

    def test_unknown_scheme_raises(self):
        with pytest.raises(KeyError):
            make_isa_query("floquet_code")


class TestModelMatrix:
    def test_defaults_are_present_in_matrix(self):
        assert DEFAULT_QUBIT_MODEL in {m.name for m in QUBIT_MODELS}
        assert any(DEFAULT_QEC_SCHEME in m.qec_schemes for m in QUBIT_MODELS)

    def test_every_config_resolves(self):
        configs = list(iter_model_configs())
        assert configs, "expected a non-empty sweep matrix"
        for model, qec, key in configs:
            assert make_architecture(model.name) is not None
            assert make_isa_query(qec) is not None
            assert key == f"{model.name}+{qec}"

    def test_matrix_is_gate_based_only(self):
        # QRE v3 produced no feasible Majorana ISA, so the sweep is gate-based.
        assert {m.family for m in QUBIT_MODELS} == {"gate_based"}


class TestSelectEntry:
    def test_picks_fewest_qubits(self):
        table = [_FakeEntry(5644, 126), _FakeEntry(3544, 274), _FakeEntry(26664, 117)]
        assert select_entry(table).qubits == 3544

    def test_breaks_ties_on_runtime(self):
        table = [_FakeEntry(3544, 900), _FakeEntry(3544, 274)]
        assert select_entry(table).runtime == 274

    def test_empty_frontier_raises_clear_error(self):
        with pytest.raises(ValueError, match="empty"):
            select_entry([])


class TestExtractSummary:
    def _entry(self) -> _FakeEntry:
        return _FakeEntry(
            qubits=1200,
            runtime=8400,
            error=2.5e-4,
            properties={
                PHYSICAL_FACTORY_QUBITS: 300,
                LOGICAL_COMPUTE_QUBITS: 15,
                LOGICAL_MEMORY_QUBITS: 2,
            },
            source="LATTICE_SURGERY @ SurfaceCode(crossing_prefactor=0.03, distance=9)",
        )

    def test_extracts_core_keys(self):
        out = extract_summary(self._entry())
        assert out["physicalQubits"] == 1200
        assert out["runtime"] == 8400
        assert out["error"] == pytest.approx(2.5e-4)

    def test_logical_qubits_sum_compute_and_memory(self):
        assert extract_summary(self._entry())["logicalQubits"] == 17

    def test_parses_code_distance_from_source(self):
        assert extract_summary(self._entry())["codeDistance"] == 9

    def test_computes_t_factory_fraction(self):
        # 300 / 1200 = 0.25
        assert extract_summary(self._entry())["tFactoryFraction"] == pytest.approx(0.25)

    def test_reports_pareto_point_count(self):
        table = [self._entry(), self._entry()]
        assert extract_summary(self._entry(), table=table)["paretoPoints"] == 2

    def test_handles_missing_properties(self):
        out = extract_summary(_FakeEntry(qubits=10, runtime=1))
        assert out["logicalQubits"] is None
        assert out["tFactoryFraction"] is None
        assert out["codeDistance"] is None

    def test_handles_missing_entry(self):
        assert extract_summary(None) == {}
