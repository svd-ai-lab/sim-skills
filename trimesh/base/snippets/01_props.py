"""Step 1: Box + sphere geometric properties (verified E2E).

Box(2, 3, 4): V=24 (exact), A=52 (exact)
Sphere(r=1, subdiv=4): V≈4.180 (theory 4.189, 0.2% err)
                      A≈12.55 (theory 12.57, 0.1% err)

Run: sim run 01_props.py --solver trimesh
"""
import json
import math
import trimesh


def main():
    box = trimesh.creation.box(extents=[2.0, 3.0, 4.0])
    sphere = trimesh.creation.icosphere(subdivisions=4, radius=1.0)
    sph_v_th, sph_a_th = 4/3*math.pi, 4*math.pi

    print(json.dumps({
        "ok": bool(
            abs(box.volume - 24.0) < 1e-10
            and abs(sphere.volume - sph_v_th) / sph_v_th < 0.05
        ),
        "box_volume": float(box.volume),
        "box_area": float(box.area),
        "sphere_volume": float(sphere.volume),
        "sphere_volume_theory": sph_v_th,
        "sphere_area": float(sphere.area),
        "sphere_area_theory": sph_a_th,
    }))


if __name__ == "__main__":
    main()
