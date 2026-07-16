# Install BMM

BMM is a **Windows** application. Installing it takes three steps:

1. Download the latest release — the installer is a Windows `.exe` (NSIS), with an `.msi`
   also available.
2. Run it. Windows may show a SmartScreen prompt the first time (it does that for any new
   publisher) — choose **More info → Run anyway**.
3. Launch BMM.

That's it: no account to create, nothing to configure beforehand. You do your first setup
*inside* the app — see [First launch](first-launch.md).

!!! tip "Pick an install location you control"

    Install BMM somewhere you own (your user folder, a games drive), not deep inside
    `Program Files` if you'd rather avoid Windows' permission prompts when it updates itself.
    BMM never touches your game folders until *you* activate a mod.

## Which build?

**Stable**, unless you have a reason. In **Settings → Updates** you can opt into
**pre-releases**: they get fixes first and bugs first. That's a real trade, which is why it's
a toggle and not the default. If you like being early and don't mind reporting the occasional
rough edge, turn it on; if you just want your mods to work, leave it off.

## Auto-update

On by default. BMM checks, tells you, and updates itself. You can turn it off in the same
place — but then update by hand, because a mod manager that's a year behind the repos it reads
will eventually disagree with them.

!!! note "Rate-limited on GitHub?"

    Update and download checks hit GitHub. If you ever see rate-limit errors, add an optional
    **GitHub token** in **Settings → Identity & API** — it raises the limit. Purely optional;
    most people never need it.

<!-- TODO(content): the installer's screens need captures. BetterInstaller (the NSIS/MSI
     replacement) will reshape this page — don't over-invest in installer specifics until it
     lands. -->
