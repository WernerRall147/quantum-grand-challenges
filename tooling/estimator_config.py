"""Single source of truth for resource-estimation config across all tooling.

Consolidates what used to be duplicated across:
  - tooling/generate_estimates.py
  - tooling/generate_multimodel_estimates.py
  - tooling/generate_circuits.py
  - tooling/generate_calibration_ensemble.py
  - agents/code_generator/generate.py

What lives here:
  - ENTRY_POINTS: per-problem Q# entry expressions (with optional ``{shots}``
    placeholder for kernels that take an iteration / shot count).
  - QUBIT_MODELS: the 6 qubit profiles × QEC schemes used for the multimodel
    Pareto sweep (matches Azure Quantum Resource Estimator names).
  - make_estimator_params / make_batch_estimator_params: typed
    ``qsharp.estimator.EstimatorParams`` factories. Batch mode lets a single
    ``qsharp.estimate()`` call evaluate every (qubit, QEC) combination in one
    pass  replacing nested per-config Python loops.
  - extract_summary: unified flat-dict shape for downstream consumers
    (website, paper figures, agent telemetry).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Iterator

from qsharp.estimator import EstimatorParams

# Conventional shot tiers  callers pass these to EntryPoint.expr().
SHOTS_KERNEL = 1       # minimal cost: structural resource estimate / circuit draw
SHOTS_ESTIMATE = 50    # moderate sampling for stability checks
SHOTS_CALIBRATION = 50  # full statistical ensemble runs

ShotsTemplate = Callable[[int], str]


def _fixed(expr: str) -> ShotsTemplate:
    """Template that ignores the shots argument (kernel takes no iteration param)."""
    return lambda _shots: expr


def _shots(template: str) -> ShotsTemplate:
    """Template that substitutes ``{shots}`` with the requested iteration count."""
    return lambda shots: template.format(shots=shots)


@dataclass(frozen=True)
class EntryPoint:
    """A Q# entry expression for one problem.

    Attributes:
        template: Function ``int -> str`` producing the Q# expression for a
            given shot/iteration count. Built via :func:`_fixed` (no shots
            parameter) or :func:`_shots` (``{shots}`` placeholder).
        default_shots: Shot count used when none is specified.
        description: Human-readable summary of what the kernel computes.
    """

    template: ShotsTemplate
    default_shots: int
    description: str

    def expr(self, shots: int | None = None) -> str:
        return self.template(self.default_shots if shots is None else shots)


# ---------------------------------------------------------------------------
# Per-problem entry points
# ---------------------------------------------------------------------------
# Note: must match actual Q# operation signatures in problems/<id>/qsharp/src/.

ENTRY_POINTS: dict[str, EntryPoint] = {
    "01_hubbard": EntryPoint(
        template=_shots("Main.EstimateHubbardEnergy(0.5, 2.0, 1.0, 0.5, 0.3, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Two-site Hubbard VQE energy estimate",
    ),
    "02_catalysis": EntryPoint(
        template=_shots("Main.EstimateMolecularEnergy(1.0, 0.5, 0.3, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="H2 molecular ground-state VQE",
    ),
    "03_qae_risk": EntryPoint(
        template=_fixed("Main.QAEKernel()"),
        default_shots=SHOTS_KERNEL,
        description="Iterative QAE risk kernel",
    ),
    "04_linear_solvers": EntryPoint(
        template=_fixed("Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)"),
        default_shots=SHOTS_KERNEL,
        description="HHL on 2x2 SPD system, 3-bit clock register",
    ),
    "05_qaoa_maxcut": EntryPoint(
        template=_shots("Main.EvaluateQaoa([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]], [0.5], [0.5], {shots})"),
        default_shots=SHOTS_KERNEL,
        description="QAOA MaxCut on triangle graph, p=1",
    ),
    "06_high_frequency_trading": EntryPoint(
        template=_shots("Main.EstimateLossProbability([0.05, -0.03, 0.02], 1, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Tail-loss probability via amplitude estimation",
    ),
    "07_drug_discovery": EntryPoint(
        template=_shots("Main.EstimateBindingEnergy(1.0, 0.5, 0.3, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Protein-ligand binding energy VQE",
    ),
    "08_protein_folding": EntryPoint(
        template=_shots("Main.EvaluateFoldingQaoa([[0.0,1.0],[1.0,0.0]], 0.5, 0.5, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Protein folding QAOA on minimal lattice",
    ),
    "09_factorization": EntryPoint(
        template=_fixed("Main.ShorPeriodFinding(3, 4)"),
        default_shots=SHOTS_KERNEL,
        description="Shor period finding for a=3, N=4",
    ),
    "10_post_quantum_cryptography": EntryPoint(
        template=_shots("Main.GroverKeySearch(3, 5, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Grover key search over 5-bit space",
    ),
    "11_quantum_machine_learning": EntryPoint(
        template=_shots("Main.SwapTest([1.0, 0.5, 0.3, 0.2], [0.8, 0.2, 0.6, 0.1], {shots})"),
        default_shots=SHOTS_KERNEL,
        description="SWAP test for state-vector overlap",
    ),
    "12_quantum_optimization": EntryPoint(
        template=_shots("Main.EvaluateQaoa([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], 0.5, 0.5, 1, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Generic QAOA, p=1",
    ),
    "13_climate_modeling": EntryPoint(
        template=_shots("Main.RunHHLClimate(3, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="HHL-based climate PDE solver",
    ),
    "14_materials_discovery": EntryPoint(
        template=_shots("Main.EstimateBandGap(1.0, -0.5, 0.8, 0.3, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Band-gap VQE for toy material",
    ),
    "15_database_search": EntryPoint(
        template=_fixed("Main.GroverSearch([7], 4, 3)"),
        default_shots=SHOTS_KERNEL,
        description="Grover search for target=7 in 4-bit space",
    ),
    "16_error_correction": EntryPoint(
        template=_fixed("Main.RunRepetitionCodeCycle(false, 0)"),
        default_shots=SHOTS_KERNEL,
        description="One repetition-code cycle, no injected error",
    ),
    "17_nuclear_physics": EntryPoint(
        template=_shots("Main.EstimateNuclearEnergy(1.0, 0.5, 0.3, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Nuclear shell-model VQE",
    ),
    "18_photovoltaics": EntryPoint(
        template=_shots("Main.RunExcitonWalk(10, 0.5, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Exciton quantum walk, 10 sites",
    ),
    "19_quantum_chromodynamics": EntryPoint(
        template=_shots("Main.SimulateLatticeGauge(2, 1.0, 0.5, 3, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Lattice gauge Trotter simulation, 2 sites",
    ),
    "20_space_mission_planning": EntryPoint(
        template=_shots("Main.EvaluateQaoaMission([[0.0,1.0,0.5],[1.0,0.0,0.8],[0.5,0.8,0.0]], 0.5, 0.5, 1, {shots})"),
        default_shots=SHOTS_KERNEL,
        description="Mission-planning QAOA, p=1",
    ),
}

# Subset suitable for circuit diagram rendering (small enough to draw).
CIRCUIT_DIAGRAM_PROBLEMS: tuple[str, ...] = (
    "01_hubbard",
    "02_catalysis",
    "03_qae_risk",
    "04_linear_solvers",
    "15_database_search",
)


# ---------------------------------------------------------------------------
# Qubit × QEC models (Azure Quantum Resource Estimator profiles)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QubitModel:
    """One row of the Pareto sweep matrix.

    ``qec_schemes`` enumerates which codes pair with this qubit family 
    floquet code is Majorana-only.
    """

    name: str
    label: str
    qec_schemes: tuple[str, ...]
    family: str
    speed: str


QUBIT_MODELS: tuple[QubitModel, ...] = (
    QubitModel("qubit_gate_ns_e3", "Superconducting (ns, 1e-3)", ("surface_code",), "gate_based", "ns"),
    QubitModel("qubit_gate_ns_e4", "Superconducting (ns, 1e-4)", ("surface_code",), "gate_based", "ns"),
    QubitModel("qubit_gate_us_e3", "Trapped Ion (\u03bcs, 1e-3)", ("surface_code",), "gate_based", "us"),
    QubitModel("qubit_gate_us_e4", "Trapped Ion (\u03bcs, 1e-4)", ("surface_code",), "gate_based", "us"),
    QubitModel("qubit_maj_ns_e4", "Majorana (ns, 1e-4)", ("surface_code", "floquet_code"), "majorana", "ns"),
    QubitModel("qubit_maj_ns_e6", "Majorana (ns, 1e-6)", ("surface_code", "floquet_code"), "majorana", "ns"),
)


def iter_model_configs(
    models: Iterable[QubitModel] = QUBIT_MODELS,
) -> Iterator[tuple[QubitModel, str, str]]:
    """Yield ``(model, qec_scheme, config_key)`` in stable order.

    ``config_key`` is ``f"{model.name}+{qec}"``  the same string used as the
    JSON key in ``multiModelEstimates.json``.
    """

    for m in models:
        for qec in m.qec_schemes:
            yield m, qec, f"{m.name}+{qec}"


# ---------------------------------------------------------------------------
# Typed EstimatorParams factories
# ---------------------------------------------------------------------------

def make_estimator_params(
    qubit_name: str,
    qec_name: str,
    error_budget: float | None = None,
) -> EstimatorParams:
    """Build a single-item ``EstimatorParams`` (typed, not raw dict)."""

    p = EstimatorParams()
    p.qubit_params.name = qubit_name
    p.qec_scheme.name = qec_name
    if error_budget is not None:
        p.error_budget = error_budget
    return p


def make_batch_estimator_params(
    configs: Iterable[tuple[str, str]],
    error_budget: float | None = None,
) -> EstimatorParams:
    """Build a multi-item ``EstimatorParams`` for one batched ``qsharp.estimate()`` call.

    Args:
        configs: ``(qubit_params_name, qec_scheme_name)`` pairs in the order
            their results will appear at ``EstimatorResult[i]``.
        error_budget: Optional per-item error budget applied to every entry.

    Returns:
        An ``EstimatorParams`` with ``num_items`` populated. Passing this to
        ``qsharp.estimate()`` returns an ``EstimatorResult`` indexable as a
        list of length ``len(configs)``.
    """

    configs = list(configs)
    p = EstimatorParams(num_items=len(configs))
    for i, (qubit_name, qec_name) in enumerate(configs):
        p.items[i].qubit_params.name = qubit_name
        p.items[i].qec_scheme.name = qec_name
        if error_budget is not None:
            p.items[i].error_budget = error_budget
    return p


# ---------------------------------------------------------------------------
# Summary extraction
# ---------------------------------------------------------------------------

def extract_summary(estimate_data: Any) -> dict[str, Any]:
    """Flatten a ``qsharp.estimate()`` result to the keys downstream consumers want.

    Works on a single-item result or one item out of a batched result (both are
    dict-like). Returns an empty dict if the input isn't a mapping.

    Keys (all may be None if unavailable):
        physicalQubits, runtime, rqops, logicalQubits, logicalDepth, tCount,
        rotationCount, cczCount, measurementCount, numQubits, codeDistance,
        tFactoryFraction
    """

    if not isinstance(estimate_data, dict):
        return {}

    pc = estimate_data.get("physicalCounts", {}) or {}
    lc = estimate_data.get("logicalCounts", {}) or {}
    bd = pc.get("breakdown", {}) or {}
    patch_raw = bd.get("logicalPatch")
    patch = patch_raw if isinstance(patch_raw, dict) else None

    physical_qubits = pc.get("physicalQubits")
    t_factory_qubits = bd.get("physicalQubitsForTfactories")
    t_factory_fraction: float | None = None
    if physical_qubits and t_factory_qubits:
        try:
            t_factory_fraction = round(t_factory_qubits / physical_qubits, 3)
        except (ZeroDivisionError, TypeError):
            pass

    return {
        "physicalQubits": physical_qubits,
        "runtime": pc.get("runtime"),
        "rqops": pc.get("rqops"),
        "logicalQubits": bd.get("algorithmicLogicalQubits"),
        "logicalDepth": lc.get("logicalDepth"),
        "tCount": lc.get("tCount"),
        "rotationCount": lc.get("rotationCount"),
        "cczCount": lc.get("cczCount"),
        "measurementCount": lc.get("measurementCount"),
        "numQubits": lc.get("numQubits"),
        "codeDistance": patch.get("codeDistance") if patch else None,
        "tFactoryFraction": t_factory_fraction,
    }
