# The mapper

BMM deploys a mod by mirroring its folder tree into the game. That only works if the mod *has* the
right tree. Plenty of downloads don't — the author zipped from the wrong folder, or dumped loose
files at the root. The mapper fixes that once, and remembers.

## The expected shape

A stored mod must contain the full path the game expects, starting from the game root. For
example:

```
\HD Texture Pack
   |_ Data
        |_ Textures
             |_ HD Texture Pack
```

`HD Texture Pack` is the mod; everything under it is the exact tree the files must land in. The
folder names here (`Data`, `Textures`, …) are just an example — use whatever path **your** game
reads from.

## What the mapper does

It's a translation table from *where a file is in the archive* to *where it belongs in the game*.
You build it by dragging, and it's saved with the mod — so the next install, or a re-download of a
new version with the same layout, applies instantly.

```mermaid
flowchart LR
    subgraph Archive["Downloaded archive (wrong shape)"]
        F1["files/hero.png"]
        F2["files/normal.png"]
    end
    subgraph Map["Saved mapping"]
        M["files/*  →  Data/Textures/HD Texture Pack/*"]
    end
    subgraph Game["Deployed (correct shape)"]
        G1["Data/Textures/HD Texture Pack/hero.png"]
        G2["Data/Textures/HD Texture Pack/normal.png"]
    end
    F1 --> Map --> G1
    F2 --> Map --> G2
```

Because the mapping is data, not a one-off manual move, it's **repeatable and versioned with the
mod** — the whole point of doing it in BMM instead of reshaping folders by hand in Explorer.

!!! info "See it in the app"
    Help &amp; other → Developer → **Mod mapper**; the **Mapper** tutorial. And the user guide's
    [Mapper](../features/mapper.md) page for the hands-on walkthrough.
