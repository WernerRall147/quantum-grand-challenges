"""Publish a dependency-free local viewer using the Blender pipeline's evidence."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import webbrowser

from viz.data import ROOT, z_marginal

ASSETS = ROOT / "viz" / "interactive"
STATIC_FILES = ("index.html", "style.css", "bloch.js", "app.js")
DATA_PREFIX = "globalThis.BLOCH_EVIDENCE = "


def viewer_data(catalog: dict) -> dict:
    """Derive every returned-bit marginal before histogram display aggregation."""
    problems = []
    for problem in catalog["problems"]:
        first = z_marginal(problem["run"])
        width = first["measurement_width"]
        marginals = [first] if width is None else [
            z_marginal(problem["run"], bit) for bit in range(width)
        ]
        problems.append({
            key: problem[key]
            for key in ("id", "title", "stage", "archived", "metadata_source", "run", "warnings")
        } | {"measurement_width": width, "marginals": marginals})
    if not problems or len({p["id"] for p in problems}) != len(problems):
        raise ValueError("Viewer requires a nonempty catalog with unique problem IDs")
    return {
        "schema_version": "1.0",
        "kind": "qgc-bloch-evidence",
        "description": (
            "Empirical computational-basis frequencies, not tomography. "
            "X, Y and phase are unknown. Marker (0, 0, z) is a diagonal-state "
            "display convention, not a reconstruction of the original state. "
            "Exploration is an independent user-created pure state, never run evidence."
        ),
        "problems": problems,
    }


def data_script(catalog: dict) -> str:
    # Classic external scripts work on file:// without fetch or module CORS.
    payload = json.dumps(viewer_data(catalog), indent=2, ensure_ascii=True, allow_nan=False)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return DATA_PREFIX + payload + ";\n"


def publish_viewer(catalog: dict, output: Path) -> Path:
    script = data_script(catalog)  # Validate all evidence before writing anything.
    destination = output / "interactive"
    assets = {name: (ASSETS / name).read_bytes() for name in STATIC_FILES}
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in assets.items():
        if (destination / name).resolve() != (ASSETS / name).resolve():
            (destination / name).write_bytes(content)
    pending = destination / "evidence.pending.js"
    pending.write_text(script, encoding="utf-8")
    pending.replace(destination / "evidence.js")
    return destination


def serve_viewer(directory: Path, port: int, open_browser: bool = False) -> None:
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    # Bind only to loopback, and expose only the generated artifact, not the repo.
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        url = f"http://127.0.0.1:{server.server_port}/"
        print(f"Bloch viewer: {url} (Ctrl+C to stop)", flush=True)
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
