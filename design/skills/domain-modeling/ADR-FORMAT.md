# ADR Format

ADRs live in `docs/adr/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Scan `docs/adr/` for the highest existing number and increment by one. Create the directory lazily: only when the first ADR is needed.

The bar for _whether_ a decision earns an ADR lives in [SKILL.md](./SKILL.md); this file is the format.

## Template

[MADR 4.0 minimal](https://github.com/adr/madr/blob/4.0.0/template/adr-template-minimal.md):

```md
# {short title, representative of solved problem and found solution}

## Context and Problem Statement

{Describe the context and problem statement, e.g., in free form using two to three sentences or in the form of an illustrative story. You may want to articulate the problem in form of a question and add links to collaboration boards or issue management systems.}

## Considered Options

- {title of option 1}
- {title of option 2}
- {title of option 3}

## Decision Outcome

Chosen option: "{title of option 1}", because {justification}.

### Consequences

- Good, because {positive consequence}
- Bad, because {negative consequence}
```

`Consequences` is optional: include it only when non-obvious downstream effects need calling out. An ADR can be short — the value is in recording _that_ a decision was made and _why_, not in filling out sections. When decisions get revisited, add `status` frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`).

## What qualifies

- **Architectural shape.** "We're using a monorepo." "The write model is
  event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing
  communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth
  provider, deployment target. Not every library: just the ones that would
  take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer
  context; other contexts reference it by ID only." The explicit no-s are as
  valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL
  instead of an ORM because X." Anything where a reasonable reader would
  assume the opposite. These stop the next engineer from "fixing" something
  that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of
  compliance requirements." "Response times must be under 200ms because of
  the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you
  considered GraphQL and picked REST for subtle reasons, record it;
  otherwise someone will suggest GraphQL again in six months.
