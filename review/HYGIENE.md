# Hygiene: the properties a healthy project holds

Reference consulted during review sweeps. `review-project` applies every
section to each partition of the scope; `review-rust-change` applies the
sections the diff touches. Each property is a question with a yes or no answer
at a file:line. This file holds the properties every language shares; the
language's own live in its lens under `lenses/`, and a sweep applies both.
Behaviour under stress (timeouts, crashes, shutdown, bad config, rendering of
secrets) lives in `PROBES.md`, not here.

## General

### Architecture

- Module boundaries sensible; a new reader can form a mental model from the
  entry point and the top-level module docs alone.
- Each module owns one concept.
- Data flow obvious: where input enters, where output leaves.
- Infrastructure (transport, storage, telemetry) lives behind its own boundary
  or feature gate, so a change there rebuilds only its dependents.

### README

- Answers **what is this**, **who is it for**, **should I use it**.
- Small projects: a five-line happy-path example. Libraries: the one-line
  dependency declaration and a minimal call site.
- Non-obvious build and run commands documented, and they match the justfile
  or CI as it exists today.

### Documentation

- Public items carry doc comments that explain _why_ and _when_.
- Doc examples compile or run, by whatever the lens names as the doc test.
- Agent docs (`CLAUDE.md`, `AGENTS.md`, `docs/agents/`) describe the tree as it
  is: file names, recipes, checks, env vars that exist. ADR numbering is
  contiguous or explained; ADR status matches shipped code; citations point at
  the ADR they mean.

### Simplicity and modularity

- Each module and file does one thing. Functions fit in one head.
- Data where a trait hierarchy would be; no inheritance-shaped trait trees.

### Information hiding

- Things that might be swapped (storage, transport, serialization, clock) sit
  behind a trait or module boundary; a non-injectable wall clock is a finding
  when the tests say they work around it.
- A premature abstraction is replaced by one quarantined concrete dependency.

### DRY balance

- Copy-paste of three-plus lines that share a real concept is extracted.
- An abstraction used once is inlined.
- Three similar lines beat a premature abstraction. The real duplication to
  hunt is the kind that shares a concept: the same acquire-and-map-error
  boilerplate at fifteen sites, two mappers for the same vendor that disagree,
  a helper defined in two modules.

### Parse, don't validate

- Untrusted input is converted to a typed representation at the edge: query
  parameters into the enum the code already has, ids into the id type, labels
  through the constructor that validates them.
- Interior code assumes validity; no re-checking the same invariant per
  function, no serialization round-trip to get a label a method already
  returns.
- Sentinel variants (`Unspecified`) are interpreted the same way at every site.

### Cleanup

- Dead code: suppressed-warning markers, commented-out blocks, orphaned files,
  public items with zero callers, tests that assert nothing.
- TODOs carry context and are still live.
- No stray print-debugging or debug-only branches.
- Every lint suppression carries a justification.
