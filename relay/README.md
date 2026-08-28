# relay

Tinker to Evers to Chance.

Relay a session to a fresh agent with a clean context: `handoff` compacts the
current conversation into a document, and `pickup` reads it back in the next
session. In Codex, invoke them as `$relay:handoff` and `$relay:pickup`; in
Claude Code, use `/handoff` and `/pickup`. My trivia-aware take on a very
common skill pair.

## The two skills

- **`handoff`** — writes a self-contained handoff document: task, state, key
  decisions with their whys, artifact links, verification commands, gotchas.
  Redacts secrets and PHI before saving. Ends by printing the one line to
  paste into the next agent.
- **`pickup`** — finds the newest handoff, checks whether the repo has moved
  past it since it was written, verifies state, resumes the work, and then
  offers to clean up the document and its pointer together.

## Two modes

If the [trivia MCP](https://github.com/chrisdickinson/trivia) is available
*and* the project is bootstrapped per the trivium plugin's conventions
(sentinel memory `<slug>/trivia-bootstrapped`), the pair goes trivia-aware:
handoff stores a pointer memory (`<slug>/handoff`, tagged `project:<slug>`),
offers to update the project's `current-focus`, and suggests a `session-retro`
first if the session produced durable lessons; pickup follows the pointer and
layers `session-start`'s recalled focus on top of the handoff's state.

Without trivia, everything works on plain files. Handoff documents land in
`./tmp/` if the project has one, otherwise in `.claude/relay/`, named
`handoff-<date>-<time>.md`.

## Other agents

The handoff document stands alone — it opens by addressing whatever agent
reads it, and keeps skill-aware suggestions in a clearly labeled section. To
relay to Codex, Claude, Grok, or anything else that can read a file, paste the
line handoff prints:

```
Read tmp/handoff-2026-08-13-1642.md and continue the work it describes.
```

Coming back to a skill-aware agent, invoke `pickup` with that host's syntax. It
also understands handoffs other tools leave behind, as long as they land in
the same place with the same naming.
