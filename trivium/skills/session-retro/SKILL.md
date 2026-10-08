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

**Budget.** A retro saves at most **three** new spokes and reports its own
cost. Recurrence is the filter: a lesson costly enough to forget comes back
and gets saved the next time. One week of ungated retros wrote 132 memories
in four days, about eight per retro, and nobody recalls 132 lessons.

## When to use

- End of a session, after a feature lands, a bug is fixed, a review is
  posted, or an investigation concludes.
- Before a final commit on a meaningful chunk of work.
- User asks for a retro explicitly.

Step 0 decides between a full retro and a maintenance pass. The user does
not need to remember whether the session earned one.

## Steps

### 0. Gate: what landed, what surprised

Fix the retro's **scope** first: everything since the last retro, handoff,
or pickup in this session. A handoff and a retro are one event; a session
that wrote a handoff retros only what happened after it.

Then enumerate from the record, not from the user's memory. Exhaustion is
why the user asked for a retro skill in the first place, so a gate that
asks "did anything surprise you?" fails exactly when it matters.

- **Landed:** `git log --since=<scope start>` and `gh pr list --author=@me
  --state=all --search "updated:>=<date>"`; plus reviews posted, documents
  written, and messages sent, which git does not see.
- **Surprised:** scan the scope for the model's own self-corrections ("one
  correction to my earlier report", "I called it wrong", "false alarm"),
  the user's corrections, a tool-error cluster, an amended or reverted
  commit, and a review finding that changed a verdict. Each hit is a
  candidate for step 3.

Present both lists in a line or two and let the user **veto**, not recall.
Both empty, or the last retro under two hours old in this project: run
the *Smooth sailing* pass below and stop. Budget for that pass: five tool
calls. Either list non-empty: continue with the candidates as step 3's
starting set.

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

`Why` is non-negotiable in all three. Draft freely, then **rank by cost to
forget** and keep the top three; the rest are dropped, not parked. A short
session keeps zero to two. Every kept candidate must pass step 4.

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
- **Related but distinct** — a new spoke whose body names the existing
  mnemonic in a `See also:` line. The link itself is a gardening move,
  made when the export shows the whole neighbourhood at once.
- **Nothing** — a new spoke.

Done when every candidate has a verdict. A candidate that duplicates an
existing spoke and gets saved anyway is the single most common way this corpus
degrades.

### 5. Save each new spoke — three moves, sometimes five

1. **Memorize** with the full tag set: `["project:<slug>", "<kind>",
   "theme:<theme>"]`, plus `"general:<domain>"` if it transfers. Read the
   response: if it reports an auto-merge into an existing memory, your
   mnemonic does not exist — switch to the *Covered* path and reinforce the
   memory it merged into instead.
2. **Alias** it, once: `edit(mnemonic, add_mnemonics = ["<question>"])`
   with the one natural-phrasing question a future session would ask. The
   slug alone embeds poorly (taxonomy, *Spokes*); one question is what
   recall matches, and a second that rephrases the first adds a call, not
   a hit.
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
4. **Link** `link(spoke, hub, "related")`: one link, to the hub. A general
   spoke also links to its domain hub — `general/habits/agent-process`,
   `general/habits/rust-toolchain`, and so on per the taxonomy — created if
   missing. Links to related spokes belong to gardening (step 4).
5. **Bug report**: a spoke with `theme:memory` and kind `avoid` is a defect in
   these skills. Memorize it, then tell the user which skill step failed so
   the skill gets patched. A process lesson that lives only in project memory
   never flows back.

Done when each saved spoke has one alias, a theme tag, a hub link, and a
hub placement — cited on a line, or lineless by design.

### 6. Update `current-focus`

The focus is rewritten only when FRONTIER or NEXT moved. A shipped
follow-up, a new tombstone, or a changed status is a **one-line patch** to
the exported file, not a rewrite. Either way, use
[Editing an existing memory](../../EDITING.md): start from a fresh export,
patch its file in the four-section format, review the diff, import, and
verify the persisted body and metadata. If the focus does not exist yet,
create it with `memorize` and tags `["project:<slug>", "seed"]`.
A FOLLOW-UP asked of a person is verified at its channel, not carried: read
the DM or thread from the ask's timestamp before writing `open`. Every
FOLLOW-UPS line carries forward; the ones that shipped get a tombstone —
`shipped <hash>` — and keep their line until the weight check below retires
them. A follow-up that lives in another repository names that repository's
absolute working-copy path, verified with `git -C <path> status -sb` as you
write the line; a repo name alone is ambiguous across clones and worktrees.
Retros hold durable lessons; state lives here.

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
weight. Over the taxonomy's cap, add one FOLLOW-UPS line — `focus at <N>
chars · memory-gardening` — and leave retirement to gardening, which sees
the counters. The one retro-time exception is a focus more than half again
over its cap: then **retire** shipped follow-ups to a history memory
(taxonomy, *Weight: hot and cold*), write and verify the cold memory, and
rewrite the focus with a pointer in its place. Name a history memory by
month AND arc — `<slug>/history/<yyyy-mm>-<arc>`, never `<yyyy-mm>` alone:
two month-only names differ by one token and embed inside `memorize`'s 0.15
auto-merge radius, so the October log lands inside September's with a
unioned tag set and nothing looks wrong. Read every `memorize` response for
"merged with" before trusting that a new memory exists.

Done when the saved body matches the edited file (or the new focus's
submitted body) and the filtered recall returns the focus with its tags,
under the cap or with the overage recorded on FOLLOW-UPS.

### 7. Confirm with the user, with the bill

Show a table: mnemonic · reinforced or new · aliases · hub placement. Ask if
any should be edited or dropped before they cement. For a smooth-sailing
session, report the maintenance done instead.

Close with one line, every time: `retro cost: <N> tool calls · <M> new
memories · <K> reinforced`. A retro past forty calls or three new memories
is the signal that the gate or the cap was skipped; say which.

## Smooth sailing is a valid outcome

Some sessions produce zero new memories — everything went the way prior
lessons said it would. That's a *successful* retro, and step 0 routes to it
directly. Its work is maintenance of the memories that got you there, within
a five-call budget:

- `rate` up the hubs and spokes that guided the session, down the noise.
- `edit` to add an alias to a memory that was hard to find this time.

Report it in two lines and stop. Running a second retro in the same session
on the same scope produces invented lessons; decline it and say why.

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
| Ask the user whether anything surprised them           | The record holds the surprises; a tired user does not. Step 0 enumerates, the user vetoes. |
| Save a fourth spoke because it is also true            | Three is the cap. A lesson worth keeping recurs and is saved then; the corpus stays recallable. |

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
You: [memorize ×2, edit add_mnemonics ×1, export/patch/import existing hub,
     link ×2, one-line patch to current-focus; verify bodies and filtered recalls]
     retro cost: 14 tool calls · 2 new memories · 0 reinforced
```

A smooth-sailing session reads: "Step 0: one commit landed, no corrections
in the record. Today went the way the saved lessons predicted. I rated
habits/rendering up and added the alias 'why does the clock flicker?' to
single-swap-per-frame, which took two tries to find. retro cost: 4 tool
calls · 0 new · 1 reinforced."
