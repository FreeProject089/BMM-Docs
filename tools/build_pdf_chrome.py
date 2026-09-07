#!/usr/bin/env python3
"""Build the docs PDF WITHOUT WeasyPrint/GTK, using headless Chrome.

Why: `mkdocs.pdf.yml` uses mkdocs-with-pdf -> WeasyPrint, which needs GTK system
libraries (libgobject/pango/cairo). Those aren't on a plain Windows box. This instead
builds with `mkdocs.pdf-chrome.yml` (mkdocs-print-site-plugin folds the whole site into
one `/print_page/`), then drives a headless Chrome/Edge to print that page to PDF. Chrome
runs the page's JS, so the Mermaid diagrams render.

    python tools/build_pdf_chrome.py            # -> pdf/bettermodsmanager.pdf
    python tools/build_pdf_chrome.py --out x.pdf

Interactive `.bmmreplay` players are a web-only feature and do not appear in a static PDF.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.request import pathname2url

ROOT = Path(__file__).resolve().parent.parent

CHROME_CANDIDATES = [
    os.environ.get("CHROME_PATH"),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "chrome",
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if not c:
            continue
        if os.path.sep in c or (os.altsep and os.altsep in c):
            if Path(c).exists():
                return c
        else:
            from shutil import which
            p = which(c)
            if p:
                return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "pdf" / "bettermodsmanager.pdf"))
    ap.add_argument("--config", default=str(ROOT / "mkdocs.pdf-chrome.yml"))
    ap.add_argument("--budget-ms", type=int, default=25000,
                    help="Chrome virtual-time budget (ms) so JS/Mermaid finishes before capture")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        sys.exit("No Chrome/Edge found. Set CHROME_PATH to a Chromium-based browser executable.")

    print("[pdf] building site with", os.path.basename(args.config))
    subprocess.run([sys.executable, "-m", "mkdocs", "build", "-f", args.config], cwd=ROOT, check=True)

    print_page = ROOT / "site" / "print_page" / "index.html"
    if not print_page.exists():
        sys.exit(f"print page not found: {print_page} (is mkdocs-print-site-plugin installed?)")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    url = "file:" + pathname2url(str(print_page))
    print("[pdf] printing with", os.path.basename(chrome))
    subprocess.run([
        chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
        "--run-all-compositor-stages-before-draw",
        f"--virtual-time-budget={args.budget_ms}",
        "--no-pdf-header-footer", f"--print-to-pdf={out}", url,
    ], check=True)

    if not out.exists() or out.stat().st_size < 10000:
        sys.exit("PDF was not written (or is suspiciously small).")

    size_mb = out.stat().st_size / (1024 * 1024)
    pages = "?"
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(str(out)).pages)
    except Exception:
        pass
    print(f"[pdf] OK -> {out}  ({size_mb:.1f} MB, {pages} pages)")


if __name__ == "__main__":
    main()
