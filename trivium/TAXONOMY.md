# Trivia memory taxonomy

Shared reference for the trivium skills. One namespace, six mnemonic shapes,
four tag rows, and four recall rules. Every skill in this plugin reads and
writes memories in this shape, so a memory written by `session-retro` is one
`session-start` can find and `memory-gardening` can sort.

## Mnemonics

| Shape                            | Kind      | Holds                                                                 |
| -------------------------------- | --------- | --------------------------------------------------------------------- |
| `<slug>/overview`                | `seed`    | What the project is and why. Slow-changing.                           |
| `<slug>/conventions`             | `seed`    | Non-obvious rules, build commands, lint config, the theme list.       |
| `<slug>/current-focus`           | `seed`    | State, in the four-section format below. Changes every session.       |
| `<slug>/habits/<theme>`          | `habits`  | A **hub**: the theme's working set — at most 12 lines, each a rule citing 1–4 spokes. |
| `<slug>/worked/<handle>`         | `worked`  | A **spoke**: an approach that paid off.                               |
| `<slug>/avoid/<handle>`          | `avoid`   | A spoke: an approach that failed, and what to do instead.             |
| `<slug>/learned/<handle>`        | `learned` | A spoke: a durable fact about the domain, a tool, or the codebase.    |
| `<slug>/history/<yyyy-mm>-<arc>` | `archive` | Merged session summaries and retired state. Excluded from recall.     |
| `general/habits/<domain>[-<facet>]` | `habits` | A cross-project hub, keyed by domain (never by a project's theme). |

`<slug>` is the project's `Cargo.toml` `[package].name`, or the directory
basename lowercased with non-alphanumerics replaced by hyphens. When a project
is renamed, `memory-gardening` renames the prefix on every memory. Any other
shape — `<slug>/reference/…`, a bare `<slug>/<thing>`, a sentence with spaces
— is legacy; gardening reshapes it into one of the rows above.

**Spokes stay where they were born.** A lesson that transfers to other
projects keeps its project mnemonic and gains a `general:<domain>` tag; the
matching general hub links to it. Nothing moves between projects.

**Every spoke carries one or two aliases** phrased as the question a future
session asks — "why does cargo check pass but clippy fail on the tests?" The
slug is for humans and hubs. The alias is what recall matches; a slug alone
embeds poorly and loses to older, vaguer memories. Add aliases with
`edit(mnemonic, add_mnemonics = [...])`.

## Tags

| Row     | Values                                                                 | On                                  |
| ------- | ---------------------------------------------------------------------- | ----------------------------------- |
| project | `project:<slug>`                                                       | every project-scoped memory         |
| kind    | `seed` · `habits` · `worked` · `avoid` · `learned` · `archive`         | every memory, exactly one           |
| theme   | `theme:<name>` from the project's declared list                        | every hub and spoke, exactly one    |
| general | `general:<domain>`                                                     | spokes that transfer; general hubs  |

Seeds and archives carry project + kind only. A general hub carries `habits`
+ `general:<domain>` and no project tag.

**Themes** are declared per project in `<slug>/conventions`. Starter list,
trimmed or extended to fit:

- `tooling` — build, lint, test runner, shell, CI gotchas
- `testing` — fixtures, vectors, harnesses, what a test proves
- `orchestration` — subagents, worktrees, fan-out, briefings, Codex
- `review` — spec, plan, and code review rounds
- `design` — design docs, specs, decisions
- `<lang>-idioms` — language idioms, separate from tooling: `rust-idioms`, `scala-idioms`
- `memory` — the memory process itself; `avoid` spokes here are bug reports against these skills
- domain themes as the project needs them (`transparency`, `installer`, `rendering`, …)

**General domains** are the cross-project recall key. Another project recalls
`tags = ["general:rust"]` and gets the lessons without copying them. The
general hubs are fixed across projects, one per domain facet:

| Domain                  | Hubs                                                                                   |
| ----------------------- | -------------------------------------------------------------------------------------- |
| `general:rust`          | `general/habits/rust-toolchain` · `general/habits/rust-idioms` · `general/habits/rust-testing` |
| `general:agent-process` | `general/habits/agent-process` — subagent, Codex, and Claude Code workflow lessons     |
| `general:<lang>`        | `general/habits/<lang>-toolchain` · `-idioms` · `-testing`, added as the language appears |

## Recall rules

1. **One tag per `recall` call.** Trivia's tag filter is OR: two tags widen
   the result set to every project carrying the second tag. Filter on the
   project tag alone.
2. **Specificity goes in the query.** Seeds and hubs: query the exact
   mnemonic, `limit = 1`. Spokes: a natural-phrasing query plus
   `full_text_search` on a distinctive body word.
3. **A hit is exact or it is absent.** Semantic recall always returns the
   nearest neighbour, so `limit = 1` on a missing mnemonic returns some
   *other* memory. A result counts as the seed, hub, or sentinel only when
   its `mnemonic` equals the queried string exactly. Anything else means the
   memory does not exist yet.
4. **`exclude_tags = ["archive"]` on every lessons recall.** Archived state
   is kept for history, never for guidance.

## Body formats

```
worked:   Situation: … | What we did: … | Why it worked: …
avoid:    Situation: … | What we tried: … | Why it failed: … | What to try instead: …
learned:  Fact: … | Where it came from: … | Why it matters: …
```

`Why` is non-negotiable. Without it the lesson cannot survive contact with a
different situation.

A **hub** is the theme's **working set** — the rules most costly to forget
right now — not an index of every spoke. Its body is an ordered list, the
most costly-to-forget rule first. Each line states one rule and cites the
spoke(s) it distills, up to four; spokes that are instances of one rule share
a line:

```
1. Run nightly fmt before declaring CI green; subagents skip it — <slug>/avoid/subagent-acceptance-skips-nightly-fmt
2. Treat every prose sentence about code as a code claim; read the source before writing it — <slug>/avoid/reuse-claims-are-code-claims, <slug>/avoid/design-doc-claims-inherited-by-citation
```

Twelve lines is the cap. Under it, a genuine new rule gets a line at its
priority position; **at the cap, admission is by displacement** — a new line
earns its place by joining an existing rule as a citation, or by being more
costly to forget than the current line 12. A spoke without a hub line is
healthy, not homeless — its aliases and the session-start probes still find
it; it just isn't front of mind. When the cap presses, the moves in order:

1. **Cluster** — fold sibling lines that state one rule into a single line
   citing all their spokes. The test: if the merged rule as written would
   not have prevented each cited spoke's specific mistake, it is two rules.
2. **Evict** — demote the line whose spokes have stopped earning recalls.
   This is a gardening-pass move: only the export's `recall_count` and
   rating counters can say which lines are cold without the survey itself
   bumping them. The spokes keep their aliases and links, so eviction is
   reversible at any pass. Coldness alone never evicts a rule whose
   violation is irreversible; such lines leave only by clustering.
3. **Split the theme** — last resort, only when the surviving lines
   genuinely serve two disciplines; every split adds a hub each
   session-start must load.

**`current-focus`** has four labelled sections, so the parts that go stale
are visibly marked as such:

```
FRONTIER: one sentence, with commit hash and date.
GROUND TRUTH: where to re-derive this — spec directory, roadmap "last refreshed" line, status header.
NEXT (claims — verify at the consumption site before planning): …
FOLLOW-UPS: <item> · added YYYY-MM-DD · open | shipped <hash>
```

Follow-ups get a tombstone (`shipped <hash>`) when they land. Silent removal
is how a list rots: the next session re-plans work that already shipped.

## Tool semantics worth knowing

- `edit` changes mnemonics, aliases, and tags. It cannot change a body.
- To rewrite a body, `memorize` with the **same mnemonic**. This overwrites
  the content, **replaces the tag set** with the one you pass, and keeps the
  memory's aliases and links. Pass the full tag set every time.
- `memorize` with a *new* mnemonic that lands within distance 0.15 of an
  existing one is auto-merged into it. Read the response: if it reports a
  merge, the memory you meant to create does not exist under your name.
- `merge(keep, discard)` deletes `discard`, appends its body to `keep`,
  unions its tags onto `keep`, and **keeps `discard`'s mnemonic as an alias**
  on `keep`. Follow a merge with `edit(keep, remove_tags = …)` to restore a
  clean tag set, and `remove_mnemonics` when the old name should stop
  attracting recall (archives), or leave it when it should (spokes).
- There is no delete. Merge is the only removal, and an export is the only
  undo.
