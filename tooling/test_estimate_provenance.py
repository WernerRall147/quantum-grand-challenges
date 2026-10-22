"""An estimate that names an operation the code no longer defines is describing a ghost.

Five problems were upgraded from VQE to QPE in August 2026. The stored emulator
histograms from April still describe the kernels that were replaced, and nothing noticed
until a human read two files side by side. `circuits/estimate.json` records the exact
expressions it was produced from - `entryExpr` and `hardwareKernelEntryPoint` - so the
drift is detectable without regenerating anything.

This checks the half of provenance that already exists. Stamping a source commit at
generation time is the other half, and it is not needed to catch this defect class.
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# `Main.EstimateHubbardEnergy(0.5, 2.0, 1)` and `HubbardQPEKernel()` both reduce to the
# operation name: drop any module qualifier and the argument list.
_CALLABLE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _operation_name(expression: str) -> str | None:
    match = _CALLABLE.search(expression or "")
    return match.group(1) if match else None


def _estimates() -> list[tuple[str, Path]]:
    found = []
    for path in sorted((REPO_ROOT / "problems").rglob("circuits/estimate.json")):
        found.append((path.relative_to(REPO_ROOT).parts[-3], path))
    return found


def _defined_operations(problem_dir: Path) -> set[str]:
    """Every operation defined anywhere in the problem's Q#.

    Deliberately not tied to a filename. Q# lives in qsharp/src/Main.qs for the estimated
    program and qsharp/HardwareKernel.qs for the submitted one, and asserting that layout
    would fail on a reorganisation that broke nothing.
    """
    names: set[str] = set()
    for source in (problem_dir / "qsharp").rglob("*.qs"):
        names.update(
            re.findall(r"^\s*operation\s+([A-Za-z_][A-Za-z0-9_]*)", source.read_text(encoding="utf-8"), re.M)
        )
    return names


ESTIMATES = _estimates()


def test_every_problem_has_an_estimate_to_check():
    """Guard the guard: a glob that silently matches nothing would pass forever."""
    assert len(ESTIMATES) >= 20, f"expected at least 20 estimate.json files, found {len(ESTIMATES)}"


@pytest.mark.parametrize("problem,path", ESTIMATES, ids=[p for p, _ in ESTIMATES])
def test_estimate_names_operations_that_still_exist(problem, path):
    data = json.loads(path.read_text(encoding="utf-8"))
    defined = _defined_operations(path.parent.parent)
    assert defined, f"{problem}: no Q# operations found, cannot verify the estimate"

    missing = []
    for field in ("entryExpr", "hardwareKernelEntryPoint"):
        expression = data.get(field)
        if not expression:
            continue
        name = _operation_name(expression)
        if name and name not in defined:
            missing.append(f"{field}={expression!r} -> operation {name!r} is not defined")

    assert not missing, (
        f"{problem}: estimate.json describes code that no longer exists: "
        + "; ".join(missing)
        + ". Regenerate the estimate, or correct the field."
    )


# ---------------------------------------------------------------------------
# The other way an estimate lies: the numbers were never measured.
#
# tooling/estimator/run_estimation.py shelled out to a `qsharp-re` executable that no
# installed package provides. The FileNotFoundError was caught and answered with
# _generate_mock_output(), so every "live" run returned a fabricated constant - which is
# how nine unrelated problems came to report an identical 16 logical / 35,200 physical.
#
# That survived because there were two estimate stores. circuits/estimate.json held
# measurements; problems/<id>/estimates/ held the constant, and fed
# tooling/azure/assess_problem_readiness.py and prepare_problem_manifest.py, so the
# fabrication reached readiness claims while the real numbers sat one directory away.
#
# There is now one store. These two checks keep it that way: the survivor must carry
# real provenance, and the retired one must stay retired.
#
# Archived problems are excluded from the retirement rule: they are downgraded work
# kept as a record, and CI still regenerates 05_qaoa_maxcut with --mock.
# ---------------------------------------------------------------------------

ACTIVE_PROBLEM_DIRS = sorted(
    path.parent.parent
    for path in (REPO_ROOT / "problems").glob("*/qsharp/qsharp.json")
    if "archived" not in path.parts
)


def _problem_id(path: Path) -> str:
    return path.relative_to(REPO_ROOT).parts[1]


def test_every_active_problem_was_discovered():
    """Guard the guard: an empty glob would make both checks below vacuous."""
    assert len(ACTIVE_PROBLEM_DIRS) >= 9, (
        f"expected at least 9 active problems, found {len(ACTIVE_PROBLEM_DIRS)}"
    )


@pytest.mark.parametrize(
    "problem_dir", ACTIVE_PROBLEM_DIRS, ids=[_problem_id(p) for p in ACTIVE_PROBLEM_DIRS]
)
def test_the_single_estimate_carries_real_provenance(problem_dir):
    """circuits/estimate.json must say which estimator produced it, and not be mock."""
    problem = _problem_id(problem_dir)
    path = problem_dir / "circuits" / "estimate.json"
    assert path.exists(), (
        f"{problem}: no circuits/estimate.json. It is the single source of truth for "
        f"this problem's resource estimate - run `python tooling/generate_estimates.py`."
    )

    build = json.loads(path.read_text(encoding="utf-8-sig")).get("build", {})
    qdk_version = str(build.get("qdkVersion", ""))
    estimator_version = str(build.get("estimatorVersion", ""))

    assert qdk_version and qdk_version not in ("mock", "unknown"), (
        f"{problem}: circuits/estimate.json build.qdkVersion is {qdk_version!r}. "
        f"An estimate that cannot name the estimator that produced it is not evidence. "
        f"Regenerate with `python tooling/generate_estimates.py`."
    )
    assert not estimator_version.startswith("mock-"), (
        f"{problem}: build.estimatorVersion is {estimator_version!r}, so these numbers "
        f"are simulated output regardless of the qdkVersion recorded."
    )


@pytest.mark.parametrize(
    "problem_dir", ACTIVE_PROBLEM_DIRS, ids=[_problem_id(p) for p in ACTIVE_PROBLEM_DIRS]
)
def test_active_problems_keep_only_one_estimate_store(problem_dir):
    """No second set of resource estimates under problems/<id>/estimates/.

    Selected by shape rather than filename: an estimate artifact from the retired
    pipeline is a mapping carrying estimator_target. Classical baselines, Azure job
    manifests, run results and calibration ensembles live in the same directory,
    describe different things, and stay.
    """
    problem = _problem_id(problem_dir)
    strays = []
    for path in sorted((problem_dir / "estimates").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError):
            continue
        if isinstance(data, dict) and "estimator_target" in data:
            strays.append(path.name)

    assert not strays, (
        f"{problem}: a second estimate store has reappeared under estimates/ - "
        + ", ".join(strays)
        + ". circuits/estimate.json is the single source of truth; two stores is how a "
        "fabricated constant went unnoticed beside real numbers for six months. "
        "tooling/estimator/run_estimation.py refuses to write here without "
        "--allow-retired-store."
    )


# ---------------------------------------------------------------------------
# The magic state cultivation scenario is a projection published beside the estimates,
# not a second store of them (issue #296). It answers "how much of the T-factory overhead
# is the round-based factory?", so it must say what produced it, cover every problem with
# the infeasible results recorded, keep its baseline columns equal to the published
# numbers, and keep its generated table in step with its data. A projection that drifted
# from the estimates it sits beside would mislead exactly the reader it was written for.
# ---------------------------------------------------------------------------

SCENARIO_PATH = REPO_ROOT / "docs" / "estimates" / "cultivation-scenario.json"
SCENARIO_TABLE_PATH = SCENARIO_PATH.with_suffix(".md")
REGENERATE_SCENARIO = "Regenerate with `python tooling/generate_estimates.py --scenario cultivation`."


def _scenario() -> dict:
    assert SCENARIO_PATH.exists(), f"docs/estimates/cultivation-scenario.json is missing. {REGENERATE_SCENARIO}"
    return json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))


def _generator():
    """tooling/generate_estimates.py, imported only by the checks that need qdk."""
    tooling = str(REPO_ROOT / "tooling")
    if tooling not in sys.path:
        sys.path.insert(0, tooling)
    import generate_estimates

    return generate_estimates


def test_cultivation_scenario_carries_real_provenance():
    """The same provenance as the baseline: qdk version, estimator version, commit, time."""
    build = _scenario().get("build", {})
    qdk_version = str(build.get("qdkVersion", ""))
    estimator_version = str(build.get("estimatorVersion", ""))
    commit = str(build.get("commit", ""))
    date_utc = str(build.get("dateUtc", ""))

    assert qdk_version and qdk_version not in ("mock", "unknown"), (
        f"cultivation scenario: build.qdkVersion is {qdk_version!r}. A projection that cannot "
        f"name the estimator that produced it is not evidence. {REGENERATE_SCENARIO}"
    )
    assert estimator_version.startswith(f"qdk-{qdk_version}/"), (
        f"cultivation scenario: build.estimatorVersion is {estimator_version!r}, which does not "
        f"name qdk {qdk_version}. {REGENERATE_SCENARIO}"
    )
    assert re.fullmatch(r"[0-9a-f]{40}", commit), (
        f"cultivation scenario: build.commit is {commit!r}, not a commit hash. {REGENERATE_SCENARIO}"
    )
    try:
        generated = datetime.fromisoformat(date_utc)
    except ValueError:
        generated = None
    assert generated is not None and generated.tzinfo is not None, (
        f"cultivation scenario: build.dateUtc is {date_utc!r}, not a UTC timestamp. {REGENERATE_SCENARIO}"
    )


def test_cultivation_scenario_covers_every_problem_and_records_infeasible_results():
    data = _scenario()
    generator = _generator()
    assert data.get("status") == "projection", (
        f"cultivation scenario: status is {data.get('status')!r}. It must be labelled a projection."
    )

    estimated = {problem for problem, _ in ESTIMATES}
    covered = set(data.get("problems", {}))
    assert covered == estimated, (
        f"cultivation scenario covers {len(covered)} problems, the published estimates "
        f"{len(estimated)}. Missing: {sorted(estimated - covered)}; extra: "
        f"{sorted(covered - estimated)}. {REGENERATE_SCENARIO}"
    )

    profiles = [model.name for model in generator.QUBIT_MODELS]
    gaps = []
    for problem, record in sorted(data["problems"].items()):
        factories = generator.SCENARIO_FACTORIES
        if record.get("toffoliCount"):
            factories += tuple(generator.CCX_VARIANTS.values())
        for profile in profiles:
            cells = record.get("profiles", {}).get(profile, {})
            for factory in factories:
                cell = cells.get(factory)
                if cell is None:
                    gaps.append(f"{problem} {profile} {factory}: missing")
                elif cell.get("feasible") is False:
                    if not cell.get("reason"):
                        gaps.append(f"{problem} {profile} {factory}: infeasible with no reason")
                elif not all(
                    isinstance(cell.get(key), int) and cell[key] > 0
                    for key in ("physicalQubits", "runtime")
                ):
                    gaps.append(f"{problem} {profile} {factory}: no physical qubits or runtime")
    assert not gaps, (
        "cultivation scenario has combinations that are neither measured nor recorded as "
        "infeasible: " + "; ".join(gaps[:10]) + f". {REGENERATE_SCENARIO}"
    )


@pytest.mark.parametrize("problem,path", ESTIMATES, ids=[p for p, _ in ESTIMATES])
def test_cultivation_scenario_baseline_is_the_published_estimate(problem, path):
    """Its baseline columns are the published numbers, not a stale copy of them."""
    data = _scenario()
    published = json.loads(path.read_text(encoding="utf-8-sig"))
    baseline = data["baseline"]
    assert (published.get("qubitModel"), published.get("qecScheme")) == (
        baseline["qubitModel"],
        baseline["qecScheme"],
    ), f"{problem}: the published estimate and the scenario's baseline use different profiles"

    cell = data["problems"].get(problem, {}).get("profiles", {}).get(baseline["qubitModel"], {})
    cell = cell.get(baseline["factory"], {})
    differences = [
        f"{key} {cell.get(key)!r} in the scenario, {published.get(key)!r} published"
        for key in ("physicalQubits", "runtime", "tFactoryFraction", "codeDistance")
        if cell.get(key) != published.get(key)
    ]
    # The Toffoli check runs only where the scenario found Toffoli gates, so a trace that
    # failed to count them would skip it silently.
    toffolis = data["problems"].get(problem, {}).get("toffoliCount")
    if toffolis != (published.get("cczCount") or 0):
        differences.append(f"toffoliCount {toffolis!r} in the scenario, cczCount {published.get('cczCount')!r} published")
    expression = data["problems"].get(problem, {}).get("entryExpr")
    if expression != published.get("entryExpr"):
        differences.append(f"entryExpr {expression!r} in the scenario, {published.get('entryExpr')!r} published")
    assert not differences, (
        f"{problem}: the cultivation scenario's baseline no longer matches circuits/estimate.json: "
        + "; ".join(differences)
        + f". The projection is stale beside the numbers it is compared with. {REGENERATE_SCENARIO}"
    )


def test_cultivation_scenario_table_is_generated_from_its_data():
    """The markdown is rendered from the JSON. A hand edit, or a stale copy, fails here."""
    expected = _generator().render_cultivation_markdown(_scenario())
    actual = SCENARIO_TABLE_PATH.read_text(encoding="utf-8")
    diff = list(
        difflib.unified_diff(
            expected.splitlines(), actual.splitlines(), "rendered from the JSON", "committed", lineterm="", n=0
        )
    )
    assert not diff, (
        "docs/estimates/cultivation-scenario.md is not what its JSON renders to:\n"
        + "\n".join(diff[:20])
        + f"\n{REGENERATE_SCENARIO}"
    )


# The checks above would pass a number someone typed in, so one cell of each kind the page
# reports is estimated again. Physical qubits, runtime and feasibility are exact: where
# configurations tie, only the recorded error fields can differ between runs.
RE_ESTIMATED_CELLS = (
    ("07_drug_discovery", "qubit_gate_ns_e3", "gsj24_5_15"),  # feasible, published profile
    ("01_hubbard", "qubit_gate_ns_e3", "gsj24_5_15"),  # infeasible within the error budget
    ("01_hubbard", "qubit_gate_ns_e4", "gsj24_5_15"),  # a 1e-4 profile, served from the 5e-4 table
    ("13_climate_modeling", "qubit_gate_ns_e3", "gsj24_3_15+ccx"),  # feasible only with GSJ24CCXFactory
)


@pytest.mark.parametrize(
    "problem,profile,factory", RE_ESTIMATED_CELLS, ids=["-".join(cell) for cell in RE_ESTIMATED_CELLS]
)
def test_cultivation_scenario_cells_are_what_the_estimator_returns(problem, profile, factory):
    from qdk import qsharp

    generator = _generator()
    published = dict(ESTIMATES)[problem]
    qsharp.init(project_root=str(published.parent.parent / "qsharp"))
    expression = json.loads(published.read_text(encoding="utf-8-sig"))["entryExpr"]
    table = generator.estimate_table(expression, profile, generator.DEFAULT_QEC_SCHEME, factory=factory)
    if len(table):
        entry = generator.select_entry(table)
        measured = {"feasible": True, "physicalQubits": entry.qubits, "runtime": entry.runtime}
    else:
        measured = {"feasible": False}

    recorded = _scenario()["problems"][problem]["profiles"][profile][factory]
    assert {key: recorded.get(key) for key in measured} == measured, (
        f"{problem} {profile} {factory}: the scenario records {recorded}, the estimator returns "
        f"{measured}. {REGENERATE_SCENARIO}"
    )


