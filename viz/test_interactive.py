"""Check delivered evidence and local assets, not just successful process exits."""

import copy
from html.parser import HTMLParser
import json
import re
import shutil
import subprocess
import uuid

import pytest

from viz import build, data, interactive


@pytest.fixture
def workdir():
    folder = data.ROOT / "viz" / "output" / "tests" / uuid.uuid4().hex
    folder.mkdir(parents=True)
    yield folder
    shutil.rmtree(folder)


def decode_script(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith(interactive.DATA_PREFIX) and text.endswith(";\n")
    return json.loads(text[len(interactive.DATA_PREFIX):-2])


def assert_marginals_match_full_counts(document):
    """Independent oracle: do not call z_marginal to calculate the expected sign."""
    for problem in document["problems"]:
        for bit, marginal in enumerate(problem["marginals"]):
            assert marginal["x"] is None and marginal["y"] is None
            assert "amplitudes" not in marginal and "phase" not in marginal
            if marginal["status"] == "unavailable":
                assert marginal["reason"]
                assert all(marginal[key] is None for key in ("z", "p0", "p1", "counts", "shots"))
                continue
            rows = problem["run"]["histogram"]
            n0 = sum(row["count"] for row in rows
                     if row["outcome"].strip("[] ").split(",")[bit].strip() == "Zero")
            n1 = problem["run"]["shots"] - n0
            assert marginal["counts"] == {"0": n0, "1": n1}
            assert marginal["z"] == pytest.approx((n0 - n1) / (n0 + n1))
            assert marginal["p0"] == pytest.approx(n0 / (n0 + n1))
            assert marginal["p1"] == pytest.approx(n1 / (n0 + n1))


def test_delivered_data_matches_all_twenty_problems_and_trusted_sources():
    catalog = data.build_catalog()
    script = interactive.ASSETS / "evidence.js"
    assert script.read_text(encoding="utf-8") == interactive.data_script(catalog)
    document = decode_script(script)
    manifest = data.read_json(data.ROOT / "viz" / "manifest.json")
    assert len(document["problems"]) == 20
    assert {p["id"] for p in document["problems"]} == {p["id"] for p in manifest["problems"]}
    assert sum(p["archived"] for p in document["problems"]) == 11
    assert_marginals_match_full_counts(document)
    for p, original in zip(document["problems"], catalog["problems"]):
        assert p["run"] == original["run"]
        assert len(p["marginals"]) == (p["measurement_width"] or 1)
        if p["measurement_width"] is None:
            assert p["marginals"][0]["status"] == "unavailable"


def catalog_with_run(run):
    catalog = data.build_catalog()
    catalog["problems"] = [catalog["problems"][0]]
    catalog["problems"][0]["run"] = run
    return catalog


def test_every_returned_bit_uses_ungrouped_histogram_and_recorded_order():
    counts = {
        "[" + ", ".join("One" if i & (1 << bit) else "Zero" for bit in range(4)) + "]": i + 1
        for i in range(16)
    }
    run = {
        "status": "available", "execution": "local-simulator", "target": "local-simulator",
        "shots": sum(counts.values()),
        "histogram": [{"outcome": label, "count": count} for label, count in counts.items()],
    }
    document = interactive.viewer_data(catalog_with_run(run))
    marginals = document["problems"][0]["marginals"]
    assert len(marginals) == 4
    assert len(data.histogram_bars(run)) == 8
    assert marginals[3]["counts"] == {"0": 36, "1": 100}
    assert marginals[3]["z"] == pytest.approx(-64 / 136)
    assert_marginals_match_full_counts(document)


@pytest.mark.parametrize("kind", ["missing", "cloud", "encoding"])
def test_unsupported_evidence_has_no_numeric_state(kind):
    run = {
        "status": "available", "execution": "local-simulator", "target": "local-simulator",
        "shots": 10, "histogram": [{"outcome": "[Zero]", "count": 10}],
    }
    if kind == "missing":
        run.update(status="missing", shots=None, histogram=[])
    elif kind == "cloud":
        run.update(execution="cloud-simulator", target="ionq.simulator")
    else:
        run["histogram"][0]["outcome"] = "[0]"
    document = interactive.viewer_data(catalog_with_run(run))
    problem = document["problems"][0]
    assert problem["measurement_width"] is None
    assert problem["marginals"][0]["status"] == "unavailable"
    assert_marginals_match_full_counts(document)


@pytest.mark.parametrize("mutation", ["sign", "transverse", "amplitudes"])
def test_independent_oracle_really_rejects_corrupted_evidence(mutation):
    document = interactive.viewer_data(data.build_catalog())
    assert_marginals_match_full_counts(document)
    corrupt = copy.deepcopy(document)
    m = next(m for p in corrupt["problems"] for m in p["marginals"] if m["z"])
    if mutation == "sign":
        m["z"] *= -1
    elif mutation == "transverse":
        m["x"] = (1 - m["z"] ** 2) ** .5
    else:
        m["amplitudes"] = [m["p0"] ** .5, m["p1"] ** .5]
    with pytest.raises(AssertionError):
        assert_marginals_match_full_counts(corrupt)


def test_interactive_cli_is_deterministic_and_does_not_replace_manifest(workdir):
    manifest = workdir / "manifest.json"
    manifest.write_text("previous rendered manifest", encoding="utf-8")
    args = ["interactive", "--output", str(workdir)]
    assert build.main(args) == 0
    destination = workdir / "interactive"
    first = (destination / "evidence.js").read_bytes()
    assert_marginals_match_full_counts(decode_script(destination / "evidence.js"))
    for name in interactive.STATIC_FILES:
        assert (destination / name).read_bytes() == (interactive.ASSETS / name).read_bytes()
    assert build.main(args) == 0
    assert first == (destination / "evidence.js").read_bytes()
    assert manifest.read_text(encoding="utf-8") == "previous rendered manifest"


def test_bad_evidence_fails_before_publication(workdir):
    destination = interactive.publish_viewer(data.build_catalog(), workdir)
    previous = (destination / "evidence.js").read_bytes()
    catalog = data.build_catalog()
    catalog["problems"][0]["run"]["shots"] += 1
    with pytest.raises(ValueError, match="partial marginal"):
        interactive.publish_viewer(catalog, workdir)
    assert (destination / "evidence.js").read_bytes() == previous


@pytest.mark.parametrize("options", [["--port", "-1"], ["--port", "65536"], ["--target", "quantinuum.sim.h2-1sc"]])
def test_invalid_interactive_options_publish_nothing(workdir, options):
    assert build.main(["interactive", "--output", str(workdir), *options]) == 1
    assert not (workdir / "interactive").exists()


def test_script_escapes_labels_and_preserves_json_values(workdir):
    catalog = data.build_catalog()
    label = '</script><script>alert("not executable")</script>&'
    catalog["problems"][0]["title"] = label
    destination = interactive.publish_viewer(catalog, workdir)
    assert "<" not in (destination / "evidence.js").read_text(encoding="utf-8")
    assert decode_script(destination / "evidence.js")["problems"][0]["title"] == label


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


def test_static_assets_have_no_external_dependencies_and_accessible_controls():
    page = Page((interactive.ASSETS / "index.html").read_text(encoding="utf-8"))
    ids = [attrs["id"] for _, attrs in page.nodes if "id" in attrs]
    assert len(ids) == len(set(ids))
    required = {
        "problem", "bit", "evidence-mode", "explore-mode", "sphere", "mode-note",
        "initial-state", "initial-theta", "initial-phi", "rotation-axis", "axis-x", "axis-y",
        "axis-z", "rotation-angle", "undo", "reset-state", "export", "amplitudes",
        "read-x", "read-y", "read-z", "read-theta", "read-phi", "fatal",
    }
    assert required <= set(ids)
    assert {attrs["data-gate"] for _, attrs in page.nodes if "data-gate" in attrs} == {
        "X", "Y", "Z", "H", "S", "Sdg", "T", "Tdg",
    }
    for tag, attrs in page.nodes:
        if tag == "script" or tag == "link":
            path = attrs.get("src", attrs.get("href"))
            assert ":" not in path and not path.startswith(("/", "\\"))
            assert (interactive.ASSETS / path).is_file()
        if tag in ("input", "select"):
            assert any(t == "label" and a.get("for") == attrs["id"] for t, a in page.nodes)
        if tag == "canvas":
            assert attrs["tabindex"] == "0" and attrs["aria-describedby"]
    assert [attrs["src"] for tag, attrs in page.nodes if tag == "script"] == [
        "evidence.js", "bloch.js", "app.js",
    ]
    assert any(attrs.get("role") == "status" and attrs.get("aria-live") == "polite" for _, attrs in page.nodes)
    css = (interactive.ASSETS / "style.css").read_text(encoding="utf-8")
    assert ":focus-visible" in css and "prefers-reduced-motion" in css
    assert "url(" not in css and "@import" not in css


def test_node_behavioral_suite():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is needed for the JavaScript behavioral checks")
    completed = subprocess.run(
        [node, "--test", "--test-reporter=tap", str(data.ROOT / "viz" / "test_interactive.js")],
        cwd=data.ROOT, capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "# fail 0" in completed.stdout
    assert re.search(r"(?m)^# pass [1-9]\d*$", completed.stdout), completed.stdout
