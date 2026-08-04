"""Single source of truth for resource-estimation config across all tooling.

Consolidates what used to be duplicated across:
  - tooling/generate_estimates.py
  - tooling/generate_multimodel_estimates.py
  - tooling/generate_calibration_ensemble.py
  - agents/code_generator/generate.py

What lives here:
  - ENTRY_POINTS: per-problem Q# entry expressions (with optional ``{shots}``
    placeholder for kernels that take an iteration / shot count).
  - QUBIT_MODELS: the qubit profiles × QEC schemes used for the multimodel
    Pareto sweep, expressed as explicit QRE v3 physical parameters.
  - make_architecture / make_isa_query: build the typed ``qdk.qre`` inputs.
  - estimate_summary: run one estimation and reduce the Pareto frontier to the
    single representative point used by downstream consumers.
  - extract_summary: unified flat-dict shape for downstream consumers
    (website, paper figures, agent telemetry).

QRE v3 returns a Pareto frontier rather than a single point. This module picks
the minimum-qubit entry, which is the most conservative hardware ask and matches
how the repo reports ``physicalQubits``. Under matched assumptions that point
uses 1-4x fewer qubits than the retired ``qsharp.estimate`` path, at 1.5-2x the
runtime, because it sits at the low-qubit corner of the frontier.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Iterator

from qdk.qre import (
    Architecture,
    EstimationTable,
    EstimationTableEntry,
    estimate,
    instruction_name,
)
from qdk.qre.application import QSharpApplication
from qdk.qre.interop import trace_from_entry_expr
from qdk.qre.models import GateBased, Majorana, RoundBasedFactory, SurfaceCode
from qdk.qre.property_keys import (
    LOGICAL_COMPUTE_QUBITS,
    LOGICAL_MEMORY_QUBITS,
    PHYSICAL_FACTORY_QUBITS,
)

# Matches the error budget the retired estimator used by default.
DEFAULT_MAX_ERROR = 1e-3

# Matches the profile the retired estimator assumed when given no parameters.
DEFAULT_QUBIT_MODEL = "qubit_gate_ns_e3"
DEFAULT_QEC_SCHEME = "surface_code"

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

    ``name`` keeps the legacy Azure Resource Estimator profile id so existing
    artifacts and website keys stay stable, but the hardware is now described by
    explicit physical parameters rather than a preset lookup.

    ``gate_time_ns`` is None for Majorana, which is measurement-driven.
    """

    name: str
    label: str
    qec_schemes: tuple[str, ...]
    family: str
    speed: str
    error_rate: float
    measurement_time_ns: int
    gate_time_ns: int | None = None

    def architecture(self) -> Architecture:
        if self.family == "majorana":
            return Majorana(error_rate=self.error_rate, time=self.measurement_time_ns)
        return GateBased(
            error_rate=self.error_rate,
            gate_time=self.gate_time_ns,
            measurement_time=self.measurement_time_ns,
        )


# QRE v3 ships no floquet code, and the Majorana architecture produced an empty
# Pareto frontier for every code and factory we tried (SurfaceCode, LowMove,
# ThreeAux, 1D/2D yoked, x RoundBased/Litinski19/GSJ24, and PSSPC as a trace
# transform). Until a supported Majorana ISA is documented, the sweep covers the
# gate-based profiles only, so the two Majorana rows have been retired.
QEC_TRANSFORMS = {"surface_code": SurfaceCode}

QUBIT_MODELS: tuple[QubitModel, ...] = (
    QubitModel("qubit_gate_ns_e3", "Superconducting (ns, 1e-3)", ("surface_code",), "gate_based", "ns", 1e-3, 100, 50),
    QubitModel("qubit_gate_ns_e4", "Superconducting (ns, 1e-4)", ("surface_code",), "gate_based", "ns", 1e-4, 100, 50),
    QubitModel("qubit_gate_us_e3", "Trapped Ion (\u03bcs, 1e-3)", ("surface_code",), "gate_based", "us", 1e-3, 100_000, 100_000),
    QubitModel("qubit_gate_us_e4", "Trapped Ion (\u03bcs, 1e-4)", ("surface_code",), "gate_based", "us", 1e-4, 100_000, 100_000),
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
# QRE v3 estimation
# ---------------------------------------------------------------------------

MODELS_BY_NAME = {m.name: m for m in QUBIT_MODELS}


def make_architecture(qubit_name: str) -> Architecture:
    """Build the typed QRE v3 architecture for a legacy qubit-profile id."""

    try:
        return MODELS_BY_NAME[qubit_name].architecture()
    except KeyError:
        raise KeyError(f"unknown qubit model {qubit_name!r}") from None


def make_isa_query(qec_name: str):
    """Compose the QEC code with a magic-state factory into an ISA query."""

    try:
        code = QEC_TRANSFORMS[qec_name]
    except KeyError:
        raise KeyError(f"unknown QEC scheme {qec_name!r}") from None
    return code.q() * RoundBasedFactory.q()


def select_entry(table: EstimationTable) -> EstimationTableEntry:
    """Reduce a Pareto frontier to the representative point: fewest qubits."""

    if not len(table):
        raise ValueError("no feasible configuration: the Pareto frontier is empty")
    return min(table, key=lambda e: (e.qubits, e.runtime))


def estimate_summary(
    entry_expr: str,
    qubit_name: str,
    qec_name: str,
    max_error: float = DEFAULT_MAX_ERROR,
) -> dict[str, Any]:
    """Estimate one (problem, qubit model, QEC) combination.

    Requires ``qsharp.init(project_root=...)`` to have been called for the
    problem whose expression is being estimated.
    """

    table = estimate(
        QSharpApplication(entry_expr),
        make_architecture(qubit_name),
        isa_query=make_isa_query(qec_name),
        max_error=max_error,
    )
    return extract_summary(select_entry(table), table=table, entry_expr=entry_expr)


# ---------------------------------------------------------------------------
# Summary extraction
# ---------------------------------------------------------------------------

_CODE_DISTANCE_RE = re.compile(r"distance=(\d+)")

# Trace instruction names that map onto the legacy logical-count fields.
_GATE_COUNT_FIELDS = {
    "T": "tCount",
    "RZ": "rotationCount",
    "CCZ": "cczCount",
    "MEAS_Z": "measurementCount",
}


def _logical_counts(entry_expr: str) -> dict[str, Any]:
    """Recover logical gate counts, depth and width from the Q# trace.

    QRE v3 keeps these on the trace rather than the estimation result, so they
    are read back separately. Failures are non-fatal: the estimate itself is
    still valid without them.
    """

    counts: dict[str, Any] = {f: None for f in _GATE_COUNT_FIELDS.values()}
    counts["logicalDepth"] = None
    counts["numQubits"] = None

    try:
        trace = trace_from_entry_expr(entry_expr)
    except Exception:
        return counts

    counts["logicalDepth"] = trace.depth
    counts["numQubits"] = trace.total_qubits

    try:
        raw = trace.gate_counts() if callable(trace.gate_counts) else trace.gate_counts
        for instruction_id, count in dict(raw).items():
            field = _GATE_COUNT_FIELDS.get(instruction_name(instruction_id))
            if field:
                counts[field] = counts[field] or 0
                counts[field] += count
    except Exception:
        pass

    return counts


def extract_summary(
    entry: EstimationTableEntry,
    table: EstimationTable | None = None,
    entry_expr: str | None = None,
) -> dict[str, Any]:
    """Flatten one QRE v3 Pareto entry to the keys downstream consumers want.

    Args:
        entry: The representative point, normally from :func:`select_entry`.
        table: The full frontier, used to report how many points were explored.
        entry_expr: Q# expression, used to recover logical counts from the trace.

    Keys (all may be None if unavailable):
        physicalQubits, runtime, logicalQubits, logicalDepth, tCount,
        rotationCount, cczCount, measurementCount, numQubits, codeDistance,
        tFactoryFraction, error, paretoPoints
    """

    if entry is None:
        return {}

    props = dict(getattr(entry, "properties", {}) or {})
    physical_qubits = entry.qubits
    factory_qubits = props.get(PHYSICAL_FACTORY_QUBITS)

    t_factory_fraction: float | None = None
    if physical_qubits and factory_qubits:
        t_factory_fraction = round(factory_qubits / physical_qubits, 3)

    logical_qubits = (props.get(LOGICAL_COMPUTE_QUBITS) or 0) + (
        props.get(LOGICAL_MEMORY_QUBITS) or 0
    )

    distance_match = _CODE_DISTANCE_RE.search(str(getattr(entry, "source", "")))

    summary: dict[str, Any] = {
        "physicalQubits": physical_qubits,
        "runtime": entry.runtime,
        "logicalQubits": logical_qubits or None,
        "codeDistance": int(distance_match.group(1)) if distance_match else None,
        "tFactoryFraction": t_factory_fraction,
        "error": entry.error,
        "paretoPoints": len(table) if table is not None else None,
    }
    summary.update(_logical_counts(entry_expr) if entry_expr else {})
    return summary
