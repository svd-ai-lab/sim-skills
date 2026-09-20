---
name: docx
description: Read, create and edit Word DOCX documents, including paragraphs, styles, tables, headers, figures and comments. Use for editable reports and document revisions, with PDF export and visual inspection when layout matters.
license: MIT
metadata:
  owner: svd-ai-lab/sim-skills
  source: https://github.com/svd-ai-lab/sim-skills/tree/main/docx
---

# Word documents

Work on explicit paths and retain the source. Discover available Word or
LibreOffice automation before choosing a rendering path. For document structure
use `python-docx`, for example `uv run --with python-docx script.py`. This workflow
uses local files and does not require an application account or a hosted API.

## Read

Open the file with `docx.Document(path)`. Inspect `iter_inner_content()` to retain
body paragraph/table order, then inspect sections, headers, footers, styles and
inline images as needed. Table cells can contain multiple paragraphs and nested
tables. Extracting only `document.paragraphs` omits important content. Revision
marks, text boxes, fields and drawings may require reading the OOXML archive or
using Word/LibreOffice. State missing coverage rather than inventing content.

## Create

Set the page size and section margins first. Define a small set of paragraph and
heading styles; use genuine headings and list numbering rather than repeated
manual formatting. Add captions and meaningful column labels. Fit tables and
images within the usable page width. Use page breaks only when needed for the
document structure. Save to a `.docx` file, then reopen it to verify text and
table values.

## Edit

Identify the exact paragraph, cell or run before modifying it. Preserve styles,
hyperlinks and surrounding formatting. A word may be split across runs: inspect
the run boundaries before replacing it. Assigning a whole paragraph's `.text`
recreates its runs and loses their formatting; do that only when this loss is
acceptable. Use targeted XML changes for unsupported structures after inspecting
the actual markup, keeping namespaces and relationships valid. Do not claim
tracked changes when making ordinary text replacements. Use document comments
or an explicit change summary if revision markup is unavailable.

## Render and verify

Use an available Word PDF export or LibreOffice conversion. With LibreOffice,
use a separate temporary user profile to avoid interfering with an open session:

```text
soffice -env:UserInstallation=file:///ABSOLUTE/TEMP/PROFILE --headless --convert-to pdf --outdir OUTPUT INPUT.docx
```

Pass each argument separately in a subprocess; construct the profile URI with
`Path.resolve().as_uri()`. Use a unique output directory and check the process
exit code and resulting PDF. Render that PDF with an available PDF renderer and
inspect every changed page for overflow, orphaned headings, broken tables,
missing glyphs and incorrect page breaks. Repeat after corrections. If no office
renderer is available, do structural checks and clearly label visual review as
not performed. Deliver the editable DOCX and the PDF when requested.

Reference: [python-docx documentation](https://python-docx.readthedocs.io/en/latest/).
