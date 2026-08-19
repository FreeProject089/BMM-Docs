# Session recordings (`.bmmreplay`)

Interactive [rrweb](https://www.rrweb.io/) recordings of BMM, played inline in the docs
instead of (or alongside) a static screenshot.

## How to record one

By hand, in BMM: **Settings → Privacy**, turn on the **local Session recorder**, do the thing
you want to show, then **export** — you get a `.bmmreplay`. Plain JSON:
`{ bmmReplay, app, masked, durationMs, events: [...] }`, where `events` is a standard rrweb
event array. DOM-only: no screenshots, no pixels.

Scripted, which is how the files in this folder were made: `record.sh` drives BMM over its
local API (`/api/recorder`, `/api/view`, `/api/replay/export`). See that script — its comments
carry the three things that are not obvious and each cost an afternoon:

- **A cold start is mandatory.** rrweb emits its Meta and FullSnapshot only when a session
  genuinely begins. Export mid-session and you get incremental events with nothing to apply
  them to — a file that opens in no player. The cold start is also what puts BMM's intro at
  the head of each recording.
- **`POST /api/restart` is not a cold start.** It takes the app down and, under `tauri dev`,
  nothing brings it back; the API keeps answering for a second or two on the dying process,
  so one export lands and every later one silently writes nothing. Kill the process and
  launch it again instead.
- **`masked`** is `true` unless the recorder was set with `full: true`. A masked recording
  shows every mod name, profile name and path as `••••` — fine for showing a flow, useless
  for showing a screen. The recordings here are unmasked, made on a demo profile.

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

Recordings are large (~20 MB each). They're tracked with **git-lfs**
(`.gitattributes` maps `docs/assets/replays/*.bmmreplay` to LFS), so the git history stays
lean. Anyone cloning needs `git lfs` installed to pull the actual files. Prefer **short,
focused** recordings (10–30 s of one task) over long sessions — smaller files, clearer docs.

All thirteen files here are distinct per-feature recordings, made 19 Aug 2026 at
1480×960 — BMM's default window. Until then they were **thirteen copies of one file**: the
same 25.3 MB placeholder under thirteen names, so the Mapper page played the Themes footage.
If you re-record, check the result rather than the exit code — an export that writes nothing
returns success, which is exactly how thirteen identical files went unnoticed. `record.sh`
verifies mtime, parsing, the FullSnapshot and the `masked` flag for that reason.
