# Recipe schema

A recipe is a JSON document that describes a sequence of `newton.ModelBuilder` method calls. The driver re-executes it end-to-end; there is no opaque binary blob — the recipe IS the model.

## Top-level structure

```json
{
  "schema": "sim/newton/recipe/v1",
  "ops": [ { "op": "<method_name>", "args": { ... } } ],
  "post_finalize": { ... }
}
```

`schema` must be `"sim/newton/recipe/v1"` or (legacy) `"newton-cli/recipe/v1"`. Any other value is a lint error.

Each entry in `ops` is dispatched via `getattr(builder, op)` unless it matches a **special op** (see below). `args` is a JSON object whose values are automatically coerced from JSON-friendly shapes into Warp types.

## Arg coercion

| JSON shape | Coerced to |
|---|---|
| `[x, y, z]` (3 numbers) | `wp.vec3(x, y, z)` |
| `[x, y, z, w]` (4 numbers) | `wp.quat(x, y, z, w)` |
| `{"axis":[x,y,z], "angle":t}` | `wp.quat_from_axis_angle(axis, t)` |
| `{"p": <vec3>, "q": <quat>}` | `wp.transform(p=..., q=...)` |
| list of `vec3`s or `quat`s | list of coerced elements |
| `{"$shape_cfg": {...}}` | `ModelBuilder.ShapeConfig(**...)` |
| `{"$heightfield": {...}}` | `newton.Heightfield(...)` |
| `{"$mesh": {...}}` | `newton.Mesh(vertices, indices, ...)` |
| `{"$mesh_from_usd": {...}}` | `newton.usd.get_mesh(...)` |

## Builder methods (the common core)

Any method on `newton.ModelBuilder` is callable as an op. The ones every workflow touches:

- `add_link` / `add_body` — articulation nodes
- `add_shape_box` / `add_shape_sphere` / `add_shape_capsule` / `add_shape_mesh` / `add_shape_plane`
- `add_joint_revolute` / `add_joint_prismatic` / `add_joint_fixed` / `add_joint_free` / `add_joint_spherical`
- `add_articulation`
- `add_ground_plane`
- `add_usd` (requires `newton[importers]`) — import USD stage
- `add_urdf` / `add_mjcf` — import URDF / MJCF
- `add_cloth_grid` / `add_particles`

## Special ops (non-method helpers)

These are not builder methods; they're interpreter-level primitives:

| Op | Purpose |
|---|---|
| `set_builder_array` | Write one element / slice / fill into a builder list (e.g. `joint_target_ke`). |
| `set_builder_attr` | Set a scalar attribute on the builder (e.g. `rigid_gap`). |
| `set_default_joint_cfg` | Populate `builder.default_joint_cfg` with scalar fields. |
| `set_default_shape_cfg` | Populate `builder.default_shape_cfg` with scalar fields. |
| `apply_body_inertia_diagonal` | Add `eye(3) * value` to every body's inertia (armature trick). |
| `pin_body` | Zero mass + inertia of a body to pin it in world. |
| `register_mujoco_custom_attributes` | Call before `add_mjcf` / `add_usd` to parse MuJoCo-native custom attrs. |
| `register_solver_custom_attributes` | Generic form with `{"solver": "SolverImplicitMPM"}`. |
| `replicate` | Build a sub-builder from an inline recipe, then `outer.replicate(sub, count, spacing)`. |

## `post_finalize`

Scalar fields applied to the finalized `Model`:

```json
"post_finalize": {
  "soft_contact_ke": 100.0,
  "soft_contact_kd": 0.0
}
```

Structured forms (recognized by reserved key):

```json
"post_finalize": {
  "mpm_attrs": [
    {"attr": "yield_pressure", "range": [0, 500], "value": 2.0e4},
    {"attr": "density", "indices": [0, 3, 7], "value": 1500.0}
  ],
  "model_calls": [
    {"method": "allocate_soft_contact_friction", "args": [], "kwargs": {}}
  ]
}
```

## Running a recipe

```bash
sim run my_recipe.json --solver newton
```

The step loop defaults to `SolverXPBD`, 60 frames, 60 fps, 10 substeps. Override via env:

```bash
NEWTON_RECIPE_SOLVER=SolverMuJoCo NEWTON_RECIPE_FRAMES=200 sim run my_recipe.json --solver newton
```

## Output

The driver writes `final.npz` into the artifact dir and emits a `sim/newton/v1` envelope on stdout:

```json
{
  "schema": "sim/newton/v1",
  "data": {
    "state_path": ".../final.npz",
    "solver": "SolverXPBD",
    "num_frames": 60,
    "body_count": 2,
    "joint_count": 2,
    "shape_count": 2,
    "artifacts": [{"path": "...", "kind": "state", "size": 1024}]
  }
}
```
