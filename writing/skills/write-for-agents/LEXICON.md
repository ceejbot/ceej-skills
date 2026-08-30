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
