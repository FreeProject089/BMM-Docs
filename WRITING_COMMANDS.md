# Commands for this documentation site

Everything you can run in the **BMM Docs** repository. For writing conventions — voice,
directives, when a page belongs here versus in the app — see [WRITING.md](WRITING.md)
([FR](WRITING_FR.md)).

## Setup, once

```bash
pip install -r requirements.txt
```

## Writing

```bash
mkdocs serve            # http://127.0.0.1:8000 — French at /fr/
mkdocs serve -a 0.0.0.0:8000   # reachable from another machine on your network
```

The site reloads as you save. French pages are `<name>.fr.md` beside the English one; a page
with no French file simply does not appear in the French navigation.

## Before committing

```bash
mkdocs build --strict          # what CI checks: a broken internal link FAILS the build
python tools/annotate.py --check   # fails if a rendered annotation is stale
python tools/check_quotes.py       # quotation marks and dashes
python tools/check_code_quotes.py  # code spans that are really prose, and vice versa
python tools/check_media.py        # which clips and screenshots are still placeholders
```

`--strict` is the one that matters. A relative link that resolves in your editor can still be
wrong once mkdocs rewrites paths for the language folders, and without `--strict` that ships
as a 404.

## Annotations

```bash
python tools/annotate.py           # render every annotated screenshot spec
python tools/annotate.py --check   # what CI runs
```

The specs are text; the images are generated from them. Editing a rendered PNG by hand is
work the next `annotate.py` run will throw away.

## Media

```bash
python tools/check_media.py
```

Reports replays that share a SHA-256 (the same take copied) and PNGs with too few distinct
colours to be a real screenshot. It exits 0 by default; `--strict` makes it fail while
placeholders remain.

The shooting list — every file still to record, with the window size, theme, profile and what
must never be on screen — is `.Assets/MEDIA_TO_RECORD.md` in the **BMM** repository.

```bash
node scripts/record-take.mjs       # from the BMM repo: arms the recorder and exports a .bmmreplay
```

## The PDF

```bash
mkdocs build -f mkdocs.pdf.yml        # light
mkdocs build -f mkdocs.pdf-dark.yml   # dark
python tools/check_pdf.py             # sanity-check the result
```

`mkdocs.yml` deliberately omits the PDF plugin. mkdocs imports a plugin even when it is
disabled, so listing it there made `mkdocs serve` fail on any machine without WeasyPrint's
GTK libraries. The PDF configs inherit from it and are used in CI, where those libraries
exist.

## How this reaches the app

BMM copies these pages into itself, so Help &amp; other renders the same markdown the site
does. From the **BMM** repository:

```bash
npm run sync-docs            # copy them in
npm run sync-docs -- --check # fail if the copy is stale — CI does this
npm run check:docs           # every cross-reference resolves
```

One source, two renderers. A page can therefore never say two different things in two places
— but the copy is committed, so it has to be regenerated when you change a page here.

!!! warning "A new page needs an entry in the app too"
    Adding a page here is not enough for `bmm://docs/open?article=…` to work. The article id
    is declared in BMM's `frontend/src/docs/docs-hub.ts`, and `npm run check:docs` fails until
    it is — which is the check catching a link that would otherwise open nothing.
