# BetterModsManager — Documentation

The user guide for [BetterModsManager](https://github.com/FreeProject089), in **English and
French**, built with MkDocs Material. Every page is meant to be readable by someone who has
never opened the app.

**Live site:** https://freeproject089.github.io/BMM-Docs/ · **PDF:** built by CI on every
push to `master` (see the workflow's artifacts).

## Run it locally

```bash
pip install -r requirements.txt
mkdocs serve            # http://127.0.0.1:8000  — FR at /fr/
```

`mkdocs.yml` is the config contributors use. It deliberately does **not** include the PDF
plugin: that plugin renders through WeasyPrint, which needs GTK system libraries, and MkDocs
imports a plugin even when it's disabled — so listing it here made `mkdocs serve` fail on
Windows with `cannot load library 'libgobject-2.0-0'`. The PDF is built from
`mkdocs.pdf.yml`, which inherits this one, and only in CI (Ubuntu, where the libs are
installed).

```bash
mkdocs build --strict                 # what CI checks: a broken internal link fails
mkdocs build -f mkdocs.pdf.yml        # the PDF — needs GTK, easiest inside CI
```

## Screenshots and their numbered call-outs

Pages box a UI element and number it, so the prose can say "click **(2)**". Those boxes are
**not** painted into the image. Each screenshot has a JSON spec beside it:

```
docs/assets/screens/
  library.png             # the RAW capture — never edited
  library.json            # the spec: which boxes, which numbers
  library.annotated.png   # generated — this is what the pages reference
```

```json
{
  "image": "library.png",
  "boxes": [
    { "n": 1, "xy": [40, 96, 260, 150], "label": "Search" },
    { "n": 2, "xy": [340, 96, 560, 150], "label": "Filters" }
  ]
}
```

```bash
python tools/annotate.py          # render every spec
python tools/annotate.py --check  # what CI runs: fails if an annotation is stale
```

Why this way: a hand-painted call-out rots the day BMM moves a button — nobody re-opens an
image editor, so the picture quietly starts lying. Here the annotation is versioned text, it
shows up in a diff, and it re-renders on every build. Retake the capture, keep the spec.

It also keeps the numbering identical across languages: one spec feeds both the EN and the
FR page, so **(2)** is the same box in both. Translate the prose, not the picture.

### Taking the captures

BMM is a desktop app, so captures are taken by hand and committed raw. Guidelines that keep
the set coherent:

- Same window size for every capture in a section, so boxes line up across pages.
- Dark theme (BMM's default) unless the page is specifically about the light one.
- No personal data — use a throwaway profile.
- If you capture on a HiDPI screen, set `"scale": 2` in the spec so the coordinates stay in
  logical pixels.

## Translating

Structure is `suffix`: `page.md` is English, `page.fr.md` is its French sibling. A page with
no `.fr.md` falls back to English rather than 404ing, so the FR site is never broken — the
gaps just show up in the build log.

Link between pages with the **base** name (`profiles.md`), even from a French page. The i18n
plugin resolves it to the reader's language. Linking `profiles.fr.md` directly fails
`--strict`.

Terminology comes from the app itself: `frontend/Lang/{en,fr}.json` in the BMM repo holds
the real UI strings in both languages (6 400+ keys). Use those exact words — a guide that
invents its own names for buttons is worse than no guide.

## Status

**All 18 pages are written, in both languages** — the prose is done and quotes BMM's own
strings rather than paraphrasing them.

The API reference is read from the source, not from memory: `src-tauri/src/api/mod.rs`
(port, bearer auth, permission filters), `src-tauri/src/models/plugin.rs` (the manifest) and
`src-tauri/src/commands/scheduler.rs` (triggers, OS task registration).
When those change, re-read them — don't trust the page.

What's missing is **real screenshots**. Every `docs/assets/screens/*.png` is a placeholder,
and every `*.json` spec has placeholder coordinates. That's the whole remaining job:

1. Capture the screen (see the guidelines above).
2. Drop the PNG over the placeholder, same filename.
3. Open the `.json` and fix the `xy` of each box.

Nothing else moves: the numbers, the labels and both language pages already reference them.
`python tools/annotate.py` re-renders, and CI fails if you forget.
