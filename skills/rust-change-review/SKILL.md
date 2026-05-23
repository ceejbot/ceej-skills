---
name: rust-change-review
description: Use when reviewing a scoped Rust change — uncommitted diff, unpushed commit stack, or open PR. Triggers on phrases like "review this change", "review my diff", "review this PR", "look over what I'm about to push", or "is this ready to merge". Applies the project-review quality lens scoped to the diff and answers four targeted questions (intent match, testing, documentation, completeness). Produces a small number of ranked, highly actionable suggestions.
---

# Rust Change / Diff / PR Review

The change-oriented counterpart to `rust-project-review`. Same standards, but ruthlessly restricted to what the diff actually touches.

**Core principle:** Every finding must cite a file and a line in the diff. "Could use more tests" is not a finding; "`src/parser.rs:42-58` adds the empty-header branch but no test covers empty input" is. Project-wide advice is out of scope unless the diff makes an existing problem materially worse.

## Determining scope

Establish exactly what is under examination before reviewing anything:

- **Uncommitted changes** — `git diff` (working tree) and `git diff --cached` (staged).
- **Unpushed commits** — `git log --oneline origin/main..HEAD` and `git diff origin/main...HEAD` for a range, or a single commit hash.
- **GitHub PR** — `gh pr view <number>` for the description, `gh pr diff <number>` for the patch.

Always:

- Capture the commit message(s) or PR description first — this is the "supposed to do" that grounds the review.
- Get the list of changed files plus the unified diff.
- Read the full content of every meaningfully changed file, not just the hunks. Context, neighboring tests, and module-level docs are part of the review.
- Note which crates are touched. Tooling commands will be scoped to those crates.

## How to run

1. Capture intent (commit message / PR description) and confirm scope.
2. Walk the **Quality Lens** below, finding issues only where the diff touches them.
3. Answer the **Four Questions** explicitly.
4. Run **Tooling** scoped to the changed crate(s).
5. Synthesize a small number of ranked suggestions (ideally 0–4 total) using the Output Template.

Findings land in a single message. Don't fix anything in this pass — review only. Fixes come after the user picks priorities.

## Quality lens (scoped to the diff)

The project-review lens, restricted to what the change actually touches. Skip anything the diff doesn't touch — listing irrelevant criteria is noise.

### General

- **Intent vs. implementation** — does the diff plausibly achieve what the commit/PR text claims it does? Anything claimed but absent?
- **Architecture impact** — does the new code sit in the right module? Does it cross a boundary it shouldn't, or smuggle a concern into a file that didn't have it?
- **Information hiding** — does the change leak internals via new `pub` items, or is the new surface minimal? Could a `pub(crate)` work instead?
- **Simplicity** — is the new code as simple as it can be? Premature abstraction, copy-pasted blocks, or three-line "helpers" used once?
- **Parse, don't validate** — if the change accepts new input, is it converted to a strongly-typed representation at the edge so interior code can assume validity?
- **Cleanup** — did the change leave behind `dbg!`, `eprintln!`, commented-out blocks, `#[allow(dead_code)]`, or TODOs without context?
- **Documentation** — new public items have `///` docs explaining *why* and *when*, not just restating the signature? Module-level docs updated if the module's shape changed?
- **README / examples** — if a user-visible feature changed, is the README still accurate? Do code examples still compile?

### Rust-specific

- **Types do work** — new primitives that should be newtypes (`UserId(u64)`, `Millis(u64)`, `Email(String)`)? Stringly-typed parameters that should be enums? `NonZeroU32` / `NonEmpty<T>` / `OnceLock` opportunities the diff just missed?
- **Errors are typed** — new failure modes added as proper enum variants? Libraries: `thiserror` with `#[source]` / `#[from]` chaining. Binaries: `anyhow` / `eyre` with `.context()` at each call. No `Box<dyn Error>` in public APIs.
- **No casual panics** — new `.unwrap()` / `.expect()` confined to tests, `main` returning `Result`, or genuine type-system invariants (with a `// SAFETY:`-style comment explaining why it can't fail)? New index access (`arr[i]`) that should be `.get()` or `.chunks()`?
- **Idiomatic shape** — iterators over manual `for i in 0..n`, `?` over manual `match`, `if let` / `let else` to cut nesting, `From` / `Into` / `TryFrom` for conversions, `Default` where there's a sensible default, `#[must_use]` on builders and query results, `Display` hand-written where it's user-facing.
- **Clones** — every new `.clone()` / `.to_string()` justified? Could it be a borrow, a move, or `Cow<'_, T>`? Particularly suspect inside hot loops, on large structs, or in trait impls.
- **Lifetimes** — elided where the compiler infers correctly; explicit only when the relationship matters. No `'static` smuggled in to silence a borrow checker complaint.
- **Module hygiene** — new `pub` intentional, not "the compiler asked for it"? `pub(crate)` / `pub(super)` used where appropriate? Re-exports build a clean public façade, not "reach through `internal::deeply::nested`"?
- **Async hygiene** — no `block_on` deep in the call stack, no second runtime introduced, `Send + 'static` bounds only where required, cancel-safe across `.await` points (no half-mutated state if the future drops).
- **`unsafe`** — every new `unsafe` block has a `// SAFETY:` comment justifying the invariants? Safer alternative considered? Default target for personal projects is zero `unsafe`.
- **`Cargo.toml`** — new dependencies justified and not duplicating something already in the graph? Features documented? `[dev-dependencies]` separated? MSRV bump intentional if any?

## The four change-specific questions

Answer each one *explicitly* in the output, not just implicitly via the suggestion list.

1. **Intent match** — Do the changes do what the commit/PR text says they do? Anything claimed but not actually present? Anything present but unclaimed?
2. **Testing** — Are the tests adequate? Specifically: do they cover the new behavior, the edges introduced or exercised by this diff, and the failure cases? If the change is in a binary that's hard to unit-test, is there at least an integration test or a reproducer?
3. **Documentation** — Does the new/changed code have enough docs? Are they *concise* rather than verbose or repetitive? Doc comments should earn their length, not restate the signature.
4. **Completeness** — Is the code complete for its stated goal? If something is intentionally deferred, is the deferral documented — a TODO with context, an issue link, or a follow-up commit listed in the PR body?

## Tooling

Run these scoped to the changed crate(s), not the whole workspace where possible:

- `cargo fmt --check` — should be clean.
- `cargo clippy --all-targets -- -D warnings` on the touched crate. New `#[allow(clippy::...)]` should carry a comment explaining why.
- `cargo test -p <crate>` — including `cargo test --doc -p <crate>` for any modified public items.
- `cargo doc --no-deps -p <crate>` — warning-free, especially if the diff added new public items.

If any of these fail or warn on the change, that's a finding, not a footnote. If the change can't be built locally (cross-compile, missing dev deps), say so explicitly rather than silently skipping.

## Writing the feedback

Constructive review is more useful than exhaustive review. The goal is to help the work land cleanly, not to demonstrate rigor.

- **Lead with what works.** A one-sentence "this change is on the right track" before the suggestion list makes the rest easier to act on.
- **Rank ruthlessly.** A short list (Critical / Important / Medium / Polish) beats ten equal-weight nits. If everything looks fine, say "ship it" — that *is* the review.
- **Cite the diff.** Every finding names a file and a line. If you can't point at a line, the finding isn't ready.
- **Describe the smallest fix.** Don't propose rewrites; propose the smallest move that resolves the concern. If a deeper rework is warranted, say so but mark it out-of-scope for this change.
- **Distinguish blocker from taste.** Critical means "this is wrong, unsafe, or doesn't do what the PR claims." Polish means "I'd write it slightly differently." Don't blur the two.
- **Say when it's done.** If a previous round of review has converged, note that explicitly: "After these adjustments the direction is solid." Don't manufacture findings to look engaged.
- **No numeric scores.** A grade out of 10 feels rigorous and isn't. Specific findings are more useful.
- **Frame feedback as the work, not the author.** "This branch could…" not "you could…". Keeps the focus on the change.

## Output template

```
## Change under review
<One-sentence description + reference to diff / PR / commit range>

## Does it achieve its stated goal?
<Direct answer with evidence from the diff and the commit/PR text>

## Four questions
- **Intent match:** ...
- **Testing:** ...
- **Documentation:** ...
- **Completeness:** ...

## Tooling
- `cargo fmt`: ...
- `cargo clippy`: ...
- `cargo test`: ...
- `cargo doc`: ...
(One line each. "Not run — <reason>" is acceptable when the change can't be built locally.)

## Suggestions (ranked)

**Critical**
1. `<file:line>` — <concrete problem>. <What a successful fix looks like>. <How to evaluate.>

**Important**
1. ...

**Medium**
...

**Polish**
...

## Overall verdict
<One or two sentences. "Ready to merge", "One critical issue, the rest is minor", "Direction is good after X", etc.>

## Recommended next action
<Single concrete step, or "None — this looks ready to land.">
```

## Anti-patterns in the review itself

| Don't | Why |
|---|---|
| Review the whole project instead of the diff | Out of scope. Project-wide concerns belong in `rust-project-review`. |
| Give 10 nits at equal weight | Forces the user to do the prioritization. Top few, then a tail. |
| Vague advice ("needs more tests") | Useless without naming the behavior or the file in the diff. |
| Suggest large refactors unrelated to the goal | The diff has a job. Don't expand its scope to fit your review. |
| Ignore the commit / PR description | The "supposed to do" is the rubric. Without it you're guessing at intent. |
| Manufacture findings to look engaged | If the change is good, saying so *is* the review. |
| Numeric scores ("7/10") | Feel rigorous, aren't. |
| Recommend rewrites | This is a review pass. Smallest move that improves it. |
| Skip Tooling because "it probably passes" | Run it. A failing clippy lint is a real finding, not a footnote. |

## Project-specific notes

Replace this section with notes for the repository being reviewed. Example shape (from Entropic):

- Pay special attention to pinned test vectors and whether new behavior has corresponding entries in the generator + regression test.
- Changes that touch sigchain actions, admission policies, or transparency should reference the relevant design doc.
- Documentation should be concise; this project values precise, non-repetitive comments and design docs over long inline prose.
- "Complete" often means "the generator produces the vector and the test asserts it" for cryptographic or protocol work.

Use the same high standards as `rust-project-review`, but ruthlessly scoped to the diff and the stated intent of the change.
