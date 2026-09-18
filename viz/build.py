"""Prepare evidence, render with Blender, or build a standalone interactive viewer."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import uuid
import zlib

from viz.data import (
    ROOT, DEFAULT_RUNS, BLOCH_LABEL, BLOCH_CONVENTION, BLOCH_LIMITATION,
    bloch_alt, build_catalog, z_marginal,
)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def verify_png(path: Path, width: int, height: int) -> None:
    """Check decoded image data, not just a successful Blender exit or a filename."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    offset, pixels, found_end = 8, bytearray(), False
    found_header = False
    while offset + 12 <= len(data):
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + size]
        crc = data[offset + 8 + size:offset + 12 + size]
        if len(crc) != 4 or zlib.crc32(kind + payload) != struct.unpack(">I", crc)[0]:
            raise ValueError(f"{path}: corrupt PNG chunk")
        if kind == b"IHDR":
            if len(payload) != 13 or struct.unpack(">II", payload[:8]) != (width, height):
                raise ValueError(f"{path}: wrong image dimensions")
            found_header = True
        elif kind == b"IDAT":
            pixels.extend(payload)
        elif kind == b"IEND":
            found_end = True
            break
        offset += size + 12
    decoded = zlib.decompress(pixels) if pixels else b""
    if not found_header or not found_end or not decoded or len(set(decoded)) < 3:
        raise ValueError(f"{path}: empty or incomplete rendered image")


def verify_bloch_report(report: dict, expected: dict) -> None:
    """Reject fabricated components or a marker that disagrees with shot evidence."""
    panel = report.get("bloch", {})
    if panel.get("evidence") != expected:
        raise ValueError("Bloch report does not match measurement evidence")
    if not {BLOCH_LABEL, BLOCH_CONVENTION, BLOCH_LIMITATION}.issubset(report.get("labels", [])):
        raise ValueError("Bloch limitations are missing from rendered labels")
    geometry = panel.get("geometry", {})
    marker, segment = geometry.get("marker"), geometry.get("segment")
    if expected["status"] == "unavailable":
        if marker is not None or segment is not None:
            raise ValueError("Unavailable Bloch evidence must not have a marker")
        if expected["reason"] not in report["labels"]:
            raise ValueError("Bloch unavailable reason is missing")
        return
    endpoint = [0.0, 0.0, expected["z"]]

    def close(actual, wanted):
        return isinstance(actual, list) and len(actual) == len(wanted) and all(
            isinstance(a, (int, float)) and not isinstance(a, bool)
            and math.isclose(a, b, rel_tol=0, abs_tol=1e-6)
            for a, b in zip(actual, wanted)
        )

    if not close(marker, endpoint):
        raise ValueError("Bloch marker fabricates or miscomputes polarization")
    if expected["z"] == 0:
        if segment is not None:
            raise ValueError("Zero polarization must not have a nonzero segment")
    elif not isinstance(segment, list) or len(segment) != 2 or not (
        close(segment[0], [0, 0, 0]) and close(segment[1], endpoint)
    ):
        raise ValueError("Bloch segment does not match polarization")


def render_problem(problem: dict, output: Path, blender: str, width: int, height: int,
                   samples: int, timeout: int, bloch_bit: int = 0) -> dict:
    marginal = z_marginal(problem["run"], bloch_bit)
    # A fresh directory prevents stale output from satisfying a failed/no-op render.
    folder = output / "assets" / problem["id"] / uuid.uuid4().hex[:12]
    folder.mkdir(parents=True)
    input_path = folder / "scene.json"
    write_json(input_path, problem)
    print(f"Rendering {problem['id']} ...", flush=True)
    completed = subprocess.run([
        blender, "--background", "--factory-startup", "--python-exit-code", "1",
        "--python", str(ROOT / "viz" / "render_scene.py"), "--",
        "--input", str(input_path), "--output", str(folder),
        "--width", str(width), "--height", str(height), "--samples", str(samples),
        "--bloch-bit", str(bloch_bit),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    log = folder / "render.log"
    log.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise ValueError(f"Blender failed for {problem['id']}; see {log}\n{completed.stderr[-2000:]}")
    poster = folder / "poster.png"
    verify_png(poster, width, height)
    blend = folder / "scene.blend"
    if not blend.is_file() or not blend.read_bytes().startswith(b"BLENDER"):
        raise ValueError(f"{problem['id']}: Blender scene missing or invalid")
    report = json.loads((folder / "render-report.json").read_text(encoding="utf-8"))
    if report.get("problem_id") != problem["id"] or report.get("input_sha256") != hashlib.sha256(input_path.read_bytes()).hexdigest():
        raise ValueError(f"{problem['id']}: render report does not match input evidence")
    if report.get("pixel_range", 0) <= 0.01:
        raise ValueError(f"{problem['id']}: rendered image is blank")
    verify_bloch_report(report, marginal)
    result = dict(problem)
    result["render_status"] = "rendered"
    estimate = problem["estimate"] or {}
    result["assets"] = [{
        "kind": "poster", "path": poster.relative_to(output).as_posix(),
        "media_type": "image/png", "width": width, "height": height,
        "sha256": hashlib.sha256(poster.read_bytes()).hexdigest(),
        "alt": (
            f"{problem['title']}: {'archived' if problem['archived'] else 'active'}, "
            f"stage {problem['stage']}. Estimated logical qubits: {estimate.get('logical_qubits')}; "
            f"physical qubits: {estimate.get('physical_qubits')}. "
            f"Simulator histogram {problem['run']['status']}. Logarithmic resource bars; "
            "sampled outcomes are separate kernel evidence, not quantum advantage. "
            + bloch_alt(marginal)
        ),
    }]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "render", "interactive"])
    parser.add_argument("--output", type=Path, default=ROOT / "viz")
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS,
                        help="Repository-local simulatorMatrix-format JSON")
    parser.add_argument("--target", default="local-simulator")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--all", action="store_true", help="Render active AND archived problems")
    selection.add_argument("--problem", action="append", help="Exact problem ID; repeat to select several")
    parser.add_argument("--blender", default=os.environ.get("BLENDER", "blender"))
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1000)
    parser.add_argument("--samples", type=int, default=16)
    parser.add_argument("--bloch-bit", type=int, default=0,
                        help="Zero-based returned measurement index (not a physical-qubit ID)")
    parser.add_argument("--timeout", type=int, default=300, help="Seconds per problem")
    parser.add_argument("--serve", action="store_true", help="Serve interactive output on localhost")
    parser.add_argument("--open", action="store_true", help="Open the viewer (implies --serve)")
    parser.add_argument("--port", type=int, default=8765, help="Local viewer port; 0 selects a free port")
    args = parser.parse_args(argv)
    try:
        if (args.serve or args.open) and args.command != "interactive":
            raise ValueError("--serve and --open are only for the interactive command")
        if not 0 <= args.port <= 65535:
            raise ValueError("Port must be between 0 and 65535")
        if min(args.width, args.height, args.samples, args.timeout) <= 0:
            raise ValueError("Dimensions, samples and timeout must be positive")
        if args.bloch_bit < 0:
            raise ValueError("Bloch bit must be a nonnegative integer")
        if not args.runs.is_file() and args.runs != DEFAULT_RUNS:
            raise ValueError(f"Run source does not exist: {args.runs}")
        manifest = build_catalog(args.runs, args.target)
        selected = set(args.problem or ["16_error_correction"])
        known = {p["id"] for p in manifest["problems"]}
        if selected - known:
            raise ValueError(f"Unknown problem IDs: {', '.join(sorted(selected - known))}")
        output = args.output.resolve()
        if args.command == "interactive":
            from viz.interactive import publish_viewer, serve_viewer

            directory = publish_viewer(manifest, output)
            print(f"{directory / 'index.html'}: {len(manifest['problems'])} problems; evidence validated")
            if args.serve or args.open:
                serve_viewer(directory, args.port, args.open)
            return 0
        if args.command == "render":
            blender = shutil.which(args.blender)
            if not blender:
                raise ValueError("Blender not found. Install Blender 4.2+ and use --blender PATH.")
            for index, problem in enumerate(manifest["problems"]):
                if args.all or problem["id"] in selected:
                    manifest["problems"][index] = render_problem(
                        problem, output, blender, args.width, args.height, args.samples,
                        args.timeout, args.bloch_bit
                    )
        # Publish only after every selected render has produced verified artifacts.
        manifest_path = output / "manifest.json"
        pending = output / "manifest.pending.json"
        write_json(pending, manifest)
        pending.replace(manifest_path)
        rendered = sum(p["render_status"] == "rendered" for p in manifest["problems"])
        print(f"{manifest_path}: {len(manifest['problems'])} problems, {rendered} rendered")
        return 0
    except (OSError, ValueError, KeyError, TypeError, zlib.error, subprocess.SubprocessError) as error:
        print(f"Visualization failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
