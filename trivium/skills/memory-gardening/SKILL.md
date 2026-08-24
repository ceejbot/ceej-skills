---
name: memory-gardening
description: Use when the user says "garden the memories" / "clean up our memories" / "tidy project memory", when session-start cannot find a lesson that current-focus names, when a project was renamed, or every ten sessions or so on a long-running project. Periodic reorganization of a project's trivia memories — archive stale state, merge duplicates, write and refresh habit hubs, add aliases and links — so recall keeps returning the lessons that matter.
---

# Memory Gardening

Reorganize a project's trivia memories so that recall keeps working. A corpus
that grows one retro at a time drifts in predictable ways: old state memories
accumulate recalls and outrank every specific lesson; the same lesson gets
saved four times in different words; themes grow past what a checklist can
hold; a project rename leaves half the mnemonics under the old prefix.
`session-retro` prevents some of this one lesson at a time. Gardening runs
fresh, over the whole corpus, and repairs the rest. The target shape and the
tool semantics this skill leans on are in `${CLAUDE_PLUGIN_ROOT}/TAXONOMY.md`;
read it first.

**Core principle:** read the export, decide on files, then execute a compiled
op list. `trivia export` writes one markdown file per memory with the recall
and rating counters in its frontmatter. Reading files costs no context per
memory and bumps no counters, so the whole corpus can be seen at once. Every
mutation is then compiled into a deterministic list and executed verbatim —
judgment happens once, on disk, where it can be validated; the store only
ever sees the result.

## When to use

- The user asks to garden, tidy, clean up, or reorganize project memory.
- `session-start` could not find a lesson that `current-focus` named.
- A project was renamed; the old slug is still a mnemonic prefix.
- A hub has hit twelve lines, or `stats.py` reports a theme over twenty spokes.
- Roughly every ten sessions on a project that retros regularly.

**Skip if:** the project has fewer than ~30 memories. Nothing has had time to
drift; a retro's maintenance pass covers it.

## Steps

### 1. Export and measure

```
export(directory = "<scratch>/export-0")          # full store, no tag filter
python3 ${CLAUDE_PLUGIN_ROOT}/skills/memory-gardening/stats.py <scratch>/export-0 <slug> [<old-slug> …]
```

`export-0` is the undo for the whole pass: copy it somewhere durable and
never write into it. Export the **whole store**, not just the project tag —
the project's real working set is usually bigger than its tag. Memories
written during briefings and prep (person facts, calendar identities,
preferences, voice notes) tend to carry topical tags (`calendar`, `meetings`,
`people`, `<user>`) but not `project:<slug>`; on the 2026-08 running-notes
pass the untagged strays (56) outnumbered the tagged corpus (49), and the
project's most-recalled memory was among them. Sweep the export for
project-relevant memories missing the project tag — skip any already homed to
another `project:` tag — and carry the list into triage. Every later step
that needs current state takes a fresh export (`export-1`, `export-2`, …)
and points `stats.py` at the newest one; tags set through MCP never reach an
old export.

The report gives recall concentration, never-recalled share, net-negative
ratings, off-prefix and off-shape mnemonics, tag coverage, hubs present
versus themes in use, alias coverage, and lexical near-duplicate pairs. Also
run `trivia automerge --dry-run` once; on a corpus of distinct slugs it finds
nothing, which confirms the duplicates are in the bodies and need step 5.

### 2. Triage with the user

Present the numbers and four decisions:

- **The adoption set.** The step-1 stray sweep's list of project-relevant
  memories missing `project:<slug>`. The user says which get adopted (tagged
  into the project and gardened with it) and which stay a shared pool.
- **The theme list.** Read it from `<slug>/conventions`; propose additions
  for clusters the stats show and splits for themes over twenty spokes. The
  user owns this list.
- **The archive set.** Every memory that is *state* rather than a lesson —
  session summaries, "phase complete" reports, gap inventories, anything with
  a date in its mnemonic and a net-negative rating. Merge is irreversible, so
  name them and get a yes.
- **Which lessons are general.** Candidates are the tooling, orchestration,
  and idiom spokes; the user confirms the `general:<domain>` tags.

### 3. Archive state by merge

Trivia has no delete. Pick one memory of the set as the keeper and
`edit(new_mnemonic = "<slug>/history/<yyyy-mm>-<arc>")`, then `merge(keep,
discard)` the rest into it in chronological order. Merge unions every
discard's tags and keeps its mnemonic as an alias, so finish with
`edit(keeper, add_tags = ["archive"], remove_tags = <every absorbed tag except
the project tag>, remove_mnemonics = <every absorbed mnemonic>)` — the old
"session retrospective" names must stop attracting recall. Before merging,
lift any lesson the summaries carry that the spokes don't; write those as
spokes in step 6.

Done when a fresh export shows no memory the user chose to archive outside
`history/`, and the keeper carries exactly `project` + `archive`.

### 4. Partition and normalize on disk

No store calls in this step. The corpus is the project-tagged memories plus
the adoption set the user approved in step 2. From `export-0`, build three
files over that corpus:

- **`decisions.tsv`** — one row per memory: mnemonic, kind, theme, action
  (`keep` / `archive` / `seed`). Kind comes from the mnemonic's second
  segment or, for legacy shapes, from the body. Theme comes from a keyword
  first pass over mnemonic, tags, and body; step 5's agents correct it.
- **`renames`** — every on-prefix mnemonic outside the taxonomy table
  (`<slug>/reference/…`, bare `<slug>/<thing>`, sentences with spaces) gets a
  target `<slug>/<kind>/<handle>`; every `<old-slug>/…` becomes `<slug>/…`.
  Renames run first in step 7, before anything merges into the new name.
- **`themes/<theme>/`** — the export files copied into one directory per
  theme, so each step-5 agent reads only its slice.

Done when every memory in the export appears in `decisions.tsv` exactly
once and every `keep` row has a kind and a theme.

### 5. Dedupe by theme — fan out over the files

One fresh-context agent per theme, reading `themes/<theme>/` (never the
MCP). Each returns JSON:

- **Merge sets**: groups that state one lesson; the survivor's mnemonic
  (prefer the most-recalled; use the *renamed* name if step 4 renamed it); a
  single body that folds in every instance's `Situation` and keeps the
  sharpest `Why` and `What to try instead`.
- **Aliases** for each survivor and each single: one or two questions a
  future session would ask.
- **Generality**: project-only or `general:<domain>`, with a one-line reason.
- **Misfiled**: memories that belong in another theme.
- **Links**: related-but-distinct pairs.
- **Hub lines**: the theme's checklist, at most twelve, most costly-to-forget
  first, each naming its spoke; an `overflow` count if more rules exist.

Validate the set with a script before reading it: every mnemonic exists in
the export, none is claimed by two themes or two merge sets, every merge set
has a body and aliases, every link endpoint resolves. Then read every merge
set and hub line yourself; reject with a reason or accept. Misfiled memories
go to one follow-up agent for aliases and a theme tag.

Done when every theme's proposal validates and you have read all of it.

### 6. Write the hubs

For each project theme, `memorize` `<slug>/habits/<theme>` with the
accepted checklist and tags `["project:<slug>", "habits", "theme:<theme>"]`.
Compose the general hubs from the agents' candidates, capped at twelve each:
`general/habits/<domain>[-<facet>]` with tags `["habits", "general:<domain>"]`
and no project tag. Hubs exist before step 7 links anything to them.

Rewrite `<slug>/overview` if it is stale, and `<slug>/current-focus` into the
four-section format if it isn't already, tombstoning any follow-up found
shipped. Add the theme list and a `last gardened <date>` line to
`<slug>/conventions`.

### 7. Compile the op list and execute it

A script turns the accepted proposals into one JSONL op list per theme, in
this order per memory: `rename` → `merge` (one per discard) → `memorize`
(survivor body with its full tag set) → `edit_tags` (add kind/theme/general;
remove legacy kinds, `retro`, and every tag a merge absorbed) → `aliases` →
`link` (spoke → its theme hub; each related pair). `memorize` replaces the
tag set and keeps aliases, so it precedes the alias edit. Links target hubs
written in step 6.

Run the smallest theme's list yourself first to confirm the semantics hold,
then hand each remaining list to an executor agent with one instruction:
execute in file order, record failures, never improvise. Read the reports.

Done when every executor reports, and each failure is either expected (a
rename of something already archived) or resolved by hand.

### 8. Turn process lessons into skill patches

Every `avoid` spoke under `theme:memory` is a bug report against the trivium
skills: a recall that used two tags, an `edit` that tried to change content,
a focus pointer nobody verified. For each, patch the skill step it names. A
spoke that is also a general lesson stays (tagged `general:agent-process`,
linked from `general/habits/agent-process`); one that was only a bug report
merges into the history memory.

### 9. Verify with a query that used to fail

Take a fresh export and rerun `stats.py`: kind tags `{1: N}`, every hub and
spoke with a theme, zero off-shape mnemonics, every spoke aliased and
linked. Then take a recall that missed in a recent session — `session-start`
names one when it suggests gardening, or the user does — and run it again
exactly. The expected memory comes back in the top three, or the pass isn't
finished: add an alias or fix a tag and rerun. `rate` what came back.

### 10. Close

Report to the user: memories before and after, merges applied, hubs written,
aliases added, skills patched, and the verification query with its result.
Run `session-retro`; a gardening pass that found a new drift pattern has a
lesson for this skill.

## Anti-patterns

| Don't                                                | Why                                                                                   |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Read the corpus through MCP `recall`                 | Every read bumps `recall_count`; the survey itself would distort the ranking.          |
| Merge without `export-0` on disk                     | Merge is the only delete trivia has. The export is the undo.                           |
| Check a done-criterion against an old export         | Tags set through MCP never reach it; take a fresh export first.                        |
| Rely on `automerge`                                  | It compares mnemonics, and retro slugs are built to be distinct. Bodies hold the dupes.|
| Let an agent decide what to merge while it executes  | Judgment on disk, validated; execution verbatim. Irreversible ops get no improvisation.|
| Treat any `limit = 1` hit as the hub                 | Recall returns the nearest neighbour; the mnemonic must match exactly or the hub is absent. |
| Let a hub grow past twelve lines                     | A checklist nobody reads to the end is a list, not a habit. Split the theme.           |
| Garden without the user on the archive set           | Merging state into history is irreversible.                                            |

## Example

```
User: let's garden the memories; session-start couldn't find the stage-6 lessons last time
You: [export-0 → 448 files; stats.py → 72% never recalled, top 15 carry 68% of recalls,
      two 2026-04 "session retrospective" memories rated -24/-28, 106 off-prefix, 0 hubs]
     Three decisions: themes (tooling, testing, orchestration, review, design,
     transparency, memory, rust-idioms), an archive set of 15 state memories
     (listed), and general tags on the tooling/orchestration/idiom spokes.
User: yes to all three.
You: [rename keeper → history/…; merge ×16; edit tags + remove 16 aliases]
     [decisions.tsv, themes/ staged; 8 theme agents → 59 merge sets, 60 misfiled, 89 hub lines; validator: 0 errors]
     [read every merge set and hub; accepted; one theme split out (installer)]
     [memorize 9 project hubs + 4 general hubs]
     [ops compiled: ~1,400 calls; ran memory (17) by hand; 8 executors for the rest, 2 expected failures]
     [patched session-start step 6; rerun the stage-6 recall with full_text_search="native" → top hit]
     448 → 341 memories, 9 project hubs + 4 general hubs, every spoke aliased and linked.
     The failing recall now returns boltzmann/learned/installer-digests-lock-native-into-generation-id first.
```
