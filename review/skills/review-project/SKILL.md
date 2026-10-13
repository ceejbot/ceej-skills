---
name: review-project
description: Use when the user asks for a holistic review of a project or of one internal system inside a monorepo — "review the project", "is this codebase healthy", "find bugs in the entities system", "audit the database access layer", "audit before sharing", or a periodic checkpoint — in Rust, Scala, Go, Python, or TypeScript. Scopes by named system, loads the language's lens, and reports verified findings ranked by production impact.
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
language can offer. In Rust the compiler witnesses most of them; in Python
and TypeScript the type checker is advisory and the witness for a boundary
property is a runtime validator or a test. The standard does not drop for a
dynamic language; the location of the evidence moves, and an instance with
no witness in the irreversible class or at a parse boundary is a finding.

## How to run

1. **Orient.** Four sub-steps, in order.
   - **Detect.** Match the repo against each lens's *Detect* section and load
     `../../lenses/<lang>.md`. Done when you can state in one sentence the
     language, the dialect the lens asks about (effect system or plain JVM,
     asyncio or threads, Node or browser), and the build system. A monorepo
     that mixes languages gets one sentence per language in scope.
   - **Scope.** The whole project, or a **named system** the user gave:
     "the entities system", "the database access layer". Resolve the name to
     modules through the repo's own doc for it: `docs/`, `CLAUDE.md` or
     `AGENTS.md`, ADRs, a design doc that names the system and lists its
     modules and key classes. Without such a doc, grep the system's word
     across module names, package paths, and class names. Done when scope
     is a list of modules with their entry points and the doc that describes
     the system, or the sentence "whole project, N modules".
   - **Read the house rules.** The repo's `CLAUDE.md` / `AGENTS.md`, its ADRs
     or design docs, its justfile or CI config. Done when you can state in one
     sentence each: the module map and entry points of the scope, which recipe
     runs the tests and what that recipe skips, and what the project itself
     calls irreversible (PHI, credentials, money, audit).
   - **Actors, deployment, production values.** Who calls it, who operates
     it, who gets paged by it, who deploys it. Whether it serves live traffic:
     telemetry when you can reach it, otherwise ask the user, or record
     "unknown". The timeouts, pool sizes, and log level, read from the chart
     or deployment config.

   Priority depends on all of these.
2. **Tooling.** Run the gates the lens's *Tooling gates* section names,
   through the project's own recipes first and then the gaps the recipes
   leave (the doctest a nextest recipe skips, the race detector a plain `go
   test` skips, the type checker a Python project runs non-strict). Scope
   them to the modules in scope. Done when every gate has a result in a table,
   or a "not run: reason" line.
3. **Sweep.** Partition the scope by the lens's *Partition unit* and sweep
   each partition against every section of `HYGIENE.md` General and the
   lens's *Hygiene* section, plus one cross-cutting sweep for the irreversible
   class that builds the type table `PROBES.md` §6 asks for, using the lens's
   §6 rendering sites. Fan out to subagents when the host provides them. Done
   when every partition has been swept and every type in the irreversible
   class has a row.
4. **Probe.** Run all eight probes in `PROBES.md` across the scope, taking
   each probe's instances from the lens's matching § and asking the witness
   question of each. §4 Boundary symmetry and §7 Promises reach one hop out
   of the scope to its callers: a client's symmetry and a system's promises
   are judged from outside it. The eighth probe is the one you invent from
   the repo's own docs; the lens may name a candidate. Done when every probe
   has a ledger line and every instance is accounted for: a finding at a
   file:line, or a reason it is fine.
5. **Verify.** Re-read every candidate top finding at its file:line. For at
   least one, reproduce it with the lens's test runner (a failing test, a fake
   transport, a paused clock) or trace its trigger to a real caller.
   - Reproduce under the production values from Orient, and state them in the
     finding. A repro under other values proves the code, not the consequence.
   - For a claim that something is broken, check whether it has run since:
     CI history, release history, telemetry.
   - A finding that was traced but not run says so in its impact line.

   Findings that fail the re-read land under **Demoted after verification**,
   with the reason. Done when every issue in the Summary has survived a
   re-read.
6. **Summarize.** Strengths, issues in priority order with impact, witness
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
  paths, a module you ran out of time on, the hop-out callers you did not
  read.
- In a monorepo, a finding in a module outside the scope is reported in one
  line under Issues' tail with "out of scope" and left for that system's
  review.
