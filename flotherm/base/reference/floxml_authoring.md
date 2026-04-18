# FloXML Authoring Reference

The vendor-blessed format for **authoring** Flotherm models from scratch.
FloSCRIPT is the wrong tool for this — use it only for orchestration and
parametric sweeps over an existing model. See
[`floscript_modeling.md`](floscript_modeling.md) for the FloSCRIPT side.

## Why FloXML

| | FloSCRIPT | FloXML |
|---|---|---|
| Designed for | record-and-replay of GUI actions | model authoring / import |
| Property names | undocumented internal enums | named XML elements (self-documenting) |
| Schema | `xs:string` for everything semantic | rich, all elements typed |
| Examples shipped | `Utilities/Grid-HeatSinks-and-Fans.xml` only | `Project FloXML Examples/`, `Assembly FloXML Examples/` |
| Authoring works | structural geometry only (size/position) | yes |

## Pipeline

```
1. Author Project FloXML  (full model in one <xml_case> file)
2. <project_import filename="..." import_type="FloXML"/>   ← via FloSCRIPT
3. <project_save_as project_name="..."/>                    ← creates .pack
4. <start start_type="solver"/>                             ← solve
5. Read .pack solution dir for results
```

## Reference templates (in install)

```
C:\Program Files\Siemens\SimcenterFlotherm\2504\examples\FloXML\FloXML Files\
├── Assembly FloXML Examples\
│   ├── Block.xml                      # 31 lines: minimal cuboid + material
│   ├── 2R-Model.xml                   # network resistance assembly
│   └── Nested-Assemblies.xml          # nested geometry tree
└── Project FloXML Examples\
    ├── Default.xml                    # bare project (no geometry)
    ├── Heatsink-Windtunnel-FullModel.xml   # full case: heatsink + fixed flow + source ★
    └── All-Objects-Attributes-Settings-FullModel.xml  # every supported element
```

**Start from `Heatsink-Windtunnel-FullModel.xml`** for any new
authored model — it's the smallest complete project FloXML with
geometry + attributes + boundaries + solver settings.

## Project FloXML structure

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<xml_case>
  <name>MyProject</name>
  <model>            <!-- modeling, turbulence, gravity, global -->
  <solve>            <!-- overall_control: iterations, relaxation -->
  <grid>             <!-- system_grid x/y/z resolution -->
  <attributes>       <!-- materials, sources, ambients, fluids, etc -->
  <geometry>         <!-- cuboids, sources, monitor_points -->
  <solution_domain>  <!-- bounding box + boundary BCs -->
</xml_case>
```

## Material attribute (canonical)

```xml
<attributes>
  <materials>
    <isotropic_material_att>
      <name>Silicon</name>
      <conductivity>148</conductivity>     <!-- W/m·K -->
      <density>2330</density>              <!-- kg/m³ -->
      <specific_heat>700</specific_heat>   <!-- J/kg·K -->
      <electrical_resistivity>
        <type>constant</type>
        <resistivity_value>0</resistivity_value>
      </electrical_resistivity>
    </isotropic_material_att>
  </materials>
</attributes>
```

For anisotropic, use `<orthotropic_material_att>` with `<x_conductivity>`,
`<y_conductivity>`, `<z_conductivity>` (note: snake_case prefix, NOT
`conductivity_x`).

## Source attribute (canonical)

```xml
<attributes>
  <sources>
    <source_att>
      <name>Source_3W</name>
      <source_options>
        <option>
          <applies_to>temperature</applies_to>
          <type>total</type>
          <value>0</value>
          <power>3</power>                <!-- Watts -->
          <linear_coefficient>0</linear_coefficient>
        </option>
      </source_options>
    </source_att>
  </sources>
</attributes>
```

## Geometry: cuboid + material attachment

```xml
<geometry>
  <cuboid>
    <name>BaseDie</name>
    <active>true</active>
    <position><x>0</x><y>0</y><z>0</z></position>
    <size><x>0.011</x><y>0.0001</y><z>0.011</z></size>     <!-- meters -->
    <orientation>
      <local_x><i>1</i><j>0</j><k>0</k></local_x>
      <local_y><i>0</i><j>1</j><k>0</k></local_y>
      <local_z><i>0</i><j>0</j><k>1</k></local_z>
    </orientation>
    <material>Silicon</material>                            <!-- attribute reference by name -->
    <localized_grid>false</localized_grid>
  </cuboid>
</geometry>
```

## Geometry: source (heater) referencing source attribute

```xml
<source>
  <name>BaseDie_Heater</name>
  <active>true</active>
  <position><x>0.001</x><y>0.00005</y><z>0.001</z></position>
  <size><x>0.009</x><y>0.00001</y><z>0.009</z></size>      <!-- thin slab inside the die -->
  <orientation>...</orientation>
  <source>Source_3W</source>                                <!-- attribute reference by name -->
  <localized_grid>false</localized_grid>
</source>
```

The `<source>` geometry overlaps the heat-generating volume of the die.
Make it thin (e.g. 10 µm) and slightly inset from the die edges to
ensure cells are captured.

## Solution domain (bounding box + BCs)

```xml
<solution_domain>
  <position><x>-0.005</x><y>-0.001</y><z>-0.005</z></position>
  <size><x>0.021</x><y>0.011</y><z>0.021</z></size>
  <x_low_ambient>Ambient</x_low_ambient>
  <x_high_ambient>Ambient</x_high_ambient>
  <y_low_boundary>symmetry</y_low_boundary>
  <y_high_ambient>Ambient</y_high_ambient>
  <z_low_ambient>Ambient</z_low_ambient>
  <z_high_ambient>Ambient</z_high_ambient>
  <fluid>Air</fluid>
</solution_domain>
```

Each face of the bounding box is either:
- `<face_ambient>NameOfAmbientAttribute</face_ambient>` (open to ambient)
- `<face_boundary>symmetry</face_boundary>` (mirror)

## Importing into Flotherm

```xml
<!-- via FloSCRIPT -->
<xml_log_file version="1.0">
  <project_import filename="C:/path/to/model.xml" import_type="FloXML"/>
</xml_log_file>
```

Then inside the same FloSCRIPT or a follow-up:

```xml
<xml_log_file version="1.0">
  <project_save_as project_name="my_project"/>
  <start start_type="solver"/>
</xml_log_file>
```

## Result extraction

After solve, results live at:
```
flouser/<project_name>.<32-hex-hash>/DataSets/BaseSolution/
  PDTemp/logit                       # solver residuals (text)
  msp_0/end/Temperature              # binary float32, 4-byte header + nx*ny*nz floats
  msp_0/end/Pressure                 # same layout
  msp_0/end/{X,Y,Z}Velocity          # same layout
  msp_0/end/Speed                    # |velocity|
```

Mesh dimensions (`nx`, `ny`, `nz`) are in the logit file:
`domain 0 no. in x =NN no. in y =NN no. in z =NN`.

Field cells are in Fortran/C-order; verify by sampling a known cell
(e.g. far-field ambient should match the ambient_att temperature).

## End-to-end example

See [hbm-flotherm/build/hbm_3block.xml](https://github.com/svd-ai-lab/hbm-flotherm/blob/main/build/hbm_3block.xml)
for a complete 3-block HBM stack (cuboids + materials + sources +
monitor points + boundaries) that imports + solves cleanly on
Flotherm 2504.

## Gotchas

### `solve_all` is not top-level FloSCRIPT — use `<start start_type="solver"/>`
`<solve_all/>` is valid only inside `external_command process="MCAD"`
scenario contexts. Top-level FloSCRIPT solve element is `<start>`.

### Don't sweep imports back-to-back
Each `<project_import>` opens the imported project as a NEW Flotherm
window. ~10 in a row exhausted Flotherm and crashed all instances.
**One import per session, then operate on it.**

### Mesh tuning matters
The default `system_grid` `max_size` of 0.001 m gives ~10K cells for
a 21mm domain. For HBM-scale (sub-millimeter features), drop `min_size`
to 1e-5 and `max_size` to 5e-4 for the y-axis (vertical, where layers
are thinnest).

### Coordinate units are meters
Throughout — sizes, positions, etc. Convert from mm to m before writing.

### "FluidConductivity" appears in solution dir even for solid-only models
That's fine. The solver always outputs the air fluid conductivity field
because the solution domain has fluid bg.
