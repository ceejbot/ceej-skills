---
name: project-trivia-setup
description: Use when starting trivia memory in a project for the first time, when the user says "set up trivia" or "bootstrap project memory", or when no project-tagged memories exist yet for this repo
---

# Project Trivia Setup

Bootstrap the trivia MCP for a project so future sessions can recall what it
is, what's being worked on, and what conventions it follows — without
polluting the global trivia DB shared across all projects. The memory shape
every later skill relies on is defined in `../../TAXONOMY.md`, relative to
this `SKILL.md`; this skill seeds it. (Trivia is
[chrisdickinson/trivia](https://github.com/chrisdickinson/trivia) — setup
instructions are Rust-oriented, but it's quite good.)

**Core principle:** every memory belonging to a project carries the tag
`project:<slug>`. Recall by tag, memorize with the tag, and the global DB
stays organized.

## When to use

- New project, first time using trivia for it.
- Existing project where memories were never set up under the tag convention.
- User asks to "set up trivia" / "bootstrap project memory" / "remember this
  project".

**Skip if:** the sentinel memory `<slug>/trivia-bootstrapped` already exists
(recall that exact mnemonic first). List what's already there and stop.

## Steps

### 1. Derive the project slug

In order:

1. Read `Cargo.toml` and use `[package].name` (lowercase, hyphens already
   canonical).
2. If no `Cargo.toml`, use the basename of the working directory, lowercased,
   with non-alphanumerics replaced by hyphens.

The slug becomes the project tag: `project:<slug>`.

### 2. Check for an existing bootstrap

```
recall(query = "<slug>/trivia-bootstrapped", tags = ["project:<slug>"], limit = 1)
```

A hit whose `mnemonic` is exactly `<slug>/trivia-bootstrapped` means
**stop**: surface the existing seeds to the user instead of overwriting them,
and offer to update individual memories rather than re-run bootstrap. Any
other mnemonic is recall's nearest neighbour, not the sentinel — proceed.

### 3. Seed the three memories

Ask the user (or infer from `README.md` / `Cargo.toml` / recent git activity
when obvious) for these facts. Memorize each with tags `["project:<slug>",
"seed"]`:

| Mnemonic               | Content                                                                                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<slug>/overview`      | One paragraph: what this project is and why it exists.                                                                                                  |
| `<slug>/current-focus` | The four-section format: `FRONTIER` / `GROUND TRUTH` / `NEXT` / `FOLLOW-UPS`. Empty sections are fine on day one.                                      |
| `<slug>/conventions`   | Non-obvious rules — build commands, MSRV, lint config, layout — and the project's **theme list** for `theme:` tags, chosen from the taxonomy's starters. |

The theme list is the one decision worth a sentence with the user: it's the
axis every later lesson gets filed on. Three to six themes is typical at the
start; `memory-gardening` extends it as spokes accumulate.

Only memorize facts the user has stated or that are unambiguous from the repo.

### 4. Drop the sentinel

```
memorize(
  mnemonic = "<slug>/trivia-bootstrapped",
  content  = "Trivia bootstrap completed for <slug> on <YYYY-MM-DD>. Project tag: project:<slug>.",
  tags     = ["project:<slug>", "seed"]
)
```

Future sessions detect this in step 2 and skip re-running.

### 5. Document the convention in the agent instructions

Append (or create) a short section in the project's agent instruction file:
`AGENTS.md` for Codex, or `CLAUDE.md` for Claude Code. If the repository
already uses one of these, update that file rather than creating a competing
instruction file.

```markdown
## Project memory

This project uses the trivia MCP. All memories are tagged `project:<slug>`
and follow the trivium taxonomy (seeds, `habits/<theme>` hubs, and
`worked` / `avoid` / `learned` spokes). Themes: <list>. Open sessions with
`session-start`, close them with `session-retro`, and run `memory-gardening`
when lessons stop surfacing.
```

This keeps the convention discoverable even if the trivia tag ever drifts.

### 6. Report back

Tell the user:

- The slug used and where it came from (`Cargo.toml` vs directory).
- Each memory created (mnemonic + one-line summary) and the theme list.
- That subsequent sessions open with `session-start`, which recalls the focus,
  hubs, and one probe — not a tag-wildcard dump.

## Anti-patterns

| Don't                                         | Why                                                                                                                 |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Overwrite an existing bootstrap               | The sentinel exists for a reason — past sessions have refined those memories.                                       |
| Seed speculative memories                     | Every memory should be a fact the user has stated or that's unambiguous from the repo. Speculation pollutes recall. |
| Store secrets, tokens, or private credentials | The trivia DB is global to your machine and easy to export. Treat it like a public README.                          |
| Use a different tag scheme per project        | The `project:<slug>` convention is the whole point. Stick to it.                                                    |
| Skip the theme list                           | Without it, every later spoke lands untagged and the hubs have nothing to hang from.                                |

## Example

```
User: set up trivia for this project
You: [reads Cargo.toml, finds name = "ratatui-clock"]
     Slug: ratatui-clock. Tag: project:ratatui-clock.
     [recall("ratatui-clock/trivia-bootstrapped", tags=["project:ratatui-clock"], limit=1) → no results]
     What's the one-line description of this project, and what are you working
     on right now? For themes I'd start with rendering, tooling, and
     rust-idioms — sound right?
User: It's a small terminal clock built on ratatui to teach myself the
      framework. Right now I'm trying to get smooth redraw without flicker.
      Themes are fine.
You: [memorizes ratatui-clock/overview; ratatui-clock/current-focus with
      FRONTIER "nothing shipped yet", NEXT "smooth redraw without flicker";
      ratatui-clock/conventions with edition 2021, MSRV 1.74, themes]
     [memorizes sentinel ratatui-clock/trivia-bootstrapped]
     [appends "Project memory" to the repo's agent instruction file]
     Done. Four memories seeded under project:ratatui-clock. Open future
     sessions with session-start.
```
