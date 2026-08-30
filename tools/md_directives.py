"""
BCWEB-style directive markdown for BMM Docs.

The in-app BMM docs (and BCWEB) author callouts with GitBook-style `:::` container directives.
This mkdocs hook lets the docs SITE accept the same syntax by translating the callout/collapsible
directives into Material for MkDocs admonitions before the page is parsed:

    :::tip[Title]              !!! tip "Title"
    body           ──►             body
    :::

    :::details[Summary]        ??? note "Summary"
    body                           body
    :::

Only the callout/details directives are rewritten; any other `:::` block or non-directive text is
left exactly as it was, so this can never damage existing Material-native (`!!!`) content — it just
means an author can reach for either syntax. Registered via `hooks:` in mkdocs.yml.

The inline `:kbd[Ctrl+K]` is translated too, into `++ctrl+k++` — pymdownx.keys already draws
that, so this hands the work to the extension rather than emitting HTML of its own. It was
measured: four `:kbd[…]` in the pages drew keycaps in the app and printed as `:kbd[Save]` on the
site, in the same two files that also use `++esc++`. Neither renderer errors on the other's
spelling; it simply comes out as the characters the author typed.
"""

import re

# BCWEB callout name → Material admonition type.
_KIND = {
    "note": "note", "info": "info", "hint": "tip", "tip": "tip",
    "success": "success", "check": "success",
    "warning": "warning", "caution": "warning",
    "danger": "danger", "error": "danger", "bug": "bug", "example": "example",
}

# Opener: `:::name[Optional Title]{optional attrs}` (3+ colons). Closer: a line of only colons.
_OPEN = re.compile(r"^:::+\s*([a-z][\w-]*)\s*(?:\[([^\]]*)\])?\s*(?:\{[^}]*\})?\s*$", re.IGNORECASE)
_CLOSE = re.compile(r"^:::+\s*$")


def _convert(md: str) -> str:
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        m = _OPEN.match(lines[i].strip())
        name = m.group(1).lower() if m else None
        if m and (name in _KIND or name in ("details", "collapse")):
            title = (m.group(2) or "").strip()
            # Collect the block body up to the matching closing fence (nesting-aware).
            body = []
            depth = 1
            i += 1
            while i < n:
                s = lines[i].strip()
                mo = _OPEN.match(s)
                if mo and (mo.group(1).lower() in _KIND or mo.group(1).lower() in ("details", "collapse")):
                    depth += 1
                    body.append(lines[i])
                elif _CLOSE.match(s):
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                    body.append(lines[i])
                else:
                    body.append(lines[i])
                i += 1
            if name in ("details", "collapse"):
                head = '??? note "%s"' % (title or "Details")
            else:
                atype = _KIND.get(name, "note")
                head = ('!!! %s "%s"' % (atype, title)) if title else ("!!! %s" % atype)
            out.append(head)
            # Recurse so nested directives convert too, then indent the body by 4 spaces.
            inner = _convert("\n".join(body))
            out.extend(("    " + ln) if ln.strip() else "" for ln in inner.split("\n"))
            out.append("")
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


# `:kbd[Ctrl+K]` → `++ctrl+k++`, which pymdownx.keys renders. Inside a code fence it must be
# left alone: the reference page documents this syntax, and a documentation page that rewrites
# its own examples teaches something that is not true.
_KBD = re.compile(r":kbd\[([^\]]+)\]")
_FENCE = re.compile(r"^(```|~~~)")


def _kbd(md: str) -> str:
    out = []
    fenced = False
    for line in md.split("\n"):
        if _FENCE.match(line.strip()):
            fenced = not fenced
        if fenced:
            out.append(line)
            continue
        out.append(_KBD.sub(lambda m: "++" + "+".join(
            p.strip().lower() for p in m.group(1).split("+") if p.strip()) + "++", line))
    return "\n".join(out)


def on_page_markdown(markdown, **kwargs):  # mkdocs hook entry point
    if ":kbd[" in markdown:
        markdown = _kbd(markdown)
    if ":::" not in markdown:
        return markdown
    return _convert(markdown)
