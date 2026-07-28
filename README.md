# ceej-skills

A small Claude Code plugin marketplace holding the workflow skills I re-use on personal projects, split into three plugins so you install only what you need.

Add the marketplace once:

```
/plugin marketplace add ceejbot/ceej-skills
```

Then install whichever plugins you want:

```
/plugin install ceej-skills@ceej-skills
/plugin install trivium@ceej-skills
/plugin install enotime@ceej-skills
```

## ceej-skills

General workflow skills for (mostly) Rust projects. No MCP servers required.

- **`rust-project-review`** — Holistic code review pass with a general (architecture, README, simplicity, parse-don't-validate) section and a Rust-specific (types, errors, clippy, clones, idioms) section.
- **`rust-change-review`** — Focused review of a scoped set of changes (uncommitted diff, unpushed commit stack, or GitHub PR). Applies the same quality lens as the full project review but restricted to the diff, plus targeted questions on intent, testing, documentation, and completeness. Produces a small number of ranked, highly actionable suggestions.
- **`rust-security-review`** — Security review: threat modeling, untrusted-input handling, secrets exposure, injection, auth, crypto, panics-as-DoS, supply-chain risk. Rust-shaped but applies to any language. Produces ranked, exploitable-first findings, each with an attacker path, a CWE reference, and the smallest fix.
- **`scala-project-review`** — The Scala counterpart to `rust-project-review`: a general section plus Scala-specific hygiene (idioms, ADTs, effects, implicits/givens, build tooling).
- **`writing-design-docs`** — Problem-statement design doc helper distilled from [my blog post on design docs](https://blog.ceejbot.com/posts/design-docs/). Includes a fillable template.
- **`writing-commit-messages`** — Helps draft a commit / PR message worth living in `main` for years. Inverted-pyramid structure, hard-wrap discipline, real-world anti-patterns. Distilled from ceej's "Writing great commit messages" doc.
- **`writing-clearly`** — A style guide for my preferred English: warm, direct, laconic, occasionally devastating. Applied whenever Claude writes prose on my behalf.
- **`plugin-curation`** — Audits an installed Claude Code setup against real usage signals (`~/.claude.json` `skillUsage` + `favoritePlugins`, plus cc-query for MCP/subagent traffic) and produces keep / consolidate / prune recommendations. Built to re-run periodically.

## trivium

The project-memory workflow. These skills require the [trivia MCP server](https://github.com/chrisdickinson/trivia).

- **`project-trivia-setup`** — Bootstraps the trivia MCP for a project. Establishes the `project:<slug>` tag convention and seeds initial overview / focus / conventions memories.
- **`session-start`** — The companion to `session-retro` and the other half of the loop. Opens a session by recalling the project's current focus and the few most relevant lessons from trivia (not the whole project memory), confirms the direction with you, then enters plan mode to design the work with those lessons in hand.
- **`session-retro`** — End-of-session reflection. Recalls prior retros, captures what worked and what didn't, and stores each lesson in trivia under the project tag.
- **`research`** — Cross-source investigation (JIRA, GitHub, Notion, Slack, the web) that stores findings as cited trivia memories, so a later session can pick up where this one stopped.

All trivia memories these skills create carry the tag `project:<slug>`, where `<slug>` is the project's `Cargo.toml` `[package].name` (or the directory name if there's no manifest yet). This keeps the global trivia DB safely shared across projects — recall by tag, never by accident.

## enotime

An Oblique Strategy at session start, courtesy of the [`oblique`](https://github.com/ceejbot/oblique) CLI, plus an `/oblique-strategy` command. See [its README](./enotime/README.md).

## Layout

The root `.claude-plugin/` holds only `marketplace.json`; each plugin lives in its own subdirectory with its own manifest.

```
.claude-plugin/marketplace.json
ceej-skills/
  .claude-plugin/plugin.json
  skills/
    <one directory per skill, each with a SKILL.md>
trivium/
  .claude-plugin/plugin.json
  skills/
    <one directory per skill, each with a SKILL.md>
enotime/
  .claude-plugin/plugin.json
  commands/
  hooks/
```

## Status

v0. The skills improve as real usage reveals failure modes — see `superpowers:writing-skills` for the TDD-style refinement loop.
