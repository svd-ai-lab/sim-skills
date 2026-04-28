# Known Issues — CalculiX Driver

## LD_LIBRARY_PATH required for Debian-packaged builds

**Discovered**: 2026-04-14
**Status**: Handled by driver
**Description**: The Debian `.deb` ccx links against `libspooles.so.2.2`
which lives in `/usr/lib/x86_64-linux-gnu` when installed via `apt`, but
when the .deb is extracted to a custom path the library is in
`<prefix>/usr/lib/x86_64-linux-gnu`. The driver auto-detects this layout
(`<ccx_dir>/../lib/x86_64-linux-gnu`) and sets `LD_LIBRARY_PATH` before
execution.

## glibc version mismatch for newer deb builds

**Discovered**: 2026-04-14
**Status**: Use buster-era .deb on buster systems
**Description**: CalculiX 2.17+ .deb packages are built against
glibc ≥ 2.29. Debian 10 (buster) has glibc 2.28 which is too old.
**Workaround**: Use the buster-era `calculix-ccx_2.11-1+b3_amd64.deb`
(available from snapshot.debian.org). The buster build works on buster
systems without glibc issues.

## Output files written next to the .inp

**Status**: By design
**Description**: `ccx <jobname>` writes `.frd`, `.dat`, `.sta`, `.cvg`,
`spooles.out` in the current working directory (== the .inp directory
when `sim run` is used). This pollutes `tests/fixtures/` if you run a
fixture directly. The E2E script uses `tempfile.TemporaryDirectory` to
isolate artifacts.

## ccx takes jobname without extension

**Status**: By design
**Description**: Unlike Abaqus (`abaqus job=X input=file.inp`), ccx takes
the jobname **without** `.inp`: `ccx beam` reads `beam.inp`. The driver
passes `script.stem`.

## No stdout version banner on 2.11

**Status**: Handled
**Description**: `ccx -v` on 2.11 prints "Usage: CalculiX.exe -i jobname"
with no version string. The driver falls back to parsing the installation
path (e.g. `calculix-2.11` in the dir name) to extract version.

## .dat is empty without *NODE PRINT

**Status**: User-input driven
**Description**: CalculiX writes to `.dat` only when the deck contains
`*NODE PRINT` or `*EL PRINT`. Without these keywords, `.dat` contains
only headers, no numeric data. `*NODE FILE` / `*EL FILE` write to `.frd`
instead (for visualization, harder to parse).
