---
name: handoff
description: Use only when the user explicitly asks for a handoff by name — "run handoff", "write a handoff", "/relay:handoff". Never invoke on your own judgment. Compacts the current conversation into a document a fresh agent can pick up.
argument-hint: "What will the next session be used for?"
---

# Handoff

Write a handoff document summarizing the current session so a fresh agent can
continue the work. The companion `pickup` skill reads it back — but the next
reader might just as easily be Codex, Grok, or a human, so the document carries
everything itself.

**Core principle:** the document must stand alone. The next reader has no
access to this conversation, this skill, or the trivia DB — and may not be
Claude at all. Reference artifacts by path or URL; the document's own words are
reserved for what no artifact records: state, decisions, and the *why* behind
them.

## When to use

- The user explicitly invokes the handoff skill or asks for a handoff, usually
  because context is filling up or the session is ending mid-task.
- Before deliberately restarting with a clean context.

If the user passed arguments, treat them as a description of what the next
session will focus on, and tailor the document to that focus.

## Steps

### 1. Detect the trivia path

Derive the project slug the way trivium does: `Cargo.toml` `[package].name`;
if there's no manifest, the working-directory basename, lowercased, with
non-alphanumerics replaced by hyphens.

If trivia MCP tools are available, check for the bootstrap sentinel:

```
recall("<slug>/trivia-bootstrapped", limit = 1)
```

A hit means **trivia mode**: steps 2, 6, and 7 apply. A miss — or no trivia
tools at all — means **plain mode**: skip those steps and rely on the file
alone. Bootstrapping trivia is `project-trivia-setup`'s job; if the user wants
memory for this project, point there rather than seeding anything here.

### 2. Offer a retro first *(trivia mode)*

Handoff captures *state*; `session-retro` captures *lessons*. If durable
lessons surfaced this session — a dead end worth avoiding, an approach that
paid off — suggest running `session-retro` before the handoff so those land in
trivia where every future session can recall them, not just the next one.
Proceed with the handoff either way.

### 3. Choose the destination

- If `./tmp/` exists, write there.
- Otherwise create `.claude/relay/` and write there.

Filename: `handoff-<yyyy-mm-dd>-<hhmm>.md`. The timestamp makes every filename
unique and makes "newest" unambiguous for pickup.

### 4. Write the document

Use this template. Fill every section; write "none" rather than omitting a
heading, so the reader knows the section was considered rather than forgotten.

```markdown
# Handoff: <one-line description of the work>

You are picking up work from a previous session. Read this whole file, run the
verification commands below to confirm the state still holds, then continue
from "Next steps."

Written: <yyyy-mm-dd hh:mm> | Branch: <branch> | Last commit: <sha> <subject>

## Task

<What the work is and why — a paragraph a stranger could act on.>

## State

- **Done:** <completed items, with the evidence: commit, passing test, merged PR>
- **In progress:** <what's half-finished and exactly where it stands>
- **Next steps:** <ordered; the first item is what to do immediately>

## Key decisions

<Each decision with its why. The why is the part a fresh context cannot
reconstruct — "chose X over Y because Z" — including approaches tried and
rejected, so the next agent doesn't re-walk dead ends.>

## Artifacts

<Paths and URLs only: specs, plans, ADRs, issues, PRs, design docs. One line
each saying what the artifact is. Content lives in the artifact, not here.>

## Verify state

<Commands to confirm the environment matches this document: build, test,
`git status`. Prefer the project's just recipes if a `.justfile` exists.>

## Watch out for

<Gotchas, flaky tests, environment quirks, anything that burned this session.>

## For skill-aware agents

<Optional section. Suggested skills to invoke, starting with `session-start`
if this project is trivia-bootstrapped, and any trivia memories worth
recalling, named by mnemonic. Use the invocation syntax of the current host.>
```

Verify every path you write into the document exists (`ls` / `fd`) — a handoff
pointing at files that were never committed sends the next agent hunting.

### 5. Redact

Re-read the draft before saving and strip anything sensitive:

- API keys, tokens, passwords, connection strings
- PII and PHI — patient or member data of any kind
- Internal hostnames or credentials quoted from earlier tool output

Replace each with a placeholder naming where the real value lives
(`$DATABASE_URL from 1Password`, `see k8s secret foo/bar`).

### 6. Write the pointer memory *(trivia mode)*

```
memorize(
  mnemonic = "<slug>/handoff",
  content  = "Handoff at <path> — <one-line summary of the state> (<yyyy-mm-dd>)",
  tags     = ["project:<slug>", "handoff"]
)
```

Repeated handoffs converge on this one pointer: trivia auto-merges mnemonics
this close, so the memory always names the latest document.

### 7. Offer to update `current-focus` *(trivia mode)*

If the session changed what the project is working toward, offer to `edit` the
`<slug>/current-focus` memory — the same maintenance `session-retro` does. The
handoff document holds the fine-grained state; `current-focus` holds the
headline.

### 8. Report

Tell the user the path, then give them the relay line to paste into whatever
agent picks this up:

```
Read <path> and continue the work it describes.
```

That single line is the whole cross-agent story: skill-aware users can invoke
`$relay:pickup` in Codex or `/pickup` in Claude Code, but any agent that can
read a file can take the baton.

## Anti-patterns

| Don't                                            | Why                                                                                                  |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Paste diff, spec, or plan content into the doc   | The artifact is the source of truth; a copy goes stale the moment the artifact changes. Link it.    |
| Write a path without checking it exists          | An uncommitted or imagined path sends the next agent hunting for a file that isn't there.           |
| Address the reader as a particular agent                 | The next reader may be Codex, Claude, Grok, or a human. Host-specific advice belongs in the skill-aware section. |
| Skip the redaction pass                          | The doc outlives the session and may be pasted into other tools. Treat it like a public README.      |
| Bury next steps under narrative                  | The first thing the next agent needs is what to do; the story of how we got here comes second.      |
| Seed trivia memories beyond the pointer          | Lessons belong to `session-retro`; bootstrap belongs to `project-trivia-setup`. Handoff writes one pointer. |

## Example

```
User: create a handoff; I'm picking this up tomorrow to finish the retry logic
You: [slug from Cargo.toml: fetch-queue; recall("fetch-queue/trivia-bootstrapped") → hit: trivia mode]
     [one durable lesson emerged (tokio::select! ordering bug) — suggests session-retro first; user declines]
     [./tmp exists → writes tmp/handoff-2026-08-13-1642.md from the template,
      verifies the two artifact paths, redacts a staging DB URL to "$STAGING_DB from 1Password"]
     [memorize("fetch-queue/handoff", "Handoff at tmp/handoff-2026-08-13-1642.md — retry logic half-done,
      backoff works, jitter untested (2026-08-13)", tags=["project:fetch-queue", "handoff"])]
     [offers to update fetch-queue/current-focus → user accepts, edits it to "finish retry jitter + tests"]
     Handoff written to tmp/handoff-2026-08-13-1642.md. To resume, invoke the
     pickup skill — or paste this into any agent: "Read tmp/handoff-2026-08-13-1642.md and
     continue the work it describes."
```
