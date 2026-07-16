# Session recordings (`.bmmreplay`)

Interactive [rrweb](https://www.rrweb.io/) recordings of BMM, played inline in the docs
instead of (or alongside) a static screenshot.

## How to record one

In BMM: **Settings → Privacy** area, turn on the **local Session recorder**, do the thing you
want to show, then **export** the session — you get a `.bmmreplay` file. It's plain JSON:
`{ bmmReplay, app, durationMs, events: [...] }`, where `events` is a standard rrweb event
array. Recordings are DOM-only and masked; they contain no screenshots or pixels.

## How to add one to a page

1. Drop the file in **`docs/assets/replays/`** (this folder).
2. Embed it in any Markdown page with a raw HTML block:

   ```html
   <div class="bmm-replay"
        data-src="../assets/replays/your-recording.bmmreplay"
        data-title="Enabling a mod and resolving a conflict"></div>
   ```

   - `data-src` is **relative to the page** (`../assets/...` from a `features/` or `reference/`
     page; `assets/...` from the docs root).
   - `data-title` is the caption on the play poster (optional).

The player (`../rrweb/bmm-replay.js`, wired in `mkdocs.yml`) lazy-loads the file only when the
reader clicks **Play**, then shows it with a play/pause button and a scrubber, auto-scaled to
the page width.

## A note on size & git

Recordings are large (this placeholder is ~26 MB). They're tracked with **git-lfs**
(`.gitattributes` maps `docs/assets/replays/*.bmmreplay` to LFS), so the git history stays
lean. Anyone cloning needs `git lfs` installed to pull the actual files. Prefer **short,
focused** recordings (10–30 s of one task) over long sessions — smaller files, clearer docs.

`bmm-demo.bmmreplay` is a placeholder; replace it with real per-feature recordings.
