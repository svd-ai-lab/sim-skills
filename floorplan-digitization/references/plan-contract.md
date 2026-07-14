# Architectural plan contract

Use one JSON document as the semantic source of truth. DXF and SVG are derived
review artifacts.

## Minimal shape

```json
{
  "schema_version": 1,
  "name": "example-plan",
  "units": "mm",
  "reference_image": "floorplan.png",
  "calibration": {
    "model_points": [[0, 0], [10000, 0], [0, 8000]],
    "image_points": [[120, 900], [1420, 900], [120, 120]]
  },
  "property_boundary": [[0, 0], [10000, 0], [10000, 8000], [0, 8000]],
  "excluded_regions": [],
  "walls": [],
  "openings": [],
  "beams": [],
  "columns": [],
  "removed_walls": [],
  "spaces": [],
  "evidence": []
}
```

## Walls

Represent straight walls by centre line and thickness:

```json
{
  "id": "wall-east",
  "a": [10000, 0],
  "b": [10000, 8000],
  "thickness": 280,
  "class": "exterior",
  "evidence": "known"
}
```

Split curved, stepped, or thickness-changing walls into stable segments.

## Openings

Assign every opening to one wall by ID. `offset` is measured from wall endpoint
`a` along its centre line.

```json
{
  "id": "window-east-bedroom",
  "kind": "window",
  "wall_id": "wall-east",
  "offset": 4200,
  "width": 1800,
  "sill": 650,
  "head": 1830,
  "evidence": "known"
}
```

Doors may add `swing`, `hinge`, and `opens_to`. Never encode an opening without
a host wall.

Verify the drawing's abbreviation convention before mapping vertical values.
On many Chinese architectural/interior drawings, `CH` means window height
(窗高) and `DH` means sill height (窗台高), so `head = DH + CH`; `CH` is not the
absolute head elevation. Preserve the source height and the derived head when
this convention is used, and validate that `head - sill == height`.

## Beams and removed walls

Represent a retained overhead beam independently from wall geometry. Give it a
plan segment, width, underside elevation, and top elevation. Record removed wall
segments separately so the 3D stage can preserve the historical/topological
meaning without generating a full-height wall.

## Spaces and exclusion

Spaces use closed polygons and stable names. `excluded_regions` must include
neighbour, common, void, or out-of-scope areas that might otherwise be mistaken
for the subject property.

## Evidence ledger

Use `known`, `derived`, `inferred`, `missing`, or `conflicting`. Each global
evidence entry should identify the source label or user confirmation. Do not
turn an inferred raster location into `known` merely because it looks aligned.
