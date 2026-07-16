# API reference

BMM runs a local HTTP API. It's what [plugins](../features/plugins.md) talk to, what the
scheduler drives, and what you can `curl` yourself.

**Base URL:** `http://127.0.0.1:51274` — local only. 51274 is the default; if it's taken, BMM
binds another and reports the effective one, so read the port from the app rather than
hard-coding it.

## Authenticating

Every call carries a bearer token:

```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:51274/api/health
```

There are **two kinds of token**, and the difference is the whole security model:

| Token | Where it comes from | What it can do |
|---|---|---|
| **Admin token** | Settings — one per install | Everything. No permission checks. |
| **Plugin token** | Issued per plugin | Only what that plugin has been granted. |

Use the admin token for your own scripts, the CLI, or the in-app tester. Give a **plugin its
own token** — BMM's own hint says it plainly: *each plugin should authenticate with its OWN
token*. That's not bookkeeping; it's what makes permissions mean anything, because BMM
resolves *who is calling* from the token itself and never from a header a caller could
simply invent.

## Permissions

Eight, in read/write pairs across four domains:

```
app.read       app.write
catalog.read   catalog.write
mods.read      mods.write
profiles.read  profiles.write
```

A write endpoint demands the matching `*.write` — `POST /api/mods/enable` requires
`mods.write`, `POST /api/profiles/create` requires `profiles.write`. A plugin calling
without the grant gets a permission error naming exactly which one it lacked, rather than a
silent no-op.

Grant them per plugin in **Plugins → Permissions**, or over the API itself:

| Endpoint | Does |
|---|---|
| `GET /api/plugins/permissions` | A map of `plugin_id → [permissions]` — every plugin at once. |
| `GET /api/plugins/{id}/permissions` | One plugin's list. |
| `POST /api/plugins/{id}/permissions` | **Replaces** the whole list. Not a merge — send the full set. |

!!! warning "Replace, not add"

    Setting permissions overwrites the list. Read it first, add to what you got, send the
    result — otherwise you'll silently revoke everything you didn't mention.

## The endpoints

74 of them. The shape is consistent: `GET` reads, `POST` acts.

### Reading

| Endpoint | Returns |
|---|---|
| `GET /api/health` | Is BMM up. No auth needed. |
| `GET /api/status` | What it's doing right now. |
| `GET /api/mods` | Every mod in the [Library](../features/library.md). |
| `GET /api/mods/active` | Only what's enabled on the current profile. |
| `GET /api/mods/{id}` | One mod. |
| `GET /api/profiles` | Every [profile](../features/profiles.md). |
| `GET /api/modpacks` | Every [modpack](../features/modpacks.md). |
| `GET /api/plugins` | Installed plugins. |
| `GET /api/creator-id` | Your creator ID — the identity [repos](../features/repo.md) know you by. |
| `GET /api/check-update` | Is a BMM update available. |

### Acting

| Endpoint | Does |
|---|---|
| `POST /api/mods/enable` · `/api/mods/disable` | Turn a mod on or off. `mods.write`. |
| `POST /api/mod/check-updates` | Ask the linked [repos](../features/repo.md) about updates. |
| `POST /api/profiles/create` · `/api/profiles/activate` | `profiles.write`. |
| `POST /api/modpacks/create` · `/enable` · `/disable` | `catalog.write`. |
| `POST /api/plugins/apply` | Run a plugin's mod list. |
| `POST /api/plugins/compare` | What *would* change — without changing it. |
| `POST /api/launchpack/run` | Launch a pack. |
| `POST /api/data/export-auto` | Trigger a data export. |

!!! tip "compare before apply"

    `plugins/compare` answers "what would this do?" and touches nothing. Use it before
    `apply` — especially in [strict mode](../features/plugins.md#strict-mode), where apply
    disables everything not in the list.

## Try it without writing code

**Plugins → API** has an in-app tester: pick an endpoint, send it, read the response. It uses
the admin token, so it sees everything — which makes it the wrong place to test whether a
plugin's *permissions* are right. For that, use the plugin's own token.

<!-- TODO(content): the full 74-endpoint list with request/response bodies. The names and
     paths above are read from src-tauri/src/api/mod.rs and the Lang strings; bodies need a
     capture of the in-app tester or a pass through the handlers. -->
