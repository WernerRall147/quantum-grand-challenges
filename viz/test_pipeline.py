"""Behavioral checks; the optional Blender tests render actual PNGs and scenes."""

import hashlib
import copy
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import jsonschema
import pytest

from viz import build, data

ROOT = data.ROOT
SCHEMA = json.loads((ROOT / "viz" / "manifest.schema.json").read_text(encoding="utf-8"))


@pytest.fixture
def workdir():
    folder = ROOT / "viz" / "output" / "tests" / uuid.uuid4().hex
    folder.mkdir(parents=True)
    yield folder
    shutil.rmtree(folder)


@pytest.fixture
def matrix():
    return {
        "generated_utc": "2026-09-17T00:00:00Z",
        "records": [{
            "problem_id": "16_error_correction", "entry_point": "QECKernel",
            "execution": "local-simulator", "target_id": None, "status": "succeeded",
            "histogram": {"shots": 10, "counts": {"[Zero]": 8, "[One]": 2}},
        }],
    }


def test_all_twenty_estimates_match_source_and_keep_archival_status():
    catalog = data.build_catalog()
    jsonschema.validate(catalog, SCHEMA)
    assert len(catalog["problems"]) == 20
    assert len({p["id"] for p in catalog["problems"]}) == 20
    assert sum(p["archived"] for p in catalog["problems"]) == 11
    for problem in catalog["problems"]:
        estimate = problem["estimate"]
        path = ROOT / estimate["source"]["path"]
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert estimate["physical_qubits"] == raw["physicalQubits"]
        assert estimate["logical_qubits"] == raw["logicalQubits"]
        assert estimate["runtime_ns"] == raw["runtime"]
        assert estimate["source"]["sha256"] == hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert estimate["entry_point"] == raw["entryExpr"]
        assert estimate["build"] == raw["build"]
        if problem["run"]["status"] == "available":
            assert sum(r["count"] for r in problem["run"]["histogram"]) == problem["run"]["shots"]
        else:
            assert problem["run"]["shots"] is None
            assert problem["run"]["histogram"] == []


def test_prepare_cli_generates_schema_valid_deterministic_catalog(workdir):
    command = [sys.executable, "-m", "viz.build", "prepare", "--output", str(workdir)]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    manifest = workdir / "manifest.json"
    first = manifest.read_bytes()
    value = json.loads(first)
    jsonschema.validate(value, SCHEMA)
    assert len(value["problems"]) == 20
    assert all(p["render_status"] == "pending" and not p["assets"] for p in value["problems"])
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    assert manifest.read_bytes() == first


def test_null_and_zero_are_distinct_and_bad_estimates_are_rejected(workdir):
    path = workdir / "estimate.json"
    build.write_json(path, {"problem": "16_error_correction", "logicalQubits": 0})
    estimate = data.load_estimate(path, "16_error_correction")
    assert estimate["logical_qubits"] == 0
    assert estimate["physical_qubits"] is None
    assert estimate["runtime_ns"] is None
    with pytest.raises(ValueError, match="does not match"):
        data.load_estimate(path, "01_hubbard")
    assert data.load_estimate(workdir / "absent.json", "01_hubbard") is None


@pytest.mark.parametrize("invalid", [-1, True, "123", float("nan"), float("inf"), 1.5])
def test_invalid_qubit_counts_fail(invalid):
    with pytest.raises(ValueError, match="finite nonnegative integer"):
        data.number(invalid, "qubits", integer=True)


def test_successful_histogram_is_not_a_syntax_checker(matrix):
    run = data.select_run(matrix, "16_error_correction", "local-simulator", None)
    assert run["status"] == "available"
    assert run["source_generated_utc"] == matrix["generated_utc"]
    assert run["histogram"][0] == {"outcome": "[Zero]", "count": 8}
    record = matrix["records"][0]
    record.update(execution="azure", target_id="quantinuum.sim.h2-1sc")
    assert data.select_run(matrix, "16_error_correction", "local-simulator", None)["status"] == "missing"
    with pytest.raises(ValueError, match="syntax checkers"):
        data.select_run(matrix, "16_error_correction", "quantinuum.sim.h2-1sc", None)
    record.update(target_id="quantinuum.sim.h2-1e")
    emulator = data.select_run(matrix, "16_error_correction", "quantinuum.sim.h2-1e", None)
    assert emulator["execution"] == "cloud-simulator"
    record["status"] = "failed"
    assert data.select_run(matrix, "16_error_correction", "quantinuum.sim.h2-1e", None)["status"] == "missing"


@pytest.mark.parametrize("counts", [{"0": 8}, {"0": -1, "1": 11}, {"0": True, "1": 9}, {}])
def test_inconsistent_run_data_is_not_rendered(matrix, counts):
    matrix["records"][0]["histogram"]["counts"] = counts
    with pytest.raises(ValueError):
        data.select_run(matrix, "16_error_correction", "local-simulator", None)


def test_log_scale_and_other_bin_preserve_evidence():
    assert data.resource_height(None) == 0
    assert data.resource_height(0) == 0
    assert data.resource_height(99) == 2
    assert data.resource_height(1746) == pytest.approx(math.log10(1747))
    rows = [{"outcome": str(i), "count": 20 - i} for i in range(12)]
    bars = data.histogram_bars({"histogram": rows})
    assert len(bars) == 8
    assert bars[-1]["outcome"] == "Other (5 outcomes)"
    assert sum(r["count"] for r in bars) == sum(r["count"] for r in rows)
    assert bars[:7] == rows[:7]


def measured_run(counts):
    return {
        "status": "available", "execution": "local-simulator", "target": "local-simulator",
        "shots": sum(counts.values()),
        "histogram": [{"outcome": label, "count": count} for label, count in counts.items()],
    }


@pytest.mark.parametrize("counts, expected", [
    ({"[Zero]": 8, "[One]": 2}, (0.8, 0.2, 0.6)),
    ({"[Zero]": 5, "[One]": 5}, (0.5, 0.5, 0)),
    ({"[Zero]": 10, "[One]": 0}, (1, 0, 1)),
    ({"[One]": 10}, (0, 1, -1)),
    ({"Zero": 1, "One": 3}, (0.25, 0.75, -0.5)),
])
def test_z_marginal_is_a_frequency_not_an_amplitude_or_pure_state(counts, expected):
    result = data.z_marginal(measured_run(counts))
    assert (result["p0"], result["p1"], result["z"]) == pytest.approx(expected)
    assert result["x"] is None and result["y"] is None
    assert result["counts"] == {
        "0": counts.get("[Zero]", counts.get("Zero", 0)),
        "1": counts.get("[One]", counts.get("One", 0)),
    }
    assert result["measurement_width"] == 1
    assert "diagonal-state representation" in result["representation"]


def test_multiqubit_marginal_uses_selected_returned_bit_not_integer_endianness():
    run = measured_run({"[Zero, One]": 8, "[One, Zero]": 2})
    assert data.z_marginal(run, 0)["z"] == pytest.approx(0.6)
    assert data.z_marginal(run, 1)["z"] == pytest.approx(-0.6)
    result = data.z_marginal(run, 2)
    assert result["status"] == "unavailable"
    assert result["measurement_width"] == 2
    assert result["z"] is None and result["counts"] is None


def test_marginal_includes_every_outcome_before_other_bin_aggregation():
    counts = {
        "[" + ", ".join("One" if i & (1 << bit) else "Zero" for bit in range(4)) + "]": i + 1
        for i in range(16)
    }
    run = measured_run(counts)
    assert len(data.histogram_bars(run)) == 8
    result = data.z_marginal(run, 3)
    assert result["counts"] == {"0": 36, "1": 100}
    assert result["z"] == pytest.approx(-64 / 136)


@pytest.mark.parametrize("counts", [
    {"[Zero]": 2, "[One, Zero]": 3},
    {"Zero": 2, "[Zero]": 3},
    {"[Zero]": 2, "[ Zero ]": 3},
    {"[Zero]": -1, "[One]": 11},
    {"[Zero]": True, "[One]": 9},
    {"[Zero]": 2.5, "[One]": 7.5},
    {},
])
def test_invalid_marginal_evidence_is_rejected(counts):
    with pytest.raises(ValueError):
        data.z_marginal(measured_run(counts))


@pytest.mark.parametrize("label", [
    "01", "0", "[0, 1]", "[]", "[Zero,]", "[Zero, Two]", "(Zero, One)",
    "Other (2 outcomes)", "[Zero, [One]]", "|+>",
])
def test_unknown_or_aggregated_outcomes_never_fabricate_a_state(label):
    result = data.z_marginal(measured_run({label: 10}))
    assert result["status"] == "unavailable"
    for field in ("p0", "p1", "x", "y", "z", "counts"):
        assert result[field] is None


def test_incomplete_histograms_and_missing_evidence_are_not_zero_polarization():
    run = measured_run({"[Zero]": 8, "[One]": 2})
    run["shots"] = 11
    with pytest.raises(ValueError, match="partial marginal"):
        data.z_marginal(run)
    run["histogram"] *= 2
    with pytest.raises(ValueError, match="duplicate"):
        data.z_marginal(run)
    missing = {"status": "missing", "histogram": [], "shots": None}
    result = data.z_marginal(missing)
    assert result["z"] is None and result["status"] == "unavailable"
    with pytest.raises(ValueError, match="Missing run"):
        data.z_marginal({**missing, "shots": 0})
    cloud = measured_run({"[Zero]": 10})
    cloud.update(execution="cloud-simulator", target="ionq.simulator")
    assert data.z_marginal(cloud)["z"] is None


@pytest.mark.parametrize("bit", [-1, True, 0.5, "0", None])
def test_invalid_measurement_index_is_rejected(bit):
    with pytest.raises(ValueError, match="nonnegative integer"):
        data.z_marginal(measured_run({"[Zero]": 10}), bit)


@pytest.mark.parametrize("mutation", ["x", "y", "sign", "pure", "evidence", "segment", "label"])
def test_publisher_rejects_fabricated_or_miscomputed_bloch_report(mutation):
    evidence = data.z_marginal(measured_run({"[Zero]": 8, "[One]": 2}))
    report = {
        "labels": [data.BLOCH_LABEL, data.BLOCH_CONVENTION, data.BLOCH_LIMITATION],
        "bloch": {
            "evidence": copy.deepcopy(evidence),
            "geometry": {"marker": [0, 0, 0.6], "segment": [[0, 0, 0], [0, 0, 0.6]]},
        },
    }
    build.verify_bloch_report(report, evidence)
    geometry = report["bloch"]["geometry"]
    if mutation == "x":
        geometry["marker"][0] = 0.8  # Fabricated coherence from sqrt(1 - z*z).
    elif mutation == "y":
        geometry["marker"][1] = 0.8
    elif mutation == "sign":
        geometry["marker"][2] = -0.6
    elif mutation == "pure":
        geometry["marker"][2] = 1
    elif mutation == "evidence":
        report["bloch"]["evidence"]["x"] = 0
    elif mutation == "segment":
        geometry["segment"][1][2] = 1
    else:
        report["labels"].remove(data.BLOCH_CONVENTION)
    with pytest.raises(ValueError, match="Bloch"):
        build.verify_bloch_report(report, evidence)


@pytest.mark.parametrize("options", [
    ["--problem", "does_not_exist"], ["--width", "0"],
    ["--target", "quantinuum.sim.h2-1sc"], ["--runs", "not-a-run-source.json"],
    ["--bloch-bit", "-1"],
])
def test_invalid_cli_options_do_not_publish(workdir, options):
    assert build.main(["prepare", "--output", str(workdir), *options]) == 1
    assert not (workdir / "manifest.json").exists()


def test_zero_exit_without_artifacts_does_not_publish_or_replace_manifest(workdir, monkeypatch):
    manifest = workdir / "manifest.json"
    manifest.write_text("previous manifest", encoding="utf-8")
    monkeypatch.setattr(build.shutil, "which", lambda value: "fake-blender")
    monkeypatch.setattr(
        build.subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess([], 0, stdout="", stderr=""),
    )
    assert build.main(["render", "--output", str(workdir)]) == 1
    assert manifest.read_text(encoding="utf-8") == "previous manifest"


def test_missing_blender_does_not_claim_render_success(workdir, monkeypatch):
    monkeypatch.setattr(build.shutil, "which", lambda value: None)
    assert build.main(["render", "--output", str(workdir)]) == 1
    assert not (workdir / "manifest.json").exists()


def test_corrupted_png_is_rejected(workdir):
    path = workdir / "invalid.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n")
    with pytest.raises(ValueError):
        build.verify_png(path, 640, 400)


def test_rendered_asset_is_required_by_contract():
    catalog = data.build_catalog()
    catalog["problems"][0]["render_status"] = "rendered"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(catalog, SCHEMA)


def test_published_manifest_references_real_matching_posters():
    manifest = json.loads((ROOT / "viz" / "manifest.json").read_text(encoding="utf-8"))
    jsonschema.validate(manifest, SCHEMA)
    assert {p["id"] for p in manifest["problems"]} == {p["id"] for p in data.build_catalog()["problems"]}
    for problem in manifest["problems"]:
        for asset in problem["assets"]:
            poster = ROOT / "viz" / asset["path"]
            build.verify_png(poster, asset["width"], asset["height"])
            assert hashlib.sha256(poster.read_bytes()).hexdigest() == asset["sha256"]
            assert "Bloch panel, returned bit " in asset["alt"]


def assert_bloch_geometry(report, expected_z):
    geometry = report["bloch"]["geometry"]
    assert len(geometry["rings"]) == 3
    for normal, points in enumerate(geometry["rings"]):
        assert len(points) == 96
        for point in points:
            assert sum(v * v for v in point) == pytest.approx(1, abs=1e-6)
            assert point[normal] == pytest.approx(0)
    for i, axis in enumerate("xyz"):
        end = [0.0, 0.0, 0.0]
        end[i] = 1
        assert geometry["axes"][axis] == [[-v for v in end], end]
    assert geometry["frame_scale"] == pytest.approx([0.85] * 3)
    if expected_z is None:
        assert geometry["marker"] is None and geometry["segment"] is None
        assert "Z unavailable / no marker" in report["labels"]
    else:
        assert geometry["marker"] == pytest.approx([0, 0, expected_z], abs=1e-6)
        if expected_z == 0:
            assert geometry["segment"] is None
        else:
            assert geometry["segment"][0] == [0, 0, 0]
            assert geometry["segment"][1] == pytest.approx([0, 0, expected_z], abs=1e-6)
        assert f"z = P(0) - P(1) = {expected_z:+.3f}" in report["labels"]
    assert {data.BLOCH_LABEL, data.BLOCH_CONVENTION, data.BLOCH_LIMITATION,
            "Diagonal-state representation only", "Z +1 / |0>", "Z -1 / |1>"
            }.issubset(report["labels"])
    assert report["bloch"]["evidence"]["x"] is None
    assert report["bloch"]["evidence"]["y"] is None


@pytest.mark.parametrize("problem_id, bit", [
    ("16_error_correction", 0), ("03_qae_risk", 0), ("01_hubbard", 1),
])
def test_real_blender_render_contains_the_evidence(workdir, problem_id, bit):
    blender = shutil.which(os.environ.get("BLENDER", "blender"))
    if not blender:
        pytest.skip("Set BLENDER to run the actual Blender integration tests")
    assert build.main([
        "render", "--problem", problem_id, "--output", str(workdir),
        "--blender", blender, "--width", "640", "--height", "400", "--samples", "2",
        "--bloch-bit", str(bit),
    ]) == 0
    manifest = json.loads((workdir / "manifest.json").read_text(encoding="utf-8"))
    jsonschema.validate(manifest, SCHEMA)
    problem = next(p for p in manifest["problems"] if p["id"] == problem_id)
    asset = problem["assets"][0]
    poster = workdir / asset["path"]
    build.verify_png(poster, 640, 400)
    assert hashlib.sha256(poster.read_bytes()).hexdigest() == asset["sha256"]
    report = json.loads((poster.parent / "render-report.json").read_text(encoding="utf-8"))
    for field in ["logical_qubits", "physical_qubits"]:
        value = problem["estimate"][field]
        assert report["resource_bars"][field]["value"] == value
        assert report["resource_bars"][field]["height"] == pytest.approx(0.65 * math.log10(1 + value))
    if problem["run"]["status"] == "available":
        assert sum(report["histogram_counts"].values()) == problem["run"]["shots"]
        assert problem["run"]["entry_point"] in report["labels"]
    else:
        assert report["histogram_counts"] == {}
        assert "No matching simulator run" in report["labels"]
    if problem["archived"]:
        assert f"ARCHIVED | Stage {problem['stage']}" in report["labels"]
    expected_z = None
    if problem["run"]["status"] == "available":
        n0 = sum(
            row["count"] for row in problem["run"]["histogram"]
            if row["outcome"][1:-1].split(",")[bit].strip() == "Zero"
        )
        expected_z = (2 * n0 - problem["run"]["shots"]) / problem["run"]["shots"]
    assert_bloch_geometry(report, expected_z)
    assert f"returned bit {bit}" in asset["alt"]
    bad = workdir / "corrupt.png"
    damaged = bytearray(poster.read_bytes())
    damaged[len(damaged) // 2] ^= 1
    bad.write_bytes(damaged)
    with pytest.raises(ValueError, match="corrupt PNG"):
        build.verify_png(bad, 640, 400)


@pytest.mark.parametrize("counts, bit, expected_z", [
    ({"[Zero, One]": 10}, 1, -1),
    ({"[One, Zero]": 10}, 1, 1),
    ({"[Zero, One]": 5, "[One, Zero]": 5}, 1, 0),
    ({"ambiguous": 10}, 0, None),
    ({"[Zero]": 10}, 1, None),
])
def test_real_blender_edge_cases_do_not_invent_vectors(workdir, counts, bit, expected_z):
    blender = shutil.which(os.environ.get("BLENDER", "blender"))
    if not blender:
        pytest.skip("Set BLENDER to run the actual Blender integration tests")
    problem = next(p for p in data.build_catalog()["problems"] if p["id"] == "16_error_correction")
    problem["run"].update(measured_run(counts))
    result = build.render_problem(problem, workdir, blender, 640, 400, 2, 120, bit)
    poster = workdir / result["assets"][0]["path"]
    report = json.loads((poster.parent / "render-report.json").read_text(encoding="utf-8"))
    assert_bloch_geometry(report, expected_z)
    if expected_z is None:
        report["bloch"]["geometry"]["marker"] = [0, 0, 0]
        with pytest.raises(ValueError, match="must not have a marker"):
            build.verify_bloch_report(report, data.z_marginal(problem["run"], bit))
