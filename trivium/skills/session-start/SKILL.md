---
name: session-start
description: Use at the start of a working session, when the user says "let's get started" / "what were we working on" / "let's pick this back up", or before beginning a meaningful chunk of work. Recalls the project's current focus, the habit hubs that bear on it, and the few relevant lessons; verifies the focus's forward claims against the code; confirms direction; enters plan mode.
---

# Session Start

Open a working session by consulting what we already know and planning before
we act. This is the reading half of the `session-retro` loop: retro writes
the focus, hubs, and lessons at session end; start reads them back so they
shape the work from the jump. The memory shape is defined in
`${CLAUDE_PLUGIN_ROOT}/TAXONOMY.md`. (Trivia is
[chrisdickinson/trivia](https://github.com/chrisdickinson/trivia) — setup
instructions are Rust-oriented, but it's quite good.)

**Core principle:** load the *few most important* memories, not everything
tagged `project:<slug>`. Walk in reminded of what matters; leave the project
history where it is.

## When to use

- The start of a session, before real work begins.
- Picking work back up after time away ("what were we working on?").
- Before a meaningful chunk of work, when a plan would help.

**Skip if:** the ask is a trivial one-off, or the user already knows exactly
what they want and says so.

## Steps

### 1. Derive the project slug

If `$0` is provided, that is the slug. Otherwise read `Cargo.toml` and use
`[package].name`; with no manifest, use the working-directory basename,
lowercased with non-alphanumerics replaced by hyphens. The tag is
`project:<slug>`.

### 2. Check that trivia is bootstrapped

```
recall(query = "<slug>/trivia-bootstrapped", tags = ["project:<slug>"], limit = 1)
```

A hit counts only if the returned `mnemonic` is exactly
`<slug>/trivia-bootstrapped`; recall always returns the nearest neighbour,
so a different mnemonic means no memory for this project. Point at
`project-trivia-setup` and stop; never fabricate context.

### 3. Recall the seeds — exact mnemonic, one tag

```
recall(query = "<slug>/current-focus", tags = ["project:<slug>"], limit = 1)
recall(query = "<slug>/conventions",   tags = ["project:<slug>"], limit = 1)
```

The exact mnemonic as the query scores far above any near miss, and the
result is the seed only when its `mnemonic` matches exactly. One tag per
call: trivia's tag filter is OR, so a second tag (`focus`, `conventions`)
widens the net to every project using it, and another project's seed can
outrank this one's.

### 4. Recall the lessons — hubs first, then one probe

From the focus's FRONTIER and NEXT sections, name the one or two themes the
session is about to work in. Recall their hubs by mnemonic:

```
recall(query = "<slug>/habits/<theme>", tags = ["project:<slug>"], limit = 1)
```

Hubs are ordered checklists that name their spokes; this is the curated view.
A result is a hub only if its `mnemonic` matches exactly; otherwise the theme
has no hub yet. Then one probe for spokes the hubs may not carry yet:

```
recall(query = "<the NEXT sentence, in plain words>", tags = ["project:<slug>"],
       full_text_search = "<a distinctive word from NEXT>",
       limit = 3, truncate = 500, exclude_tags = ["archive"])
```

If `current-focus` names a lesson the probe did not return, probe once more
with `full_text_search` on a word from that lesson's handle before concluding
it is missing. A lesson that stays unfindable is a reason to suggest
`memory-gardening` to the user.

Let the params cap the pull. A tag-wildcard dump (`recall(tags =
["project:<slug>"])`) loads the universe and buries today's lessons.

### 5. Confirm the focus with the user

Summarize the recalled FRONTIER in one or two sentences, and surface the hub
lines or spokes that bear on it ("last time we learned X"). Ask: **is this
what you want to work on this session?**

If the user redirects, re-run step 4 against the new focus before planning.

### 6. Verify the NEXT claims before they enter the plan

Every NEXT and FOLLOW-UPS item in `current-focus` is a *claim* written at
ship time from a tiring session's mental model — the one part of the memory
nobody checked against the code. Before an item becomes a plan step, verify
it at its consumption site:

- A deferred item may have shipped as a side effect of later work: `git log
  --oneline -S <keyword>`, or grep the generated artifact.
- A named target may sit in the wrong component: read the cited spec section,
  not the paraphrase.
- A type described with a shape may never have had it: grep the type and read
  its real definition.
- A "next spec" pointer more than two weeks old is probably overtaken:
  re-derive the frontier from the specs directory sorted by date, the target
  design doc's implementation-status header, and the roadmap's "last
  refreshed" line — the GROUND TRUTH section says where.

A fan-out Explore agent over the specs directory and the cited types returns
an authoritative map in one shot and keeps this context clean. Done when every
item the plan depends on has been read at its source.

An item found already shipped gets a tombstone now — `memorize`
`<slug>/current-focus` with the same tags and `shipped <hash>` on that line —
so the next session doesn't re-plan it.

### 7. Rate what helped

`rate` the recalled hubs and spokes up if they shaped the direction, down if
they were noise. Ranking learns from this; it is what keeps the caps
meaningful next time.

### 8. Enter plan mode and plan

Call `EnterPlanMode`, then produce a plan for the confirmed focus that
**explicitly carries the recalled lessons forward** — "we hit Y last time, so
the plan avoids it by doing Z." This is the payoff: the lessons inform the
design before any code is written.

## Anti-patterns

| Don't                                                    | Why                                                                                          |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `recall` everything tagged `project:<slug>`              | That's the universe. Load the hubs plus one probe keyed on today's focus.                    |
| Pass two tags to `recall`                                | OR semantics: the second tag pulls in other projects, which can outrank this one's seeds.     |
| Plan against a NEXT item without reading its source      | Three sessions of this project's history lost their first hour to a stale pointer.           |
| Plan against a stale focus without confirming            | Step 5 exists to verify direction before investing in a plan.                                |
| Start editing files before entering plan mode            | Defeats "plan from the jump." Confirm, verify, then `EnterPlanMode`, then act.               |
| Write a retro here                                       | That's `session-retro`'s job. This skill reads, rates, and tombstones shipped follow-ups.    |
| Fabricate context when trivia isn't bootstrapped         | No memory means no recall. Point at `project-trivia-setup` and stop.                         |

## Example

```
User: what were we working on?
You: [recall("ratatui-clock/trivia-bootstrapped", tags=["project:ratatui-clock"], limit=1) → hit]
     [recall("ratatui-clock/current-focus", …, limit=1)
        → FRONTIER: flicker-free redraw landed (a1b2c3d, 2026-08-20).
          NEXT: add a second pane without reintroducing flicker.]
     [recall("ratatui-clock/conventions", …, limit=1) → edition 2021, MSRV 1.74; themes: rendering, tooling]
     [recall("ratatui-clock/habits/rendering", …, limit=1)
        → 1. Swap the buffer once per frame — worked/single-swap-per-frame …]
     [recall("add a second pane without flicker", …, full_text_search="pane", limit=3, exclude_tags=["archive"])
        → nothing new beyond the hub]
     Last session you landed flicker-free redraw with one buffer swap per frame.
     The rendering hub's first rule is exactly that. NEXT says a second pane —
     still the plan?
User: yes.
You: [git log -S "second_pane" → nothing; confirmed unshipped]
     [rate habits/rendering up]
     [EnterPlanMode]
     Plan: draw the second pane into the same back buffer and keep the single
     end-of-frame swap (per the hub — no per-pane swap), then verify on resize.
```
