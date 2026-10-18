# Scoping a named system

Reached from `SKILL.md` Orient when the user named a system inside a larger
project: "the entities system", "the database access layer". A whole-project
review needs none of this.

## Resolve the name

Resolve the name to modules through the repo's own doc for it: `docs/`,
`CLAUDE.md` or `AGENTS.md`, ADRs, a design doc that names the system and
lists its modules and key classes. Without such a doc, grep the system's word
across module names, package paths, and class names. Done when scope is a
list of modules with their entry points and the doc that describes the
system.

## Judge the boundary from outside

§4 Boundary symmetry and §7 Promises reach one hop out of the scope to its
callers: a client's symmetry and a system's promises are judged from outside
it. Read the callers, and name under "what the review did not exercise" the
ones you did not.

## Findings outside the scope

A finding in a module outside the scope is reported in one line under the
Issues tail with "out of scope" and left for that system's review.
