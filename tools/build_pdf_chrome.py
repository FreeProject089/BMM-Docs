#!/usr/bin/env python3
"""Build the docs PDFs WITHOUT WeasyPrint/GTK, using headless Chrome, one book per language.

Why: `mkdocs.pdf.yml` uses mkdocs-with-pdf -> WeasyPrint, which needs GTK system
libraries (libgobject/pango/cairo). Those aren't on a plain Windows box. This instead
builds with `mkdocs.pdf-chrome.yml` (mkdocs-print-site-plugin folds the whole site into
one `/print_page/`), then drives a headless Chrome/Edge to print that page to PDF. Chrome
runs the page's JS, so the Mermaid diagrams render.

    python tools/build_pdf_chrome.py                     # EN + FR, light
    python tools/build_pdf_chrome.py --theme dark        # EN + FR, dark
    python tools/build_pdf_chrome.py --lang fr           # one language
    python tools/build_pdf_chrome.py --lang en --out x.pdf

Output, in pdf/: bettermodsmanager.pdf (EN), bettermodsmanager.fr.pdf (FR), and the same
names with -dark for the dark edition.

One site per language
---------------------
With mkdocs-static-i18n, print-site writes ONE /print_page/ and the French pass of the i18n
build overwrites it: building mkdocs.pdf-chrome.yml as is gave a French « English » book.
So each language is built as its own single-language site, under .pdf-chrome-build/
(ignored by git):

  1. docs/ is copied to .pdf-chrome-build/docs-<lang>; for French every `page.fr.md` replaces
     `page.md` (an untranslated page keeps its English text, as fallback_to_default does on the
     site); for English the `.fr.md` pages are removed;
  2. a generated mkdocs-<theme>-<lang>.yml INHERITs mkdocs.pdf-chrome.yml (or its dark
     edition), so theme, markdown extensions and stylesheets stay the ones in this repo, and
     overrides only docs_dir, site_dir, the theme language, the absolute custom_dir and hooks,
     the nav titles (French: the i18n plugin's own nav_translations) and the plugins
     (search + print-site, no i18n).

Interactive `.bmmreplay` players are a web-only feature and do not appear in a static PDF.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import pathname2url

import yaml

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / ".pdf-chrome-build"

CHROME_CANDIDATES = [
    os.environ.get("CHROME_PATH"),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "chrome",
]

# The print page's own title and table-of-contents heading, per language.
TEXT = {
    "en": {"title": "BetterModsManager — Documentation", "toc": "Contents"},
    "fr": {"title": "BetterModsManager — Documentation (français)", "toc": "Sommaire"},
}


class _Loader(yaml.SafeLoader):
    pass


# mkdocs.yml carries !!python/name tags (markdown extensions). Only nav, hooks, custom_dir and
# the i18n settings are read here, so those tags are read as None; mkdocs itself reads the
# inherited file directly and resolves them.
_Loader.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)
_Loader.add_multi_constructor("!", lambda loader, suffix, node: None)


def find_chrome():
    for c in CHROME_CANDIDATES:
        if not c:
            continue
        if os.path.sep in c or (os.altsep and os.altsep in c):
            if Path(c).exists():
                return c
        else:
            p = shutil.which(c)
            if p:
                return p
    return None


def translate(nav, words):
    out = []
    for item in nav:
        if isinstance(item, dict):
            (title, value), = item.items()
            out.append({words.get(title, title): translate(value, words) if isinstance(value, list) else value})
        else:
            out.append(item)
    return out


def language_config(lang, theme_config, tag):
    """Write the single-language docs tree and its config; return (config path, site dir)."""
    base = yaml.load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"), Loader=_Loader)
    words = {}
    for p in base.get("plugins", []):
        if isinstance(p, dict) and "i18n" in p:
            for entry in p["i18n"].get("languages", []):
                if entry.get("locale") == lang and not entry.get("default"):
                    words = entry.get("nav_translations", {}) or {}

    src = ROOT / (base.get("docs_dir") or "docs")
    dst = BUILD / f"docs-{lang}"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for f in list(dst.rglob("*.fr.md")):
        if lang == "fr":
            f.replace(f.with_name(f.name[: -len(".fr.md")] + ".md"))
        else:
            f.unlink()

    site_dir = BUILD / f"site-{tag}-{lang}"
    cfg = {
        "INHERIT": str(theme_config.resolve()),
        "docs_dir": str(dst),
        "site_dir": str(site_dir),
        "theme": {"custom_dir": str((ROOT / base["theme"]["custom_dir"]).resolve()), "language": lang},
        "hooks": [str((ROOT / h).resolve()) for h in base.get("hooks", [])],
        "nav": translate(base.get("nav", []), words),
        "plugins": [
            {"search": {"lang": [lang]}},
            {"print-site": {
                "add_to_navigation": False,
                "print_page_title": TEXT[lang]["title"],
                "add_cover_page": True,
                "add_table_of_contents": True,
                "toc_title": TEXT[lang]["toc"],
                "enumerate_headings": False,
                "enumerate_figures": False,
            }},
        ],
    }
    out = BUILD / f"mkdocs-{tag}-{lang}.yml"
    out.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return out, site_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=["light", "dark"], default="light",
                    help="which edition to build; picks the config, the output names and the "
                         "Mermaid palette in one go")
    ap.add_argument("--lang", choices=["en", "fr", "all"], default="all",
                    help="which book(s) to build (default: both)")
    ap.add_argument("--out", default=None, help="output file (only with a single --lang)")
    ap.add_argument("--config", default=None,
                    help="the Chrome PDF config each language inherits (default: by --theme)")
    ap.add_argument("--budget-ms", type=int, default=25000,
                    help="Chrome virtual-time budget (ms) so JS/Mermaid finishes before capture")
    args = ap.parse_args()

    langs = ["en", "fr"] if args.lang == "all" else [args.lang]
    if args.out and len(langs) > 1:
        sys.exit("--out needs a single --lang (en or fr).")

    # One flag decides config, output names and Mermaid palette together, because getting two
    # of them right and the third wrong is the failure this replaces: a dark stylesheet with a
    # light Mermaid palette, or a dark build written over the light PDF.
    dark = args.theme == "dark"
    tag = "dark" if dark else "light"
    config = Path(args.config) if args.config else ROOT / ("mkdocs.pdf-chrome-dark.yml" if dark else "mkdocs.pdf-chrome.yml")
    # Mermaid is rendered by the browser BEFORE any of the print CSS applies, so its palette
    # comes from the hook reading this — not from the stylesheet.
    os.environ["BMM_PDF_THEME"] = tag

    chrome = find_chrome()
    if not chrome:
        sys.exit("No Chrome/Edge found. Set CHROME_PATH to a Chromium-based browser executable.")

    BUILD.mkdir(exist_ok=True)
    for lang in langs:
        stem = "bettermodsmanager" + ("-dark" if dark else "") + ("" if lang == "en" else f".{lang}")
        out = Path(args.out) if args.out else ROOT / "pdf" / f"{stem}.pdf"

        cfg, site_dir = language_config(lang, config, tag)
        print(f"[pdf] {lang}: building the site from {config.name}")
        subprocess.run([sys.executable, "-m", "mkdocs", "build", "-q", "-f", str(cfg)], cwd=ROOT, check=True)

        print_page = site_dir / "print_page" / "index.html"
        if not print_page.exists():
            sys.exit(f"print page not found: {print_page} (is mkdocs-print-site-plugin installed?)")

        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            out.unlink()

        url = "file:" + pathname2url(str(print_page))
        print(f"[pdf] {lang}: printing with", os.path.basename(chrome))
        # Semgrep flags `chrome` because it can come from CHROME_PATH. That variable is set by the
        # person running this local build tool on their own machine, the call is an argument list
        # (no shell), and CI never runs this script. Reviewed 2026-09-25.
        subprocess.run([  # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            f"--virtual-time-budget={args.budget_ms}",
            "--no-pdf-header-footer", f"--print-to-pdf={out}", url,
        ], check=True)

        if not out.exists() or out.stat().st_size < 10000:
            sys.exit(f"{out}: PDF was not written (or is suspiciously small).")

        size_mb = out.stat().st_size / (1024 * 1024)
        pages = "?"
        try:
            from pypdf import PdfReader
            pages = len(PdfReader(str(out)).pages)
        except Exception:
            pass
        print(f"[pdf] {lang}: OK -> {out}  ({size_mb:.1f} MB, {pages} pages)")


if __name__ == "__main__":
    main()
