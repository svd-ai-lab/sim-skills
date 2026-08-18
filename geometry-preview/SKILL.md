---
name: geometry-preview
description: Generate, preview, export, and sanity-check topology-aware 3D geometry before CAD or solver import. Use when users ask for text-to-geometry, parametric CAD, STEP/STL/mesh previews, geometry from sketches/images/papers/code, COMSOL/Fluent/Mechanical/Workbench/Abaqus geometry preflight, or fast iteration on dimensions, contacts, gaps, repeated cells, cavities, swept paths, porous structures, interlacing, membranes, or other geometry that should be checked before launching a heavy solver.
---

# Geometry Preview

## Overview

Use this skill to turn geometry intent into cheap, inspectable artifacts before
escalating to CAD kernels or solvers. Treat the workflow as guardrails, not a
fixed recipe: prefer the fastest artifact that can answer the current
uncertainty, and escalate immediately when the uncertainty is solver-specific.

## Exploration Ladder

Work from light to heavy, but skip upward when the task already demands a heavier
truth source.

1. Extract dimensions, units, parameters, coordinate frames, and topology
   invariants from the request.
2. Choose the smallest geometry representation that naturally expresses those
   invariants: analytic curve/surface, B-rep solid, semantic spline,
   graph-to-geometry generator, mesh, level set, or solver-native feature.
3. Generate a lightweight candidate with Python or browser-native geometry:
   `build123d`, `cadquery`, `trimesh`, `pyvista`, `gmsh`, `meshio`, or Three.js
   depending on what is installed and the artifact needed.
4. Produce review artifacts: at least one preview image or HTML viewer, plus an
   exported geometry artifact when useful (`.stl`, `.step`, `.msh`, `.vtk`,
   `.vtu`) and a short QA summary.
5. Check invariants directly: bounds, units, volume, surface/solid count,
   connected components, holes, contacts, gaps, clearances, self-intersections,
   non-manifold edges, repeated-cell continuity, and feature size versus target
   mesh size.
6. Escalate to a CAD kernel or solver only when the current uncertainty requires
   it: B-rep validity, STEP import, Boolean acceptance, meshing, named
   selections, physics/material/boundary binding, or solver-specific feature
   tags.

## Topology First Gate

Before making a pretty render, separate source authority:

- numeric authority: dimensions, coordinates, material thickness, pitch,
  clearance, feature size
- topology authority: CAD, reference code, equations, physical sketches, known
  connectivity, manufacturing constraints
- visual-only reference: screenshots, PPT drawings, non-dimensional meshes,
  icons, arrows, captions
- calibration target: points or images used to fit parameters, not necessarily
  ordered path constraints

Then write the non-negotiable topology:

- continuity: one body, many bodies, repeated cells, closed surface, open shell
- inside/outside: cavities, holes, membranes, channels, porous regions
- adjacency: contacts, gaps, bonded faces, shared boundaries, clearance targets
- ordering: over/under paths, front/back depth, layering, sweep direction
- periodicity: cell pitch, boundary continuation, mirrored or rotated repeats

Do not connect arbitrary points just because they are labeled. Treat points as
calibration targets unless the source explicitly says they are ordered path
points. Treat screenshots and hand sketches as visual references unless they
include explicit dimensions or coordinate data.

## Review Views

Use only the views needed to answer the current topology risk. For fragile
topology, generate more than one view before accepting the model:

- labeled single primitive or minimal repeat unit
- tiled or repeated cell when periodicity matters
- front view plus side/depth view when ordering or clearance matters
- back view or depth-colored view when front/back topology could be ambiguous
- exported geometry preview when CAD or solver transfer is expected

## Tool Choices

Prefer pip-ready tools for the first pass when they fit the task:

- `build123d` or `cadquery`: parametric B-rep CAD, Booleans, STEP/STL export.
- `trimesh`: mesh creation, repair attempts, mass properties, STL/OBJ/PLY IO,
  bounds, component counts, and quick surface checks.
- `pyvista`: 3D visualization, screenshots, mesh inspection, VTK/VTU outputs.
- `gmsh`: geometry/mesh preflight, `.msh` generation, feature-size and meshing
  failures before solver import.
- `meshio`: mesh conversion between `.msh`, `.vtk`, `.vtu`, `.xdmf`, and other
  solver-adjacent formats.
- Three.js or another lightweight viewer: interactive HTML preview when a
  browser artifact is more useful than a static image.

Do not assume any tool is installed. Probe the project environment first and use
the smallest install or fallback that fits the user's constraints.

Do not force this stack when another representation is more natural. A formula,
existing CAD file, solver-native feature tree, or project-specific generator can
be the better kernel.

## Artifact Contract

For geometry-generation tasks, try to leave a small artifact set:

- source script or notebook cell that regenerates the geometry
- preview image or HTML viewer
- export file when useful: `.step` for CAD/COMSOL, `.stl` for surface preview,
  `.msh` for mesh preflight, `.vtk`/`.vtu` for visualization
- QA notes listing dimensions, units, topology invariants, checks run, and known
  limitations

Say clearly what each artifact proves. A mesh preview does not prove COMSOL can
build the geometry; a STEP export does not prove physics selections are correct;
a successful Gmsh mesh does not prove the solver mesh will be acceptable.

Keep the artifact set proportional. A simple bracket may only need a script, one
preview, and a STEP file. A porous, interlaced, or repeated topology may need
multiple views and invariant notes.

## Solver Handoff Gate

Before calling a mesh solver-ready, verify the handoff rather than only the
picture or mesher exit code:

- units, scale, bounds, dimensionality, region count, and connected components
- required physical groups or named zones exist, are non-empty, and have the
  expected entity dimension
- boundary orientation and inside/outside assignment are consistent
- periodic partners have compatible topology, ordering, orientation, and
  transform; visual similarity alone is insufficient
- quality evidence names the metric, worst value, and location; do not apply a
  universal threshold without the target solver and element type
- a solver import or native mesh-check dry run can inventory the same regions
  and boundary names without silently dropping entities

Report the strongest state actually proven: `preview-ready`, `mesh-generated`,
`solver-imported`, or `setup-ready`. These states are not interchangeable.

## Solver Escalation

Use heavy solvers as authority layers, not as the first sketchpad.

- Escalate to COMSOL when the user needs `.mph` creation or inspection,
  geometry build, selections, mesh, material/physics/boundary binding, Java API
  tags/properties, or solver results.
- Escalate to Fusion, FreeCAD, or another CAD kernel when B-rep validity,
  feature history, editable solids, or STEP round-tripping is the question.
- Escalate to Fluent, Mechanical, Workbench, Abaqus, or STAR-CCM+ when the
  geometry must be imported into that solver's workflow or checked against its
  meshing/setup constraints.

If the user explicitly asks to work inside a solver, or provides a solver-native
model file, use the relevant solver skill directly and treat this skill as a
preflight companion.

## Failure Handling

- If a lightweight render looks right but topology checks fail, revise the
  geometry kernel instead of polishing the render.
- If B-rep export fails, reduce to the smallest failing primitive and record the
  failed operation.
- If continuity is only represented by captions, labels, arrows, or metadata,
  encode it in geometry or report that the model is only schematic.
- If a connector is patching a broken local primitive, revisit the kernel or
  parameterization instead of adding more connector patches.
- If solver import fails after lightweight checks pass, preserve both artifact
  sets and report the boundary: preview passed, solver-specific validation did
  not.
- If a task depends on software or licenses not visible in the environment,
  state the missing dependency and offer a lighter artifact that can still be
  produced.
