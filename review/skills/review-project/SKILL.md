---
name: review-project
description: Use when the user asks for a holistic review of a Scala, Go, Python, or TypeScript project, or of one internal system inside a monorepo — "review the project", "is this codebase healthy", "find bugs in the entities system", "audit the database access layer", "audit before sharing", or a periodic checkpoint. In a Rust project use review-rust-project instead. Scopes by named system, loads the language's lens, and reports verified findings ranked by production impact.
---

# Project Review

A read-only pass over a project, or over one named system inside a larger
one. Three kinds of material feed it, all reached relative to this
`SKILL.md`: the hygiene properties every project holds, in
[`HYGIENE.md`](../../HYGIENE.md); the probes that find what lints cannot see,
in [`PROBES.md`](../../PROBES.md); and the **lens** for the language under
review, in [`lenses/`](../../lenses/), which says where the probes' instances
live, what the toolchain already proves, and which properties the language
adds. The output is a ranked set of findings, each at a file:line, each with
an impact statement, each verified before it is ranked.

**Core principle:** every finding cites a file and a reason. "The architecture
could be cleaner" is not a finding; "`src/lib.rs:42` re-exports
`internal::Inner`, which three other modules reach through; a `pub use` there
lets callers stop reaching" is.

**The bar is one bar, read through the lens.** Every property the review
cares about needs a witness: a type, a lint, or a test that fails when the
property stops holding. The lens's evidence model says which witnesses the
language can offer and where the review asks for one: of every instance where
the type checker is advisory, at the irreversible class and the parse
boundaries where the compiler is the witness. The standard does not drop for
a dynamic language; the location of the evidence moves, and an instance with
no witness in the irreversible class or at a parse boundary is a finding.

## How to run

1. **Orient.** Match the repo against each lens's *Detect* section and load
   `../../lenses/<lang>.md`. Read the repo's `CLAUDE.md` / `AGENTS.md`, its
   ADRs or design docs, and its justfile or CI config. Done when you can
   state in one sentence each: the language, the dialect the lens asks about
   (effect system or plain JVM, asyncio or threads, Node or browser), and the
   build system; the module map and entry points; which recipe runs the tests
   and what that recipe skips; and what the project itself calls irreversible
   (PHI, credentials, money, audit). A monorepo that mixes languages gets one
   language sentence per language in scope. Then write down four more things:
   - **Scope**: "whole project, N modules", unless the user named a system
     inside it ("the entities system", "the database access layer"); a named
     system resolves to modules through [`SCOPING.md`](./SCOPING.md).
   - **Actors**: who calls it, who operates it, who gets paged by it, who
     deploys it.
   - **Deployment state**: whether it serves live traffic, and which version
     each environment runs, from a build-info metric or the deployed chart's
     image tag. Telemetry when you can reach it; otherwise ask the user, or
     record "unknown". A checkout at HEAD is not what production runs.
   - **Production values**: the timeouts, pool sizes, and log level, read
     from the chart or deployment config.

   Priority depends on all of these.
2. **Tooling.** Seed the results table before running anything, one row per
   check, from two sources: every checking recipe in the justfile, Makefile,
   or CI config (format, lint, test, audit, docs, whatever the project runs on
   itself), and the lens's *Tooling checks* list. Then run each row: the
   project's own recipes first, then the gaps the recipes leave (the doctest a
   nextest recipe skips, the race detector a plain `go test` skips, the type
   checker a Python project runs non-strict). Scope them to the modules in
   scope. Done when every row has a result or a "not run: reason" line; a
   table that lists only the checks you chose to run is not done.
3. **Sweep.** Partition the scope by the lens's *Partition unit* and sweep
   each partition against every section of `HYGIENE.md` General and the
   lens's *Hygiene* section, plus one cross-cutting sweep for the irreversible
   class that builds the type table `PROBES.md` §6 asks for, using the lens's
   §6 rendering sites. Fan out to subagents when the host provides them. Done
   when every partition has been swept and every type in the irreversible
   class has a row.
4. **Compose the probe sheet.** Write one scratch file with eight sections.
   For each of the seven probes in `PROBES.md`, copy its questions and finding
   shape, then the lens's matching § beneath them: the grep hints and the
   consequence the language attaches to the mechanism. The eighth is the one
   you invent from the repo's own docs; `PROBES.md` §8 says how, and the lens
   may name a candidate. Done when every section carries grep hints you can
   run as written.
5. **Probe.** Run all eight probes from the sheet across the scope, asking
   the witness question where the lens's evidence model says to. Done when
   every probe has a ledger line and every instance is accounted for: a
   finding at a file:line, or a reason it is fine.
6. **Verify.** Re-read every candidate top finding at its file:line. For at
   least one, reproduce it with the lens's test runner (a failing test, a fake
   transport, a paused clock) or trace its trigger to a real caller.
   - Reproduce under the production values from Orient, and state them in the
     finding. A repro under other values proves the code, not the consequence.
   - For a claim that something is broken, check whether it has run since,
     in three places: CI and release history; the alert state series
     (`ALERTS` or its equivalent) for every rule in scope over the last week,
     with the events behind each firing; and the log lines the runbooks tell
     an operator to search for. One metric query is not telemetry.
   - A finding that was traced but not run says so in its impact line.

   Findings that fail the re-read land under **Demoted after verification**,
   with the reason. Done when every issue in the Summary has survived a
   re-read.
7. **Summarize.** Strengths, issues in priority order with impact, witness
   gaps, demoted findings, one recommended next action. Priority follows
   impact on the actors Orient named, given the deployment state, not the
   section a finding came from: a probe finding, a hygiene finding, and a
   witness gap compete on consequence.

Findings land in a single message. Review only: fixes come after the user
picks priorities.

## Impact statements

Every issue carries one sentence saying what happens in production if nothing
changes, written as a scenario with an actor from Orient's list and a
consequence: "a deploy during a placement kills the task after the caller got
`Accepted`, and the operator's phone rings for a call the system later marks
abandoned." A category word ("data loss", "security") is not an impact
statement. The sentence is what a manager or a teammate who did not read the
code acts on.

## Summary template

```
Scope
  language, dialect, build system; whole project or the named system and
  the modules it resolved to, with the doc that named them

Deployment
  live callers and traffic, "not launched", or "unknown: reason"

Strengths
  1. ... (file:line)
  2. ...
  3. ...

Issues (in priority order)
  1. file:line — the finding. Impact: what happens in production if nothing changes.
  2. ...
  3. ...
  (long tail below the top three, same shape, shorter)

Witness gaps
  irreversible-class and parse-boundary instances with no type, lint, or
  test witness: file:line — the property — what would witness it

Probe ledger
  §1 Bounds: N instances, N accounted, k findings
  ... one line per probe, through §8 <its name>

Actors
  one line each: the issues that reach them, or "none" and what was checked

Demoted after verification
  - the claim, where it was checked, why it does not hold

Recommended next action
  one concrete first step
```

Three issues carry the weight; the tail follows in the same shape. The
recommended next action is a single concrete step, usually the smallest one
that closes an irreversible-class gap or witnesses one. The user picks from
the list and the work proceeds together from there.

## Review craft

- Suggest the smallest move that improves the situation. A rewrite is a design
  conversation, named as one and left for the user to open.
- Specific findings, no numeric scores.
- Where two findings share a mechanism (three unsupervised tasks, a stale token
  feeding a missing retry), say so: one fix pattern beats three patches, and
  the interaction is often the real P1.
- Name what the review did not exercise: environment-gated tests, live-service
  paths, a module you ran out of time on.
