---
name: pdf
description: Read, create, combine, annotate, or revise PDF documents using local Python libraries and inspect rendered pages. Use for PDF reports, forms, page operations, and extracted text; route source Word or Excel edits to their corresponding skills.
license: MIT
metadata:
  owner: svd-ai-lab/sim-skills
  source: https://github.com/svd-ai-lab/sim-skills/tree/main/pdf
---

# PDF documents

Resolve input and output paths explicitly. Keep the original file and save edits
to a new path unless the user asked for replacement. Prefer an installed local
tool; otherwise use a project environment, for example
`uv run --with pypdf --with reportlab --with pypdfium2 --with pillow script.py`.
No hosted service or application account is required.

## Read and inspect

Use `pypdf.PdfReader(path)` to inspect metadata, page count, outlines, forms and
`page.extract_text()`. Keep page numbers with extracted evidence. Text extraction
does not establish layout or reading order. Render tables, plots, equations and
columns before interpreting them. For image-only scans use an available OCR
engine, retain the original page, and flag uncertain characters. Do not treat an
empty extracted string as an empty page. Encrypted documents require the user's
authorized password; never print it.

Run the bundled renderer using its path relative to this skill directory:

```text
uv run --with pypdfium2 --with pillow scripts/render_pdf.py input.pdf output-pages
```

It writes numbered PNGs without modifying the PDF. Open the relevant PNGs with
the available image viewer. PDFium is a renderer, not an OCR engine.

## Create and edit

For a report, use ReportLab `SimpleDocTemplate`, `Paragraph`, `Table`, and
`PageBreak` with explicit page size and margins. Use paragraph styles for
headings, wrapping, spacing and captions. Register an appropriate licensed font
for the actual text, especially non-Latin characters. Escape user text when
feeding ReportLab's paragraph markup.

Use `PdfWriter` to append, reorder, rotate or crop existing pages and to update
supported fields. For a visible annotation or watermark, create a correctly
sized overlay and merge it onto the target page. Ordinary overlays do not erase
underlying text. For removal of confidential content, use a tool with actual
redaction support and verify the removed content is absent from extraction and
embedded objects. For substantial prose edits, modify the source document when
available and export again instead of painting over the old text.

## Verify delivery

Reopen the saved PDF, check page count and required text, then render every
changed page. Inspect clipping, glyphs, margins, table splits and captions at
readable resolution. Verify forms after saving. Report any rendering or OCR
limitations honestly and link the final PDF using an absolute path.

API references: [pypdf](https://pypdf.readthedocs.io/en/stable/),
[ReportLab](https://docs.reportlab.com/),
[pypdfium2](https://pypdfium2.readthedocs.io/en/stable/).
