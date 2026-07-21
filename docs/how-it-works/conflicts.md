# Conflict resolution

Two mods are in **conflict** when they ship the same file. In most managers the one activated last
silently wins. BMM refuses to be silent: it detects the overlap from the index *before* anything is
written, and asks you.

## Detection is just an index lookup

Because every file is indexed by its destination path, finding conflicts is a grouping operation —
no disk access needed. Any path claimed by more than one enabled mod is a conflict.

```mermaid
flowchart TB
    subgraph Enabled["Enabled mods"]
        A["Mod A → cockpit.lua"]
        B["Mod B → cockpit.lua"]
        C["Mod C → sound.ogg"]
    end
    A --> G{"group by<br/>destination path"}
    B --> G
    C --> G
    G -- "cockpit.lua: A, B" --> CONF["⚠ conflict"]
    G -- "sound.ogg: C" --> OK["clean"]
```

## Resolving

For each conflicting file you pick a winner, or set a **priority order** so the higher-priority mod
wins wherever it overlaps. Your decisions are stored **per profile**, so the same two mods can
resolve differently in "vanilla-ish" and "kitchen-sink" setups.

```mermaid
flowchart LR
    CONF["cockpit.lua<br/>A vs B"] --> CHOICE{Your choice}
    CHOICE -- "A wins" --> DEP["deploy A's file"]
    CHOICE -- "B wins" --> DEP2["deploy B's file"]
    CHOICE -- "priority" --> RULE["apply order<br/>everywhere"]
```

Once resolved, the deploy is unambiguous — BMM writes exactly the winning file for each path, and
records which mod it came from so deactivation stays clean.

!!! info "See it in the app"
    Help &amp; other → Developer → **Conflict management**; the **Conflicts** tutorial.
