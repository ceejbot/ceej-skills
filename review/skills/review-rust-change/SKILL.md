---
name: review-rust-change
description: Use when reviewing a scoped Rust change — uncommitted diff, unpushed commit stack, or open PR. Triggers on phrases like "review this change", "review my diff", "review this PR", "look over what I'm about to push", or "is this ready to merge". Applies the project-review hygiene lens and probes scoped to the diff and answers four targeted questions (intent match, testing, documentation, completeness). Produces a small number of ranked, highly actionable suggestions.
---

# Rust Change / Diff / PR Review

The change-oriented counterpart to `review-rust-project`. Same standards,
restricted to what the diff actually touches. The hygiene properties live in
[`HYGIENE.md`](../../HYGIENE.md) and the probes in
[`PROBES.md`](../../PROBES.md), both relative to this `SKILL.md`.

**Core principle:** every finding cites a file and a line in the diff. "Could
use more tests" is not a finding; "`src/parser.rs:42-58` adds the empty-header
branch and no test covers empty input" is. Project-wide advice is in scope only
when the diff makes an existing problem materially worse.

## Determining scope

Establish exactly what is under examination before reviewing anything:

- **Uncommitted changes:** `git diff` (working tree) and `git diff --cached`.
- **Unpushed commits:** `git log --oneline origin/main..HEAD` and
  `git diff origin/main...HEAD`, or a single commit hash.
- **GitHub PR:** `gh pr view <number>` for the description, `gh pr diff <number>`
  for the patch.

Always:

- Capture the commit messages or PR description first: this is the "supposed
  to do" that grounds the review.
- Read the full content of every meaningfully changed file, not just the
  hunks. Context, neighbouring tests, and module docs are part of the review.
- Read the prior review rounds and inline threads on a PR: they are the
  discussion, and they carry the author's own deferrals.
- Note which crates are touched; tooling is scoped to them.

## How to run

1. **Capture intent** and confirm scope. Done when the claimed behaviour is
   written down in one sentence.
2. **Sweep the diff** against the sections of `HYGIENE.md` the change touches.
   Skip what the diff leaves alone; listing untouched criteria is noise.
3. **Probe the diff.** For each mechanism the change adds or alters, run the
   matching probe from `PROBES.md` against the new instance and its
   neighbours: a new timeout or pool size (§1 Bounds), a commit followed by a
   publish (§2 Dual writes), a new spawn or shutdown path (§3 Supervision), a
   new vendor call (§4 Boundary symmetry), a new config parse (§5 Startup
   truth), a new type in the irreversible class (§6). Done when every new
   instance is accounted for. The bounds probe in particular finds what bot
   reviewers miss: they verify the bound is set, and never ask what it
   releases.
4. **Answer the Four Questions** explicitly.
5. **Run Tooling** scoped to the changed crates.
6. **Verify and rank.** Re-read each candidate finding at its line. Synthesize a
   small number of ranked suggestions, ideally zero to four, using the output
   template.

Findings land in a single message. Review only: fixes come after the user
picks priorities.

## The four change-specific questions

Answer each one explicitly in the output, not only through the suggestion
list.

1. **Intent match.** Do the changes do what the commit or PR text says?
   Anything claimed but absent? Anything present but unclaimed?
2. **Testing.** Do the tests cover the new behaviour, the edges this diff
   introduces or exercises, and the failure cases? For a binary that is hard to
   unit-test, is there an integration test or a reproducer?
3. **Documentation.** Does the new or changed code have enough docs, and are
   they concise? Doc comments earn their length rather than restating the
   signature.
4. **Completeness.** Is the code complete for its stated goal? Where something
   is deferred, is the deferral documented: a TODO with context, an issue link,
   or a follow-up named in the PR body?

## Tooling

Run these scoped to the changed crates:

- `cargo fmt --check`.
- `cargo clippy --all-targets -- -D warnings` on the touched crate. A new
  `#[allow(clippy::...)]` carries a comment saying why.
- `cargo test -p <crate>`, and `cargo test --doc -p <crate>` for any modified
  public item. A nextest recipe skips doctests, so run them separately.
- `cargo doc --no-deps -p <crate>`, warning-free when the diff adds public
  items.

A failure or warning on the change is a finding, not a footnote. When the
change cannot be built locally (cross-compile, missing dev deps), say so
rather than silently skipping.

## Writing the feedback

Constructive review is more useful than exhaustive review. The goal is to help
the work land cleanly.

- **Lead with what works.** One sentence on what the change gets right before
  the suggestion list.
- **Rank ruthlessly.** Critical / Important / Medium / Polish. If everything
  looks fine, "ship it" is the review.
- **Cite the diff.** Every finding names a file and a line. A finding that
  cannot point at a line is not ready.
- **Carry an impact statement on every Critical and Important finding.** One
  sentence: what happens in production if this lands as is, written as a
  scenario, not a category.
- **Describe the smallest fix.** Where a deeper rework is warranted, say so
  and mark it out of scope for this change.
- **Distinguish blocker from taste.** Critical means wrong, unsafe, or not what
  the PR claims. Polish means "I'd write it differently."
- **Say when it's done.** When a previous round has converged, say so.
- **Frame feedback as the work, not the author.** "This branch could…" rather
  than "you could…".
- **Specific findings, no numeric scores.**

## Output template

```
## Change under review
<One sentence plus a reference to the diff, PR, or commit range>

## Does it achieve its stated goal?
<Direct answer with evidence from the diff and the commit or PR text>

## Four questions
- **Intent match:** ...
- **Testing:** ...
- **Documentation:** ...
- **Completeness:** ...

## Probes
<One line per probe that applied, or "no new mechanisms in this diff">

## Tooling
- `cargo fmt`: ...
- `cargo clippy`: ...
- `cargo test`: ... (doctests: ...)
- `cargo doc`: ...

## Suggestions (ranked)

**Critical**
1. `<file:line>` — <concrete problem>. Impact: <production scenario>. <What a successful fix looks like.>

**Important**
1. ...

**Medium**
...

**Polish**
...

## Overall verdict
<One or two sentences: "Ready to merge", "One critical issue, the rest is minor", "Direction is good after X".>

## Recommended next action
<Single concrete step, or "None — this looks ready to land.">
```

## Project-specific notes

Check the repository's agent instructions (`AGENTS.md` or `CLAUDE.md`) and
`docs/review-notes.md` for project-specific review notes, and honour them
alongside this skill. The shape such notes take (from Entropic):

- Pay special attention to golden test vectors and whether new behaviour has
  corresponding entries in the generator and regression test.
- Changes that touch sigchain actions, admission policies, or transparency
  should reference the relevant design doc.
- Documentation should be concise; this project values precise,
  non-repetitive comments and design docs over long inline prose.
- "Complete" often means "the generator produces the vector and the test
  asserts it" for cryptographic or protocol work.
