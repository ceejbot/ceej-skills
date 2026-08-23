# ceej-skills

A small Claude Code plugin marketplace holding the agentic workflow skills I re-use on my projects, split into five plugins so you install only what you need. I wrote these to help me get things done at work. Judge me all you feel you need to in order to make yourself feel good.

Add the marketplace once:

```
/plugin marketplace add ceejbot/ceej-skills
```

Then install whichever plugins you want:

```
/plugin install enotime@ceej-skills
/plugin install relay@ceej-skills
/plugin install review@ceej-skills
/plugin install trivium@ceej-skills
/plugin install writing@ceej-skills
```

## enotime

An Oblique Strategy at session start, courtesy of the [`oblique`](https://github.com/ceejbot/oblique) CLI, plus an `/oblique-strategy` command. See [its README](./enotime/README.md).

## relay

Relay a session to a fresh agent with a clean context. Trivia is optional here, unlike `trivium`: with it, the pair follows the `project:<slug>` conventions; without it, everything works on plain files. See [its README](./relay/README.md).

- **`handoff`** — Compacts the current session into a self-contained document: task, state, decisions with their whys, artifact links, verification commands. Redacts secrets before saving. The document addresses whatever agent reads it, so Codex, Grok, or a human can pick it up with one pasted line.
- **`pickup`** — Finds the newest handoff (trivia pointer first, then `./tmp/`, then `.claude/relay/`), checks whether the repo has drifted past it, resumes the work, and offers to clean up the document and its pointer together.

## review

General workflow skills for (mostly) Rust projects. No MCP servers required.

- **`review-rust-project`** — Holistic code review pass with a general (architecture, README, simplicity, parse-don't-validate) section and a Rust-specific (types, errors, clippy, clones, idioms) section.
- **`review-rust-change`** — Focused review of a scoped set of changes (uncommitted diff, unpushed commit stack, or GitHub PR). Applies the same quality lens as the full project review but restricted to the diff, plus targeted questions on intent, testing, documentation, and completeness. Produces a small number of ranked, highly actionable suggestions.
- **`review-rust-security`** — Security review: threat modeling, untrusted-input handling, secrets exposure, injection, auth, crypto, panics-as-DoS, supply-chain risk. Rust-shaped but applies to any language. Produces ranked, exploitable-first findings, each with an attacker path, a CWE reference, and the smallest fix.

## trivium

The project-memory workflow. These skills require the [trivia MCP server](https://github.com/chrisdickinson/trivia).

- **`project-trivia-setup`** — Bootstraps the trivia MCP for a project. Establishes the `project:<slug>` tag convention, picks the project's theme list, and seeds the overview / focus / conventions memories.
- **`session-start`** — The reading half of the loop. Opens a session by recalling the project's current focus, the habit hubs that bear on it, and one probe for specific lessons (not the whole project memory); verifies the focus's forward-looking claims against the code; confirms direction with you; then enters plan mode with those lessons in hand.
- **`session-retro`** — The writing half. Captures what worked, what didn't, and what we learned — deduping each lesson against the corpus before saving, aliasing it with the question a future session would ask, and filing it on its theme's habit hub.
- **`memory-gardening`** — Periodic reorganization of a project's memories: archive stale state, merge duplicates by theme, write and refresh the hubs, add aliases and links, and turn process lessons into skill patches. Ships a `stats.py` that reports corpus health from a `trivia export`.
- **`research`** — Cross-source investigation (JIRA, GitHub, Notion, Slack, the web) that stores findings as cited trivia memories, so a later session can pick up where this one stopped.

All four project-memory skills share one memory shape, defined in [`trivium/TAXONOMY.md`](./trivium/TAXONOMY.md): seed memories for state, `habits/<theme>` hubs (ordered checklists), and `worked` / `avoid` / `learned` spokes, each tagged with `project:<slug>`, a kind, a `theme:`, and — when the lesson transfers between projects — a `general:<domain>` tag that other projects recall by. `<slug>` is the project's `Cargo.toml` `[package].name` (or the directory name if there's no manifest yet). Recall filters on one tag at a time, because trivia's tag filter is OR.

## writing

- **`write-clearly`** — A style guide for my preferred English: warm, direct, laconic, occasionally devastating. Applied whenever Claude writes prose on my behalf.
- **`write-code-comments`** — Comments and doc strings that earn their place: document what the code cannot say, explain why rather than what, stay sparse. Doc strings answer the caller's real questions instead of restating the signature. Fires whenever generated code includes comments, not just on request.
- **`write-commit-message`** — Helps draft a commit / PR message worth living in `main` for years. Inverted-pyramid structure, hard-wrap discipline, real-world anti-patterns. Distilled from ceej's "Writing great commit messages" doc.
- **`write-design-doc`** — Problem-statement design doc helper distilled from [my blog post on design docs](https://blog.ceejbot.com/posts/design-docs/). Includes a fillable template.

## ceej-skills

The plugin used to have all its skills under a single grab-bag. Some of the skills are still there with their original names, but I will be retiring them. All one users care. These are the skills I haven't moved yet:

- **`plugin-curation`** — Audits an installed Claude Code setup against real usage signals (`~/.claude.json` `skillUsage` + `favoritePlugins`, plus cc-query for MCP/subagent traffic) and produces keep / consolidate / prune recommendations. Built to re-run periodically.
- **`scala-project-review`** — The Scala counterpart to `review-rust-project`: a general section plus Scala-specific hygiene (idioms, ADTs, effects, implicits/givens, build tooling).

## LICENSE

MIT. Share and enjoy.
