"""Normalize checked-in evidence without estimating or simulating anything."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re

from tooling.discover_problems import discover_all_problems

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS = ROOT / "website" / "data" / "simulatorMatrix.json"
DISCLAIMER = (
    "Resource estimates and sampled kernel outcomes describe different programs. "
    "Neither demonstrates quantum advantage; this is not a quantum-state animation."
)
SIMULATORS = {"quantinuum.sim.h2-1e", "rigetti.sim.qvm", "ionq.simulator"}
BLOCH_LABEL = "Measurement-derived Z polarization"
BLOCH_CONVENTION = "X/Y unknown; drawn as 0 by convention"
BLOCH_LIMITATION = "Phase unavailable; not state tomography"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source(path: Path) -> dict:
    return {
        "path": path.resolve().relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def number(value, field: str, *, integer: bool = False):
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
        or (integer and not isinstance(value, int))
    ):
        raise ValueError(f"{field} must be a finite nonnegative {'integer' if integer else 'number'}")
    return value


def load_estimate(path: Path, problem_id: str) -> dict | None:
    if not path.is_file():
        return None
    raw = read_json(path)
    if raw.get("problem") != problem_id:
        raise ValueError(f"{path}: estimate problem does not match {problem_id}")
    return {
        "source": source(path),
        "entry_point": raw.get("entryExpr"),
        "target": raw.get("estimateTarget"),
        "qubit_model": raw.get("qubitModel"),
        "qec_scheme": raw.get("qecScheme"),
        "build": raw.get("build"),
        "logical_qubits": number(raw.get("logicalQubits"), "logicalQubits", integer=True),
        "physical_qubits": number(raw.get("physicalQubits"), "physicalQubits", integer=True),
        "runtime_ns": number(raw.get("runtime"), "runtime"),
    }


def select_run(document: dict, problem_id: str, target: str, provenance: dict | None) -> dict:
    empty = {
        "status": "missing", "source": provenance,
        "source_generated_utc": document.get("generated_utc") or document.get("updated_utc"),
        "execution": None, "target": None, "entry_point": None,
        "shots": None, "histogram": [],
    }
    if target != "local-simulator" and target not in SIMULATORS:
        raise ValueError(f"Unsupported run target {target!r}; syntax checkers are not physics data")
    candidates = [
        r for r in document.get("records", [])
        if r.get("problem_id") == problem_id
        and r.get("status") == "succeeded"
        and (
            (target == "local-simulator" and r.get("execution") == target and not r.get("target_id"))
            or (target in SIMULATORS and r.get("target_id") == target)
        )
    ]
    if not candidates:
        return empty
    raw = candidates[-1]
    hist = raw.get("histogram") or {}
    shots = number(hist.get("shots"), "shots", integer=True)
    counts = hist.get("counts")
    if not shots or not isinstance(counts, dict) or not counts:
        raise ValueError(f"{problem_id}: successful run has no usable histogram")
    for label, count in counts.items():
        if not isinstance(label, str) or not label or number(count, "count", integer=True) is None:
            raise ValueError(f"{problem_id}: invalid histogram bin")
    if sum(counts.values()) != shots:
        raise ValueError(f"{problem_id}: histogram counts do not sum to shots")
    if not raw.get("entry_point"):
        raise ValueError(f"{problem_id}: run entry_point is required")
    return {
        **empty, "status": "available",
        "execution": "local-simulator" if target == "local-simulator" else "cloud-simulator",
        "target": target, "entry_point": raw["entry_point"], "shots": shots,
        "histogram": [
            {"outcome": label, "count": count}
            for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ],
    }


def histogram_bars(run: dict, limit: int = 8) -> list[dict]:
    """Keep every shot: combine the tail into an explicitly labelled Other bin."""
    rows = run["histogram"]
    if len(rows) <= limit:
        return rows
    return rows[:limit - 1] + [{
        "outcome": f"Other ({len(rows) - limit + 1} outcomes)",
        "count": sum(row["count"] for row in rows[limit - 1:]),
    }]


def z_marginal(run: dict, bit: int = 0) -> dict:
    """Empirical marginal of a returned Z-measurement, never a reconstructed state.

    Only the local Q# Result/Result[] encoding has a known output order here.
    Index zero is the first returned result, not a register-endianness assertion
    or a physical-qubit identifier. Sum the full histogram before bar aggregation.
    """
    if isinstance(bit, bool) or not isinstance(bit, int) or bit < 0:
        raise ValueError("Bloch bit must be a nonnegative integer")
    unavailable = {
        "status": "unavailable", "reason": None, "bit": bit,
        "measurement_width": None, "shots": None, "counts": None,
        "p0": None, "p1": None, "z": None, "x": None, "y": None,
        "representation": "measurement-derived diagonal-state representation",
    }
    if run.get("status") == "missing":
        if run.get("histogram") or run.get("shots") is not None:
            raise ValueError("Missing run must not carry histogram evidence")
        return {**unavailable, "reason": "No matching simulator run"}
    if run.get("status") != "available":
        raise ValueError("Unknown run status")
    shots = number(run.get("shots"), "shots", integer=True)
    rows = run.get("histogram")
    if not shots or not isinstance(rows, list) or not rows:
        raise ValueError("Z marginal requires a complete nonempty histogram")
    seen, total = set(), 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid histogram bin")
        label, count = row.get("outcome"), row.get("count")
        if not isinstance(label, str) or not label or label in seen:
            raise ValueError("Invalid or duplicate histogram outcome")
        seen.add(label)
        if number(count, "count", integer=True) is None:
            raise ValueError("Missing histogram count")
        total += count
    if total != shots:
        raise ValueError("Histogram counts do not sum to shots; no partial marginal")
    if run.get("execution") != "local-simulator" or run.get("target") != "local-simulator":
        return {**unavailable, "reason": "Provider basis / result order not established"}
    parsed = []
    for row in rows:
        label = row["outcome"].strip()
        if label in ("Zero", "One"):
            bits = (int(label == "One"),)
        elif re.fullmatch(r"\[\s*(?:Zero|One)(?:\s*,\s*(?:Zero|One))*\s*\]", label):
            bits = tuple(int(token.strip() == "One") for token in label[1:-1].split(","))
        else:
            return {**unavailable, "reason": "Outcome encoding is not Q# Result / Result[]"}
        parsed.append((bits, row["count"]))
    widths = {len(bits) for bits, _ in parsed}
    if len(widths) != 1:
        raise ValueError("Inconsistent measurement widths; no Z marginal")
    if len({bits for bits, _ in parsed}) != len(parsed):
        raise ValueError("Duplicate decoded measurement outcome")
    width = widths.pop()
    if bit >= width:
        return {**unavailable, "measurement_width": width,
                "reason": f"Returned bit {bit} absent (width {width})"}
    n0 = sum(count for bits, count in parsed if bits[bit] == 0)
    n1 = shots - n0
    return {
        **unavailable, "status": "available", "measurement_width": width,
        "shots": shots, "counts": {"0": n0, "1": n1},
        "p0": n0 / shots, "p1": n1 / shots, "z": (n0 - n1) / shots,
    }


def bloch_alt(marginal: dict) -> str:
    prefix = f"Bloch panel, returned bit {marginal['bit']} (zero-based result order): "
    if marginal["status"] == "unavailable":
        return prefix + f"unavailable ({marginal['reason']}); no marker. "
    return (
        prefix + f"{BLOCH_LABEL.lower()}, z = {marginal['z']:.6g}, "
        f"P(0) = {marginal['p0']:.6g}, P(1) = {marginal['p1']:.6g}. "
        f"Diagonal-state representation; {BLOCH_CONVENTION.lower()}. "
        f"{BLOCH_LIMITATION}. "
    )


def resource_height(value: int | None) -> float:
    """One scene unit per log10(1 + qubits), not one object per physical qubit."""
    return 0.0 if value is None else math.log10(1 + value)


def build_catalog(runs_path: Path = DEFAULT_RUNS, target: str = "local-simulator") -> dict:
    metadata_path = ROOT / "docs" / "objective-kpis.json"
    stages = {r["problem"]: r["stage"] for r in read_json(metadata_path)["records"]}
    document = read_json(runs_path) if runs_path.is_file() else {"records": []}
    if not isinstance(document, dict) or not isinstance(document.get("records"), list):
        raise ValueError("Run input must use simulatorMatrix.json's records format")
    provenance = source(runs_path) if runs_path.is_file() else None
    problems = []
    for directory in discover_all_problems():
        estimate = load_estimate(directory / "circuits" / "estimate.json", directory.name)
        run = select_run(document, directory.name, target, provenance)
        warnings = [DISCLAIMER]
        if estimate is None:
            warnings.append("Resource estimate unavailable; missing values are not zero.")
        elif not estimate["build"]:
            warnings.append("Estimate build provenance unavailable.")
        if run["status"] == "missing":
            warnings.append(f"No successful {target} histogram in the selected run source.")
        archived = directory.parent.name == "archived"
        if archived:
            warnings.append("Archived problem; not an active quantum-advantage candidate.")
        problems.append({
            "id": directory.name,
            "title": directory.name.split("_", 1)[1].replace("_", " ").title(),
            "archived": archived, "stage": stages.get(directory.name, "Unknown"),
            "metadata_source": source(metadata_path),
            "estimate": estimate, "run": run, "warnings": warnings,
            "render_status": "pending", "assets": [],
        })
    ids = [p["id"] for p in problems]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate active/archived problem IDs")
    return {"schema_version": "1.0", "description": DISCLAIMER, "problems": problems}
