# Library

The **Library** is where every mod you own lives — installed or not, from any source. If you
only ever learn one screen in BMM, make it this one: everything else (profiles, modpacks,
lists) is a different way of arranging what the Library holds.

![The Library screen](../assets/screens/library.annotated.png)

| | | |
|---|---|---|
| **1** | **Search** | Filters as you type, across names, authors and tags. |
| **2** | **Filters** | Narrow by game, category, or install state. |
| **3** | **Install** | Adds the selected mod to the profile you're currently on. |

## Adding your first mod

=== "From a file"

    Drag a `.zip` or a mod folder anywhere onto the window. BMM reads it, works out which
    game it belongs to, and files it — no dialog.

=== "From a repo"

    See [Server Repo](repo.md). A repo is a shared source; once added, its mods appear here
    alongside your local ones and are marked with the repo's name.

!!! tip "Archived mods stay archived"

    A `.zip` is kept zipped. BMM extracts it to a temporary cache only when something
    actually needs the files, so a big library doesn't cost you disk space you're not using.

## What "installed" means here

A mod in the Library is *available*; a mod is *installed* only relative to a
[profile](profiles.md). That distinction is the thing newcomers trip on: uninstalling from a
profile doesn't delete the mod, it just stops that profile from using it. The mod stays in
the Library, ready for another profile.

<!-- TODO(content): the per-mod detail panel, the bulk actions bar, and the right-click menu
     still need their own capture + spec before they can be documented honestly. -->
