# Doc-vs-code audit — where it stands

State of the "read the docs against the code" pass. Written to be picked up cold, in a
fresh session, without the conversation that produced it.

The audit is **prio 1** per the owner. `repo.md` is now the most likely to have drifted —
the Server Repo feature changed substantially after most of it was reviewed (see
"Changed under the audit" below).

## The method that actually found things

Reading a page against the code found real errors, but the higher-yield technique was
**cross-referencing two pages that describe the same thing** and looking for where they
disagree. Two pages that agree with each other can still both be wrong, but a disagreement
is always a defect in at least one of them, and it costs no code reading to spot.

The Mapper pair is the case to imitate. Both pages agreed on the central claim — "the
Mapper edits the mod, not the game" — and the code confirmed it. But both also promised
*"the worst case is a mis-shaped mod, which you can reshape again"*, and the code did
`remove_dir_all(&dst)` on a name collision: dropping `Data/` onto a mod that already had a
`Data/` destroyed its contents, no confirmation, no backup. **The doc claim was the thing
that exposed the bug.** Fixed in both (BMM `489d7e5`, docs `5546287`).

Second technique, cheaper than it sounds: for any doc sentence naming a **default value, a
threshold, or a trigger**, grep the constant. Several claims were right about the value and
wrong about when it applies — `storage.md`'s auto-calibration description was correct on
the default and wrong on what triggers it, and checking only the number would have passed
it.

Third: when a doc describes a setting, confirm something **consumes** it. One setting was
nearly filed as dead after three greps missed its only reader in
`frontend/src/ui/app.ts` — search the frontend, not just `src-tauri`.

## Tools in the repo

- `tools/check_quotes.py` — doc quotes vs. source strings.
- `tools/check_code_quotes.py` — code identifiers quoted in docs that no longer exist.

Both had bugs that would have been reported as ~25 false doc errors (wrong search roots; a
word-run matcher broken by short intervening words). Fixed, but **treat their output as
leads, not findings** — confirm each against the file before editing a page.

## Pages already reviewed

`library.md`, `profiles.md`, `modpacks.md`, `modlist.md`, `launch-packs.md`, `plugins.md`,
`scheduler.md`, `themes.md`, `storage.md`, `community.md`, `repo.md`, `features/mapper.md`,
`how-it-works/mapper.md`, `integrity-hashing.md`, `sync-repos.md`, `scanning-cache.md`,
`performance.md`, `security.md`, `index.md`, `reference/api.md`, `reference/actions.md`,
`reference/troubleshooting.md`, `reference/github-pat.md`.

18 corrections landed from these.

## Still unread — 2 pages

| Page | Why it is worth reading |
|---|---|
| `how-it-works/extending.md` | Plugins/API surface; cross-check against `features/plugins.md` and `reference/api.md`. |
| `how-it-works/architecture.md` | Partially done. Cross-check against `how-it-works/index.md`. |

## What the finished pages taught

A pattern held across every page checked, and it is worth using rather than re-deriving:

**Pages describing a MECHANISM were accurate.** `privacy-telemetry`, `reference/mcp`,
`credits`, `how-it-works/index`, `profiles-activation` — all correct, including their
strongest claims. A mechanism rarely changes, so prose about it ages well.

**Pages listing UI ELEMENTS had OMISSIONS, not errors.** `settings.md` was missing the local
session recorder entirely (privacy-relevant) and the scanning section. `apps.md` covered four
of six tabs. `tips.md` described the pre-registry shortcut system. Nothing in them was false —
they were simply incomplete, which reads perfectly well and is therefore far harder to spot.

**So the technique that works on a list page is NOT reading it.** Enumerate from the code —
`const TABS = [...]`, the `settings-*` ids in index.html, the dispatch arms in the MCP server
— and check each entry against the page. Every omission above was found that way, and none of
them would have been found by reading.

**Verifying a page also finds things beside it.** `credits.md` was correct about GPL-3.0, but
checking it revealed that neither Cargo.toml nor package.json declared a licence at all.

## Two real bugs came from doc claims

Both worth remembering, because they justify the whole exercise:

- `conflicts.md` promised the Mapper's worst case was "a mis-shaped mod you can reshape
  again". The code did `remove_dir_all` on a name collision. (BMM `489d7e5`)
- The same page said disabling walks the active list "in reverse, so the most recently
  enabled mod wins". The code walked it forward and restored the OLDEST layer — the game
  silently dropped two layers instead of one. **The docs were right and the code was wrong.**
  (BMM `da8ff91`)

## Changed under the audit — re-verify these

Server Repo moved a lot after most of `repo.md` was reviewed. Docs have **not** been
updated for any of it:

- **Manifest-only generation.** New: point BMM at an existing mods folder, get a `repo.json`
  with nothing copied. `mods_dir`, `only_dirs`, `files_base_url`, `files_layout`.
- **`files_layout`.** `{id}`/`{path}` template. Default is derived from where the manifest
  lands relative to the scanned folder — *not* a hardcoded `mods/{id}/{path}`.
- **Signing.** Every generation re-signs, including updates.
- **Modpacks in manifests**, with mod ids remapped from BMM ids to folder names.
- **Account-based ban/allow lists** via BCWEB-signed attestations (`commands/identity.rs`),
  and BCWEB's `/me/repo-identity`.
- **Sync option**: record the repo as a visible update source on the mods it installs.
- **Per-repo auto-sync**: checked at launch. It does **not** sync by itself — the docs must
  not imply otherwise.

`repo.md` and `how-it-works/sync-repos.md` are both stale on these.

## Guards that now exist

`npm run ci` includes `check-diagrams.mjs` (every `openDiagram` id in the markup resolves)
and `check-imports.mjs`. Both were added after real bugs. If a doc page references a
diagram id, the guard covers the markup, not the docs.

## Not verified by clicking

None of the Server Repo work above has been exercised in a running app — tsc, cargo tests
and the guard scripts only. A doc claim about that UI should be checked against the code,
not against a screenshot or memory of it working.
