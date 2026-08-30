# ceej-skills

A small Codex and Claude Code plugin marketplace holding the agentic workflow
skills I re-use on my projects, split into focused plugins so you install only
what you need. I wrote these to help me get things done at work. Judge me all
you feel you need to in order to make yourself feel good.

For Codex, add the marketplace once:

```
codex plugin marketplace add ceejbot/ceej-skills
```

Then install whichever skill plugins you want:

```
codex plugin add design@ceej-skills
codex plugin add enotime@ceej-skills
codex plugin add relay@ceej-skills
codex plugin add review@ceej-skills
codex plugin add trivium@ceej-skills
codex plugin add writing@ceej-skills
```

For Claude Code, add the marketplace once:

```
/plugin marketplace add ceejbot/ceej-skills
```

Then install whichever plugins you want:

```
/plugin install design@ceej-skills
/plugin install enotime@ceej-skills
/plugin install relay@ceej-skills
/plugin install review@ceej-skills
/plugin install trivium@ceej-skills
/plugin install writing@ceej-skills
```

## design

Design-phase skills, adapted from [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT) and reframed from interrogation to mutual exploration. Trivia is optional: with it, a dive's settled decisions can be memorized; without it, the glossary and ADRs are the record.

- **`deep-dive`** — Explore a plan, decision, or idea together until nothing is silently assumed. Maps the territory as a design tree and asks whole rounds of frontier questions at a time, each with a recommended answer; the agent's own assumptions go on the frontier too. Facts are the agent's job, decisions are made together. Hands off to `domain-modeling` for capture and to `write-design-doc` when the direction deserves a full document.
- **`domain-modeling`** — Actively build and sharpen the project's domain model: challenge terms against the `CONTEXT.md` glossary, sharpen fuzzy language, stress-test relationships with edge-case scenarios, and record qualifying decisions as [MADR-minimal](https://github.com/adr/madr) ADRs in `docs/adr/`. ADRs are offered only when a decision is hard to reverse, surprising without context, and a real trade-off.
- **`prototype`** — Throwaway code that answers a design question. Two branches: a logic prototype is a single shareable HTML file anyone can drive by clicking buttons; a UI prototype renders radically different variants on one route, switchable from a floating bar. Deep-dive reaches for it when a frontier question can only be answered in running code.

## ENOTIME

**ENOTIME** draws an Oblique Strategy on demand via the
[`oblique`](https://github.com/ceejbot/oblique) CLI. Invoke
`$enotime:oblique-strategy` in Codex or `/oblique-strategy` in Claude Code;
Claude Code also draws one automatically at session start. See
[its README](./enotime/README.md).

## relay

Relay a session to a fresh agent with a clean context. Trivia is optional here, unlike `trivium`: with it, the pair follows the `project:<slug>` conventions; without it, everything works on plain files. See [its README](./relay/README.md).

- **`handoff`** — Compacts the current session into a self-contained document: task, state, decisions with their whys, artifact links, verification commands. Redacts secrets before saving. The document addresses whatever agent reads it, so Codex, Grok, or a human can pick it up with one pasted line.
- **`pickup`** — Finds the newest handoff (trivia pointer first, then `./tmp/`, then `.claude/relay/`), checks whether the repo has drifted past it, resumes the work, and offers to clean up the document and its pointer together.

## review

General workflow skills for (mostly) Rust projects. No MCP servers required.

- **`review-rust-project`** — Holistic code review pass with a general (architecture, README, simplicity, parse-don't-validate) section and a Rust-specific (types, errors, clippy, clones, idioms) section.
- **`review-rust-change`** — Focused review of a scoped set of changes (uncommitted diff, unpushed commit stack, or GitHub PR). Applies the same quality lens as the full project review but restricted to the diff, plus targeted questions on intent, testing, documentation, and completeness. Produces a small number of ranked, highly actionable suggestions.
- **`review-application-security`** — Language-neutral application and service security: threat modeling, injection, authorization, secrets and PHI, cryptography, abuse resistance, and dependency exposure. Produces ranked, exploitable-first findings with attacker paths and the smallest fixes.
- **`review-rust-security`** — The Rust-specific overlay: unsafe and FFI invariants, attacker-reachable panics or allocation, deserialization limits, concurrency, cryptographic APIs, and Cargo supply-chain exposure. A comprehensive Rust service review combines it with `review-application-security` into one report.

## trivium

The project-memory workflow. These skills require the [trivia MCP server](https://github.com/chrisdickinson/trivia).

- **`project-trivia-setup`** — Bootstraps the trivia MCP for a project. Establishes the `project:<slug>` tag convention, picks the project's theme list, and seeds the overview / focus / conventions memories.
- **`session-start`** — The reading half of the loop. Opens a session by recalling the project's current focus, the habit hubs that bear on it, and one probe for specific lessons (not the whole project memory); verifies the focus's forward-looking claims against the code; confirms direction with you; then enters plan mode with those lessons in hand.
- **`session-retro`** — The writing half. Captures what worked, what didn't, and what we learned — deduping each lesson against the corpus before saving, aliasing it with the question a future session would ask, and filing it on its theme's habit hub.
- **`memory-gardening`** — Periodic reorganization of a project's memories: archive stale state, merge duplicates by theme, write and refresh the hubs, add aliases and links, and turn process lessons into skill patches. Ships a `stats.py` that reports corpus health from a `trivia export`.
- **`research`** — Cross-source investigation (JIRA, GitHub, Notion, Slack, the web) that stores findings as cited trivia memories, so a later session can pick up where this one stopped.

All four project-memory skills share one memory shape, defined in [`trivium/TAXONOMY.md`](./trivium/TAXONOMY.md): seed memories for state, `habits/<theme>` hubs (ordered checklists), and `worked` / `avoid` / `learned` spokes, each tagged with `project:<slug>`, a kind, a `theme:`, and — when the lesson transfers between projects — a `general:<domain>` tag that other projects recall by. `<slug>` is the project's `Cargo.toml` `[package].name` (or the directory name if there's no manifest yet). Recall filters on one tag at a time, because trivia's tag filter is OR.

## writing

- **`write-clearly`** — A style guide for my preferred English: warm, direct, laconic, occasionally devastating. Applied whenever the agent writes prose on my behalf.
- **`write-code-comments`** — Comments and doc strings that earn their place: document what the code cannot say, explain why rather than what, stay sparse. Doc strings answer the caller's real questions instead of restating the signature. Fires whenever generated code includes comments, not just on request.
- **`write-commit-message`** — Helps draft a commit / PR message worth living in `main` for years. Inverted-pyramid structure, hard-wrap discipline, real-world anti-patterns. Distilled from ceej's "Writing great commit messages" doc.
- **`write-for-agents`** — Reference for writing any document an agent consumes: skills, `AGENTS.md` / `CLAUDE.md`, docs reached by pointers. Context pointers, the two loads, information hierarchy, completion criteria, leading words, pruning. Carries the house `LEXICON.md`: canonical engineering vocabulary with `Avoid` lists, because agent documents have a human reader too. Adapted from [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT).
- **`wait-what`** — "Stop. That last message did not land: re-pitch it." User-invoked conversational repair, in Simplified Technical English and the project's ubiquitous language.
- **`write-design-doc`** — Problem-statement design doc helper distilled from [my blog post on design docs](https://blog.ceejbot.com/posts/design-docs/). Includes a fillable template.

## LICENSE

MIT. Share and enjoy.
