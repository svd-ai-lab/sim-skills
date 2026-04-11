# FloSCRIPT Modeling Reference

Generate Flotherm models from natural language by producing FloSCRIPT
XML that `sim exec` plays step by step. Each step is a separate file
validated via `sim lint` before playback.

## Workflow

```
sim connect --solver flotherm --ui-mode gui
# For each step:
#   1. Generate stepN.xml
#   2. sim lint stepN.xml          ← XSD validates automatically
#   3. sim exec stepN.xml          ← plays in Flotherm GUI
#   4. sim screenshot              ← verify visually
# When done:
sim disconnect
```

## Step Template

Every step file must follow this structure:

```xml
<?xml version="1.0"?>
<xml_log_file version="1.0">
    <!-- modeling commands here -->

    <!-- checkpoint (use incrementing names) -->
    <project_save_as project_name="model_stepN"
                     project_title="Description of what this step did"/>
</xml_log_file>
```

## Crash Recovery

If the session dies mid-build, reload from the last checkpoint:

```xml
<xml_log_file version="1.0">
    <project_load project_name="model_step2"/>
    <!-- continue from step 3 -->
</xml_log_file>
```

---

## Command Reference

### Create geometry

```xml
<create_geometry geometry_type="TYPE">
    <source_geometry>
        <geometry name="PARENT_ASSEMBLY"/>
    </source_geometry>
</create_geometry>
```

**Common geometry types** (full list in XSD schema):

| Type | Use for |
|---|---|
| `cuboid` | Generic block, board, wall, enclosure wall |
| `source` | Heat source (power dissipation) |
| `fan` | Axial or radial fan |
| `heatSink` | Finned heat sink |
| `pcb` | Printed circuit board (with layers) |
| `pcbComponent` | Component on PCB |
| `enclosure` | Box/chassis around components |
| `cylinder` | Round geometry (pipes, posts) |
| `resistance` | Thermal interface material (TIM) |
| `monitorPoint` | Temperature probe point |
| `assembly` | Grouping container |
| `hole` | Ventilation opening in enclosure |
| `cooler` | Liquid cooling block |
| `heatPipe` | Heat pipe |
| `tec` | Thermoelectric cooler |
| `die` | Semiconductor die (with discrete sources) |
| `rack` | Equipment rack |

### Rename geometry

Rename immediately after create — default names are generic (`Cuboid`, `Source`, etc.).

```xml
<rename_geometry new_name="MyChip">
    <geometry_name>
        <geometry name="Root Assembly">
            <geometry name="Source" position_in_parent="INDEX"/>
        </geometry>
    </geometry_name>
</rename_geometry>
```

### Modify geometry

Set size, position, material, power, or any property:

```xml
<modify_geometry new_value="VALUE" property_name="PROPERTY">
    <geometry_name>
        <geometry name="Root Assembly">
            <geometry name="MyChip" position_in_parent="INDEX"/>
        </geometry>
    </geometry_name>
</modify_geometry>
```

**Common properties:**

| Property | Applies to | Example |
|---|---|---|
| `sizeX`, `sizeY`, `sizeZ` | All geometry | `"0.05"` (meters) |
| `positionX`, `positionY`, `positionZ` | All geometry | `"0.01"` |
| `material` | cuboid, resistance | `"Aluminum"` |
| `power` | source | `"5.0"` (watts) |
| `finHeight` | heatSink | `"0.02"` |
| `numberOfFins` | heatSink | `"12"` |
| `finThickness` | heatSink | `"0.001"` |
| `flowRate` | fan | `"0.01"` (m³/s) |
| `conductivity` | resistance | `"5.0"` (W/m·K) |

### Create attribute

Attributes control grid, materials, boundary conditions, etc.:

```xml
<create_attribute attribute_type="TYPE" id="ATTR_NAME"/>
```

**Attribute types:** `ambient`, `control`, `fluid`, `gridConstraint`,
`material`, `occupancy`, `radiation`, `resistance`, `source`, `surface`,
`surfaceExchange`, `thermal`, `transient`

### Modify attribute

```xml
<modify_attribute new_value="VALUE" property_name="PROPERTY">
    <attribute_name id="ATTR_NAME"/>
</modify_attribute>
```

### Delete geometry

```xml
<delete_geometry>
    <geometry_name>
        <geometry name="Root Assembly">
            <geometry name="OldPart" position_in_parent="INDEX"/>
        </geometry>
    </geometry_name>
</delete_geometry>
```

### Save project

```xml
<project_save_as project_name="NAME" project_title="TITLE"/>
```

### Solve

```xml
<start start_type="solver"/>
```

---

## Geometry Naming and `position_in_parent`

**Critical:** `position_in_parent` is a 0-based index within the parent
assembly, assigned in creation order. When you create the 3rd object
under `Root Assembly`, it gets `position_in_parent="2"`.

**Best practice:**
1. Create geometry → immediately rename to a meaningful name
2. Reference by name (not index) in subsequent steps
3. After renaming, use the new name in the `<geometry name="...">` path

```xml
<!-- Step 1: Create and rename -->
<create_geometry geometry_type="cuboid">
    <source_geometry><geometry name="Root Assembly"/></source_geometry>
</create_geometry>
<rename_geometry new_name="BoardBase">
    <geometry_name>
        <geometry name="Root Assembly">
            <geometry name="Cuboid" position_in_parent="0"/>
        </geometry>
    </geometry_name>
</rename_geometry>

<!-- Step 1 continued: modify using the renamed name -->
<modify_geometry new_value="0.1" property_name="sizeX">
    <geometry_name>
        <geometry name="Root Assembly">
            <geometry name="BoardBase" position_in_parent="0"/>
        </geometry>
    </geometry_name>
</modify_geometry>
```

**Important:** Even after renaming, you still need
`position_in_parent` in the path. The name changes but the index
doesn't.

---

## Common Patterns

### PCB with chip and heat sink

```xml
<xml_log_file version="1.0">
    <!-- PCB: 100mm × 80mm × 1.6mm -->
    <create_geometry geometry_type="pcb">
        <source_geometry><geometry name="Root Assembly"/></source_geometry>
    </create_geometry>
    <rename_geometry new_name="MainPCB">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="PCB" position_in_parent="0"/>
            </geometry>
        </geometry_name>
    </rename_geometry>
    <modify_geometry new_value="0.1" property_name="sizeX">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="MainPCB" position_in_parent="0"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.08" property_name="sizeY">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="MainPCB" position_in_parent="0"/>
            </geometry>
        </geometry_name>
    </modify_geometry>

    <!-- Chip: 10mm × 10mm × 2mm, 5W, centered on PCB -->
    <create_geometry geometry_type="source">
        <source_geometry><geometry name="Root Assembly"/></source_geometry>
    </create_geometry>
    <rename_geometry new_name="Chip">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Source" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </rename_geometry>
    <modify_geometry new_value="0.01" property_name="sizeX">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chip" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.01" property_name="sizeY">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chip" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.002" property_name="sizeZ">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chip" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.045" property_name="positionX">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chip" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.035" property_name="positionY">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chip" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.0016" property_name="positionZ">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chip" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="5.0" property_name="power">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chip" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </modify_geometry>

    <!-- Heat sink: 30mm × 30mm, on top of chip -->
    <create_geometry geometry_type="heatSink">
        <source_geometry><geometry name="Root Assembly"/></source_geometry>
    </create_geometry>
    <rename_geometry new_name="HS1">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Heat Sink" position_in_parent="2"/>
            </geometry>
        </geometry_name>
    </rename_geometry>
    <modify_geometry new_value="0.03" property_name="sizeX">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="HS1" position_in_parent="2"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.03" property_name="sizeY">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="HS1" position_in_parent="2"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.04" property_name="positionX">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="HS1" position_in_parent="2"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.025" property_name="positionY">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="HS1" position_in_parent="2"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.0036" property_name="positionZ">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="HS1" position_in_parent="2"/>
            </geometry>
        </geometry_name>
    </modify_geometry>

    <!-- Monitor point at chip center -->
    <create_geometry geometry_type="monitorPoint">
        <source_geometry><geometry name="Root Assembly"/></source_geometry>
    </create_geometry>
    <modify_geometry new_value="0.05" property_name="positionX">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Monitor Point" position_in_parent="3"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.04" property_name="positionY">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Monitor Point" position_in_parent="3"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.003" property_name="positionZ">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Monitor Point" position_in_parent="3"/>
            </geometry>
        </geometry_name>
    </modify_geometry>

    <project_save_as project_name="pcb_chip_hs"
                     project_title="PCB with chip source and heat sink"/>
</xml_log_file>
```

### Enclosure with fan (natural convection + forced air)

```xml
<xml_log_file version="1.0">
    <!-- Enclosure: 200mm × 150mm × 50mm -->
    <create_geometry geometry_type="enclosure">
        <source_geometry><geometry name="Root Assembly"/></source_geometry>
    </create_geometry>
    <rename_geometry new_name="Chassis">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Enclosure" position_in_parent="0"/>
            </geometry>
        </geometry_name>
    </rename_geometry>
    <modify_geometry new_value="0.2" property_name="sizeX">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chassis" position_in_parent="0"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.15" property_name="sizeY">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chassis" position_in_parent="0"/>
            </geometry>
        </geometry_name>
    </modify_geometry>
    <modify_geometry new_value="0.05" property_name="sizeZ">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Chassis" position_in_parent="0"/>
            </geometry>
        </geometry_name>
    </modify_geometry>

    <!-- Fan at inlet -->
    <create_geometry geometry_type="fan">
        <source_geometry><geometry name="Root Assembly"/></source_geometry>
    </create_geometry>
    <rename_geometry new_name="InletFan">
        <geometry_name>
            <geometry name="Root Assembly">
                <geometry name="Fan" position_in_parent="1"/>
            </geometry>
        </geometry_name>
    </rename_geometry>

    <project_save_as project_name="chassis_fan"
                     project_title="Enclosure with inlet fan"/>
</xml_log_file>
```

---

## Pitfalls

1. **Units are always SI** (meters, watts, kg, K). No unit conversion —
   `sizeX="0.01"` means 10 mm.

2. **Default names vary by type.** `cuboid` → `"Cuboid"`, `source` →
   `"Source"`, `heatSink` → `"Heat Sink"` (with space), `fan` → `"Fan"`,
   `pcb` → `"PCB"`, `monitorPoint` → `"Monitor Point"`.
   When creating a second of the same type, Flotherm appends `:1`
   (e.g. `"Cuboid:1"`).

3. **`position_in_parent` is required** even when referencing by name.
   It's the creation order index (0-based) under the parent assembly.

4. **Lint before play.** `sim lint stepN.xml` catches typos in
   geometry_type, unknown commands, and structural errors — with line
   numbers. Fix all errors before `sim exec`.

5. **One step per file** for the iterate loop. Don't put the entire
   model in one file — if step 5 fails, you'd have to regenerate
   everything.

6. **Always `project_save_as` at the end of each step** so you have a
   checkpoint to recover from.

7. **XML comments are allowed** inside `<xml_log_file>` and are useful
   for documenting what each section does.
