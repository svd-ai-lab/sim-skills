---
name: xlsx
description: Inspect, create and edit Excel XLSX workbooks with formulas, tables, charts and formatting. Use for spreadsheet reports, calculations and data cleanup; verify values and rendered output with an available spreadsheet application.
license: MIT
metadata:
  owner: svd-ai-lab/sim-skills
  source: https://github.com/svd-ai-lab/sim-skills/tree/main/xlsx
---

# Excel workbooks

Use local files and explicit output paths. Preserve the original workbook.
Discover installed spreadsheet tools first. For OOXML manipulation use openpyxl,
for example `uv run --with openpyxl --with defusedxml script.py`. No hosted service
or application account is required.

## Inspect

Load formulas with `openpyxl.load_workbook(path, data_only=False)`; inspect sheet
names, used ranges, dimensions, merged cells, tables, charts, named ranges and
external links relevant to the task. For a large read-only extraction use
`read_only=True` and bounded iteration. A second load with `data_only=True`
returns cached results, which can be absent or stale. Do not save that second
workbook over the formula-bearing original. Use `keep_vba=True` for a supported
macro-enabled file and preserve its extension; do not execute its macros.

## Create and edit

Use clear sheet names, headers with units, consistent number formats, sensible
column widths and frozen headers. Put changeable assumptions in labeled cells;
reference them with formulas instead of embedding duplicate constants. Use
formulas for calculated results and inspect references after inserts or moves.
Never turn imported text beginning with formula markers into executable formulas
unless that is intended. Preserve existing formatting and validation rules when
editing a template. Work in the original format when unsupported charts,
embedded objects, signatures or macros must be preserved; a library round trip
may not retain every Excel feature.

For printable reports set print area, orientation, margins, scaling and repeated
header rows. Choose chart types and scales that reflect the data and label axes
with units. Avoid merging cells inside sortable data tables.

## Calculate and verify

openpyxl writes formulas but does not calculate them. Recalculate with an
available Excel or LibreOffice engine, save a copy, then inspect both formulas
and cached results. Check totals against independent arithmetic, spot-check edge
cases, and reject unexpected `#REF!`, `#DIV/0!`, `#VALUE!` or other error cells.
Do not report a formula as evaluated merely because it exists in the file.

Export relevant sheets to PDF with the spreadsheet engine and inspect rendered
pages for truncated labels, unreadable scales and missing columns. A unique
LibreOffice profile can be passed as `-env:UserInstallation=<file URI>` together
with `--headless --convert-to pdf --outdir OUTPUT INPUT.xlsx`. Construct arguments
as an array and check both exit status and output existence. When no calculation
or rendering engine is installed, report the exact verification that remains.
Deliver the editable workbook with concise notes on assumptions and sources.

Reference: [openpyxl documentation](https://openpyxl.readthedocs.io/en/stable/).
