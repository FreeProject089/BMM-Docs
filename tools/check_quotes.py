"""Find documentation blockquotes that claim to be the app's words but are not.

The .MM page quoted BMM's own definition of the format and had changed a word — then
reasoned from the substituted one. Nothing could catch that: the quote is well-formed, the
links resolve, nothing is stale. The only handle is that the app's strings are all in
frontend/Lang/en.json, so a quote presented as the app's can be looked up.

Heuristic, not proof. A blockquote is only reported when it looks like it is quoting the UI
— it is close to a real string but not equal to it. Prose quotes that resemble nothing in
the dictionary are ignored: those are the author's own words, which is most of them.

    python check_quotes.py            # report near-misses
    python check_quotes.py --all      # also list quotes with no match at all
"""

import argparse
import difflib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve()
# Run from the BMM repo root.
DOCS = Path("BMM Docs/docs")
LANG = Path("frontend/Lang/en.json")
LANG_FR = Path("frontend/Lang/fr.json")

# A blockquote line, minus the marker. Admonitions (`> **Note**`) and link-only lines are
# not quotes of the app.
QUOTE = re.compile(r"^>\s?(.*)$")


def blockquotes(text: str):
    """Yield (line_no, joined_text) for each contiguous blockquote block."""
    buf, start = [], 0
    for i, line in enumerate(text.splitlines(), 1):
        m = QUOTE.match(line)
        if m:
            if not buf:
                start = i
            buf.append(m.group(1).strip())
        elif buf:
            yield start, " ".join(buf).strip()
            buf = []
    if buf:
        yield start, " ".join(buf).strip()


def norm(s: str) -> str:
    """Compare on words only — markdown emphasis and wrapping are not differences."""
    s = re.sub(r"[*_`]", "", s)
    return " ".join(s.split()).rstrip(".").lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--threshold", type=float, default=0.72,
                    help="similarity above which a quote is treated as quoting the UI")
    args = ap.parse_args()

    strings = []
    for f in (LANG, LANG_FR):
        if f.exists():
            for k, v in json.loads(f.read_text(encoding="utf-8")).items():
                if isinstance(v, str) and len(v) > 25:
                    strings.append((k, v))
    index = {norm(v): k for k, v in strings}
    keys = list(index)

    findings = 0
    for page in sorted(DOCS.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        for line_no, quote in blockquotes(text):
            if len(quote) < 25:
                continue
            n = norm(quote)
            if n in index:
                continue  # exact match — the quote is faithful
            close = difflib.get_close_matches(n, keys, n=1, cutoff=args.threshold)
            if close:
                findings += 1
                key = index[close[0]]
                print(f"\n{page.relative_to(DOCS)}:{line_no}  ~{difflib.SequenceMatcher(None, n, close[0]).ratio():.0%} match on `{key}`")
                print(f"  docs: {quote[:150]}")
                print(f"  app : {dict(strings)[key][:150] if False else close[0][:150]}")
            elif args.all:
                print(f"\n{page.relative_to(DOCS)}:{line_no}  (no match — probably the author's own words)")
                print(f"  {quote[:110]}")

    print(f"\n{findings} blockquote(s) that look like an altered UI string")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
