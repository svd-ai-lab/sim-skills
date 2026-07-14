#!/usr/bin/env python3
"""Build a validation-first Blender architectural shell from a plan contract."""

from __future__ import annotations

import json
import hashlib
import math
from pathlib import Path

import bpy
from mathutils import Vector


COLLECTION_NAME = "cad_2d_to_3d/shell"
CUT_COLLECTION_NAME = "cad_2d_to_3d/validation-cut"
SPACE_COLLECTION_NAME = "cad_2d_to_3d/spaces"
OPENING_COLLECTION_NAME = "cad_2d_to_3d/opening-markers"


def mm(value):
    return float(value) / 1000.0


def material(name, color):
    existing = bpy.data.materials.get(name)
    mat = existing or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = 1.0
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return mat


def ensure_collection(name):
    existing = bpy.data.collections.get(name)
    if existing:
        for obj in list(existing.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(existing)
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def create_validation_cut(source_objects, plan, cut_height_mm, collection, mat):
    """Intersect built solids with a thin horizontal slab for plan validation."""
    points = plan["property_boundary"]
    xs = [mm(point[0]) for point in points]
    ys = [mm(point[1]) for point in points]
    margin = 1.0
    thickness = 0.02
    slab = add_box(
        "validation-cut/slab",
        ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2,
         mm(cut_height_mm)),
        (max(xs) - min(xs) + 2 * margin,
         max(ys) - min(ys) + 2 * margin, thickness),
        0.0, collection, mat,
    )
    cut_objects = []
    for source in source_objects:
        duplicate = source.copy()
        duplicate.data = source.data.copy()
        duplicate.name = f"validation-cut/{source.name}"
        collection.objects.link(duplicate)
        modifier = duplicate.modifiers.new("validation-cut/intersect", "BOOLEAN")
        modifier.operation = "INTERSECT"
        modifier.solver = "EXACT"
        modifier.object = slab
        bpy.context.view_layer.objects.active = duplicate
        duplicate.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        duplicate.select_set(False)
        duplicate.data.materials.clear()
        duplicate.data.materials.append(mat)
        duplicate.hide_set(True)
        duplicate.hide_render = True
        cut_objects.append(duplicate)
    bpy.data.objects.remove(slab, do_unlink=True)
    return cut_objects


def add_space_markers(plan, collection, mat):
    markers = []
    for space in plan.get("spaces", []):
        polygon = space["polygon"]
        center = (
            mm(sum(point[0] for point in polygon) / len(polygon)),
            mm(sum(point[1] for point in polygon) / len(polygon)),
            0.03,
        )
        curve = bpy.data.curves.new(f"space/{space['id']}-text", type="FONT")
        curve.body = space.get("label", space["id"])
        curve.align_x = "CENTER"
        curve.align_y = "CENTER"
        curve.size = 0.24 if len(curve.body) > 16 else 0.28
        obj = bpy.data.objects.new(f"space/{space['id']}", curve)
        obj.location = center
        obj["space_id"] = space["id"]
        obj["evidence"] = space.get("evidence", "inferred")
        obj["polygon_mm"] = json.dumps(polygon)
        curve.materials.append(mat)
        collection.objects.link(obj)
        obj.hide_render = True
        markers.append(obj)
    return markers


def add_acceptance_marker(plan, collection, review_mat, accepted_mat):
    acceptance = plan.get("acceptance", {})
    status = acceptance.get("status", "needs_review")
    points = plan["property_boundary"]
    center_x = mm((min(point[0] for point in points)
                   + max(point[0] for point in points)) / 2)
    top_y = mm(max(point[1] for point in points)) + 0.5
    curve = bpy.data.curves.new("validation/acceptance-status-text", type="FONT")
    curve.body = ("2D PLAN ACCEPTED" if status == "accepted"
                  else "PROVISIONAL - 2D REVIEW REQUIRED")
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 0.24
    obj = bpy.data.objects.new("validation/acceptance-status", curve)
    obj.location = (center_x, top_y, 0.03)
    obj["acceptance_status"] = status
    obj["acceptance_note"] = acceptance.get("note", "")
    curve.materials.append(accepted_mat if status == "accepted" else review_mat)
    collection.objects.link(obj)
    obj.hide_render = True
    return obj


def frame_top_view(plan):
    points = plan["property_boundary"]
    xs = [mm(point[0]) for point in points]
    ys = [mm(point[1]) for point in points]
    center = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 0.0))
    distance = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.5
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((item for item in area.regions if item.type == "WINDOW"), None)
            if region:
                with bpy.context.temp_override(window=window, area=area, region=region):
                    bpy.ops.view3d.view_axis(type="TOP", align_active=False)
            region_3d = area.spaces.active.region_3d
            region_3d.view_location = center
            region_3d.view_distance = distance
            area.tag_redraw()


def set_reference_review_mode():
    """Show the true plan cut as wire over the calibrated source image."""
    scene = bpy.context.scene
    camera = bpy.data.objects["validation/camera-top"]
    scene.camera = camera
    camera.hide_set(False)
    for obj in bpy.data.collections[COLLECTION_NAME].objects:
        if obj.type == "MESH":
            obj.hide_set(True)
    for obj in bpy.data.collections[CUT_COLLECTION_NAME].objects:
        obj.hide_set(False)
        obj.display_type = "WIRE"
        obj.show_in_front = True
    for obj in bpy.data.collections[SPACE_COLLECTION_NAME].objects:
        obj.hide_set(True)
    for obj in bpy.data.collections[OPENING_COLLECTION_NAME].objects:
        obj.hide_set(True)
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.overlay.show_overlays = True
                area.spaces.active.overlay.show_extras = True
                area.tag_redraw()
    bpy.context.view_layer.update()


def set_model_top_view(plan):
    """Restore solid shell and semantic space labels after reference review."""
    camera = bpy.data.objects["validation/camera-top"]
    camera.hide_set(True)
    for obj in bpy.data.collections[COLLECTION_NAME].objects:
        if obj.type == "MESH":
            obj.hide_set(False)
            obj.display_type = "SOLID"
            obj.show_in_front = False
    for obj in bpy.data.collections[CUT_COLLECTION_NAME].objects:
        obj.hide_set(True)
    for obj in bpy.data.collections[SPACE_COLLECTION_NAME].objects:
        obj.hide_set(False)
    for obj in bpy.data.collections[OPENING_COLLECTION_NAME].objects:
        obj.hide_set(False)
    frame_top_view(plan)
    bpy.context.view_layer.update()


def reset_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    root = bpy.context.scene.collection
    for child in list(root.children):
        root.children.unlink(child)
        bpy.data.collections.remove(child)


def move_to_collection(obj, collection):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def add_box(name, center, size, angle, collection, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    # primitive_cube_add(size=1) creates unit dimensions, so scale equals the
    # requested full dimension on each axis.
    obj.scale = size
    obj.rotation_euler.z = angle
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    move_to_collection(obj, collection)
    return obj


def add_wall(wall, height, collection, mat):
    a = Vector((mm(wall["a"][0]), mm(wall["a"][1])))
    b = Vector((mm(wall["b"][0]), mm(wall["b"][1])))
    delta = b - a
    length = delta.length
    angle = math.atan2(delta.y, delta.x)
    center = (a + b) / 2
    return add_box(
        f"wall/{wall['id']}",
        (center.x, center.y, height / 2),
        (length, mm(wall["thickness"]), height),
        angle,
        collection,
        mat,
    )


def cut_opening(wall_obj, wall, opening, collection):
    a = Vector((mm(wall["a"][0]), mm(wall["a"][1])))
    b = Vector((mm(wall["b"][0]), mm(wall["b"][1])))
    direction = (b - a).normalized()
    start = a + direction * mm(opening["offset"])
    end = start + direction * mm(opening["width"])
    center = (start + end) / 2
    z0 = mm(opening.get("sill", 0)) if opening["kind"] == "window" else 0.0
    z1 = mm(opening["head"])
    cutter = add_box(
        f"opening-cutter/{opening['id']}",
        (center.x, center.y, (z0 + z1) / 2),
        ((end - start).length + 0.02, mm(wall["thickness"]) + 0.08, z1 - z0),
        math.atan2(direction.y, direction.x),
        collection,
        # The cutter material becomes visible on window sills when viewed from
        # above. Keep it white so the orthographic cut mask treats the opening
        # as void instead of wall geometry.
        material("validation/opening", (1.0, 1.0, 1.0, 1.0)),
    )
    modifier = wall_obj.modifiers.new(f"cut/{opening['id']}", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = wall_obj
    wall_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    wall_obj.select_set(False)
    bpy.data.objects.remove(cutter, do_unlink=True)


def add_opening_marker(wall, opening, collection, mat):
    """Add a reversible frame proxy without inventing door-leaf geometry."""
    a = Vector((mm(wall["a"][0]), mm(wall["a"][1])))
    b = Vector((mm(wall["b"][0]), mm(wall["b"][1])))
    direction = (b - a).normalized()
    start = a + direction * mm(opening["offset"])
    end = start + direction * mm(opening["width"])
    center = (start + end) / 2
    angle = math.atan2(direction.y, direction.x)
    sill = mm(opening.get("sill", 0)) if opening["kind"] == "window" else 0.0
    head = mm(opening["head"])
    frame_width = 0.05
    depth = mm(wall["thickness"]) + 0.03
    pieces = []
    for suffix, point in (("jamb-a", start), ("jamb-b", end)):
        pieces.append(add_box(
            f"opening/{opening['id']}/{suffix}",
            (point.x, point.y, (sill + head) / 2),
            (frame_width, depth, head - sill), angle, collection, mat))
    pieces.append(add_box(
        f"opening/{opening['id']}/head",
        (center.x, center.y, head - frame_width / 2),
        ((end - start).length, depth, frame_width), angle, collection, mat))
    if opening["kind"] == "window":
        pieces.append(add_box(
            f"opening/{opening['id']}/sill",
            (center.x, center.y, sill + frame_width / 2),
            ((end - start).length, depth, frame_width), angle, collection, mat))
    for piece in pieces:
        piece["opening_id"] = opening["id"]
        piece["opening_kind"] = opening["kind"]
        piece["wall_id"] = opening["wall_id"]
        piece.hide_render = True
    return pieces


def add_floor(boundary, collection, mat, thickness=0.05):
    points = [(mm(x), mm(y)) for x, y in boundary]
    bottom = [(x, y, -thickness) for x, y in points]
    top = [(x, y, 0.0) for x, y in points]
    vertices = bottom + top
    count = len(points)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new("floor/property-boundary-mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("floor/property-boundary", mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def configure_top_camera(plan, image_size, collection, cut_height_mm):
    model = plan["calibration"]["model_points"]
    image = plan["calibration"]["image_points"]
    import numpy as np

    design = np.column_stack([np.asarray(model, dtype=float), np.ones(len(model))])
    coeff, _, _, _ = np.linalg.lstsq(design, np.asarray(image, dtype=float), rcond=None)
    linear = coeff[:2, :].T
    offset = coeff[2, :]
    inverse = np.linalg.inv(linear)
    width, height = image_size
    center_mm = inverse @ (np.asarray([width / 2, height / 2]) - offset)
    x_scale = abs(linear[0, 0])
    # Blender's orthographic camera scale is the horizontal view width for this
    # render setup; derive it from the calibrated image X scale.
    ortho_width_m = width / x_scale / 1000.0
    bpy.ops.object.camera_add(location=(mm(center_mm[0]), mm(center_mm[1]), 30.0))
    camera = bpy.context.object
    camera.name = "validation/camera-top"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_width_m
    camera.data.clip_start = 0.1
    camera.data.clip_end = camera.location.z + 1.0
    camera.rotation_euler = (0.0, 0.0, 0.0)
    move_to_collection(camera, collection)
    camera.hide_set(True)
    return camera


def attach_reference_background(camera, reference_path):
    image = bpy.data.images.load(str(reference_path), check_existing=True)
    camera.data.show_background_images = True
    camera.data.background_images.clear()
    background = camera.data.background_images.new()
    background.image = image
    background.alpha = 0.72
    background.display_depth = "BACK"
    background.frame_method = "FIT"
    return image


def build(plan_path, output_blend, render_path=None, wall_height_mm=2700,
          image_size=(1600, 1280), validation_cut_height_mm=1200,
          reset_current_scene=True, report_path=None):
    plan_path = Path(plan_path).resolve()
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes.decode("utf-8"))
    if plan.get("units") != "mm":
        raise ValueError("architecture builder currently requires units=mm")
    reference_path = (plan_path.parent / plan["reference_image"]).resolve()
    if not reference_path.exists():
        raise FileNotFoundError(f"reference image not found: {reference_path}")
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "METERS"
    if reset_current_scene:
        reset_scene()
    collection = ensure_collection(COLLECTION_NAME)
    cut_collection = ensure_collection(CUT_COLLECTION_NAME)
    space_collection = ensure_collection(SPACE_COLLECTION_NAME)
    opening_collection = ensure_collection(OPENING_COLLECTION_NAME)
    wall_mat = material("validation/wall", (0.08, 0.08, 0.08, 1.0))
    floor_mat = material("validation/floor", (0.98, 0.98, 0.98, 1.0))
    beam_mat = material("validation/beam", (0.35, 0.12, 0.55, 1.0))
    space_mat = material("validation/space-label", (0.05, 0.25, 0.75, 1.0))
    window_mat = material("validation/window-frame", (0.05, 0.55, 0.95, 1.0))
    door_mat = material("validation/door-frame", (1.0, 0.35, 0.05, 1.0))
    review_mat = material("validation/status-needs-review", (0.9, 0.03, 0.03, 1.0))
    accepted_mat = material("validation/status-accepted", (0.05, 0.65, 0.15, 1.0))
    add_floor(plan["property_boundary"], collection, floor_mat)
    height = mm(wall_height_mm)
    wall_map = {}
    structural_objects = []
    for wall in plan.get("walls", []):
        wall_obj = add_wall(wall, height, collection, wall_mat)
        wall_map[wall["id"]] = (wall, wall_obj)
        structural_objects.append(wall_obj)
    for opening in plan.get("openings", []):
        wall, wall_obj = wall_map[opening["wall_id"]]
        cut_opening(wall_obj, wall, opening, collection)
        add_opening_marker(
            wall, opening, opening_collection,
            window_mat if opening["kind"] == "window" else door_mat)
    for beam in plan.get("beams", []):
        a = Vector((mm(beam["a"][0]), mm(beam["a"][1])))
        b = Vector((mm(beam["b"][0]), mm(beam["b"][1])))
        delta = b - a
        center = (a + b) / 2
        z0, z1 = mm(beam["underside"]), mm(beam["top"])
        beam_obj = add_box(f"beam/{beam['id']}", (center.x, center.y, (z0 + z1) / 2),
                           (delta.length, mm(beam["width"]), z1 - z0),
                           math.atan2(delta.y, delta.x), collection, beam_mat)
        structural_objects.append(beam_obj)
    cut_objects = create_validation_cut(
        structural_objects, plan, validation_cut_height_mm, cut_collection, wall_mat)
    add_space_markers(plan, space_collection, space_mat)
    add_acceptance_marker(plan, space_collection, review_mat, accepted_mat)
    camera = configure_top_camera(plan, image_size, collection, validation_cut_height_mm)
    attach_reference_background(camera, reference_path)
    scene = bpy.context.scene
    scene["cad_2d_to_3d.plan_path"] = str(plan_path)
    scene["cad_2d_to_3d.plan_sha256"] = hashlib.sha256(plan_bytes).hexdigest()
    scene["cad_2d_to_3d.reference_image"] = str(reference_path)
    scene["cad_2d_to_3d.acceptance_status"] = plan.get(
        "acceptance", {}).get("status", "needs_review")
    acceptance_checks = plan.get("acceptance_checks", [])
    scene["cad_2d_to_3d.acceptance_checks"] = json.dumps(
        acceptance_checks, ensure_ascii=False)
    scene["cad_2d_to_3d.pending_acceptance_checks"] = json.dumps([
        check.get("id") for check in acceptance_checks
        if check.get("status") != "confirmed" and check.get("id")
    ], ensure_ascii=False)
    scene["cad_2d_to_3d.schema_version"] = int(plan.get("schema_version", 1))
    scene["cad_2d_to_3d.validation_cut_height_mm"] = float(validation_cut_height_mm)
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = image_size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 1.0
    bpy.context.view_layer.update()
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
    output_blend = str(Path(output_blend).resolve())
    bpy.ops.wm.save_as_mainfile(filepath=output_blend)
    if render_path:
        previous_source_render = {obj: obj.hide_render for obj in collection.objects}
        for obj in collection.objects:
            obj.hide_render = True
        for obj in cut_objects:
            obj.hide_render = False
        scene.render.filepath = str(Path(render_path).resolve())
        bpy.ops.render.render(write_still=True)
        for obj, hidden in previous_source_render.items():
            obj.hide_render = hidden
        for obj in cut_objects:
            obj.hide_render = True
        bpy.ops.wm.save_as_mainfile(filepath=output_blend)
    frame_top_view(plan)
    bpy.context.view_layer.update()
    report = {
        "status": "ok",
        "blend_file": output_blend,
        "render_path": str(Path(render_path).resolve()) if render_path else None,
        "plan_path": str(plan_path),
        "plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
        "reference_image": str(reference_path),
        "acceptance_status": plan.get("acceptance", {}).get(
            "status", "needs_review"),
        "acceptance_checks": acceptance_checks,
        "pending_acceptance_checks": [
            check.get("id") for check in acceptance_checks
            if check.get("status") != "confirmed" and check.get("id")
        ],
        "wall_height_mm": wall_height_mm,
        "walls": len(plan.get("walls", [])),
        "openings": len(plan.get("openings", [])),
        "beams": len(plan.get("beams", [])),
        "spaces": len(plan.get("spaces", [])),
        "opening_marker_objects": len(opening_collection.objects),
        "window_verticals_mm": {
            opening["id"]: {
                "sill": opening.get("sill", 0),
                "height": opening.get(
                    "height", opening["head"] - opening.get("sill", 0)),
                "head": opening["head"],
            }
            for opening in plan.get("openings", [])
            if opening["kind"] == "window"
        },
        "validation_cut_height_mm": validation_cut_height_mm,
        "collection": COLLECTION_NAME,
        "validation_collection": CUT_COLLECTION_NAME,
        "space_collection": SPACE_COLLECTION_NAME,
        "opening_collection": OPENING_COLLECTION_NAME,
    }
    if report_path:
        report_file = Path(report_path).resolve()
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report["report_path"] = str(report_file)
    return report
