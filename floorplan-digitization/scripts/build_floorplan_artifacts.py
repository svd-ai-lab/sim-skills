#!/usr/bin/env python3
"""Generate review CAD/vector/overlay artifacts from a semantic floor-plan JSON."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw


LAYER_COLORS = {
    "boundary": (220, 30, 30, 210),
    "exterior": (15, 70, 180, 120),
    "interior": (30, 130, 70, 120),
    "opening": (245, 145, 20, 220),
    "beam": (145, 60, 180, 190),
    "removed": (220, 40, 160, 190),
    "excluded": (110, 110, 110, 80),
}


def fit_affine(model_points: list[list[float]], image_points: list[list[float]]):
    if len(model_points) < 3 or len(model_points) != len(image_points):
        raise ValueError("calibration requires equal model/image lists with at least 3 points")
    source = np.asarray(model_points, dtype=float)
    target = np.asarray(image_points, dtype=float)
    design = np.column_stack([source, np.ones(len(source))])
    coeff, _, rank, _ = np.linalg.lstsq(design, target, rcond=None)
    if rank < 3:
        raise ValueError("calibration model points must be non-collinear")
    predicted = design @ coeff
    residuals = np.linalg.norm(predicted - target, axis=1)
    return coeff, residuals


def transform_point(coeff: np.ndarray, point: Iterable[float]) -> tuple[float, float]:
    x, y = point
    px, py = np.asarray([x, y, 1.0]) @ coeff
    return float(px), float(py)


def wall_polygon(wall: dict) -> list[tuple[float, float]]:
    ax, ay = wall["a"]
    bx, by = wall["b"]
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length <= 0:
        raise ValueError(f"wall {wall.get('id')} has zero length")
    nx = -dy / length * wall["thickness"] / 2
    ny = dx / length * wall["thickness"] / 2
    return [(ax + nx, ay + ny), (bx + nx, by + ny),
            (bx - nx, by - ny), (ax - nx, ay - ny)]


def opening_segment(opening: dict, wall: dict) -> tuple[tuple[float, float], tuple[float, float]]:
    ax, ay = wall["a"]
    bx, by = wall["b"]
    length = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / length, (by - ay) / length
    start = opening["offset"]
    end = start + opening["width"]
    return ((ax + ux * start, ay + uy * start),
            (ax + ux * end, ay + uy * end))


def dxf_pair(code, value) -> str:
    return f"{code}\n{value}\n"


def write_dxf(path: Path, plan: dict) -> None:
    layers = ["BOUNDARY", "WALL_EXT", "WALL_INT", "OPENING", "BEAM",
              "REMOVED", "EXCLUDED", "SPACE"]
    out = [dxf_pair(0, "SECTION"), dxf_pair(2, "HEADER"), dxf_pair(9, "$INSUNITS"),
           dxf_pair(70, 4), dxf_pair(0, "ENDSEC"), dxf_pair(0, "SECTION"),
           dxf_pair(2, "TABLES"), dxf_pair(0, "TABLE"), dxf_pair(2, "LAYER"),
           dxf_pair(70, len(layers))]
    for index, layer in enumerate(layers, 1):
        out += [dxf_pair(0, "LAYER"), dxf_pair(2, layer), dxf_pair(70, 0),
                dxf_pair(62, index), dxf_pair(6, "CONTINUOUS")]
    out += [dxf_pair(0, "ENDTAB"), dxf_pair(0, "ENDSEC"),
            dxf_pair(0, "SECTION"), dxf_pair(2, "ENTITIES")]

    def polyline(points, layer, closed=True):
        out.extend([dxf_pair(0, "LWPOLYLINE"), dxf_pair(8, layer),
                    dxf_pair(90, len(points)), dxf_pair(70, 1 if closed else 0)])
        for x, y in points:
            out.extend([dxf_pair(10, x), dxf_pair(20, y)])

    polyline(plan["property_boundary"], "BOUNDARY")
    for region in plan.get("excluded_regions", []):
        polyline(region["polygon"], "EXCLUDED")
    for wall in plan.get("walls", []):
        layer = "WALL_EXT" if wall.get("class") == "exterior" else "WALL_INT"
        polyline(wall_polygon(wall), layer)
    wall_map = {wall["id"]: wall for wall in plan.get("walls", [])}
    for opening in plan.get("openings", []):
        a, b = opening_segment(opening, wall_map[opening["wall_id"]])
        polyline([a, b], "OPENING", closed=False)
    for key, layer in (("beams", "BEAM"), ("removed_walls", "REMOVED")):
        for item in plan.get(key, []):
            polyline([item["a"], item["b"]], layer, closed=False)
    for space in plan.get("spaces", []):
        polyline(space["polygon"], "SPACE")
    out += [dxf_pair(0, "ENDSEC"), dxf_pair(0, "EOF")]
    path.write_text("".join(out), encoding="ascii")


def svg_points(points) -> str:
    return " ".join(f"{x},{-y}" for x, y in points)


def write_svg(path: Path, plan: dict) -> None:
    points = list(plan["property_boundary"])
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    margin = 500
    view = f"{min(xs)-margin} {-max(ys)-margin} {max(xs)-min(xs)+2*margin} {max(ys)-min(ys)+2*margin}"
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}">',
             '<rect width="100%" height="100%" fill="white"/>']
    lines.append(f'<polygon points="{svg_points(points)}" fill="none" stroke="#dc1e1e" stroke-width="35"/>')
    for region in plan.get("excluded_regions", []):
        lines.append(f'<polygon points="{svg_points(region["polygon"])}" fill="#999" fill-opacity=".25" stroke="#777" stroke-width="25"/>')
    for wall in plan.get("walls", []):
        color = "#0f46b4" if wall.get("class") == "exterior" else "#1e8246"
        lines.append(f'<polygon points="{svg_points(wall_polygon(wall))}" fill="{color}" fill-opacity=".35" stroke="{color}" stroke-width="18"/>')
    wall_map = {wall["id"]: wall for wall in plan.get("walls", [])}
    for opening in plan.get("openings", []):
        a, b = opening_segment(opening, wall_map[opening["wall_id"]])
        lines.append(f'<polyline points="{svg_points([a,b])}" fill="none" stroke="#f59114" stroke-width="70"/>')
    lines.append('</svg>')
    path.write_text("\n".join(lines), encoding="utf-8")


def draw_plan(image: Image.Image, plan: dict, coeff: np.ndarray, opaque=False) -> Image.Image:
    base = image.convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    layer_color = lambda name: (LAYER_COLORS[name][:3] + (255,)) if opaque else LAYER_COLORS[name]
    tx = lambda pts: [transform_point(coeff, p) for p in pts]
    draw.line(tx(plan["property_boundary"] + [plan["property_boundary"][0]]),
              fill=layer_color("boundary"), width=5)
    for region in plan.get("excluded_regions", []):
        draw.polygon(tx(region["polygon"]), fill=layer_color("excluded"))
    for wall in plan.get("walls", []):
        draw.polygon(tx(wall_polygon(wall)), fill=layer_color(wall.get("class", "interior")))
    wall_map = {wall["id"]: wall for wall in plan.get("walls", [])}
    for opening in plan.get("openings", []):
        draw.line(tx(opening_segment(opening, wall_map[opening["wall_id"]])),
                  fill=layer_color("opening"), width=7)
    for key, color_name in (("beams", "beam"), ("removed_walls", "removed")):
        for item in plan.get(key, []):
            draw.line(tx([item["a"], item["b"]]), fill=layer_color(color_name), width=6)
    return Image.alpha_composite(base, layer)


def draw_semantic_review(image: Image.Image, plan: dict, coeff: np.ndarray) -> Image.Image:
    """Add concise semantic IDs to the calibrated overlay for human review."""
    reviewed = draw_plan(image, plan, coeff)
    draw = ImageDraw.Draw(reviewed, "RGBA")
    wall_map = {wall["id"]: wall for wall in plan.get("walls", [])}

    def label(point, text, fill=(20, 20, 20, 255)):
        x, y = transform_point(coeff, point)
        box = draw.textbbox((x, y), text, anchor="mm")
        pad = 3
        draw.rectangle((box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad),
                       fill=(255, 255, 255, 215))
        draw.text((x, y), text, fill=fill, anchor="mm")

    legend = []
    for index, space in enumerate(plan.get("spaces", []), 1):
        polygon = space["polygon"]
        center = (sum(point[0] for point in polygon) / len(polygon),
                  sum(point[1] for point in polygon) / len(polygon))
        code = f"S{index}"
        label(center, code, (25, 70, 150, 255))
        legend.append((code, f"space/{space['id']}", (25, 70, 150, 255)))
    for index, opening in enumerate(plan.get("openings", []), 1):
        a, b = opening_segment(opening, wall_map[opening["wall_id"]])
        center = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        code = f"O{index}"
        label(center, code, (180, 80, 0, 255))
        if opening["kind"] == "window":
            vertical = (f"sill={opening.get('sill', 0)} "
                        f"height={opening.get('height', opening['head'] - opening.get('sill', 0))} "
                        f"head={opening['head']}")
        else:
            vertical = f"head={opening['head']}"
        legend.append((
            code, f"{opening['kind']}/{opening['id']} {vertical}",
            (180, 80, 0, 255)))
    for index, beam in enumerate(plan.get("beams", []), 1):
        center = ((beam["a"][0] + beam["b"][0]) / 2,
                  (beam["a"][1] + beam["b"][1]) / 2)
        code = f"B{index}"
        label(center, code, (110, 35, 140, 255))
        legend.append((code, f"beam/{beam['id']}", (110, 35, 140, 255)))

    columns = 2
    rows = math.ceil(len(legend) / columns)
    start_y = max(0, reviewed.height - rows * 14 - 8)
    column_width = reviewed.width // columns
    draw.rectangle((0, start_y - 4, reviewed.width, reviewed.height),
                   fill=(255, 255, 255, 235))
    for index, (code, description, color) in enumerate(legend):
        column = index // rows
        row = index % rows
        x = 10 + column * column_width
        y = start_y + row * 14
        draw.text((x, y), f"{code}  {description}", fill=color)
    return reviewed


def draw_shell_mask(size, plan: dict, coeff: np.ndarray) -> Image.Image:
    canvas = Image.new("L", size, 255)
    draw = ImageDraw.Draw(canvas)
    tx = lambda pts: [transform_point(coeff, p) for p in pts]
    for wall in plan.get("walls", []):
        draw.polygon(tx(wall_polygon(wall)), fill=0)
    for beam in plan.get("beams", []):
        proxy = {"a": beam["a"], "b": beam["b"], "thickness": beam["width"]}
        draw.polygon(tx(wall_polygon(proxy)), fill=0)
    return canvas


def draw_cut_mask(size, plan: dict, coeff: np.ndarray, cut_height_mm: float) -> Image.Image:
    """Draw the architectural shell intersected by a horizontal cut plane."""
    canvas = Image.new("L", size, 255)
    draw = ImageDraw.Draw(canvas)
    tx = lambda pts: [transform_point(coeff, p) for p in pts]
    for wall in plan.get("walls", []):
        draw.polygon(tx(wall_polygon(wall)), fill=0)
    wall_map = {wall["id"]: wall for wall in plan.get("walls", [])}
    for opening in plan.get("openings", []):
        sill = float(opening.get("sill", 0.0)) if opening["kind"] == "window" else 0.0
        head = float(opening["head"])
        if not sill <= cut_height_mm < head:
            continue
        wall = wall_map[opening["wall_id"]]
        a, b = opening_segment(opening, wall)
        opening_proxy = {
            "a": a,
            "b": b,
            "thickness": float(wall["thickness"]) + 40.0,
        }
        draw.polygon(tx(wall_polygon(opening_proxy)), fill=255)
    for beam in plan.get("beams", []):
        if float(beam["underside"]) <= cut_height_mm < float(beam["top"]):
            proxy = {"a": beam["a"], "b": beam["b"], "thickness": beam["width"]}
            draw.polygon(tx(wall_polygon(proxy)), fill=0)
    return canvas


def validate(plan: dict, residuals: np.ndarray) -> dict:
    errors, warnings = [], []
    wall_map = {}
    for wall in plan.get("walls", []):
        if wall["id"] in wall_map:
            errors.append(f"duplicate wall id: {wall['id']}")
        wall_map[wall["id"]] = wall
        if math.dist(wall["a"], wall["b"]) <= 0:
            errors.append(f"zero-length wall: {wall['id']}")
    for opening in plan.get("openings", []):
        wall = wall_map.get(opening["wall_id"])
        if wall is None:
            errors.append(f"opening {opening['id']} references missing wall {opening['wall_id']}")
            continue
        length = math.dist(wall["a"], wall["b"])
        if opening["offset"] < 0 or opening["offset"] + opening["width"] > length:
            errors.append(f"opening {opening['id']} lies outside wall {wall['id']}")
        if opening.get("kind") not in {"door", "window"}:
            errors.append(f"opening {opening['id']} has unsupported kind {opening.get('kind')}")
        sill = float(opening.get("sill", 0.0)) if opening.get("kind") == "window" else 0.0
        if float(opening.get("head", 0.0)) <= sill:
            errors.append(f"opening {opening['id']} head must be above sill")
        if "height" in opening and abs(
                float(opening["head"]) - sill - float(opening["height"])) > 1e-6:
            errors.append(
                f"opening {opening['id']} head-sill does not equal source height")
    space_ids = set()
    for space in plan.get("spaces", []):
        if space["id"] in space_ids:
            errors.append(f"duplicate space id: {space['id']}")
        space_ids.add(space["id"])
        polygon = space.get("polygon", [])
        if len(polygon) < 3:
            errors.append(f"space {space['id']} requires at least three polygon points")
            continue
        signed_area = sum(
            polygon[index][0] * polygon[(index + 1) % len(polygon)][1]
            - polygon[(index + 1) % len(polygon)][0] * polygon[index][1]
            for index in range(len(polygon))
        ) / 2.0
        if abs(signed_area) < 1.0:
            errors.append(f"space {space['id']} has zero-area polygon")
    for beam in plan.get("beams", []):
        if float(beam["top"]) <= float(beam["underside"]):
            errors.append(f"beam {beam['id']} top must be above underside")
    if not plan.get("excluded_regions"):
        warnings.append("no excluded regions recorded; confirm property ownership boundary")
    evidence_states = {item.get("status") for item in plan.get("evidence", [])}
    acceptance = plan.get("acceptance", {})
    acceptance_status = acceptance.get("status", "needs_review")
    if acceptance_status not in {"needs_review", "accepted"}:
        errors.append(f"unsupported acceptance status: {acceptance_status}")
    needs_review = ("missing" in evidence_states or "conflicting" in evidence_states
                    or acceptance_status != "accepted")
    if needs_review:
        warnings.append("plan has not passed the human 2D acceptance gate")
    status = "fail" if errors else ("needs_review" if needs_review else "pass")
    return {
        "status": status,
        "acceptance": {
            "status": acceptance_status,
            "note": acceptance.get("note"),
        },
        "calibration": {
            "anchor_count": int(len(residuals)),
            "rms_residual_px": float(np.sqrt(np.mean(residuals ** 2))),
            "max_residual_px": float(np.max(residuals)),
            "residuals_px": residuals.tolist(),
        },
        "counts": {
            "walls": len(plan.get("walls", [])),
            "openings": len(plan.get("openings", [])),
            "beams": len(plan.get("beams", [])),
            "removed_walls": len(plan.get("removed_walls", [])),
            "excluded_regions": len(plan.get("excluded_regions", [])),
            "spaces": len(plan.get("spaces", [])),
        },
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cut-height-mm", type=float, default=1200.0)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if plan.get("units") != "mm":
        raise ValueError("this artifact builder currently requires units=mm")
    reference = (args.plan.parent / plan["reference_image"]).resolve()
    image = Image.open(reference)
    coeff, residuals = fit_affine(plan["calibration"]["model_points"],
                                  plan["calibration"]["image_points"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_dxf(args.output_dir / "floorplan.dxf", plan)
    write_svg(args.output_dir / "floorplan.svg", plan)
    overlay = draw_plan(image, plan, coeff)
    overlay.save(args.output_dir / "floorplan_overlay.png")
    draw_semantic_review(image, plan, coeff).save(
        args.output_dir / "floorplan_semantic_review.png")
    blank = Image.new("RGBA", image.size, "white")
    draw_plan(blank, plan, coeff, opaque=True).save(args.output_dir / "floorplan_cad.png")
    draw_shell_mask(image.size, plan, coeff).save(args.output_dir / "floorplan_shell_mask.png")
    draw_cut_mask(image.size, plan, coeff, args.cut_height_mm).save(
        args.output_dir / f"floorplan_cut_{int(args.cut_height_mm)}_mask.png")
    report = validate(plan, residuals)
    report["cut_height_mm"] = args.cut_height_mm
    report["affine_model_to_image"] = coeff.tolist()
    (args.output_dir / "floorplan_validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] in {"pass", "needs_review"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
