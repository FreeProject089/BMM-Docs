#!/usr/bin/env python3
"""Prove the generated PDF actually contains the documentation.

Why this exists: the published PDF was 8 pages. Not "8 pages of a section" — the whole
book, cover + table of contents + the first three articles, and then it simply stopped
mid-heading. The table of contents listed all 40 pages; every entry outside "Getting
started" resolved to page 0, which is what mkdocs-with-pdf writes when it cannot find the
anchor in the rendered document. Both the English and the French PDF stopped at exactly
8 pages despite different text, so it is not a content coincidence.

Nothing upstream noticed. `mkdocs build` exited 0, the artifact uploaded, Pages deployed,
and the only signal was a reader opening the file. The build cannot tell whether WeasyPrint
laid out what it was handed, so this reads the finished PDF back and says so.

Run: python tools/check_pdf.py site/pdf/bettermodsmanager.pdf --min-pages 40
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - a missing dep is a setup error, not a doc error
    print("pypdf is required: pip install -r requirements.txt", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument(
        "--min-pages",
        type=int,
        default=40,
        help="floor, not a target — the docs are ~40 markdown pages, so a PDF under this "
        "has dropped whole sections",
    )
    ap.add_argument(
        "--expect",
        action="append",
        default=[],
        help="text that must appear somewhere in the PDF; repeatable. Use a phrase from a "
        "LATE page — a truncated render still contains all the early ones.",
    )
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"::error::{args.pdf} was not generated")
        return 1

    reader = PdfReader(str(args.pdf))
    pages = len(reader.pages)
    size_mb = args.pdf.stat().st_size / (1024 * 1024)
    print(f"{args.pdf.name}: {pages} pages, {size_mb:.1f} MB")

    failed = False
    if pages < args.min_pages:
        print(
            f"::error::only {pages} pages — expected at least {args.min_pages}. "
            "WeasyPrint stopped early; the PDF is missing whole sections."
        )
        failed = True

    if args.expect:
        # Extracting every page is slow but this runs once per build, and a per-page search
        # is what makes the failure message useful ("found on page 132" vs "found").
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        # Strip whitespace entirely on both sides rather than collapsing it. Two separate
        # extraction artefacts break a naive search: a phrase that wraps comes back with a
        # newline in the middle, and depending on which font WeasyPrint embedded, pypdf can
        # return every glyph individually spaced ("t e c h  s t a c k"). Both are artefacts
        # of reading the PDF, not of its content — so ignore spacing on both sides.
        flat = "".join(text.split())
        for needle in args.expect:
            if "".join(needle.split()) in flat:
                print(f"  ok: {needle!r}")
            else:
                print(f"::error::{needle!r} is not in the PDF — content was dropped")
                failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
