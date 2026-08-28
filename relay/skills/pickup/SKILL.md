---
name: pickup
description: Use only when the user explicitly asks to resume a handoff. Read the document written by an earlier session and continue the work it describes.
disable-model-invocation: true
---

# Pickup

Find the handoff document a previous session left behind, verify the world
still matches it, and resume the work. The other half of the `handoff` skill.

**Core principle:** the document describes the world as it was when written.
Verify before trusting — check the file exists, check the repo hasn't moved
past it, run its verification commands — and report drift to the user instead
of silently acting on stale instructions.

## When to use

- The user explicitly invokes the pickup skill or asks to resume a handoff at
  the start of a session that continues earlier work.

## Steps

### 1. Locate the handoff

Derive the project slug the way trivium does: `Cargo.toml` `[package].name`,
else the lowercased working-directory basename with non-alphanumerics replaced
by hyphens. Then check, in order:

1. **Trivia pointer.** If trivia MCP tools are available:
   `recall("<slug>/handoff", limit = 1)`. If the memory exists and the file it
   names exists, use that file. If the memory exists but the file is gone,
   tell the user the pointer is stale and fall through to the file search.
2. **`./tmp/`** — the newest file matching `handoff-*.md`. Match the pattern;
   tmp holds plenty that isn't a handoff.
3. **`.claude/relay/`** — the newest file matching `handoff-*.md`.

If several candidates exist, take the newest and name the others so the user
can redirect you. If nothing turns up anywhere, say so plainly and stop —
summarize nothing, since there is nothing to summarize.

### 2. Check for drift

The document records when it was written and the commit it was written at.
Compare against the present:

```
git log --oneline <handoff-sha>..HEAD
```

Commits since the handoff — especially ones touching the files it discusses —
mean parts of the doc may already be done or invalidated. Flag exactly which
sections look overtaken before acting on them. A handoff from a different
branch than the current one deserves the same flag.

### 3. Read, verify, resume

- Summarize the task and state back to the user in a few sentences — this is
  their confirmation that you picked up the right baton.
- Run the document's "Verify state" commands and report any mismatch.
- Follow its "For skill-aware agents" section if present: invoke
  `session-start` when the doc calls for it (it layers the project's recalled
  focus and lessons on top of the handoff's fine-grained state), and recall
  any trivia memories it names. Older handoffs may call this section "For
  Claude Code readers"; treat it the same way when the named skills exist.
- Then continue from the document's "Next steps."

### 4. Offer cleanup — both halves together

Once the handoff is absorbed, offer to remove it: delete the file **and**, in
trivia mode, update the `<slug>/handoff` memory in the same breath — either
delete it or edit it to say the handoff was consumed on `<date>`. File and
pointer move together so they never disagree; a pointer to a deleted file is
this skill's main failure mode. If the user declines, leave both in place.

## Anti-patterns

| Don't                                             | Why                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Grab the newest file in tmp regardless of name    | tmp holds build junk and scratch files. Only `handoff-*.md` is a handoff.                       |
| Trust the trivia pointer without checking the file | The file may have been cleaned up by hand. Stale pointer → say so, fall through to the search. |
| Act on the doc without the drift check            | The repo may have moved past it; you'd redo finished work or resurrect abandoned plans.         |
| Delete the file but keep the memory (or vice versa) | A pointer and its file must agree. Clean up both together or neither.                        |
| Invent context when no handoff exists             | Nothing found means nothing to summarize. Report it and let the user steer.                     |
| Skip the read-back summary                        | The user needs to confirm you grabbed the right handoff before you act on it.                   |

## Example

```
User: resume from the handoff
You: [slug: fetch-queue; recall("fetch-queue/handoff") → tmp/handoff-2026-08-13-1642.md; file exists]
     [git log 4f3a2c1..HEAD → one commit since, touching src/retry.rs]
     Found yesterday's handoff (tmp/handoff-2026-08-13-1642.md): retry logic
     half-done — backoff working, jitter untested. One commit has landed since,
     touching src/retry.rs, so the "in progress" section may be partly done.
     [runs `just test` per the doc's Verify state section → passes]
     The doc suggests session-start; invoking it to load the project focus and lessons.
     [session-start recalls current-focus "finish retry jitter + tests" — matches the handoff]
     Next step per the handoff: property-test the jitter distribution. Starting there.
     [... work happens ...]
     Done with what the handoff described. Delete tmp/handoff-2026-08-13-1642.md
     and mark the fetch-queue/handoff memory consumed?
User: yes
You: [deletes the file; edits the memory to "Handoff consumed 2026-08-14; no live handoff."]
```
