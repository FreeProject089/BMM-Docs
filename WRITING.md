# Writing the BMM documentation

**There is one source.** `BMM Docs/docs/*.md` is the only place the documentation is
written. `scripts/sync-docs.mjs` copies those files into the app, so the mkdocs site and
BMM's **Help & other** render the *same* files through two different renderers.

That is the single most important thing to know here, and it is easy to get wrong: there is
no separate "in-app documentation" to update. Editing a page updates both.

```
BMM Docs/docs/<lang>/…/page.md      ← you write here
        │
        ├── mkdocs build             → the published site
        └── node scripts/sync-docs.mjs
              → frontend/assets/docs/<lang>/…/page.md   ← BMM reads this
              → frontend/assets/docs/manifest.json
```

---

## The loop

```bash
# 1. edit a page under BMM Docs/docs/
# 2. copy it into the app
node scripts/sync-docs.mjs
# 3. check everything still holds
npm run ci
```

`npm run ci` runs `sync-docs --check`, which **fails if the copy is stale**. So forgetting
step 2 is caught, not shipped. It also runs `check-docs-xref`, which is the gate that
actually reads your prose — see [What CI checks](#what-ci-checks).

To preview the site itself:

```bash
cd "BMM Docs" && mkdocs serve
```

---

## What renders in BOTH

Write these freely — they work on the site and in the app.

| Syntax | Notes |
|---|---|
| Headings, lists, links, `**bold**`, `*italic*`, `***both***` | |
| GFM tables | The reference pages are long lookup tables; prose cannot carry them |
| Fenced code, with a language | The language is what colours it in the app |
| ` ```mermaid ` fences | Rendered as SVG in both. 56 diagrams currently rely on this |
| `!!! note "Title"` + a 4-space indented body | Admonitions. Kinds: `note` `tip` `success` `warning` `danger` |
| `??? note "Title"` / `???+ note` | Collapsible; `+` starts open |
| `=== "Tab"` + indented body, repeated | Content tabs |
| `## Heading {#custom-anchor}` | Stable link target. **sync-docs** rewrites it into `<a id>` while copying — md-lite alone prints the braces, so a page rendered outside the pipeline has no anchors |
| Images with a relative path | |

!!! tip "Admonition titles may contain quotes"

    Escape them: `!!! note "\"Conflict rules\" = the order"`. An unescaped inner quote used to
    make the whole block render as literal `!!! note …` text — CI now catches that.

---

## What only renders on the SITE

These are mkdocs/Material features the in-app renderer does not implement. Use them only
where the page is site-only, or accept that the app shows the raw text.

| Syntax | In the app |
|---|---|
| `++ctrl+k++` (pymdownx.keys) | Prints the plus signs literally |
| `{: .some-class }` attribute lists other than `{#anchor}` | Ignored or printed |
| Raw HTML blocks | Escaped and shown as text |
| Footnotes, definition lists | Not implemented |

### Keyboard keys are the trap

The two renderers each have their **own** syntax and neither understands the other's:

| | Site (mkdocs) | App (md-lite) |
|---|---|---|
| `++ctrl+k++` | styled keys | literal `++ctrl+k++` |
| `:kbd[Ctrl+K]` | literal `:kbd[Ctrl+K]` | styled keys |

There is no form that works in both. Pick by where the page matters most, or write the keys
as plain text (`Ctrl + K`) — which is what most pages do, and it reads fine in both.

!!! warning "Check before you rely on one"

    The honest test is not this table — it is `npm run ci`. `check-docs-xref` renders every
    page through the app's renderer and fails on markup that leaked through as visible text.

---

## What only works in the APP

Two things exist for BMM and are inert on the site:

- **`bmm-replay` blocks** — a session recording that plays inline in the app. Large ones are
  not bundled; the app fetches them from the published site instead.
- **In-app deeplinks** — `bmm://docs/open?page=…`. There are 42 of them and CI checks every
  one resolves to a real page.

---

## Adding a page

1. Create the file under `BMM Docs/docs/en/…`, and its French counterpart under `docs/fr/…`
   at the same relative path.
2. Add it to `nav:` in `mkdocs.yml`. **This is what orders it in the app too** — `sync-docs`
   reads that nav to build the manifest order, so a page absent from the nav is absent from
   the app's page list.
3. Run `node scripts/sync-docs.mjs` and `npm run ci`.

!!! note "French is not optional for the nav"

    A page with no French file still appears in the French app, with its English text and a
    note saying so. That is deliberate — an empty page would be worse — but it is a gap to
    close, not a finished state.

---

## Images, diagrams and recordings

- **Diagrams**: prefer a ` ```mermaid ` fence over a screenshot. It stays legible in both
  themes, survives a re-theme, and is diffable. CI verifies all 56 survive the app's HTML
  escaping intact.
- **Images**: relative paths. Keep them small; everything under `docs/` is bundled into the
  app and ships with every install.
- **Recordings**: there is a per-file cap (8 MB) and a total media budget (48 MB). Over
  budget, `sync-docs` leaves the file on the site and the app streams it — you do not have to
  do anything, but a very large recording will not be available offline.

---

## What CI checks

`npm run ci` is the contract. The gates that concern writers:

| Gate | Fails when |
|---|---|
| `sync-docs --check` | The bundled copy is stale — you edited a page and did not re-sync |
| `check-docs-xref` | A cross-link, a `docsPath` target or a `bmm://docs/open` link points at nothing |
| | A page renders visible `!!! …`, an HTML comment, raw HTML, or `{#anchor}` braces |
| | A mermaid source does not survive the app's escaping |
| `check-encoding` | A file is not clean UTF-8 |
| `check-markup` | A typographic quote (`"` `"`) appears inside an HTML attribute |

The last one bites more often than you would expect: pasting from a word processor turns
`"` into `"`, and in an attribute that breaks the element silently.

---

## House style

- **Say what it does, then why.** A reader who knows *why* can work out the *what* next time.
- **Name the failure.** "If the manifest is unreachable, the repo browser is empty; joining
  by direct URL still works" beats "make sure the manifest is reachable".
- **Numbers over adjectives.** "72 hours" not "a short grace period".
- **Second person, present tense.** "You pick a pool", not "the user will select a pool".
- **Do not promise what is not built.** If something is planned, say so in the same sentence.

---

## Editing BetterCommunity's own documentation

Different system, and worth not confusing with this one. The website's docs live in its
database and are edited **in the browser** at `/docs` by anyone holding the `manage_docs`
capability (or an admin). They support the BCWEB block syntax (`:::cards`, `::toc`,
`:icon[…]`), have revisions and per-page comments, and are seeded by
`apps/api/src/seed-docs.mjs` and `seed-site-guide.mjs`.

Rule of thumb: **BMM the app → this repo. The website → the browser.**
