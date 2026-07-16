# Troubleshooting

Start here before reinstalling anything.

## The game acts like the mod isn't there

Almost always packaging, not BMM. The archive has one folder too many, so the game looks for
`Data/` and finds `MyMod-v3/Data/`. Open the [Mapper](../features/mapper.md), run the
**Structure Diagnostic**, and check the final path *before* applying.

## A mod I disabled is still active

Two profiles pointing at the same game folder. BMM warns about this when you set it up —
it's *a major source of human error*. Each profile deploys into the same place and neither
knows what the other left behind. Give each profile its own folder. See
[Profiles](../features/profiles.md).

## Two mods fight — one overwrites the other

That's a [conflict](../features/library.md#conflicts), and it's expected: they ship the same
file. BMM shows you exactly which files overlap and lets you set the activation order. The
last one activated wins.

## BMM says a mod has no updates, but I know it does

If the mod's source is a **direct download**, BMM is being honest:

> A direct download has no version, so BMM cannot tell if it is newer.

There's nothing to compare. Link the mod to a [repo](../features/repo.md) that publishes
versions, or use the direct re-download.

## My PC lags while mods are activating

**Settings → Storage**. Turn on **Smart I/O** and run **Auto-Calibration** once — it
benchmarks your drives and paces the copies so activation stops starving everything else.

## A modpack won't apply fully

The card will say some mods are missing or corrupted, and offer **Repair**. Run it. A pack
that can't fully apply explains far more bugs than the game does.

## Something is badly wrong

**Settings → Data → Export** first, always. Then the Debug section has a crash-log folder and
a factory reset. The reset has no undo — export before you go near it.
