# Privacy, telemetry & offline

## Telemetry is opt-in

Until you explicitly accept the consent dialog, **nothing is collected at all** — the tracker
is a no-op. Declining (or never answering) collects zero data, and declining also wipes
anything previously buffered.

```mermaid
graph TD
    CONSENT{Opt-in consent?} -- "declined / not asked" --> NOTHING["Nothing collected"]
    CONSENT -- "accepted" --> EVENTS["Events: pages, clicks, perf, errors"]
    REPLAY["Session replay (masked by default)"] --> EVENTS

    EVENTS --> QUEUE["Local queue (jsonl, 10 MB cap)"]
    QUEUE --> ENDPOINT{Endpoint configured?}
    ENDPOINT -- no --> LOCAL["Stays on disk"]
    ENDPOINT -- yes --> GZIP["Gzip batch + packet id"]
    GZIP --> ALLOWLIST["HTTPS-only allow-list"]
    ALLOWLIST --> SERVER["Telemetry server"]

    GDPR["Export / per-packet deletion (72 h)"] --> SERVER
    GDPR --> QUEUE
```

## If you opt in

- **What's sent:** pages visited, clicks (**labels only — never what you type**), performance
  samples, errors, and an anonymous hardware profile. No file paths, no mod contents, no name
  or e-mail; your identity is an anonymous id.
- **Session replay** (optional, on by default when telemetry is on) records the UI **masked**:
  mod names, profile names and paths appear as `••••`. Unmasking is a separate, explicit toggle.
- Everything buffers to a **local file (10 MB cap)** first and is only uploaded as gzip batches
  over **HTTPS** — if no endpoint is configured, data never leaves your machine.

## What a session replay actually looks like

Rather than describe it, here is one. This is a real `.bmmreplay` played back in the browser by the
same rrweb player the app uses — the DOM is replayed, so it is **not a video**: text stays text, and
you can see the masking in action.

<div class="bmm-replay"
     data-src="../assets/replays/bmm-demo.bmmreplay"
     data-title="A masked BMM session, replayed in the browser"></div>

!!! note "It loads on demand"

    The player only fetches the recording when you press play — a replay is a JSON event stream and
    this one is around 25 MB, so it is never pulled in just by opening the page.

Notice that mod and profile names read as `••••`. That is the default masking, and it is what gets
recorded — the unmasked values never enter the file at all, so there is nothing to leak later. The
*Full* switch is what changes that, and it is deliberately separate.

## Your controls (Settings → Privacy)

- Master toggle, plus separate toggles for the 7-day benchmark / extra-hardware report and
  session replay.
- **Export** the raw buffer as JSON any time.
- See every **sent packet** (event names and counts only) and request its **deletion** —
  honoured within 72 hours.

Crash reports and saved session replays stay **local** under retention limits you control
(default: 30 sessions / 2 GB) — a crash report is only ever shared when *you* export or send it.

## Offline mode

BMM doesn't just trust the OS "connected" flag — it **probes** two lightweight endpoints; if
neither answers within 5 seconds, you're offline.

- A discreet **"no connection" banner** appears, and network features (repo syncs, catalogs,
  update checks) pause with a warning toast instead of failing cryptically.
- **Everything local keeps working** — library, profiles, activation, the mapper, themes.
- Recovery is automatic: while offline BMM re-probes every **15 seconds**; online, a 2-minute
  re-check catches connections that died silently.

```mermaid
graph TD
    NAVIGATOR["navigator.onLine + events"] --> PROBE{Probe 2 endpoints}
    PROBE -- "any responds" --> ONLINE[Online]
    PROBE -- "both fail" --> OFFLINE[Offline state]

    OFFLINE --> BANNER["'No connection' banner"]
    OFFLINE --> GATES["Online features paused (toast)"]
    OFFLINE --> FAST["Re-probe every 15 s"]
    FAST --> PROBE
    ONLINE --> SLOW["Re-check every 120 s"]
    SLOW --> PROBE
```
