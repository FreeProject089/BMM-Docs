# Scheduling & automation

> Schedule BMM actions (one-time or recurring) — activate a mod, modpack, profile…

Reachable from [Plugins & API](plugins.md). This is the part of BMM that does things while
you're not looking.

![The scheduler](../assets/screens/scheduler.annotated.png)

| | | |
|---|---|---|
| **1** | **Trigger** | *When* it runs. |
| **2** | **Rules** | *Whether* it runs, and what it does. |
| **3** | **New task** | One task, one job. |

## A task has three parts

**Trigger → rules → action.** The trigger asks *when*, the rules ask *whether*, the action is
*what*.

### 1. Trigger — when

| Type | Runs |
|---|---|
| `once` | One time, at a date and time. |
| `interval` | Every N minutes. |
| `hourly` | Every N hours. |

There's also a monthly option, built through the OS's own scheduling classes rather than a
simple cmdlet — so it exists, it's just assembled differently under the hood.

### 2. Rules — whether

A rule is `IF <condition> THEN <action>`, and this is where the scheduler stops being a
timer and starts being useful. Conditions:

| Condition | True when |
|---|---|
| `Always` | Unconditionally. |
| `Profile is active` | A given [profile](profiles.md) is the current one. |
| `Mod is enabled` / `Mod is disabled` | A given mod's state. |
| `Modpack is active` | A [modpack](modpacks.md) is applied. |
| `All active-profile mods are on` | Nothing in the profile is off. |
| `App is running` | A process is up — e.g. the game itself. |
| `Day of week` | Monday…Sunday. |
| `Time is within` | A time range. |
| `Value compare` | `if X > Y` — a numeric comparison. |
| `Command succeeds` | An external command exits 0. |

!!! warning "First match wins"

    From the scheduler's own empty state: *No rules — add one. **First matching row wins**
    (top to bottom).*

    Order your rules **most specific first**, exactly like firewall rules. A rule with
    `Always` at the top makes every rule below it dead code — and nothing will tell you,
    because as far as the scheduler is concerned it did its job.

### 3. Action — what

| | |
|---|---|
| **Mods** | Enable / disable one · enable all · disable all · scan the mods folder |
| **Profiles** | Activate a profile |
| **Modpacks** | Enable / disable |
| **App** | Launch an app · run a benchmark · set a theme |
| **Other** | Show a notification · run a `bmm://` deeplink · run a custom command |

## Running when BMM is closed

> Run even when BMM is closed.

This registers the task with **your operating system's scheduler**, not BMM's own loop. The
OS wakes it up on time whether or not the app is running — which is the whole point for
"prepare my modpack at 6am".

It also means the task lives outside BMM. Deleting it in BMM removes the OS task too; if you
go poking in your OS's task list, that's what those entries are.

## Custom commands

> Allow custom commands.

Off by default, and rightly: a scheduled task that can run arbitrary commands is a scheduled
task that can do anything, at a time you're not watching. Turn it on when you need it, and
know what the command does.

## Example

The scheduler ships one, and it's a good shape to copy:

> Every hour, loop 3× and show a notification each time.

Start there, swap the notification for a real action, and add a condition so it only fires
when it should.

<!-- TODO(content): the value-compare condition's operands and the loop/repeat options need
     their own capture + spec. -->
