"""Verify the *"…"* fragments the docs present as quotes from the source.

The BLAKE3 one was the warning: the page quoted a benchmark comment describing what the
library CAN do, as if it described what BMM DOES, and named the exact variant the code
rejects. It read as a faithful quote and was checked off as "paraphrase, meaning is fine".

Anything the docs set in *"…"* is claiming to be someone else's words. Those are checkable:
the Rust and TypeScript sources are right there. This finds the ones that are not.

    python check_code_quotes.py           # only the fragments with no source match
    python check_code_quotes.py --all     # every fragment and its verdict
"""

import argparse
import re
from pathlib import Path

DOCS = Path("BMM Docs/docs")
# BetterInstaller too: the docs legitimately quote the installer channel, and leaving it
# out reported two faithful quotes as missing.
SEARCH_ROOTS = ["src-tauri", "frontend/src", "scripts", ".github", "BetterInstaller/crates"]

# *"…"* — italic, quoted. The docs' convention for "these are not my words".
FRAG = re.compile(r'\*"([^"]{25,})"\*')


def words(s: str):
    return [w for w in re.split(r"[^A-Za-z0-9_]+", s) if len(w) > 2]


_CORPUS = None


def corpus() -> str:
    """Every source file, concatenated once. Cheaper than a grep per fragment, and it
    removes the dependency on rg being on PATH — which it is not, from here."""
    global _CORPUS
    if _CORPUS is None:
        parts = []
        for root in SEARCH_ROOTS:
            for p in Path(root).rglob("*"):
                if p.suffix in (".rs", ".ts", ".js", ".mjs", ".toml", ".yml", ".yaml", ".json") and p.is_file() and "target" not in p.parts and "node_modules" not in p.parts:
                    try:
                        parts.append(p.read_text(encoding="utf-8", errors="ignore"))
                    except OSError:
                        pass
        _CORPUS = chr(10).join(parts)
    return _CORPUS


def found_in_source(fragment: str) -> bool:
    """Present if a distinctive run of its words appears together in the source.

    Exact matching fails on line wrapping — a comment is broken across lines with `//` in
    the middle — so this looks for a run of words that survives the wrap.
    """
    w = words(fragment)
    if len(w) < 4:
        return True  # too short to judge; not worth a false positive
    hay = corpus()
    mid = len(w) // 2
    for span in (6, 5, 4):
        for start in (mid - span // 2, 0, len(w) - span):
            if start < 0 or start + span > len(w):
                continue
            needle = r".{0,24}?".join(re.escape(x) for x in w[start:start + span])
            if re.search(needle, hay, re.S):
                return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    total = missing = 0
    for page in sorted(DOCS.rglob("*.md")):
        if page.name.endswith(".fr.md"):
            continue  # the French quotes translate the English ones; check the source language
        text = page.read_text(encoding="utf-8")
        for m in FRAG.finditer(text):
            frag = " ".join(m.group(1).split())
            total += 1
            ok = found_in_source(frag)
            if ok and not args.all:
                continue
            if not ok:
                missing += 1
            line = text[: m.start()].count("\n") + 1
            mark = "OK " if ok else "!! "
            print(f"{mark}{page.relative_to(DOCS)}:{line}  {frag[:120]}")

    print(f"\n{total} quoted fragment(s); {missing} with no match in the source")


if __name__ == "__main__":
    main()
