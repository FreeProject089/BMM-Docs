# Server Repo

A repo is a **source that tells BMM when a mod has an update**. Without one, a mod you
installed by hand stays at the version you installed, forever, silently.

> Browse Server Repositories — official and partner server repositories.

![The Server Repo screen](../assets/screens/repo.annotated.png)

| | | |
|---|---|---|
| **1** | **Repo list** | Sources you've added. |
| **2** | **Browse** | Official and partner repos. |
| **3** | **Add** | Point BMM at a repo URL. |

## Linking a mod to a repo

Adding a repo isn't enough on its own — a mod has to be linked to it:

> Link this mod to one or more repos so BMM can detect updates for it.

One mod can point at several repos. That's deliberate: if a source disappears, the mod is
still tracked by the other.

## Direct downloads have no version

Worth understanding, because it looks like a bug and isn't:

> No update detected. A direct download has no version, so BMM cannot tell if it is newer.

A raw file URL carries no version number, so BMM has nothing to compare. It offers a
**direct re-download** instead of pretending to know. If you want real update detection,
link the mod to a repo that publishes versions.

## Hosting your own

A repo can be yours — see [BetterCommunity](community.md), which hosts repos and can serve
the feed BMM reads. Repo owners get access control (whitelists, bans by IP or creator key).

<!-- TODO(content): the repo dashboard, ban management and access rules deserve their own
     page once captured. -->
