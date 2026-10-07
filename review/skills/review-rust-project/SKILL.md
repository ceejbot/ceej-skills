---
name: review-rust-project
description: Use when the user asks for a holistic / wholistic review of a Rust project, "is this codebase healthy", "review the project", "audit before sharing", or at a periodic checkpoint in a personal Rust project
---

# Rust Project Review

A read-only pass over a whole Rust workspace. Two kinds of material feed it:
the hygiene properties every project should hold, in
[`HYGIENE.md`](../../HYGIENE.md), and the probes that find what lints cannot
see, in [`PROBES.md`](../../PROBES.md). Both paths are relative to this
`SKILL.md`. The output is a ranked set of findings, each at a file:line, each
with an impact statement, each verified before it is ranked.

**Core principle:** every finding cites a file and a reason. "The architecture
could be cleaner" is not a finding; "`src/lib.rs:42` re-exports
`internal::Inner`, which three other modules reach through; a `pub use` there
lets callers stop reaching" is.

## How to run

1. **Orient.** Read the repo's `CLAUDE.md` / `AGENTS.md`, its ADRs or design
   docs, and its justfile or CI config. Done when you can state in one sentence
   each: the crate map and entry points, which recipe runs the tests and what
   that recipe skips, and what the project itself calls irreversible (PHI,
   credentials, money, audit).
2. **Tooling.** Run the project's own gates (fmt, clippy, deny, machete, doc,
   test) through its recipes, then run `cargo test --doc` on its own:
   nextest-based recipes skip doctests, so a green `just test` says nothing
   about them. Run `cargo audit`. Done when every gate has a result in a
   table, or a "not run: reason" line.
3. **Sweep.** Partition the workspace by crate group and sweep each partition
   against every section of `HYGIENE.md`, plus one cross-cutting sweep for the
   irreversible class that builds the type table `PROBES.md` §6 asks for. Fan
   out to subagents when the host provides them. Done when every crate has
   been swept and every type in the irreversible class has a row.
4. **Probe.** Run all seven probes in `PROBES.md` across the whole tree, the
   seventh being the one you invent from the repo's own docs. Done when every
   grep hit per probe is accounted for: a finding at a file:line, or a reason
   it is fine.
5. **Verify.** Re-read every candidate top finding at its file:line. For at
   least one, reproduce it (a failing doctest, a fake-transport harness, a
   `cargo test` of the claim) or trace its trigger to a real caller. Findings
   that fail the re-read land under **Demoted after verification** with the
   reason. Done when every issue in the Summary has survived a re-read.
6. **Summarize.** Strengths, issues in priority order with impact, demoted
   findings, one recommended next action. Priority follows impact, not the
   section a finding came from: a probe finding and a hygiene finding compete
   on consequence.

Findings land in a single message. Review only: fixes come after the user
picks priorities.

## Impact statements

Every issue carries one sentence saying what happens in production if nothing
changes, written as a scenario with an actor and a consequence: "a deploy
during a placement kills the task after the caller got `Accepted`, and the
operator's phone rings for a call the system later marks abandoned." A
category word ("data loss", "security") is not an impact statement. The
sentence is what a manager or a teammate who did not read the code acts on.

## Summary template

```
Strengths
  1. ... (file:line)
  2. ...
  3. ...

Issues (in priority order)
  1. file:line — the finding. Impact: what happens in production if nothing changes.
  2. ...
  3. ...
  (long tail below the top three, same shape, shorter)

Demoted after verification
  - the claim, where it was checked, why it does not hold

Recommended next action
  one concrete first step
```

Three issues carry the weight; the tail follows in the same shape. The
recommended next action is a single concrete step, usually the smallest one
that closes an irreversible-class gap. The user picks from the list and the
work proceeds together from there.

## Review craft

- Suggest the smallest move that improves the situation. A rewrite is a design
  conversation, named as one and left for the user to open.
- Specific findings, no numeric scores.
- Where two findings share a mechanism (three unsupervised tasks, a stale token
  feeding a missing retry), say so: one fix pattern beats three patches, and
  the interaction is often the real P1.
- Name what the review did not exercise: environment-gated tests, live-service
  paths, a crate you ran out of time on.
