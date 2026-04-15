# PyMAPDL 0.72 SDK notes

Covers ansys-mapdl-core 0.68 ≤ SDK < 0.80.

## Verified API

- `launch_mapdl(exec_file=..., run_location=..., nproc=..., loglevel="ERROR")` — stable
- `Mapdl(ip, port)` — connect to already-running gRPC server
- `mapdl.prep7()`, `mapdl.solution()`, `mapdl.slashsolu()`, `mapdl.post1()`, `mapdl.finish()` — processor control
- `mapdl.post_processing.nodal_displacement("X"|"Y"|"Z"|"NORM")` → numpy
- `mapdl.post_processing.nodal_eqv_stress()` → numpy
- `mapdl.post_processing.plot_*(savefig=..., off_screen=True, window_size=(w,h), cmap=..., show_edges=True)` — headless PNG
- `mapdl.result` → `ansys.mapdl.reader.Result` — file-based access
- `mapdl.mesh.nnum`, `mapdl.mesh.nodes`, `mapdl.mesh.enum` — mesh introspection
- `mapdl.parameters[name]` — APDL scalar params
- `mapdl.input(path)`, `mapdl.input_strings(text)` — run legacy APDL
- `mapdl.with non_interactive:` — buffer `*DO`/`*IF` blocks
- `mapdl.convert_script(in, out, macros_as_functions=True)` — APDL → Python

## Ship-blocking bugs

None known at 0.72.1.

## Deprecation warnings (cosmetic only)

- `ansys-tools-path` is being migrated to `ansys-tools-common`; the
  warning fires on first `find_mapdl()` / `launch_mapdl()`. No
  functional impact.
- `PyVistaFutureWarning` on `UnstructuredGrid.extract_surface` —
  plots still render correctly.

## Newer SDK pre-release

SDK ≥ 0.80 is expected to drop `ansys-tools-path` and vendor in
`ansys-tools-common`. Keep an eye on imports; the public PyMAPDL API
itself is stable.
