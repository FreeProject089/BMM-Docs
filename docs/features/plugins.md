# Plugins & API

> Extend BMM with community plugins and automate actions.

If BMM doesn't do the thing you need, this is where the thing gets added — without waiting
for a release.

![The Plugins screen](../assets/screens/plugins.annotated.png)

| | | |
|---|---|---|
| **1** | **Installed** | Your plugins. |
| **2** | **Browse** | Community plugins. |
| **3** | **API** | The endpoints a plugin can call. |

!!! warning "Community plugins are not reviewed"

    BMM says it plainly on the banner: these plugins are created by the community and are
    **not officially reviewed**. Install from people you have some reason to trust, the same
    way you'd treat any other executable.

    They are, however, **bounded**: a plugin acts through the [API](../reference/api.md) with
    its own token, and only does what you've granted it — `mods.write`, `profiles.write`, and
    so on. Review those grants in **Plugins → Permissions**. A plugin that only reads your
    mod list needs no grant at all: reads aren't permission-gated, so there is nothing to
    give it. What a grant buys a plugin is the ability to *change* things.

## Strict mode

Some plugins apply a list of mods. *Strict* decides what happens to everything else:

> This plugin will disable all mods not in the list.

Non-strict adds; strict makes your setup **match** the list exactly. BMM asks before doing
it, and shows you which mods it's about to turn off — read that list rather than clicking
through it.

## Scheduling & automation

Reachable from here, and the reason the API exists:

> Schedule BMM actions (one-time or recurring) — activate a mod, modpack, profile…

A task can run **even when BMM is closed** (it registers with the OS scheduler). Rules are
evaluated top to bottom and *the first matching row wins* — so order your rules from most
specific to most general, exactly like a firewall.

<!-- TODO(content): the API reference, the endpoint list and custom commands need their own
     pages — this is 960+ strings' worth of surface. -->
