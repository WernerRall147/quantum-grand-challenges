"""Blender-only scene builder, invoked by python -m viz.build render."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

# Blender's bundled Python does not add the repository to its module search path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from viz.data import (
    BLOCH_LABEL, BLOCH_CONVENTION, BLOCH_LIMITATION,
    histogram_bars, resource_height, z_marginal,
)

PALETTE = {
    "background": (0.009, 0.018, 0.035),
    "panel": (0.023, 0.040, 0.065),
    "track": (0.045, 0.072, 0.105),
    "white": (0.85, 0.94, 1.0),
    "muted": (0.40, 0.56, 0.68),
    "cyan": (0.02, 0.70, 0.82),
    "purple": (0.46, 0.26, 0.96),
    "amber": (1.0, 0.55, 0.12),
}


def material(name: str, emission: bool = False):
    key = name + ("_text" if emission else "")
    existing = bpy.data.materials.get(key)
    if existing:
        return existing
    mat = bpy.data.materials.new(key)
    mat.diffuse_color = (*PALETTE[name], 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*PALETTE[name], 1)
    shader.inputs["Roughness"].default_value = 0.4
    if emission:
        shader.inputs["Emission Color"].default_value = (*PALETTE[name], 1)
        shader.inputs["Emission Strength"].default_value = 1.0
    return mat


def box(name, x, y, width, height, color, z=0, depth=0.18):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (width, height, depth)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material(color))
    bevel = obj.modifiers.new("Soft edges", "BEVEL")
    bevel.width = min(0.065, width / 5, height / 5, depth / 3)
    bevel.segments = 3
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def text(name, body, x, y, size=0.24, color="white", width=None, align="LEFT"):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = str(body)
    curve.size = size
    curve.align_x = align
    curve.space_character = 1.1
    curve.extrude = 0.001
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, 0.38)
    obj.data.materials.append(material(color, emission=True))
    if width:
        bpy.context.view_layer.update()
        if obj.dimensions.x > width:
            curve.size *= width / obj.dimensions.x
    return obj


def format_count(value):
    return "unavailable" if value is None else f"{value:,}"


def resource_panel(problem):
    estimate = problem["estimate"] or {}
    text("estimate_heading", "01 / RESOURCE ESTIMATE", -9.1, 3.0, 0.29, "cyan")
    text("estimate_program", estimate.get("entry_point") or "No estimate available",
         -9.1, 2.55, width=8.0)
    text("resource_scale", "Height = log10(1 + qubits) | same scale for both bars",
         -9.1, 2.1, 0.19, "muted", width=8.2)
    baseline = -2.5
    for power in range(7):
        y = baseline + power * 0.65
        box(f"grid_{power}", -4.3, y, 5.9, 0.012, "track", z=-0.03, depth=0.02)
        text(f"tick_{power}", f"{10 ** power - 1:,}", -7.8, y - 0.06,
             0.17, "muted", width=1.2, align="RIGHT")
    for field, label, x, color in [
        ("logical_qubits", "Logical", -5.8, "cyan"),
        ("physical_qubits", "Physical", -2.9, "purple"),
    ]:
        value = estimate.get(field)
        height = resource_height(value) * 0.65
        if height > 0:
            bar = box(field, x, baseline + height / 2, 1.2, height, color, depth=0.35)
            bar["evidence_value"] = value
            bar["height_formula"] = "0.65 * log10(1 + qubits)"
        text(field + "_value", format_count(value), x, baseline + height + 0.22,
             0.31, color, width=2.3, align="CENTER")
        text(field + "_label", label, x, -2.97, 0.23, align="CENTER")
    runtime = estimate.get("runtime_ns")
    runtime_text = "unavailable" if runtime is None else f"{runtime / 1e6:,.6g} ms ({runtime:,} ns)"
    text("runtime", f"Estimated runtime: {runtime_text}", -9.1, -3.55,
         0.22, width=8.2)


def run_panel(problem):
    run = problem["run"]
    text("run_heading", "02 / SAMPLED KERNEL OUTCOMES", 0.9, 3.0, 0.29, "cyan", width=8.2)
    if run["status"] == "missing":
        text("no_run", "No matching simulator run", 1.1, 1.9, 0.42, "amber", width=8.0)
        text("no_run_detail", "No histogram is fabricated from resource estimates.",
             1.1, 1.25, 0.23, "muted", width=8.0)
        text("no_run_note", "Missing data does not mean zero probability.", 1.1, 0.8,
             0.23, "muted", width=8.0)
        return
    text("run_target", f"{run['target']} | {run['shots']:,} shots", 0.9, 2.55, width=8.0)
    text("run_program", run["entry_point"], 0.9, 2.15, 0.21, "muted", width=8.2)
    text("probability_axis", "Count / shots (linear width)   0% ---------------- 100%",
         0.9, 1.65, 0.18, "muted", width=8.2)
    for index, row in enumerate(histogram_bars(run)):
        y = 1.25 - index * 0.25
        label = row["outcome"].replace("Zero", "0").replace("One", "1")
        text(f"outcome_{index}", label, 0.95, y - 0.05, 0.17, width=3.4)
        box(f"outcome_track_{index}", 6.2, y, 3.3, 0.17, "track", z=-0.02)
        probability = row["count"] / run["shots"]
        if probability:
            bar = box(f"histogram_{index}", 4.55 + 3.3 * probability / 2, y,
                      3.3 * probability, 0.17, "cyan", z=0.08)
            bar["outcome"] = row["outcome"]
            bar["count"] = row["count"]
            bar["shots"] = run["shots"]
        text(f"probability_{index}", f"{row['count']} / {probability:.1%}", 9.1, y - 0.05,
             0.16, width=1.1, align="RIGHT")
    text("run_note", "Recorded outcome order; Other combines all remaining shots.",
         0.9, -0.85, 0.17, "muted", width=8.2)


def bloch_curve(name, points, frame, color="muted", thickness=0.009, cyclic=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = thickness
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinates in zip(spline.points, points):
        point.co = (*coordinates, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.parent = frame
    curve.materials.append(material(color, emission=True))
    return obj


def bloch_panel(problem, bit):
    marginal = z_marginal(problem["run"], bit)
    bpy.context.scene["bloch_evidence"] = json.dumps(marginal, sort_keys=True)
    box("bloch_divider", 5, -1.02, 8.2, 0.012, "track", depth=0.02)
    text("bloch_heading", "03 / BLOCH SPHERE", 0.9, -1.40, 0.27, "cyan")
    frame = bpy.data.objects.new("bloch_frame", None)
    bpy.context.collection.objects.link(frame)
    frame.location = (2.35, -2.75, 1.4)
    frame.rotation_euler = (
        Matrix.Rotation(math.radians(-65), 4, "X")
        @ Matrix.Rotation(math.radians(35), 4, "Z")
    ).to_euler()
    frame.scale = (0.85,) * 3
    # All local coordinates are normalized Bloch coordinates. Tilt only the
    # reference frame for readability; never rotate the evidence toward a pole.
    for normal in range(3):
        points = []
        for step in range(96):
            angle = 2 * math.pi * step / 96
            point = [0.0, 0.0, 0.0]
            point[(normal + 1) % 3] = math.cos(angle)
            point[(normal + 2) % 3] = math.sin(angle)
            points.append(point)
        bloch_curve(f"bloch_ring_{normal}", points, frame, cyclic=True)
    for index, axis in enumerate("xyz"):
        end = [0.0, 0.0, 0.0]
        end[index] = 1
        bloch_curve(f"bloch_axis_{axis}", [tuple(-v for v in end), end],
                    frame, "cyan" if axis == "z" else "muted")
    if marginal["status"] == "available":
        z = marginal["z"]
        if z != 0:
            bloch_curve("bloch_segment", [(0, 0, 0), (0, 0, z)],
                        frame, "amber", thickness=0.025)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.065)
        marker = bpy.context.object
        marker.name = "bloch_marker"
        marker.parent = frame
        marker.location = (0, 0, z)
        marker.data.materials.append(material("amber", emission=True))
    text("bloch_north", "Z +1 / |0>", 2.35, -1.80, 0.17, align="CENTER")
    text("bloch_south", "Z -1 / |1>", 2.35, -3.83, 0.17, align="CENTER")
    bpy.context.view_layer.update()
    for axis, point, align in [("x", (1.15, 0, 0), "LEFT"), ("y", (0, 1.15, 0), "RIGHT")]:
        position = frame.matrix_world @ Vector(point)
        text(f"bloch_{axis}_axis", f"{axis.upper()} ?", position.x, position.y,
             0.16, "muted", align=align)
    text("bloch_label", BLOCH_LABEL, 4.2, -1.78, 0.20, "cyan", width=4.95)
    text("bloch_selection", f"Returned bit {bit} | zero-based result order",
         4.2, -2.10, 0.18, width=4.95)
    if marginal["status"] == "available":
        text("bloch_probabilities",
             f"P(0) = {marginal['p0']:.3f} | P(1) = {marginal['p1']:.3f}",
             4.2, -2.42, 0.20, width=4.95)
        text("bloch_z", f"z = P(0) - P(1) = {marginal['z']:+.3f}",
             4.2, -2.74, 0.22, "amber", width=4.95)
    else:
        text("bloch_unavailable", "Z unavailable / no marker", 4.2, -2.42,
             0.20, "amber", width=4.95)
        text("bloch_reason", marginal["reason"], 4.2, -2.74, 0.18, "amber", width=4.95)
    text("bloch_diagonal", "Diagonal-state representation only", 4.2, -3.06, 0.18, width=4.95)
    text("bloch_convention", BLOCH_CONVENTION, 4.2, -3.38, 0.18, width=4.95)
    text("bloch_limitation", BLOCH_LIMITATION, 4.2, -3.70, 0.18, "amber", width=4.95)
    text("bloch_sampling", "Sample frequencies, not exact probabilities", 4.2, -4.02,
         0.17, "muted", width=4.95)


def bloch_report(scene):
    """Read back the actual normalized geometry, not a copy of desired positions."""
    def points(name):
        obj = scene.objects.get(name)
        return [list(p.co[:3]) for p in obj.data.splines[0].points] if obj else None

    frame = scene.objects["bloch_frame"]
    marker = scene.objects.get("bloch_marker")
    return {
        "evidence": json.loads(scene["bloch_evidence"]),
        "geometry": {
            "frame_location": list(frame.location), "frame_scale": list(frame.scale),
            "frame_rotation": list(frame.rotation_euler),
            "marker": list(marker.location) if marker else None,
            "segment": points("bloch_segment"),
            "rings": [points(f"bloch_ring_{i}") for i in range(3)],
            "axes": {axis: points(f"bloch_axis_{axis}") for axis in "xyz"},
        },
    }


def build_scene(problem: dict, width: int, height: int, samples: int, bloch_bit: int = 0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene["problem_id"] = problem["id"]
    scene["evidence"] = json.dumps(problem, sort_keys=True)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "Standard"
    scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.15, 0.2, 0.3, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.5

    bpy.ops.object.camera_add(location=(0, 0, 30))
    camera = bpy.context.object
    camera.name = "Evidence camera"
    camera.data.type = "ORTHO"
    # Fit the whole 20 x 12.5 layout, including non-default aspect ratios.
    camera.data.ortho_scale = max(21.0, 13.2 * width / height) if width >= height else max(13.2, 21.0 * height / width)
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(-4, 3, 10))
    bpy.context.object.data.energy = 1700
    bpy.context.object.data.shape = "DISK"
    bpy.context.object.data.size = 12
    box("background", 0, 0, 200, 200, "background", z=-0.8)
    box("estimate_panel", -5.0, -0.25, 9.4, 8.0, "panel", z=-0.35)
    box("run_panel", 5.0, -0.25, 9.4, 8.0, "panel", z=-0.35)
    text("eyebrow", "QUANTUM GRAND CHALLENGES / EVIDENCE AT A GLANCE", -9.5, 5.5,
         0.22, "cyan")
    text("title", f"{problem['id'][:2]} / {problem['title']}", -9.5, 4.55,
         0.66, width=15.0)
    text("status", f"{'ARCHIVED' if problem['archived'] else 'ACTIVE'} | Stage {problem['stage']}",
         9.4, 4.7, 0.27, "amber" if problem["archived"] else "cyan", align="RIGHT")
    resource_panel(problem)
    run_panel(problem)
    bloch_panel(problem, bloch_bit)
    estimate = problem["estimate"] or {}
    text("model", f"Estimate model: {estimate.get('qubit_model') or 'unavailable'}"
         f" / {estimate.get('qec_scheme') or 'unavailable'}", -9.4, -4.75, 0.21, "muted", width=9)
    build = estimate.get("build") or {}
    text("estimate_date", f"Estimate: {build.get('dateUtc', 'date unavailable')}",
         -9.4, -5.13, 0.18, "muted", width=9)
    text("run_date", f"Run source snapshot: {problem['run']['source_generated_utc'] or 'unavailable'}",
         0.8, -4.75, 0.19, "muted", width=8.6)
    text("separation", "Different programs / dates. Not a like-for-like comparison.",
         0.8, -5.13, 0.19, "amber", width=8.6)
    text("disclaimer", "Estimates are not measured hardware. Simulator samples are not quantum advantage.",
         -9.4, -5.75, 0.24, "amber", width=19)
    return scene


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--samples", type=int, required=True)
    parser.add_argument("--bloch-bit", type=int, default=0)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    problem = json.loads(args.input.read_text(encoding="utf-8"))
    scene = build_scene(problem, args.width, args.height, args.samples, args.bloch_bit)
    scene.render.filepath = str(args.output / "poster.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output / "scene.blend"), compress=False)
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(args.output / "poster.png"), check_existing=False)
    pixels = image.pixels[:]
    # Ignore alpha: otherwise a flat black image with opaque alpha would pass.
    rgb = [v for index, v in enumerate(pixels) if index % 4 != 3]
    report = {
        "problem_id": problem["id"],
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "blender_version": bpy.app.version_string,
        "pixel_range": max(rgb) - min(rgb),
        "resource_bars": {
            obj.name: {"value": obj["evidence_value"], "height": obj.dimensions.y}
            for obj in scene.objects if "evidence_value" in obj
        },
        "histogram_counts": {
            obj["outcome"]: obj["count"] for obj in scene.objects if "outcome" in obj
        },
        "labels": [obj.data.body for obj in scene.objects if obj.type == "FONT"],
        "bloch": bloch_report(scene),
    }
    (args.output / "render-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Verified render: {problem['id']}, {tuple(image.size)}, pixel range {report['pixel_range']:.3f}")


if __name__ == "__main__":
    main()
