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


# ── B.MD 2.0 blocks ───────────────────────────────────────────────────────────
# The website's newer blocks, rewritten to HTML that `md_in_html` keeps parsing markdown
# inside (`markdown="1"`), styled by assets/extra.css under `.bmd-*`. Same shapes as the app's
# md-lite and the site's React kit, so a page written once reads the same on all three.
_BLOCKS = {
    "timeline": 1, "event": 1, "moment": 1, "compare": 1, "before": 1, "after": 1, "stats": 1, "stat": 1, "kpi": 1,
    "quote": 1, "testimonial": 1, "hero": 1, "changelog": 1, "version": 1, "release": 1, "spoiler": 1,
    "faq": 1, "q": 1, "question": 1, "checklist": 1, "grid": 1,
    # 3.0
    "table": 1, "audio": 1, "youtube": 1, "yt": 1, "spotify": 1, "img": 1, "image": 1,
    "api": 1, "endpoint": 1, "params": 1, "request": 1, "response": 1, "mermaid": 1, "diagram": 1,
    "openapi": 1, "swagger": 1, "include": 1, "embed-md": 1, "live": 1,
}
# The 3.0 leaves on their own line — `::spotify{src=…}`, `::youtube{…}`, `::audio{…}`, `:img[…]{…}`.
_LEAF = re.compile(r"^::?(spotify|youtube|yt|audio|include|embed-md|openapi|swagger|live|image|img)\s*(?:\[([^\]]*)\])?\s*(?:\{([^}]*)\})?\s*$", re.IGNORECASE)
_WEBONLY = "Interactive on the website"
_ATTR = re.compile(r'([a-zA-Z][\w-]*)(?:=("([^"]*)"|\'([^\']*)\'|([^\s}]+)))?')


def _attrs(raw):
    out = {}
    for m in _ATTR.finditer(raw or ""):
        out[m.group(1)] = m.group(3) if m.group(3) is not None else (m.group(4) if m.group(4) is not None else (m.group(5) if m.group(5) is not None else ""))
    return out


def _esc(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


_OPEN_ANY = re.compile(r"^:::+\s*([a-z][\w-]*)\s*(?:\[([^\]]*)\])?\s*(?:\{([^}]*)\})?\s*$", re.IGNORECASE)


def _block_html(name, title, a, inner):
    md = ' markdown="1"'
    if name == "timeline":
        head = '<div class="bmd-timeline-title">%s</div>' % _esc(title) if title else ""
        return '<div class="bmd-timeline"%s>\n%s\n%s\n</div>' % (md, head, inner)
    if name in ("event", "moment"):
        raw = (a.get("state") or a.get("status") or "").lower()
        state = "done" if raw in ("done", "past", "shipped") else "now" if raw in ("now", "current", "active") else "next"
        style = ' style="--ev:%s"' % _esc(a["color"]) if a.get("color") else ""
        meta = ('<div class="bmd-event-date">%s</div>' % _esc(a["date"]) if a.get("date") else "") + ('<div class="bmd-event-title">%s</div>' % _esc(title) if title else "")
        return '<div class="bmd-event bmd-event-%s"%s><div class="bmd-event-marker"></div><div class="bmd-event-body"%s>\n%s\n%s\n</div></div>' % (state, style, md, meta, inner)
    if name == "compare":
        for side in ("before", "after"):
            if a.get(side):
                inner = inner.replace('<div class="bmd-compare-label" data-side="%s">' % side + {"before": "Before", "after": "After"}[side] + "</div>",
                                      '<div class="bmd-compare-label" data-side="%s">%s</div>' % (side, _esc(a[side])), 1)
        return '<div class="bmd-compare"%s>\n%s\n</div>' % (md, inner)
    if name in ("before", "after"):
        lab = title or {"before": "Before", "after": "After"}[name]
        return '<div class="bmd-compare-side bmd-compare-%s"%s>\n<div class="bmd-compare-label" data-side="%s">%s</div>\n%s\n</div>' % (name, md, name, _esc(lab), inner)
    if name == "stats":
        return '<div class="bmd-stats"%s>\n%s\n</div>' % (md, inner)
    if name in ("stat", "kpi"):
        delta = str(a.get("delta") or a.get("trend") or "")
        d = "down" if delta.startswith("-") else "up" if delta.startswith("+") else "flat"
        style = ' style="--stat:%s"' % _esc(a["color"]) if a.get("color") else ""
        parts = ['<div class="bmd-stat-value">%s</div>' % _esc(str(a.get("value") or ""))]
        if title or a.get("label"): parts.append('<div class="bmd-stat-label">%s</div>' % _esc(title or a.get("label")))
        if delta: parts.append('<div class="bmd-stat-delta bmd-stat-%s">%s</div>' % (d, _esc(delta)))
        if inner.strip(): parts.append('<div class="bmd-stat-note"%s>\n%s\n</div>' % (md, inner))
        return '<div class="bmd-stat"%s>%s</div>' % (style, "".join(parts))
    if name in ("quote", "testimonial"):
        who = title or a.get("author") or a.get("by") or ""
        style = ' style="--q:%s"' % _esc(a["color"]) if a.get("color") else ""
        foot = ""
        if who or a.get("role") or a.get("avatar"):
            av = '<img class="bmd-quote-avatar" src="%s" alt="" loading="lazy">' % _esc(a["avatar"]) if a.get("avatar") else ""
            author = ('<a class="bmd-quote-author" href="%s">%s</a>' % (_esc(a["href"]), _esc(who))) if (who and a.get("href")) else ('<span class="bmd-quote-author">%s</span>' % _esc(who) if who else "")
            role = '<span class="bmd-quote-role">%s</span>' % _esc(a["role"]) if a.get("role") else ""
            foot = '<div class="bmd-quote-foot">%s<div class="bmd-quote-who">%s%s</div></div>' % (av, author, role)
        return '<blockquote class="bmd-quote"%s><div class="bmd-quote-body"%s>\n%s\n</div>%s</blockquote>' % (style, md, inner, foot)
    if name == "hero":
        align = a.get("align") if a.get("align") in ("left", "center", "right") else "left"
        style = ' style="--hero:%s"' % _esc(a["color"]) if a.get("color") else ""
        img = '<img class="bmd-hero-media" src="%s" alt="%s" loading="lazy">' % (_esc(a["image"]), _esc(title)) if a.get("image") else ""
        head = ('<div class="bmd-hero-title">%s</div>' % _esc(title) if title else "") + ('<div class="bmd-hero-sub">%s</div>' % _esc(a["subtitle"]) if a.get("subtitle") else "")
        return '<div class="bmd-hero bmd-hero-%s"%s>%s<div class="bmd-hero-body"%s>\n%s\n%s\n</div></div>' % (align, style, img, md, head, inner)
    if name == "changelog":
        head = '<div class="bmd-changelog-title">%s</div>' % _esc(title) if title else ""
        return '<div class="bmd-changelog"%s>\n%s\n%s\n</div>' % (md, head, inner)
    if name in ("version", "release"):
        v = title or a.get("v") or ""
        head = ('<span class="bmd-version-tag">%s</span>' % _esc(v) if v else "") + ('<span class="bmd-version-date">%s</span>' % _esc(a["date"]) if a.get("date") else "") + ('<span class="bmd-badge">%s</span>' % _esc(a["label"]) if a.get("label") else "")
        return '<div class="bmd-version"><div class="bmd-version-head">%s</div><div class="bmd-version-body"%s>\n%s\n</div></div>' % (head, md, inner)
    if name == "spoiler":
        return '<details class="bmd-spoiler"><summary>%s</summary><div class="bmd-details-body"%s>\n%s\n</div></details>' % (_esc(title or "Spoiler — click to reveal"), md, inner)
    if name == "faq":
        head = '<div class="bmd-faq-title">%s</div>' % _esc(title) if title else ""
        return '<div class="bmd-faq"%s>\n%s\n%s\n</div>' % (md, head, inner)
    if name in ("q", "question"):
        return '<details class="bmd-faq-item"%s><summary>%s</summary><div class="bmd-faq-a"%s>\n%s\n</div></details>' % (" open" if "open" in a else "", _esc(title or "Question"), md, inner)
    if name == "checklist":
        lines = inner.split("\n")
        total = sum(1 for l in lines if re.match(r"^\s*[-*]\s+\[[ xX]\]", l))
        done = sum(1 for l in lines if re.match(r"^\s*[-*]\s+\[[xX]\]", l))
        pct = round(done * 100 / total) if total else 0
        ticked = "\n".join(re.sub(r"^(\s*[-*]\s+)\[ \]\s*", r"\1☐ ", re.sub(r"^(\s*[-*]\s+)\[[xX]\]\s*", r"\1☑ ", l)) for l in lines)
        style = ' style="--check:%s"' % _esc(a["color"]) if a.get("color") else ""
        cls = "bmd-checklist" + (" bmd-checklist-done" if total and done == total else "")
        return '<div class="%s"%s><div class="bmd-checklist-head"><span class="bmd-checklist-title">%s</span><span class="bmd-checklist-count">%d / %d</span><span class="bmd-checklist-bar"><i style="width:%d%%"></i></span></div><div%s>\n%s\n</div></div>' % (cls, style, _esc(title or "Checklist"), done, total, pct, md, ticked)
    if name == "grid":
        try: cols = max(1, min(6, int(a.get("cols") or a.get("columns") or 3)))
        except ValueError: cols = 3
        return '<div class="bmd-grid" style="--cols:%d"%s>\n%s\n</div>' % (cols, md, inner)
    # ── 3.0 ──
    if name == "table":
        styles = "".join(" bmd-table-" + _esc(x) for x in re.split(r"[\s,+]+", (a.get("style") or a.get("variant") or "").lower()) if x)
        cap = title or a.get("caption") or ""
        return '<figure class="bmd-table%s"%s%s>\n%s\n%s</figure>' % (styles, (' data-align="%s"' % _esc(a["align"])) if a.get("align") else "", md, inner, ('<figcaption class="bmd-table-caption">%s</figcaption>' % _esc(cap)) if cap else "")
    if name == "audio":
        src = a.get("src") or a.get("href") or ""
        if not src: return inner
        return '<figure class="bmd-audio">%s<audio class="bmd-audio-player" controls preload="none" src="%s"></audio></figure>' % (('<figcaption class="bmd-audio-title">%s</figcaption>' % _esc(title)) if title else "", _esc(src))
    if name in ("youtube", "yt"):
        raw = a.get("src") or a.get("href") or a.get("id") or ""
        m = re.search(r"(?:youtu\.be/|[?&]v=|/embed/|/shorts/|/live/)([A-Za-z0-9_-]{6,})", raw) or re.match(r"^([A-Za-z0-9_-]{6,})$", raw)
        if not m: return inner
        return '<div class="bmd-embed bmd-embed-video"><iframe class="bmd-embed-frame" src="https://www.youtube-nocookie.com/embed/%s" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>' % _esc(m.group(1))
    if name == "spotify":
        raw = a.get("src") or a.get("href") or ""
        m = re.search(r"open\.spotify\.com/(?:embed/)?(?:intl-[a-z]+/)?(track|album|playlist|episode|show|artist)/([A-Za-z0-9]+)", raw) or re.match(r"^(?:spotify:)?(track|album|playlist|episode|show|artist)[:/]([A-Za-z0-9]+)$", raw)
        if not m: return inner
        return '<div class="bmd-embed bmd-embed-spotify%s"><iframe class="bmd-embed-frame" src="https://open.spotify.com/embed/%s/%s" loading="lazy" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe></div>' % (" bmd-embed-compact" if "compact" in a else "", m.group(1), _esc(m.group(2)))
    if name in ("img", "image"):
        src = a.get("src") or a.get("href") or ""
        if not src: return inner
        dim = lambda v: (v + "px") if re.match(r"^\d+$", v) else v
        style = ";".join(x for x in [("width:%s" % _esc(dim(a["width"]))) if a.get("width") else "", ("height:%s" % _esc(dim(a["height"]))) if a.get("height") else ""] if x)
        cls = "bmd-img" + ((" bmd-img-" + _esc(a["align"])) if a.get("align") in ("left", "center", "right") else "") + (" bmd-img-border" if "border" in a else "") + (" bmd-img-rounded" if "rounded" in a else "")
        img = '<img src="%s" alt="%s" loading="lazy"%s>' % (_esc(src), _esc(title or a.get("alt") or ""), (' style="%s"' % style) if style else "")
        if a.get("link"): img = '<a href="%s">%s</a>' % (_esc(a["link"]), img)
        return '<figure class="%s">%s%s</figure>' % (cls, img, ('<figcaption class="bmd-img-caption">%s</figcaption>' % _esc(a["caption"])) if a.get("caption") else "")
    if name in ("api", "endpoint"):
        sig = (title or a.get("title") or ("%s %s" % (a.get("method") or "", a.get("path") or ""))).strip()
        mm = re.match(r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|WS|SSE)\s+(\S.*)$", sig, re.IGNORECASE)
        method = (mm.group(1) if mm else (a.get("method") or "GET")).upper()
        path = mm.group(2) if mm else (a.get("path") or sig)
        head = '<div class="bmd-api-head"><span class="bmd-api-method">%s</span><code class="bmd-api-path">%s</code>%s</div>' % (_esc(method), _esc(path), ('<span class="bmd-api-auth">%s</span>' % _esc(a["auth"])) if a.get("auth") else "")
        summ = ('<div class="bmd-api-summary">%s</div>' % _esc(a["summary"])) if a.get("summary") else ""
        return '<div class="bmd-api bmd-api-%s%s">%s%s<div class="bmd-api-body"%s>\n%s\n</div></div>' % (method.lower(), " bmd-api-deprecated" if "deprecated" in a else "", head, summ, md, inner)
    if name in ("request", "response", "params"):
        status = str(a.get("status") or a.get("code") or "")
        ttl = title or {"params": "Parameters", "request": "Request"}.get(name, "Response" + ((" " + status) if status else ""))
        return '<div class="bmd-api-section bmd-api-%s%s"><div class="bmd-api-section-title">%s</div><div%s>\n%s\n</div></div>' % (name, (" bmd-api-status-%sxx" % status[0]) if status else "", _esc(ttl), md, inner)
    if name in ("mermaid", "diagram"):
        # Material draws ```mermaid fences itself: hand the body back as one.
        code = re.sub(r"^```[^\n]*\n?", "", inner.strip()); code = re.sub(r"\n?```\s*$", "", code)
        return "```mermaid\n%s\n```\n%s" % (code, ("*%s*" % title) if title else "")
    if name in ("openapi", "swagger", "include", "embed-md", "live"):
        src = a.get("src") or a.get("href") or ""
        return '<div class="bmd-webonly-block"><span class="bmd-webonly">%s</span>%s</div>' % (_WEBONLY, (" <code>%s</code>" % _esc(src)) if src else "")
    return inner


def _convert_blocks(md):
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)
    fenced = False
    while i < n:
        line = lines[i]
        if _FENCE.match(line.strip()):
            fenced = not fenced
        leaf = None if fenced else _LEAF.match(line.strip())
        if leaf:
            out.append("")
            out.append(_block_html(leaf.group(1).lower(), (leaf.group(2) or "").strip(), _attrs(leaf.group(3) or ""), ""))
            out.append("")
            i += 1
            continue
        m = None if fenced else _OPEN_ANY.match(line.strip())
        name = m.group(1).lower() if m else None
        if m and name in _BLOCKS:
            title = (m.group(2) or "").strip()
            a = _attrs(m.group(3) or "")
            body = []
            depth = 1
            i += 1
            while i < n:
                st = lines[i].strip()
                if _OPEN_ANY.match(st):
                    depth += 1
                    body.append(lines[i])
                elif _CLOSE.match(st):
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                    body.append(lines[i])
                else:
                    body.append(lines[i])
                i += 1
            inner = _convert_blocks("\n".join(body)).strip("\n")
            out.append("")
            out.append(_block_html(name, title, a, inner))
            out.append("")
        else:
            out.append(line)
            i += 1
    return "\n".join(out)


# Inline: `:meter[60]{label=Done}` and Phosphor icons `:icon[ph:rocket]` — the site draws both.
_METER = re.compile(r":meter\[([^\]]+)\](?:\{([^}]*)\})?")
_AUDIO = re.compile(r":audio\[([^\]]*)\](?:\{([^}]*)\})?")
_IMG = re.compile(r":(?:img|image)\[([^\]]*)\](?:\{([^}]*)\})?")
_LIVE = re.compile(r":(?:counter|fetch)\[([^\]]*)\](?:\{([^}]*)\})?")
_ACTION = re.compile(r":action\[([^\]]*)\](?:\{([^}]*)\})?")
_MARK = re.compile(r"==([^=\n]+?)==")
_WIKI = re.compile(r"\[\[([^\]|#\n]*)(?:#([^\]|\n]+))?(?:\|([^\]\n]+))?\]\]")
_INLINE_TOKENS = (":meter[", ":icon[ph", ":audio[", ":img[", ":image[", ":counter[", ":fetch[", ":action[", "==", "[[")
_PHICON = re.compile(r":icon\[(?:ph|phosphor)(?:-(thin|light|regular|bold|fill|duotone))?:([a-z0-9]+(?:-[a-z0-9]+)*)\](?:\{[^}]*\})?", re.IGNORECASE)


def _inline_2(md):
    out = []
    fenced = False
    for line in md.split("\n"):
        if _FENCE.match(line.strip()):
            fenced = not fenced
        if fenced or ("`" in line and any(tok in line for tok in _INLINE_TOKENS)):
            # inline code on the line: leave the whole line, a reference page shows the syntax
            out.append(line)
            continue

        def meter(m):
            a = _attrs(m.group(2) or "")
            try: mx = max(1, float(a.get("max") or 100))
            except ValueError: mx = 100.0
            try: v = float(re.sub(r"[^0-9.]", "", m.group(1)) or 0)
            except ValueError: v = 0.0
            pct = int(round(max(0.0, min(mx, v)) * 100 / mx))
            style = ' style="--meter:%s"' % _esc(a["color"]) if a.get("color") else ""
            lab = (_esc(a["label"]) + " ") if a.get("label") else ""
            return '<span class="bmd-meter"%s><span class="bmd-meter-track"><span class="bmd-meter-fill" style="width:%d%%"></span></span><span class="bmd-meter-text">%s%d%%</span></span>' % (style, pct, lab, pct)

        def ph(m):
            w = (m.group(1) or "regular").lower()
            f = m.group(2).lower() + ("" if w == "regular" else "-" + w)
            return '<span class="bmd-ph" style="-webkit-mask:url(https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2/assets/%s/%s.svg) center/contain no-repeat;mask:url(https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2/assets/%s/%s.svg) center/contain no-repeat"></span>' % (w, f, w, f)
        line = _METER.sub(meter, line)
        line = _PHICON.sub(ph, line)
        # 3.0 inline
        def audio(m):
            a = _attrs(m.group(2) or ""); src = a.get("src") or a.get("href") or ""
            if not src: return _esc(m.group(1))
            return '<span class="bmd-audio bmd-audio-inline">%s<audio class="bmd-audio-player" controls preload="none" src="%s"></audio></span>' % (('<span class="bmd-audio-title">%s</span>' % _esc(m.group(1))) if m.group(1) else "", _esc(src))
        def img(m):
            a = _attrs(m.group(2) or ""); src = a.get("src") or a.get("href") or ""
            if not src: return _esc(m.group(1))
            dim = lambda v: (v + "px") if re.match(r"^\d+$", v) else v
            style = ";".join(x for x in [("width:%s" % _esc(dim(a["width"]))) if a.get("width") else "", ("height:%s" % _esc(dim(a["height"]))) if a.get("height") else ""] if x)
            return '<span class="bmd-img bmd-img-inline%s"><img src="%s" alt="%s" loading="lazy"%s>%s</span>' % ((" bmd-img-" + _esc(a["align"])) if a.get("align") in ("left", "center", "right") else "", _esc(src), _esc(m.group(1)), (' style="%s"' % style) if style else "", ('<span class="bmd-img-caption">%s</span>' % _esc(a["caption"])) if a.get("caption") else "")
        line = _AUDIO.sub(audio, line)
        line = _IMG.sub(img, line)
        line = _LIVE.sub(lambda m: '<span class="bmd-webonly" title="%s">%s —</span>' % (_WEBONLY, _esc(m.group(1))), line)
        line = _ACTION.sub(lambda m: '<span class="bmd-btn bmd-webonly" title="%s">%s</span>' % (_WEBONLY, _esc(m.group(1))), line)
        line = _MARK.sub(lambda m: "<mark>%s</mark>" % m.group(1), line)
        line = _WIKI.sub(lambda m: '<span class="bmd-ref" title="%s">%s</span>' % (_esc((m.group(1) or m.group(2) or "").strip()), _esc((m.group(3) or m.group(1) or m.group(2) or "").strip())), line)
        out.append(line)
    return "\n".join(out)


def on_page_markdown(markdown, **kwargs):  # mkdocs hook entry point
    if ":kbd[" in markdown:
        markdown = _kbd(markdown)
    if any(tok in markdown for tok in _INLINE_TOKENS):
        markdown = _inline_2(markdown)
    if ":::" not in markdown:
        return markdown
    return _convert(_convert_blocks(markdown))
