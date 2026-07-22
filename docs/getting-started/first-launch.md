# First launch

Three steps. Do them in order — the second one is the one people skip, and it's the one that
matters.

## 1. Create a profile

BMM opens on an empty [Profiles](../features/profiles.md) screen and says:

> No active profile — create your first profile so a game update or a reinstall never wipes
> your setup again.

Give it a name and point it at your game folder. One folder per profile.

## 2. Understand what just happened

> Your first profile is ready! Everything you enable from now on is saved right here — safe
> from game updates and reinstalls.

That's the deal in one sentence. Your mods live in BMM, not in the game. The game folder
becomes something BMM *writes to*, not something you maintain by hand.

## 3. Add a mod and turn it on

Drag a `.zip` or a mod folder anywhere onto the window. It lands in the
[Library](../features/library.md). Then enable it — a single click on the card's toggle, or a
**double-click anywhere on the card**, is what puts it in the game, for *this* profile.

Select a card (single click) and the **detail panel** opens: version, author, description, its
cross-machine identity, any conflicts with other mods, dependencies, tags, and an integrity
check. You don't need any of it on day one — but it's there when you do.

If the game acts like the mod isn't there, it's almost always packaging, not BMM: see the
[Mapper](../features/mapper.md).

## Coming from another manager?

Don't rebuild a setup by hand if you don't have to. BMM imports existing profiles from:

- **OvGME** — it scans your OvGME data folder and brings the profiles over.
- **OMM / Open Mod Manager** — import an `.omm` or `.omx` profile directly.

Do that first; then tidy up in BMM.

!!! tip "Practise without risk"

    **Help & other → Interactive Tutorial Hub** ships with small bundled games and a mod pack,
    so you can learn the whole flow — profiles, activation, conflicts, sharing — without
    touching a real install.
