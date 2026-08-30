# Shot list — what each recording has to show

The neighbouring `README.md` says how to record. This says **what**.

It exists because the two are not the same problem, and the second one is the one that goes
wrong quietly: a recording that plays perfectly and shows the wrong screen looks fine to
everyone except the reader who came to that page for that thing. Thirteen of these files were
once thirteen copies of one recording, under thirteen names, and nothing complained.

Every row below is taken from the page that embeds the file — its heading and its
`data-title` — so the brief is what the page already promises a reader, not what somebody
thought the feature was about.

## The rule

**A recording answers the caption above it.** If the caption says "Adding a mod and enabling
it", the recording opens with no mod added and ends with one enabled. Anything else in the
clip is noise the reader has to sit through.

Three things follow from that:

- **10–30 seconds.** One task. A file is ~20 MB per twenty seconds, tracked in git-lfs, and
  read by somebody who wanted a two-sentence answer.
- **Unmasked, on the demo profile.** A masked recording shows every mod name and path as
  `••••`, which is fine for showing a flow and useless for showing a screen. The demo profile
  is what makes unmasked safe.
- **Start cold.** rrweb writes its FullSnapshot only when a session genuinely begins, so the
  intro is the head of every clip. That is also the check: a clip that starts mid-screen was
  exported from a session that was already running, and it will open in no player.

## The thirteen

| File | Page · caption | Show, in order | Do not |
|---|---|---|---|
| `library.bmmreplay` | Library · *Adding a mod and enabling it* | the empty list → add a mod → it appears disabled → enable it → the count changes | browse a catalogue; that is `apps` |
| `profiles.bmmreplay` | Profiles · *Creating a profile and switching to it* | create → name it → switch → the mod list changes with it | edit paths; the point is that the switch is visible |
| `modlist.bmmreplay` | .MM Lists · *Exporting and importing a .MM list* | export from a profile → open the file picker → import into another → the mods arrive | narrate the format; the page does that |
| `modpacks.bmmreplay` | Modpacks · *Building and applying a modpack* | pick mods → build → apply to a profile → the result | the creator's advanced tabs |
| `mapper.bmmreplay` | Mapper · *Remapping a badly-packaged mod* | a mod that lands in the wrong folder → open Mapper → drag the root → apply → the corrected tree | explain archives; show the fix |
| `apps.bmmreplay` | App Catalog · *Installing an app from the catalog* | browse → pick one → install → it appears installed | sign in; the catalogue is public |
| `repo.bmmreplay` | Server Repo · *Connecting to a repo and syncing* | add a repo by URL → connect → sync → the mods arrive | credentials on screen, even a demo one |
| `plugins.bmmreplay` | Plugins & API · *Granting a permission and using a plugin* | install → the permission prompt → grant → the plugin does its thing | the plugin editor |
| `scheduler.bmmreplay` | Scheduling & automation · *Building a scheduled task* | new task → a trigger → an action → save → it appears in the list, with its next run | wait for it to fire |
| `themes.bmmreplay` | Themes & Appearance · *Restyling BMM with the theme editor* | open the editor → change a colour → watch the app follow → save the theme | every token; two or three are the point |
| `settings.bmmreplay` | Settings · *A tour of Settings* | the sections in order, pausing on the ones the page names | change anything destructive |
| `community.bmmreplay` | Community · *Reading the community blog* | open the tab → a post with rich blocks → scroll it | post or comment |
| `bmm-demo.bmmreplay` | Privacy · *A masked BMM session*<br>Tips · *A recorded BMM session* | a short ordinary session — this is the one clip that is **masked on purpose**, because the page is about what masking does | unmask it; that is the whole point of this file |

## What to re-record, and when

- **The screen changed.** A recording is a screenshot that moves; it goes stale the same way,
  and worse, because a reader watches it for twenty seconds before noticing.
- **The caption changed.** The caption is the brief. Changing one without the other is how a
  clip ends up answering a question nobody asked.
- **It is over 30 seconds.** Not a rule about size — a rule about attention.

`record.sh` verifies mtime, that the file parses, that a FullSnapshot is present and what the
`masked` flag says. It does not and cannot verify that the clip shows the right thing: an
export that writes nothing still returns success. **Watch the result.**

## Still to record

Nothing, today: every page that embeds a recording has its own, and every file in this folder
is embedded. Add a row above before recording a new one — a file nobody planned is a file
nobody reviews, and the folder already has one of those in its history.
