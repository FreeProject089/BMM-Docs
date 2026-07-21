# Extending BMM

Everything the UI can do, it does by asking the core through one channel. That same channel is open
to **plugins, scripts and AI clients** — so anything BMM does, you can automate.

## Three ways in

```mermaid
flowchart TB
    subgraph Clients
        PLUG["Plugins"]
        SCRIPT["Scripts / CLI"]
        AI["AI client<br/>(MCP)"]
        PAGE["Custom pages<br/>(bmmpage://)"]
    end
    subgraph BMM
        API["Local HTTP API"]
        MCP["MCP server"]
        BROKER["Permission broker"]
        CORE["Core commands"]
    end
    PLUG --> API
    SCRIPT --> API
    AI --> MCP
    PAGE --> BROKER
    API --> CORE
    MCP --> CORE
    BROKER --> CORE
```

- **Local API** — a small HTTP server on your machine. Plugins and scripts call it to scan,
  activate, build packs, read state, and more.
- **MCP server** — the same capabilities exposed as Model Context Protocol tools, so an AI assistant
  can drive BMM conversationally. It runs over stdio, not a public port.
- **Custom pages** — sandboxed `bmmpage://` mini-apps you pin to the navbar. They talk to BMM only
  through a **permission broker**, so a page gets exactly the access you grant it and nothing more.

## Deeplinks

Buttons on the web ("Install this mod in BMM") work through **deeplinks** — a URL scheme BMM
registers with the OS. Clicking one hands the request to the running app, which confirms and acts.

```mermaid
flowchart LR
    WEB["Web button"] --> LINK["bmm:// deeplink"]
    LINK --> APP["BMM (running)"]
    APP --> CONFIRM{"confirm"}
    CONFIRM -- yes --> ACT["install / add source"]
```

!!! info "See it in the app"
    Help &amp; other → Developer → **MCP server &amp; local API**, **Custom pages**,
    **One-click install**. Reference: [API](../reference/api.md).
