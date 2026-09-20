"""Render a PDF to numbered PNG files. MIT; svd-ai-lab/sim-skills/pdf."""

import argparse
from pathlib import Path

import pypdfium2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--scale", type=float, default=1.5)
    args = parser.parse_args()
    if not 0 < args.scale <= 8:
        parser.error("scale must be greater than zero and at most eight")
    args.output.mkdir(parents=True, exist_ok=True)
    with pypdfium2.PdfDocument(args.input) as document:
        for index in range(len(document)):
            page = document[index]
            try:
                bitmap = page.render(scale=args.scale)
                try:
                    destination = args.output / f"page-{index + 1:04d}.png"
                    bitmap.to_pil().save(destination)
                    print(destination.resolve())
                finally:
                    bitmap.close()
            finally:
                page.close()


if __name__ == "__main__":
    main()
