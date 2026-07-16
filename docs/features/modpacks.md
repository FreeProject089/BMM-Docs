# Modpacks

A modpack is a **named bundle of mods you can toggle in one click**. Where a
[profile](profiles.md) is "my setup for this game", a modpack is "this group of mods,
together" — and BMM's own screen calls the action *Quick Apply*: click to toggle a modpack
on or off.

![The Modpacks screen](../assets/screens/modpacks.annotated.png)

| | | |
|---|---|---|
| **1** | **Pack card** | Click toggles the whole pack on or off. |
| **2** | **Export** | Produces a file you can hand to someone. |
| **3** | **Import** | Reads someone else's pack. |

## Modpack or profile?

They solve different problems, and using the wrong one is the usual confusion:

| | Profile | Modpack |
|---|---|---|
| Answers | "Which mods are on for this game?" | "Which mods belong together?" |
| Scope | One game, one setup | A group, reusable |
| Switching | Changes your whole setup | Toggles just that group |

A modpack can also **mix mods from different profiles** — BMM's *multi-profile* option
exists exactly for the pack that doesn't belong to a single setup.

## Sharing one: the hash is the point

When you export, BMM doesn't ship the mods — it ships a **signature**:

> BMM creates a unique signature (hash) for each mod. When a friend imports your pack, BMM
> recognises the exact mods.

So the file stays small, and "the same mod" means byte-identical, not "same name, probably".
That's what makes an import either work exactly or tell you the truth:

> The following mods are not installed on this PC.

You get the list. Nothing silently half-applies.

## Repair

If a pack's mods go missing or get corrupted, the card says so — *Some mods are missing or
corrupted* — and offers **Repair**. Use it before debugging the game: a pack that can't fully
apply is a far more likely explanation than the game itself.

<!-- TODO(content): the export dialog's options need a capture + spec. -->
