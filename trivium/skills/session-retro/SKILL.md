---
name: session-retro
description: Use at the end of a working session, before final commit, when the user says "let's wrap up" / "let's retro" / "any lessons from this session", or after a meaningful unit of work just landed
---

# Session Retro

Turn a session's lessons into trivia memories the next session can actually
find. This is half of a loop: retro writes, `session-start` reads. A lesson
nobody recalls is a lesson not learned, so this skill spends as much care on
*findability* — dedupe, aliases, hubs — as on the lesson itself. The memory
shape is defined once in `../../TAXONOMY.md`, relative to this `SKILL.md`;
read it at the top of every retro. (Trivia is
[chrisdickinson/trivia](https://github.com/chrisdickinson/trivia) — setup
instructions are Rust-oriented, but it's quite good.)

**Core principle:** specific lessons or none. "Be more careful" is not a
lesson. "Don't reach for `Box<dyn Error>` in library APIs because we hit `?`
ergonomic problems three times" is.

## When to use

- End of a session.
- Before a final commit on a meaningful chunk of work.
- After a feature lands, a bug is fixed, or an investigation concludes.
- User asks for a retro explicitly.

**Skip if:** the session was trivial (one-line fix, doc tweak) or was pure
exploration with no conclusion.

## Steps

### 1. Recall the hubs for the themes this session touched

Name the one to three themes the session worked in (from the project's list in
`<slug>/conventions`). For each:

```
recall(query = "<slug>/habits/<theme>", tags = ["project:<slug>"], limit = 1)
```

One tag per call — a second tag widens the filter to other projects. A result
is the hub only when its `mnemonic` equals the queried string exactly; recall
always returns *something*, and a near miss is another memory, not the hub.
Skim each real hub. If it guided the session, `rate` it up; if it was noise,
down. Note any theme with no hub yet; step 5 creates it.

### 2. Summarize the session in 3–6 bullets

Plain prose, not a diff. What got done, what stalled, what surprised us. This
is for the user to confirm before lessons cement; it is not memorized.

### 3. Draft candidates in three columns

Walk the session and draft each candidate with four labels — **kind**,
**theme**, **generality** (project-only, or `general:<domain>`), and the body
in the taxonomy's format:

- **Worked** — an approach, tool, or framing that produced results faster or
  cleaner than expected. `Situation | What we did | Why it worked`.
- **Avoid** — a dead end, a tool that fought us, advice that was wrong.
  `Situation | What we tried | Why it failed | What to try instead`.
- **Learned** — a durable fact about the domain, a tool, an API, or the
  codebase. Not process (that's worked/avoid), not state (that's
  `current-focus`). `Fact | Where it came from | Why it matters`.

`Why` is non-negotiable in all three. A long subagent-driven session may
legitimately produce three to five candidates; a short one, zero to two. The
bar is per lesson, not per session: every candidate must pass step 4.

### 4. Dedupe every candidate

The corpus probably already holds a version of this lesson. For each
candidate:

```
recall(query = "<the lesson's gist in plain words>", tags = ["project:<slug>"],
       full_text_search = "<one distinctive term from the body>",
       limit = 3, truncate = 400, exclude_tags = ["archive"])
```

Three verdicts:

- **Covered** — an existing spoke says this. *Reinforce* it: `memorize` the
  same mnemonic with the same tags and a sharper body that folds in today's
  instance; `rate` it up. No new memory. **The body you pass REPLACES the old
  one entirely** — fold means recall the full existing body and rewrite it
  whole; an "ADDENDUM"-only save silently deletes everything else.
- **Related but distinct** — a new spoke, plus `link(new, existing,
  "related")` in step 5.
- **Nothing** — a new spoke.

Done when every candidate has a verdict. A candidate that duplicates an
existing spoke and gets saved anyway is the single most common way this corpus
degrades.

### 5. Save each new spoke — five moves

1. **Memorize** with the full tag set: `["project:<slug>", "<kind>",
   "theme:<theme>"]`, plus `"general:<domain>"` if it transfers. Read the
   response: if it reports an auto-merge into an existing memory, your
   mnemonic does not exist — switch to the *Covered* path and reinforce the
   memory it merged into instead.
2. **Alias** it: `edit(mnemonic, add_mnemonics = [...])` with one or two
   natural-phrasing questions a future session would ask. The slug alone
   embeds poorly; the alias is what recall matches.
3. **Hub line**: the hub from step 1 (exact mnemonic match, or none). Insert
   a one-line rule naming the spoke at its priority position and `memorize`
   `<slug>/habits/<theme>` with the new body and tags `["project:<slug>",
   "habits", "theme:<theme>"]`. No hub yet means this line is the first. If
   the hub would reach thirteen lines, say so to the user —
   `memory-gardening` splits it; the retro doesn't squeeze.
4. **Link** `link(spoke, hub, "related")`, plus `link(spoke, existing,
   "related")` for each memory step 4 judged related but distinct. A general
   spoke also links to its domain hub — `general/habits/agent-process`,
   `general/habits/rust-toolchain`, and so on per the taxonomy — created if
   missing.
5. **Bug report**: a spoke with `theme:memory` and kind `avoid` is a defect in
   these skills. Memorize it, then tell the user which skill step failed so
   the skill gets patched. A process lesson that lives only in project memory
   never flows back.

Done when each saved spoke has an alias, a theme tag, a hub line, a hub
link, and a link to every related memory from step 4.

### 6. Update `current-focus`

If the session moved the frontier, first recall `<slug>/current-focus` by
exact mnemonic (a retro without a preceding `session-start` has no copy in
context), then rewrite it in the four-section format: `memorize` the same
mnemonic with tags `["project:<slug>", "seed"]`. `edit` cannot change a body.
Every FOLLOW-UPS line carries forward; the ones that shipped get a tombstone
— `shipped <hash>` — and stay on the list. Retros hold durable lessons; state
lives here.

### 7. Confirm with the user

Show a table: mnemonic · reinforced or new · aliases · hub line. Ask if any
should be edited or dropped before they cement. For a smooth-sailing session,
report the maintenance done instead.

## Smooth sailing is a valid outcome

Some sessions produce zero new memories — everything went the way prior
lessons said it would. That's a *successful* retro. Its work is maintenance of
the memories that got you there:

- `rate` up the hubs and spokes that guided the session, down the noise.
- `edit` to add an alias to a memory that was hard to find this time.
- `link` memories the session revealed are related.

Don't invent a lesson to have something to save.

## Anti-patterns

| Don't                                                  | Why                                                                                       |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| Memorize the diff or session transcript                | Git has it. Trivia holds the *meaning* you extracted.                                     |
| Memorize "currently debugging X" as a retro            | State, not a lesson. It belongs in `current-focus`.                                       |
| Save a lesson without running step 4                   | Four memories saying "nightly fmt got skipped" is how a corpus drowns its own lessons.    |
| Save a spoke with no alias                             | The slug loses to older, vaguer memories; the lesson is unfindable by the session it's for.|
| Pass two tags to `recall`                              | OR semantics: the second tag pulls in every other project carrying it.                   |
| `edit` to update content                               | `edit` only touches mnemonics, aliases, and tags. Re-`memorize` the same mnemonic.        |
| Write a lesson whose content is "be more careful"      | Too vague to match a future situation. Be specific or skip.                               |
| Skip the `Why` field                                   | Without the reason, the lesson can't generalize.                                          |

## Example

```
User: let's wrap up
You: [recall("ratatui-clock/habits/rendering", tags=["project:ratatui-clock"], limit=1)
        → hub with 3 lines; the frame-timing line guided today. Rated up.]
     Today: smooth redraw is working. The fix was a single buffer.swap_buffers()
     at the end of each frame, not the per-widget approach we tried first.
     Candidates:
       Worked · theme:rendering · project-only
         ratatui-clock/worked/single-swap-per-frame
         Situation: flicker on full-screen redraws. | What we did: one swap at
         end of frame, draw to back buffer only. | Why it worked: ratatui diffs
         per frame; per-widget swaps fight it.
       Avoid · theme:rendering · project-only
         ratatui-clock/avoid/per-widget-redraw
         … | What to try instead: trust the framework's diff, swap once per tick.
     [dedupe: recall("flicker from swapping buffers", tags=[project], full_text_search="swap")
        → nothing covers it; the frame-timing memory is related]
     Saving both with aliases ("why does ratatui flicker on redraw?",
     "how many buffer swaps per frame?"), a new line at the top of
     habits/rendering, and links to the hub and to frame-timing. OK?
User: yes
You: [memorize ×2, edit add_mnemonics ×2, memorize hub, link ×3, memorize current-focus]
```

A smooth-sailing session reads: "Today went the way the saved lessons
predicted — nothing new. I rated habits/rendering up and added the alias 'why
does the clock flicker?' to single-swap-per-frame, which took two tries to
find."
