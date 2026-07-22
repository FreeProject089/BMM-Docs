# Hosting & sync (server repos)

A server repo turns one person's profile into a **hosted source of truth**: everyone who subscribes
converges on the exact same mods, versions and order — and stays converged as the owner updates it.
There are two halves — hosting it, and syncing from it.

## Hosting

BMM turns the chosen profile into a servable repository:

- A **manifest** (`repo.json`) listing every file with its **SHA-256** hash, plus **4&nbsp;MB chunk
  hashes** (also SHA-256) so updates can be differential.
- A cryptographic **signature**: the manifest is signed with an **ed25519** key derived from the
  host's identity, and the public key is the repo's `author_id`. A subscriber can verify the
  signature to confirm the repo really came from that author.

You serve it either from BMM's **built-in mini-server** or a generated standalone server (Node, or a
`.bat`/`.sh` script) on a dedicated machine, over HTTP — **HTTPS is strongly recommended**.

```mermaid
flowchart LR
    PROF["Profile"] --> GEN["Build repo.json<br/>(files + SHA-256 + chunk hashes)"]
    GEN --> SIGN["Sign (ed25519 author_id)"]
    SIGN --> SERVE["Serve over HTTP(S)<br/>(mini-server or standalone)"]
    SERVE --> LINK["Share the link"]
```

### Access control (self-hosted)

A self-hosted repo is **public by default**. It can be restricted two ways:

- A **whitelist / ban list**, matched automatically against a subscriber's linked account or device
  identity.
- An optional **download password**. Set it when you generate the server; subscribers are then asked
  for it the first time they connect (BMM sends it as an `X-Repo-Password` header and remembers it for
  later syncs). Leave it blank for an open repo.

Keep the download password distinct from the `admin_password`: the latter only protects the *host's*
admin panel (pushing new versions) and is not a subscriber gate.

## Sync

The client never blindly re-downloads. It fetches the manifest and reconciles it with what it has.

```mermaid
sequenceDiagram
    participant Host as Server repo
    participant Client as Subscriber's BMM
    Client->>Host: GET repo.json (files + SHA-256)
    Host-->>Client: manifest
    Note over Client: skip files whose SHA-256 already matches
    Client->>Host: for a changed file, request only the mismatched 4 MB chunks (HTTP Range)
    Host-->>Client: those chunks
    Note over Client: verify each file's SHA-256, then deploy
```

A **version string** on the repo drives update *detection*: BMM flags a mod when the repo's published
version differs from the one installed. Applying the update re-runs the sync above — transferring only
the changed files (down to the changed chunks) and removing mods the host has dropped. That's why a
small update to a huge collection costs a few MB.

!!! note "BetterCommunity is not the same thing"
    The BetterCommunity hub adds features a repo you host yourself does **not** have: a
    `BCR-XXXX-XXXX` repo fingerprint, account-based (email / password) access, and managed hosting.
    A plain self-hosted repo has the `author_id` signature above — not a BCR fingerprint.

!!! info "See it in the app"
    Help &amp; other → Developer → **Server mode** and **Hosting flow**. User guide:
    [Server Repo](../features/repo.md).
