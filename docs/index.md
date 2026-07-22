# BetterModsManager

BMM installs, organises and shares your mods — across games, without ever touching the
original files more than it has to.

If you're new, read this page. It's short, and it explains the one idea the rest of the app
is built on. Skipping it is why people get lost on screen three.

!!! tip "Two ways to read these docs"
    The **Getting started** and **Features** sections teach you how to *use* BMM. The new
    **[How it works](how-it-works/index.md)** section is for the curious and for contributors —
    it explains *why* BMM behaves the way it does, with diagrams. Read whichever half you came for.

## The one idea: your mods and your setups are separate things

Most mod managers put mods *in the game*. BMM keeps them apart:

- The **[Library](features/library.md)** holds every mod you own. It's a shelf. A mod sitting
  there does nothing.
- A **[Profile](features/profiles.md)** decides which of those mods are *on*, and in what
  order, for one game.

That split is the whole point. As BMM puts it on its own empty-profile screen:

> A profile is your safety net: enable, disable and reorder mods freely, and a game update
> never wipes your setup again.

Because the mods live in the Library, a game update, a reinstall, or a bad mod can't take
them with it. You rebuild by switching a profile back on, not by re-downloading anything.

This is also why **uninstalling a mod from a profile doesn't delete it**. It goes back to
being a mod on a shelf, ready for another profile. Newcomers expect a delete; BMM gives them
an undo.

## What each screen is for

| Screen | Use it when |
|---|---|
| **[Library](features/library.md)** | You want to see, add, or verify the mods you own. |
| **[Profiles](features/profiles.md)** | You want a setup per game — or several per game (vanilla-ish, heavy, testing). |
| **[.MM Lists](features/modlist.md)** | You want to hand your exact setup to someone, links included. |
| **[Modpacks](features/modpacks.md)** | You want to toggle a whole bundle of mods on and off at once. |
| **[Server Repo](features/repo.md)** | You want a source that tells BMM when a mod has an update. |
| **[Plugins & API](features/plugins.md)** | You want BMM to do something it doesn't do out of the box. |
| **[App Catalog](features/apps.md)** | You want the tools *around* modding, installed in one click. |
| **[Mapper](features/mapper.md)** | A mod's folders don't match what the game expects. |
| **[BetterCommunity](features/community.md)** | You want news and posts from the project's blogs. |
| **[Settings](features/settings.md)** | Themes, updates, storage limits, data export. |

## Conflicts, in one paragraph

Two mods that ship the same file are in **conflict** — whichever is activated last wins, and
overwrites the other. BMM detects this before you commit, tells you exactly which files
overlap, and lets you decide the order. You'll meet this the first time you enable two big
mods, so it's worth knowing the word now. See [Library](features/library.md#conflicts).

## Where to go next

1. **[Install BMM](getting-started/install.md)** — a few minutes.
2. **[First launch](getting-started/first-launch.md)** — create a profile, add a mod, turn it on.
3. Then pick whichever screen matches what you're trying to do.

!!! tip "There's a tutorial *inside* the app"

    **Help & other → Interactive Tutorial Hub** teaches BMM step by step with a built-in
    practice sandbox (an example profile, example mods and a modpack, cleaned up automatically)
    so you can practise without risking a real install. If you learn by doing rather than
    reading, start there and use this site as reference.
