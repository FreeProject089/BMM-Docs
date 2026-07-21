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


def on_page_markdown(markdown, **kwargs):  # mkdocs hook entry point
    if ":::" not in markdown:
        return markdown
    return _convert(markdown)
