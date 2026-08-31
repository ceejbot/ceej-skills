# Engineering Lexicon

The canonical vocabulary for documents with two readers: the agent that runs
them and the human who maintains them. A term earns its place by recruiting
both readers' priors; a term that anchors the model but trips the maintainer
gets swapped for one from the maintainer's 35 years of working vocabulary.

Maintained the way `domain-modeling` maintains a `CONTEXT.md`: opinionated
canonical terms, tight definitions, `_Avoid_` lists. When a jarring term
turns up in a document being written or adapted, resolve it here first, then
use the resolution everywhere.

## Language

**Module**:
The unit of code with an interface and an implementation behind it. The most
important concept programmers work with; when in doubt, speak in modules and
their boundaries.

**Interface** / **boundary**:
The line where one implementation can be swapped for another, and where tests
attach. "Module boundary" already carries everything the borrowed term tried
to say.
_Avoid_: seam

**Check** / **step**:
A required verification before work proceeds. A pipeline has steps; a step
has checks; a failed check stops the work.
_Avoid_: gate, quality gate

**Decision** / **ratification decision**:
The point where a human approves or rejects a proposed bundle of changes.
Checks verify; decisions choose.
_Avoid_: gate, approval gate

**Integrate**:
Bring reviewed changes or amendment text into the authoritative document or
line of work.
_Avoid_: fold, fold in

**Golden**:
A committed expected artifact that tests compare against: golden vector,
golden file, golden test. Reserve "pin" for dependency and toolchain
versions — its package-management sense.
_Avoid_: pinned test vector, pinned constant

**Case**:
One path through a multi-path verification or test matrix.
_Avoid_: leg

**Wrap-up**:
The finishing work that closes a stage or arc: final review, docs, loose
ends.
_Avoid_: closeout

**Re-verify**:
Check work or claims against the authoritative source again. "Re-ground"
points elsewhere in both electrical engineering and plain English.
_Avoid_: re-ground, re-grounding

## Shared vocabulary

Confirmed shared between both readers, no swap needed: land, arc, lane,
latch, wire up, ship, spike, fan out, polish, harden.
