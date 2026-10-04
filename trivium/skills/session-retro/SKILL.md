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

- **Covered** — an existing spoke says this. *Reinforce* it using
  [Editing an existing memory](../../EDITING.md): export, patch, and import
  long bodies; reserve `memorize` for short spokes whose complete body is
  visible and easy to review. Integrate today's instance, verify the saved
  body and tags, and `rate` it up. No new memory.
  A **hot** spoke (taxonomy, *Weight: hot and cold*) takes the instance
  as ONE line; its evidence goes in the spoke's cold log.
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
3. **Hub placement**: the hub from step 1 (exact mnemonic match, or none —
   no hub yet means this spoke's rule is the first line). The hub is a
   working set; place the spoke by the first test it passes:
   - *Instance of an existing line's rule* → append the spoke's mnemonic
     to that line's citations. A line carries up to four; at four, the
     oldest citation rotates out — the rule already covers it.
   - *A genuinely new rule, hub under twelve lines* → insert a line at
     its priority position.
   - *A genuinely new rule, hub at the cap* → admission is by
     displacement: it enters only if it is more costly to forget than the
     current line 12. Make room by clustering sibling lines that state
     one rule; twelve lines stays the cap.
   - *None of these* → the spoke ships **lineless by design**: its
     aliases and the session-start probes carry it. A normal outcome, not
     a deferral.

   When an existing hub line changes, follow
   [Editing an existing memory](../../EDITING.md) to export, patch, and
   import `<slug>/habits/<theme>`, then verify the body and tags. For a new
   hub, use `memorize` with tags `["project:<slug>", "habits",
   "theme:<theme>"]` and verify it with step 1's recall.
   Eviction is a gardening move, not a retro move — only the export's
   counters can say which lines are cold without the check itself bumping
   them — so a full hub where nothing clusters is the one case to flag
   for `memory-gardening`.
4. **Link** `link(spoke, hub, "related")`, plus `link(spoke, existing,
   "related")` for each memory step 4 judged related but distinct. A general
   spoke also links to its domain hub — `general/habits/agent-process`,
   `general/habits/rust-toolchain`, and so on per the taxonomy — created if
   missing.
5. **Bug report**: a spoke with `theme:memory` and kind `avoid` is a defect in
   these skills. Memorize it, then tell the user which skill step failed so
   the skill gets patched. A process lesson that lives only in project memory
   never flows back.

Done when each saved spoke has an alias, a theme tag, a hub link, a link to
every related memory from step 4, and a hub placement — cited on a line, or
lineless by design.

### 6. Update `current-focus`

If the session moved the frontier, update `<slug>/current-focus` using
[Editing an existing memory](../../EDITING.md): start from a fresh export,
patch its file in the four-section format, review the diff, import, and
verify the persisted body and metadata. If the focus does not exist yet,
create it with `memorize` and tags `["project:<slug>", "seed"]`.
Every FOLLOW-UPS line carries forward; the ones that shipped get a tombstone
— `shipped <hash>` — and keep their line until the weight check below
retires them. A follow-up that lives in another repository names that
repository's absolute working-copy path, verified with
`git -C <path> status -sb` as you write the line; a repo name alone is
ambiguous across clones and worktrees. Retros hold durable lessons; state
lives here.

**The focus holds state.** A ruling, a protected decision, or a working list
made this session is a spoke saved in step 5, and the focus gains one GROUND
TRUTH pointer to it: `<mnemonic> — load when <task>`.

**Then verify the write with a tag-filtered recall** — `recall(query =
"<slug>/current-focus", tags = ["project:<slug>"], limit = 1, truncate =
200)`, session-start's call with a truncation added — and confirm the
result's mnemonic *and* its `tags:` line. An untagged seed still answers a
bare-mnemonic query but disappears from session-start's filtered recall.
Repair missing tags with `edit(mnemonic, add_tags = ["project:<slug>",
"seed"])` and repeat the filtered recall.

**Weigh the focus on the same recall.** The `(N more chars)` remainder is its
weight. Over the taxonomy's cap, **retire** content to its home (taxonomy,
*Weight: hot and cold*), shipped follow-ups first: the cold memory written
and verified, then the focus rewritten with a pointer in its place.

Done when the saved body matches the edited file (or the new focus's
submitted body) and the filtered recall returns the focus with its tags
and under the cap — or, when a retro has no time to retire, with the overage on the
FOLLOW-UPS list as `focus at <N> chars · memory-gardening`.

### 7. Confirm with the user

Show a table: mnemonic · reinforced or new · aliases · hub placement. Ask if any
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
| Park a ruling or a working list in `current-focus`     | The focus is loaded every session. Keep the ruling or list in a spoke the focus points to. |
| Save a lesson without running step 4                   | Four memories saying "nightly fmt got skipped" is how a corpus drowns its own lessons.    |
| Save a spoke with no alias                             | The slug loses to older, vaguer memories; the lesson is unfindable by the session it's for.|
| Give every spoke its own hub line                      | The hub is a working set; a line per spoke saturates the cap in weeks and buries the costly-to-forget rules. Cluster, or ship the spoke lineless. |
| Pass two tags to `recall`                              | OR semantics: the second tag pulls in every other project carrying it.                   |
| `edit` to update content                               | The tool only changes metadata. For long bodies, export, patch the file, and import per [Editing an existing memory](../../EDITING.md). |
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
You: [memorize ×2, edit add_mnemonics ×2, export/patch/import existing hub,
     link ×3, export/patch/import current-focus; verify bodies and filtered recalls]
```

A smooth-sailing session reads: "Today went the way the saved lessons
predicted — nothing new. I rated habits/rendering up and added the alias 'why
does the clock flicker?' to single-swap-per-frame, which took two tries to
find."
