# Mapper

Some mods are packaged wrong. The files are fine; the folders around them aren't. The Mapper
fixes that without you unzipping anything by hand.

> Reorganize your mod structure to match the game directory.

![The Mod Mapper](../assets/screens/mapper.annotated.png)

| | | |
|---|---|---|
| **1** | **Source tree** | What the mod actually contains. |
| **2** | **Target** | Where those files must land for the game to see them. |
| **3** | **Diagnostic** | Shows the final location *before* you commit. |

## When you need it

The symptom is always the same: **you install a mod, and the game acts like it isn't there.**
Nine times out of ten the archive has one folder too many — the author zipped the containing
folder instead of its contents — so the game looks for `Data/textures/` and finds
`MyMod-v3/Data/textures/`.

## Check before you commit

The Mapper's **Structure Diagnostic** exists for one reason:

> Check the final location of your files before applying changes.

Use it. Guessing at a path and applying is how you end up with files scattered in a game
folder that nothing tracks — the one situation BMM's whole design is trying to avoid.

<!-- TODO(content): the drag-to-remap interaction and the sub-folder stats need a capture. -->
