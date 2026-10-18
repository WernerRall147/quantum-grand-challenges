#!/usr/bin/env python3
"""Generate resource estimation JSON for all Q# problems using the QRE v3 estimator.

Saves estimate.json to each problem's circuits/ directory, and exports the
Pareto frontiers to website/data/paretoFrontiers.json so the site can show the
qubit-versus-runtime trade rather than a single point.

With ``--scenario cultivation`` it writes none of those. It estimates every problem
again with QRE v3's model of magic state cultivation beside the round-based factory the
published estimates use, on every qubit profile, and writes the labelled projection to
docs/estimates/cultivation-scenario.json and a generated table beside it.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from discover_problems import discover_all_problems
from estimator_config import (
    DEFAULT_MAX_ERROR,
    DEFAULT_QEC_SCHEME,
    DEFAULT_QUBIT_MODEL,
    ENTRY_POINTS,
    QUBIT_MODELS,
    _logical_counts,
    estimate_summary,
    estimate_table,
    extract_summary,
    make_architecture,
    make_isa_query,
    select_entry,
)

FRONTIERS_PATH = Path(__file__).resolve().parent.parent / "website" / "data" / "paretoFrontiers.json"
# Was hand-maintained and never regenerated, so it still described the VQE kernels
# that #176 replaced with QPE: 18 logical qubits and 45 rotations for Hubbard where
# every qubit model now reports 12 and 12. Logical counts are hardware-independent,
# so no configuration explained the gap - the file simply measured deleted code.
ESTIMATES_PATH = Path(__file__).resolve().parent.parent / "website" / "data" / "resourceEstimates.json"

_KERNEL_ENTRY_RE = re.compile(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)")


def _qdk_version() -> str:
    """The installed QDK version, recorded on every estimate."""
    from importlib import metadata

    for dist in ("qdk", "qsharp"):
        try:
            return metadata.version(dist)
        except metadata.PackageNotFoundError:
            continue
    return "unknown"


def _git_commit() -> str:
    import subprocess

    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parent.parent,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def kernel_entry_point(qsharp_dir: Path) -> str | None:
    """The operation Azure Quantum actually executes, which is not what we estimate."""

    kernel = qsharp_dir / "HardwareKernel.qs"
    if not kernel.exists():
        return None
    m = _KERNEL_ENTRY_RE.search(kernel.read_text(encoding="utf-8"))
    return f"{m.group(1)}()" if m else None


# ---------------------------------------------------------------------------
# Magic state cultivation scenario: a labelled projection, never the baseline
# ---------------------------------------------------------------------------

SCENARIO_JSON = Path(__file__).resolve().parent.parent / "docs" / "estimates" / "cultivation-scenario.json"
SCENARIO_MD = SCENARIO_JSON.with_suffix(".md")

# The published factory first, then the two distances QRE v3's cultivation model supports.
SCENARIO_FACTORIES = ("round_based", "gsj24_3_15", "gsj24_5_15")
CULTIVATION_DISTANCES = {"gsj24_3_15": (3, 15), "gsj24_5_15": (5, 15)}
# The same cultivation factories with GSJ24CCXFactory beside them, estimated only for
# programs that contain Toffoli gates, to find out whether those need it.
CCX_VARIANTS = {"gsj24_3_15": "gsj24_3_15+ccx", "gsj24_5_15": "gsj24_5_15+ccx"}

CULTIVATION_REFERENCE = {
    "arxiv": "2409.17595v1",
    "title": "Magic state cultivation: growing T states as cheap as CNOT gates",
    "authors": ["Craig Gidney", "Noah Shutty", "Cody Jones"],
    "url": "https://arxiv.org/abs/2409.17595v1",
    "simulationData": "https://doi.org/10.5281/zenodo.13777072",
}
EXPERIMENT_REFERENCE = {
    "arxiv": "2512.13908v1",
    "title": "Magic state cultivation on a superconducting quantum processor",
    "url": "https://arxiv.org/abs/2512.13908v1",
    "quote": (
        "Cultivation reduces the error by a factor of 40, with a state fidelity of "
        "0.9999(1) (retaining 8% of attempts)."
    ),
    "announcement": (
        "https://blog.google/innovation-and-ai/models-and-research/quantum-computing/"
        "magic-state-cultivation-quantum-computing/"
    ),
    "announcementQuote": (
        "we still need to demonstrate magic state cultivation at a larger scale to make it "
        "realistic for practical quantum computing"
    ),
}


def _describe_query(node) -> str:
    """Compact text for an ISA query, read from the query object rather than restated."""

    if hasattr(node, "sources"):
        joiner = " + " if type(node).__name__ == "_SumNode" else " * "
        return joiner.join(_describe_query(source) for source in node.sources)
    args = [f"{key}={value!r}" for key, value in node.kwargs.items()]
    if type(node.source).__name__ != "RootNode":
        args.append(f"source={_describe_query(node.source)}")
    return f"{node.component.__name__}.q({', '.join(args)})"


def _cultivation_simulated_error_rates() -> list[float]:
    """The physical error rates GSJ24Factory has simulation tables for."""

    from qdk.qre.models import GSJ24Factory

    return sorted(GSJ24Factory()._data)


def _cultivation_tables_used(qubit_model: str) -> dict[str, dict]:
    """Which of GSJ24Factory's simulation tables the estimator drew T states from.

    Measured, not assumed: the T states the factory offers at this profile are matched
    against each table it ships. qdk 1.31.0 keeps the tables in ``GSJ24Factory()._data``,
    keyed by the physical error rate they were simulated at.
    """

    from qdk.qre.instruction_ids import T
    from qdk.qre.models import GSJ24Factory

    tables = GSJ24Factory()._data
    used = {}
    for factory, distance in CULTIVATION_DISTANCES.items():
        offered = sorted(
            isa[T].expect_error_rate()
            for isa in GSJ24Factory.q(distance=distance).enumerate(
                make_architecture(qubit_model).context()
            )
        )
        matches = [
            rate
            for rate, by_distance in sorted(tables.items())
            if sorted(entry.logical_error for entry in by_distance[distance]) == offered
        ]
        if offered and len(matches) != 1:
            raise RuntimeError(
                f"{qubit_model} {distance}: GSJ24Factory offered T states that match "
                f"{len(matches)} of its tables, so the scenario cannot say what it did"
            )
        used[factory] = {
            "simulatedErrorRate": matches[0] if matches else None,
            "tStatesOffered": len(offered),
            "lowestTStateError": offered[0] if offered else None,
        }
    return used


def _scenario_cell(entry_expr: str, qubit_model: str, factory: str) -> dict:
    """One (program, profile, factory) result. An infeasible one is recorded, not dropped."""

    from qdk.qre import PHYSICAL, instruction_name

    table = estimate_table(entry_expr, qubit_model, DEFAULT_QEC_SCHEME, factory=factory)
    if not len(table):
        return {
            "feasible": False,
            "reason": f"empty Pareto frontier at maxError {DEFAULT_MAX_ERROR:g}",
        }
    entry = select_entry(table)
    summary = extract_summary(entry, table=table)
    magic_states = {}
    for instruction, result in sorted(entry.factories.items()):
        # What supplied the states: a factory, or (when the budget allows) the profile's own
        # physical gate, in which case no factory was used at all.
        source = entry.source.get(instruction)
        magic_states[instruction_name(instruction)] = {
            "source": type(source.transform).__name__ if source is not None else None,
            "physical": source is not None and source.instruction.encoding == PHYSICAL,
            "factoryCopies": result.copies,
            "states": result.states,
            "errorRate": result.error_rate,
        }
    return {
        "feasible": True,
        "physicalQubits": summary["physicalQubits"],
        "runtime": summary["runtime"],
        "tFactoryFraction": summary["tFactoryFraction"],
        "logicalQubits": summary["logicalQubits"],
        "codeDistance": summary["codeDistance"],
        "error": summary["error"],
        "paretoPoints": summary["paretoPoints"],
        "magicStates": magic_states,
    }


def cultivation_scenario() -> int:
    from qdk import qsharp

    qdk_version = _qdk_version()
    commit = _git_commit()
    factories_used = SCENARIO_FACTORIES + tuple(CCX_VARIANTS.values())
    problems: dict[str, dict] = {}

    for pd in discover_all_problems():
        qsharp_dir = pd / "qsharp"
        ep = ENTRY_POINTS.get(pd.name)
        if not (qsharp_dir / "qsharp.json").exists() or ep is None:
            continue

        # Unlike the published run, any failure stops the scenario: a partial projection
        # would read as a complete one.
        qsharp.init(project_root=str(qsharp_dir))
        expr = ep.expr()
        toffolis = _logical_counts(expr).get("cczCount") or 0
        factories = SCENARIO_FACTORIES + (tuple(CCX_VARIANTS.values()) if toffolis else ())
        profiles = {
            model.name: {factory: _scenario_cell(expr, model.name, factory) for factory in factories}
            for model in QUBIT_MODELS
        }
        problems[pd.name] = {"entryExpr": expr, "toffoliCount": toffolis, "profiles": profiles}

        published = profiles[DEFAULT_QUBIT_MODEL]
        print(
            f"OK {pd.name}: "
            + ", ".join(
                f"{factory} {published[factory].get('physicalQubits', 'infeasible')}"
                for factory in SCENARIO_FACTORIES
            )
        )

    data = {
        "scenario": "magic state cultivation",
        "status": "projection",
        "statement": (
            "A projection, not a published estimate. QRE v3's model of magic state "
            "cultivation (GSJ24Factory) replaces the round-based factory the published "
            "estimates use, with the same programs, trace transform, error budget and "
            "selection rule, on every gate-based qubit profile. The published estimates are "
            "each problem's circuits/estimate.json, and this scenario does not change them."
        ),
        "build": {
            "commit": commit,
            "qdkVersion": qdk_version,
            "estimatorVersion": (
                f"qdk-{qdk_version}/{DEFAULT_QEC_SCHEME}+{'|'.join(SCENARIO_FACTORIES)}"
            ),
            "dateUtc": datetime.now(timezone.utc).isoformat(),
        },
        "baseline": {
            "factory": "round_based",
            "publishedAs": "problems/<id>/circuits/estimate.json",
            "qubitModel": DEFAULT_QUBIT_MODEL,
            "qecScheme": DEFAULT_QEC_SCHEME,
        },
        "maxError": DEFAULT_MAX_ERROR,
        "qecScheme": DEFAULT_QEC_SCHEME,
        "selection": "min-qubits",
        "ties": (
            "Where several configurations tie on physical qubits and runtime, which one the "
            "estimator reports can change between runs, so a combination's recorded error and "
            "magic-state error rates can change on regeneration. Its physical qubits and "
            "runtime cannot."
        ),
        "traceQuery": "qdk.qre default (PSSPC * LatticeSurgery)",
        "cultivationModel": CULTIVATION_REFERENCE,
        "cultivationSimulatedErrorRates": _cultivation_simulated_error_rates(),
        "experiment": EXPERIMENT_REFERENCE,
        "factories": {
            factory: {"isaQuery": _describe_query(make_isa_query(DEFAULT_QEC_SCHEME, factory))}
            for factory in factories_used
        },
        "profiles": {
            model.name: {
                "label": model.label,
                "physicalErrorRate": model.error_rate,
                "gateTimeNs": model.gate_time_ns,
                "measurementTimeNs": model.measurement_time_ns,
                "cultivation": _cultivation_tables_used(model.name),
            }
            for model in QUBIT_MODELS
        },
        "problems": problems,
    }

    SCENARIO_JSON.parent.mkdir(parents=True, exist_ok=True)
    SCENARIO_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    SCENARIO_MD.write_text(render_cultivation_markdown(data), encoding="utf-8", newline="\n")
    print(f"\nProjection for {len(problems)} problems -> {SCENARIO_JSON.name}, {SCENARIO_MD.name}")
    return 0


_FACTORY_LABELS = {
    "round_based": "RoundBasedFactory",
    "gsj24_3_15": "GSJ24Factory (3, 15)",
    "gsj24_5_15": "GSJ24Factory (5, 15)",
}


def _distance_label(factory: str) -> str:
    return _FACTORY_LABELS[factory].removeprefix("GSJ24Factory ")


def _fmt_runtime(ns: int) -> str:
    for unit, size in (("days", 86_400e9), ("h", 3_600e9), ("min", 60e9), ("s", 1e9), ("ms", 1e6), ("µs", 1e3)):
        if ns >= size:
            value = ns / size
            return f"{value:,.0f} {unit}" if value >= 100 else f"{value:.3g} {unit}"
    return f"{ns:,} ns"


def _fmt_rate(rate: float) -> str:
    """1e-3 rather than 0.001, the way the profiles are named."""

    mantissa, exponent = f"{rate:.0e}".split("e")
    return f"{mantissa}e{int(exponent)}"


def _fmt_ratio(value: float, baseline: float) -> str:
    ratio = value / baseline
    return f"{ratio:.0f}x" if ratio >= 10 else f"{ratio:#.2g}x"


def _join(items: list[str]) -> str:
    if not items:
        return "none"
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _physical_states(cell: dict) -> list[str]:
    return [name for name, state in cell.get("magicStates", {}).items() if state["physical"]]


def _fmt_cell(cell: dict, baseline: dict | None) -> list[str]:
    """Qubits, runtime and T-factory fraction, with ratios to the baseline when it has one."""

    if not cell["feasible"]:
        return ["infeasible", "-", "-"]
    qubits = f"{cell['physicalQubits']:,}"
    runtime = _fmt_runtime(cell["runtime"])
    if baseline is not None and baseline["feasible"]:
        qubits += f" ({_fmt_ratio(cell['physicalQubits'], baseline['physicalQubits'])})"
        runtime += f" ({_fmt_ratio(cell['runtime'], baseline['runtime'])})"
    if not cell["magicStates"]:
        fraction = "no magic states"
    elif cell["tFactoryFraction"] is None:
        fraction = "-"
    else:
        fraction = f"{cell['tFactoryFraction']:.1%}"
    if _physical_states(cell):
        fraction += f", physical {' and '.join(_physical_states(cell))}"
    return [qubits, runtime, fraction]


def _same_point(a: dict, b: dict) -> bool:
    return (a["feasible"], a.get("physicalQubits"), a.get("runtime")) == (
        b["feasible"],
        b.get("physicalQubits"),
        b.get("runtime"),
    )


def render_cultivation_markdown(data: dict) -> str:
    """The human-readable table, generated from the scenario JSON and nothing else."""

    build = data["build"]
    problems = data["problems"]
    profiles = data["profiles"]
    factories = data["factories"]
    baseline_factory = data["baseline"]["factory"]
    baseline_model = data["baseline"]["qubitModel"]
    scenario = [f for f in factories if f != baseline_factory and not f.endswith("+ccx")]
    n = len(problems)
    budget = data["maxError"]
    model = data["cultivationModel"]
    experiment = data["experiment"]
    qdk = build["qdkVersion"]

    lines = [
        "# Magic state cultivation scenario: a projection",
        "",
        "<!-- Generated by `python tooling/generate_estimates.py --scenario cultivation` from",
        "cultivation-scenario.json. Do not edit by hand: tooling/test_estimate_provenance.py fails",
        "when this file and the JSON disagree. -->",
        "",
        "**Every cultivation number on this page is a projection, not a published estimate.** It is",
        f"what the QRE v3 estimator in qdk {qdk} returns when the round-based distillation factory",
        "behind the published estimates is replaced by its model of magic state cultivation,",
        "`GSJ24Factory`. The published estimates are each problem's `circuits/estimate.json`. This",
        f"scenario does not change them, and its baseline columns for `{baseline_model}` are those",
        "estimates.",
        "",
        f"The cultivation model is {_join(model['authors'])}, \"{model['title']}\",",
        f"[arXiv:{model['arxiv']}]({model['url']}), which qdk implements from the authors' simulation",
        f"data ([Zenodo]({model['simulationData']})). On hardware, Rosenfeld et al.",
        f"([arXiv:{experiment['arxiv']}]({experiment['url']})) report: \"{experiment['quote']}\"",
        "That is the post-selected fidelity of a T state in a distance-3 color code, not of logical",
        "gates; grafting a cultivated state into a distance-5 surface code is a separate step in the",
        f"same paper. Google writes that \"{experiment['announcementQuote']}\"",
        f"([announcement]({experiment['announcement']})), and nothing here shows cultivation working",
        "at the scale these programs need.",
        "",
        "## How it was produced",
        "",
        f"- Generated {build['dateUtc']} from commit `{build['commit']}` with qdk {qdk}, estimator",
        f"  version `{build['estimatorVersion']}`.",
        f"- Each of the {n} programs is estimated from the entry expression of its published",
        "  estimate, on every gate-based qubit profile in `tooling/estimator_config.py`. The",
        f"  published estimates use `{baseline_model}` only; the baselines for the other profiles",
        "  come from the same run.",
        "- ISA queries:",
    ]
    for factory in (baseline_factory, *scenario):
        role = "baseline" if factory == baseline_factory else "cultivation"
        lines.append(f"  - {role}: `{factories[factory]['isaQuery']}`")
    lines += [
        "- The rest is the published method: the estimator's default trace transform, a total",
        f"  error budget of {budget:g} and the fewest-qubit point of each Pareto frontier.",
        "- Infeasible means the estimator returned an empty Pareto frontier: no configuration it",
        "  explored stayed within the error budget. Those results are recorded, not left out.",
        "- T-factory fraction is the share of physical qubits in magic-state factories. Brackets",
        "  give the ratio to the baseline on the same profile.",
    ]
    physical = sorted(
        {
            name
            for record in problems.values()
            for cells in record["profiles"].values()
            for factory in (baseline_factory, *scenario)
            for name in _physical_states(cells[factory])
        }
    )
    if physical:
        names = " and ".join(physical)
        lines += [
            f"- \"physical {names}\" marks results where the estimator took its {names} states",
            "  straight from the profile's physical gate instead of a factory: the program needs so",
            "  few that their error fits the budget. No factory is used; qdk still counts one factory",
            "  qubit for them, hence a T-factory fraction near zero.",
        ]

    lines += [
        "",
        "## What the estimator does at each profile",
        "",
        f"`GSJ24Factory` in qdk {qdk} ships simulation tables at physical error rates of",
        _join([_fmt_rate(r) for r in data["cultivationSimulatedErrorRates"]])
        + ". Matching the T states it offered at each profile against those tables gives:",
        "",
        "| Profile | Physical error rate | Table used | "
        + " | ".join(f"Lowest T-state error {_distance_label(f)}" for f in scenario)
        + " | "
        + " | ".join(f"Most T states within the budget {_distance_label(f)}" for f in scenario)
        + " |",
        "|---|---|---|" + "---:|" * (2 * len(scenario)),
    ]
    for name, profile in profiles.items():
        cultivation = profile["cultivation"]
        tables = sorted({c["simulatedErrorRate"] for c in cultivation.values() if c["simulatedErrorRate"]})
        lowest = [cultivation[f]["lowestTStateError"] for f in scenario]
        lines.append(
            f"| `{name}` | {_fmt_rate(profile['physicalErrorRate'])} | "
            + (", ".join(_fmt_rate(t) for t in tables) or "none")
            + " | "
            + " | ".join(f"{e:.2e}" if e else "none offered" for e in lowest)
            + " | "
            + " | ".join(f"{int(budget // e):,}" if e else "-" for e in lowest)
            + " |"
        )
    lines.append("")
    groups: dict[tuple, list[str]] = {}
    for name, profile in profiles.items():
        used = tuple(sorted({c["simulatedErrorRate"] or 0 for c in profile["cultivation"].values()}))
        groups.setdefault((profile["physicalErrorRate"], used), []).append(f"`{name}`")
    for (rate, used), names in groups.items():
        if used == (rate,):
            continue
        if 0 in used:
            lines.append(f"- {_join(names)} ({_fmt_rate(rate)}): the factory offered no T states, so it refuses.")
            continue
        table = max(used)
        lines.append(
            f"- {_join(names)} ({_fmt_rate(rate)}): the estimator neither refuses nor extrapolates."
            f" `GSJ24Factory` supplies the T states simulated at {_fmt_rate(table)}, the nearest"
            " tabulated rate above the profile's, so these rows take T states simulated at"
            f" {table / rate:g} times the profile's physical error rate."
        )
    lines += [
        "- The estimator adds error contributions, so N T states with error at least e use at least",
        "  N times e of the budget. A program that needs more T states than the last columns allow",
        "  cannot be feasible with that factory; the results tables give the baseline's T states.",
        "",
    ]

    toffoli = {name: p["toffoliCount"] for name, p in problems.items() if p["toffoliCount"]}
    combos, changes = 0, []
    for name in toffoli:
        for profile_name, cells in problems[name]["profiles"].items():
            for variant in (f for f in cells if f.endswith("+ccx")):
                base = variant.removesuffix("+ccx")
                combos += 1
                if not _same_point(cells[base], cells[variant]):
                    changes.append(
                        f"| {name} | `{profile_name}` | {_FACTORY_LABELS[base]} | "
                        + " | ".join(
                            f"{c['physicalQubits']:,}" if c["feasible"] else "infeasible"
                            for c in (cells[base], cells[variant])
                        )
                        + " |"
                    )
    ccx = [f for f in factories if f.endswith("+ccx")]
    heaviest = max(toffoli, key=toffoli.get) if toffoli else None
    lines += [
        "## Toffoli gates",
        "",
        f"{len(toffoli)} of the {n} programs contain Toffoli gates: "
        + _join([f"{name} ({count:,})" for name, count in toffoli.items()])
        + ". With `GSJ24Factory` alone, the estimator's default trace transform breaks each",
        "Toffoli into T states, so the results tables compose `SurfaceCode` with `GSJ24Factory`",
        "and nothing else.",
        "",
        "To find out whether these programs need a Toffoli factory as well, each was also estimated",
        "with `GSJ24CCXFactory`, qdk's model of turning eight T states into one CCX state, composed",
        "beside `GSJ24Factory`. The trace transform may then consume CCX states instead. The ISA",
        "queries were:",
        "",
        *[f"- `{factories[f]['isaQuery']}`" for f in ccx],
        "",
        f"Across the {combos} combinations of program, profile and distance, adding `GSJ24CCXFactory`",
        f"changed the fewest-qubit point in {len(changes)}."
        + (
            f" The program with the most Toffoli gates, {heaviest}, is "
            + ("" if any(f"| {heaviest} |" in c for c in changes) else "not ")
            + "among them."
            if heaviest
            else ""
        ),
    ]
    if changes:
        lines += [
            "",
            "Projection, physical qubits at the fewest-qubit point, where `GSJ24CCXFactory` changes it:",
            "",
            "| Program | Profile | Factory | Without GSJ24CCXFactory | With GSJ24CCXFactory |",
            "|---|---|---|---:|---:|",
            *changes,
        ]
    lines += ["", "## Results", ""]

    header = ["Problem", "Baseline qubits", "Baseline runtime", "Baseline T-factory fraction", "Baseline T states"]
    for factory in scenario:
        label = _distance_label(factory)
        header += [f"{label} qubits", f"{label} runtime", f"{label} T-factory fraction"]
    for name, profile in profiles.items():
        published = " Its baseline columns are the published estimates." if name == baseline_model else ""
        feasible = _join(
            [
                f"{_FACTORY_LABELS[f]} for {sum(p['profiles'][name][f]['feasible'] for p in problems.values())}"
                for f in scenario
            ]
        )
        lines += [
            f"### `{name}`: {profile['label']}",
            "",
            f"Projection on profile `{name}`: `GSJ24Factory` at each distance against the",
            f"`RoundBasedFactory` baseline on the same profile.{published} Feasible, of {n}: {feasible}.",
            "",
            "| " + " | ".join(header) + " |",
            "|---|" + "---:|" * (len(header) - 1),
        ]
        for problem, record in problems.items():
            cells = record["profiles"][name]
            base = cells[baseline_factory]
            t_states = base.get("magicStates", {}).get("T", {}).get("states")
            row = [problem, *_fmt_cell(base, None), f"{t_states:,}" if t_states else "-"]
            for factory in scenario:
                row += _fmt_cell(cells[factory], base)
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    timings: dict[tuple, list[str]] = {}
    for name, profile in profiles.items():
        gate, measure = profile["gateTimeNs"], profile["measurementTimeNs"]
        timings.setdefault((4 * gate, gate + 4 * gate + measure), []).append(f"`{name}`")
    lines += [
        "## Limits of this projection",
        "",
        "- Only the factory changes. The programs are the toy instances the published estimates",
        "  use, not utility-scale versions of the problems.",
        f"- qdk {qdk} times each cultivation step as four CNOT gate times, while the surface code",
        "  cycle it uses for the rest of the estimate also includes a single-qubit gate and a",
        "  measurement: "
        + "; ".join(
            f"{_fmt_runtime(step)} against {_fmt_runtime(cycle)} on {_join(names)}"
            for (step, cycle), names in timings.items()
        )
        + ". Runtimes and factory copy counts here inherit that choice.",
        "- The factory's T-state error rates and space-time volumes, including the overhead of",
        "  discarded attempts, come from the authors' simulations, not from hardware.",
        f"- {data['ties']}",
        "",
    ]
    return "\n".join(lines)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--scenario",
        choices=("cultivation",),
        help=(
            "write a labelled projection to docs/estimates/ instead of the published "
            "estimates, which are left untouched"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None):
    args = _parse_args(argv)
    if args.scenario == "cultivation":
        return cultivation_scenario()

    from qdk import qsharp

    problem_dirs = discover_all_problems()

    qdk_version = _qdk_version()
    commit = _git_commit()
    ok = 0
    fail = 0
    frontiers: dict[str, dict] = {}
    site_estimates: dict[str, dict] = {}

    for pd in problem_dirs:
        qsharp_dir = pd / "qsharp"
        circuits_dir = pd / "circuits"
        circuits_dir.mkdir(exist_ok=True)

        if not (qsharp_dir / "qsharp.json").exists():
            continue

        name = pd.name

        try:
            qsharp.init(project_root=str(qsharp_dir))
        except Exception as e:
            print(f"XX {name}: compile error -- {str(e)[:100]}")
            fail += 1
            continue

        ep = ENTRY_POINTS.get(name)
        if ep is None:
            print(f"-- {name}: no entry point mapped")
            continue

        try:
            summary = {
                "problem": name,
                # Records which program was estimated: a Main.* expression, the toy
                # instance compiled for fault tolerance (not a utility-scale version),
                # and not the smaller HardwareKernel that Azure Quantum runs, so estimate
                # figures and run histograms are not directly comparable.
                "entryExpr": ep.expr(),
                "estimateTarget": "Main",
                "hardwareKernelEntryPoint": kernel_entry_point(qsharp_dir),
                "qubitModel": DEFAULT_QUBIT_MODEL,
                "qecScheme": DEFAULT_QEC_SCHEME,
                # Provenance on the single source of truth. Without it, "was this
                # measured or invented?" is unanswerable from the artifact alone -
                # which is exactly how a fabricated constant survived in
                # problems/*/estimates/ for six months.
                "build": {
                    "commit": commit,
                    "qdkVersion": qdk_version,
                    "estimatorVersion": (
                        f"qdk-{qdk_version}/{DEFAULT_QUBIT_MODEL}+{DEFAULT_QEC_SCHEME}"
                    ),
                    "dateUtc": datetime.now(timezone.utc).isoformat(),
                },
                **estimate_summary(ep.expr(), DEFAULT_QUBIT_MODEL, DEFAULT_QEC_SCHEME),
            }

            out_path = circuits_dir / "estimate.json"
            out_path.write_text(
                json.dumps(summary, indent=2, default=str), encoding="utf-8"
            )

            pq = summary.get("physicalQubits", "?")
            lq = summary.get("logicalQubits", "?")
            tc = summary.get("tCount", "?")
            print(f"OK {name}: {pq} physical qubits, {lq} logical qubits, {tc} T-gates")
            ok += 1

            points = summary.get("paretoFrontier") or []
            if points:
                frontiers[name] = {
                    "qubitModel": DEFAULT_QUBIT_MODEL,
                    "qecScheme": DEFAULT_QEC_SCHEME,
                    "selected": "min-qubits",
                    "entryExpr": summary.get("entryExpr"),
                    "hardwareKernelEntryPoint": summary.get("hardwareKernelEntryPoint"),
                    "points": points,
                }

            # Flat map keyed by problem id: compare.tsx iterates Object.entries, so a
            # wrapper object would render as a phantom row.
            site_estimates[name] = {
                "physicalQubits": summary.get("physicalQubits"),
                "logicalQubits": summary.get("logicalQubits"),
                "tCount": summary.get("tCount"),
                "rotationCount": summary.get("rotationCount"),
                # Toffoli-class gates; each consumes a CCZ magic state like a T gate does.
                "cczCount": summary.get("cczCount"),
                "tFactoryFraction": summary.get("tFactoryFraction"),
                "runtime": summary.get("runtime"),
                "entryExpr": summary.get("entryExpr"),
                "qubitModel": DEFAULT_QUBIT_MODEL,
                "qecScheme": DEFAULT_QEC_SCHEME,
            }

        except Exception as e:
            err = str(e)[:150]
            print(f"XX {name}: {err}")
            fail += 1

    if frontiers:
        FRONTIERS_PATH.parent.mkdir(parents=True, exist_ok=True)
        FRONTIERS_PATH.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "generated_utc": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "maxError": 1e-3,
                    "problems": frontiers,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Frontiers for {len(frontiers)} problems -> {FRONTIERS_PATH.name}")

    if site_estimates:
        ESTIMATES_PATH.parent.mkdir(parents=True, exist_ok=True)
        ESTIMATES_PATH.write_text(
            json.dumps(site_estimates, indent=2, default=str), encoding="utf-8"
        )
        print(f"Estimates for {len(site_estimates)} problems -> {ESTIMATES_PATH.name}")

    print(f"\nDone: {ok} estimates generated, {fail} failed")


if __name__ == "__main__":
    sys.exit(main() or 0)
