# ceej-skills

A small Claude Code plugin holding the workflow skills I re-use on Rust personal projects.

## Skills

- **`project-trivia-setup`** — Bootstraps the trivia MCP for a project. Establishes the `project:<slug>` tag convention and seeds initial overview / focus / conventions memories.
- **`session-retro`** — End-of-session reflection. Recalls prior retros, captures what worked and what didn't, and stores each lesson in trivia under the project tag.
- **`rust-project-review`** — Holistic code review pass with a general (architecture, README, simplicity, parse-don't-validate) section and a Rust-specific (types, errors, clippy, clones, idioms) section.
- **`rust-change-review`** — Focused review of a scoped set of changes (uncommitted diff, unpushed commit stack, or GitHub PR). Applies the same quality lens as the full project review but restricted to the diff, plus targeted questions on intent, testing, documentation, and completeness. Produces a small number of ranked, highly actionable suggestions.
- **`writing-design-docs`** — Problem-statement design doc helper distilled from [my blog post on design docs](https://blog.ceejbot.com/posts/design-docs/). Includes a fillable template.
- **`writing-commit-messages`** — Helps draft a commit / PR message worth living in `main` for years. Inverted-pyramid structure, hard-wrap discipline, real-world anti-patterns. Distilled from ceej's "Writing great commit messages" doc.

## Install

From this repository:

```
/plugin install /Users/ceej/code/personal/rust/ceej-skills
```

Or, if published to a marketplace:

```
/plugin install ceej-skills
```

## Layout

```
.claude-plugin/plugin.json
skills/
  project-trivia-setup/SKILL.md
  session-retro/SKILL.md
  rust-project-review/SKILL.md
  rust-change-review/SKILL.md
  writing-design-docs/
    SKILL.md
    template.md
  writing-commit-messages/SKILL.md
```

## Conventions

All trivia memories created by these skills carry the tag `project:<slug>` where `<slug>` is the project's `Cargo.toml` `[package].name` (or the directory name if there's no manifest yet). This keeps the global trivia DB safely shared across projects — recall by tag, never by accident.

## Status

v0. The skills will improve as real usage reveals failure modes — see `superpowers:writing-skills` for the TDD-style refinement loop.
