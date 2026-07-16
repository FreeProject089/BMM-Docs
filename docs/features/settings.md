# Settings

Settings is a long page, but most of it you set once and forget. This tour starts with the
handful that change how BMM *feels*, then walks the rest section by section so nothing is a
mystery.

## The four that matter most

### Themes & Appearance

> Customise every colour, font and element of BMM. Share themes in one click.

Not a light/dark toggle — a theme editor. You can replace BMM's built-in images (logo,
wallpaper, even the Tasky mascot), and *add your own buttons, banners, badges or widgets
anywhere in BMM*. Themes export as a file and import as one, and a catalog of themes works
like the [App Catalog](apps.md). See [Themes](themes.md) for the whole engine.

Start from one of the built-in presets and tweak. The editor's own advice: hover a label for
help, click **?** for the MDN docs on that CSS property.

### Storage & Smart I/O

The setting to know if BMM ever makes your PC feel sluggish while activating mods:

> Limit the read/write speed on your disks during mod activation to prevent system lag.
> (0 = unlimited)

**Auto-Calibration** benchmarks your drives and suggests an I/O limit per disk. Run it once;
it's the difference between "mods activate in the background" and "my machine froze for thirty
seconds". Limits are per-disk, so a fast NVMe and a slow external drive get their own ceilings.

### Updates

Check for a new BMM version, opt into **pre-releases**, or turn **auto-update** off.
Pre-releases get fixes first and bugs first — the toggle is there so it's your call, not a
surprise. A separate control checks your *mods* for updates (see [Mod updates](modlist.md)),
distinct from updating the app itself.

### Data

Export everything, import it back. Use export before anything you're not sure about — it's the
cheapest insurance in the app.

!!! danger "Factory reset"

    The Debug section can wipe BMM back to zero. It asks first. There is no undo — export your
    data before you go near it.

## Everything else, section by section

### Language

Switch BMM's interface language. Translations are community-editable — the same files this
picker reads can be exported, translated, and imported back (see the translation tools further
down the page).

### Identity & API

> All your important credentials in one place. Click the eye icon to reveal a value.

Your **creator ID**, the local **API token**, the API **URL and port**, and the app version.
The [local API](../reference/api.md) binds to `127.0.0.1` on port **51274** by default; you can
change the port here (it takes effect after a restart). This is also where you reveal or reset
the API token that plugins and scripts authenticate with.

### Privacy & Telemetry

Opt in or out of anonymous usage data, and manage the sub-options (session replays, full
capture, benchmark sharing) independently. Everything is off unless you turn it on, and the
page spells out exactly what each toggle sends.

### Security (plugin trust)

Choose how much freedom plugins get: **full access** or a **limited/sandboxed** mode. This is
the global backstop for the per-plugin permissions you grant in
[Plugins & API](plugins.md) — tighten it if you run plugins you don't fully trust.

### Discord Rich Presence

Show what you're doing in BMM on your Discord profile, or turn it off. Purely cosmetic.

### Launch Packs

Bundle several apps/executables into one pack you can launch together — handy for "start the
game, the voice-attack tool, and the map app" in one click. Create, edit, and delete packs
here; run them from here, the [API](../reference/api.md), or a deeplink.

### Scheduling & automation

Save tasks — apply a modpack, run a launch pack, export your data — and trigger them on a
schedule or on demand. See [Scheduler](scheduler.md) for the full picture.

### Storage tools: integrity & benchmark

Beyond the Smart I/O limits above, this area holds the **SHA recalculation** control (rebuild
the per-file hashes the integrity engine checks against) and the **benchmark** (measure how
fast BMM moves files on your hardware — the same engine Auto-Calibration uses).

### Tags

Manage your custom mod tags — the labels you filter the [Library](library.md) by. Rename or
remove them here in one place.

### Sound & keyboard shortcuts

Toggle UI sounds, and review the keyboard shortcuts BMM responds to.

### GitHub token

An optional personal access token, used when BMM talks to GitHub (release checks, raw
downloads) to avoid the stricter anonymous rate limit. Optional — only add one if you hit rate
limits.

### Tutorial

Replay the interactive in-app tutorials at any time. New to BMM? Start here.

### Debug & developer tools

Diagnostics, crash-report tools, and the **factory reset** noted above. Handy when something's
wrong; the reset is the one control in the whole app with no undo, so it's fenced behind a
confirmation.
