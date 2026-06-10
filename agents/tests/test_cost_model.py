"""Unit tests for the cost model: AI/ML pricing + hardware-grounded quantum cost.

Covers the additions that introduced Azure Machine Learning instance-size
pricing and the feasibility-aware capping that prevents fault-tolerant resource
estimates from producing physically meaningless headline costs.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents.classifier import azure_pricing  # noqa: E402
from agents.classifier.cost_model import (  # noqa: E402
    REPRESENTATIVE_NISQ_DEPTH,
    estimate_aml_cost,
    estimate_quantum_cost,
    quantum_hardware_feasibility,
)


class TestAmlPricing:
    def test_provider_and_sku(self):
        aml = estimate_aml_cost(compute_hours=1.0, instance_size="medium")
        assert aml["provider"] == "Azure Machine Learning"
        assert aml["sku"] == azure_pricing.AML_INSTANCE_SIZES["medium"]
        assert aml["instance_size"] == "medium"

    def test_cost_orders_by_instance_size(self):
        small = estimate_aml_cost(compute_hours=2.0, instance_size="small")
        medium = estimate_aml_cost(compute_hours=2.0, instance_size="large")
        # CPU small must be cheaper than A100 large for the same wall time.
        assert small["estimated_cost_usd"] < medium["estimated_cost_usd"]

    def test_cost_scales_with_hours(self):
        one = estimate_aml_cost(compute_hours=1.0, instance_size="medium")
        ten = estimate_aml_cost(compute_hours=10.0, instance_size="medium")
        assert ten["estimated_cost_usd"] > one["estimated_cost_usd"]

    def test_unknown_size_falls_back_to_default(self):
        aml = estimate_aml_cost(compute_hours=1.0, instance_size="enormous")
        assert aml["sku"] == azure_pricing.AML_INSTANCE_SIZES[azure_pricing.DEFAULT_AML_INSTANCE]


class TestHardwareFeasibility:
    def test_ft_projection_flagged_not_feasible(self):
        feas = quantum_hardware_feasibility(132_000, "azure_quantum_quantinuum_h2", logical_depth=10_000)
        assert feas["feasible_today"] is False
        # Width capped to device, depth capped to the representative NISQ bound.
        assert feas["priced_circuit_qubits"] == feas["hardware_qubits"]
        assert feas["priced_circuit_depth"] == REPRESENTATIVE_NISQ_DEPTH

    def test_small_circuit_is_feasible(self):
        feas = quantum_hardware_feasibility(20, "azure_quantum_ionq_aria", logical_depth=50)
        assert feas["feasible_today"] is True
        assert feas["priced_circuit_qubits"] == 20
        assert feas["priced_circuit_depth"] == 50


class TestDeScareGuarantee:
    def test_fault_tolerant_estimate_stays_bounded(self):
        """A 1M-qubit FT estimate must not produce an absurd headline cost."""
        feas = quantum_hardware_feasibility(1_000_000, "azure_quantum_quantinuum_h2", logical_depth=1_000_000)
        q = estimate_quantum_cost(
            physical_qubits=feas["priced_circuit_qubits"],
            runtime_ns=10_000_000_000,
            target_platform="azure_quantum_quantinuum_h2",
            shots=256,
            logical_depth=feas["priced_circuit_depth"],
        )
        cost = q["estimated_cost_usd"]
        assert isinstance(cost, (int, float))
        # Bounded: grounded to a 56-qubit, depth-capped circuit at official rates.
        # The pre-fix code produced > $1e12 here.
        assert cost < 1_000_000
