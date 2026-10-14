# Hygiene: the properties a healthy Rust project holds

Reference consulted during review sweeps. `review-rust-project` applies every
section to each crate; `review-rust-change` applies the sections the diff
touches. Each property is a question with a yes or no answer at a file:line.
Behaviour under stress (timeouts, crashes, shutdown, bad config, rendering of
secrets) lives in `PROBES.md`, not here.

## General

### Architecture

- Module boundaries sensible; a new reader can form a mental model from
  `main.rs` / `lib.rs` alone, and the crate doc describes what the crate holds.
- Each module owns one concept.
- Data flow obvious: where input enters, where output leaves.
- Infrastructure (transport, storage, telemetry) lives behind its own boundary
  or feature gate, so a change there rebuilds only its dependents.

### README

- Answers **what is this**, **who is it for**, **should I use it**.
- Small projects: a five-line happy-path example. Libraries: a one-line
  `Cargo.toml` snippet and a minimal call site.
- Non-obvious build and run commands documented, and they match the justfile
  or CI as it exists today.

### Documentation

- Public items carry `///` docs that explain _why_ and _when_.
- Doc examples compile (`cargo test --doc`).
- Agent docs (`CLAUDE.md`, `AGENTS.md`, `docs/agents/`) describe the tree as it
  is: file names, recipes, gates, env vars that exist. ADR numbering is
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
  a macro defined in two crates.

### Parse, don't validate

- Untrusted input is converted to a strongly-typed representation at the edge:
  query parameters into the enum that already derives `Deserialize`, ids into
  `Uuid`, labels through the `const fn` the type already has.
- Interior code assumes validity; no re-checking the same invariant per
  function, no serde round-trip to get a label a method already returns.
- Sentinel variants (`Unspecified`) are interpreted the same way at every site.

### Cleanup

- Dead code: `#[allow(dead_code)]`, commented-out blocks, orphaned files,
  `pub` items with zero callers, tests that assert nothing.
- TODOs carry context and are still live.
- No stray `dbg!`, `eprintln!`, debug-only branches.
- Every `#[allow]` carries a justification.

## Rust-specific

### Types do work

- Newtypes where the primitive is meaningful (`UserId(u64)`, `Millis(u64)`,
  `Email(String)`), and the one payload left as a bare `String` is a finding.
- `NonZeroU32`, `NonZeroUsize`, `NonEmpty<T>`, `OnceLock` where they fit.
- Type-state for objects with phases.
- Enums for sum types; no stringly-typed match.

### Errors are typed

- Library code: `thiserror`-style enums whose variants describe failure modes,
  not sources; `#[source]` / `#[from]` chain the cause.
- Binaries: `anyhow` or `miette` with `.context()` per call.
- No `Box<dyn Error>` in public APIs.
- Transient versus permanent classification matches the error's documentation
  and covers every variant of the SDK error it wraps.

### No casual panics

- `.unwrap()` and `.expect()` confined to tests, `main` returning `Result`, and
  genuine invariants with a comment saying why they hold.
- Index access uses `get`, `chunks`, `windows` where practical.
- In a server, an attacker-reachable panic is an availability bug.

### Idiomatic shape

- Iterators over index loops; `?` over manual `match`; `if let` and `let else`
  to cut nesting.
- `From` / `Into` / `TryFrom` for conversions; `Default` where sensible.
- `#[must_use]` on builders, query results, and types where ignoring the value
  is a bug.
- `Debug` derived except where the type carries a secret (see `PROBES.md` §6);
  `Display` hand-written for user-facing output.

### Clones

- Every `.clone()` and `.to_string()` justified: borrow, move, or `Cow` first.
- Suspect: clones in hot loops, of large structs, in trait impls, of `Copy`
  values into `String` for a log line.

### Lifetimes

- Elided where the compiler infers; explicit only when the relationship
  matters; no `'static` to silence the borrow checker.

### Module hygiene

- `pub` is intentional. `pub(crate)` / `pub(super)` scope the rest. A
  crate-wide `must_use_candidate` allow or a semver-lint exemption is usually
  the shadow of an over-wide `pub` surface.
- Re-exports build a clean façade.
- `mod.rs` versus `name.rs` consistent.
- Inline test modules over ~1000 lines move to a sibling `tests.rs`.

### Async hygiene

- No `block_on` deep in the call stack; one runtime.
- `Send + 'static` only where the runtime requires.
- `select!` biased toward shutdown. Lifetimes, cancellation, and supervision
  are probed, not checked: `PROBES.md` §1 and §3.

### `unsafe`

- Every block carries a `// SAFETY:` comment. A safer alternative was weighed.
  Zero `unsafe` is the target for most projects.

### `Cargo.toml`

- Features documented. `[dev-dependencies]` separate. MSRV declared when it
  matters. No unused dependencies (`cargo machete`).
- Workspace dependencies used; a crate that pins its own version of a
  workspace dep is a finding. The same dependency block repeated verbatim in
  several manifests is a finding.
- HTTP clients built with a timeout.

### Security and supply chain

- Secrets: none hardcoded, no committed `.env`, none reachable through a
  derived `Debug` (see `PROBES.md` §6).
- Untrusted input parsed at a typed edge; no `unsafe` transmute of
  attacker-controlled bytes.
- `cargo audit` and `cargo deny check` reviewed; `Cargo.lock` churn eyeballed
  for unexpected transitive deps and typosquats.
- The ignore list in `deny.toml` or `audit.toml` describes each advisory
  accurately (a vulnerability is not "unmaintained").

> For a focused security pass (threat model, injection, authz, crypto, PHI
> handling) use `review-application-security`, with `review-rust-security` for
> the Rust overlay.

### Dependency-audit output shape

When `cargo audit` or `cargo deny` surface anything, emit a table so the fix
path is obvious. "Reachable?" is the column that matters: a dev-only or
unreached advisory ranks below one on a live path.

```
| Advisory / issue  | Crate @ version | Severity | Reachable?             | Fix                        |
|-------------------|-----------------|----------|------------------------|----------------------------|
| RUSTSEC-YYYY-NNNN | foo @ 1.2.3     | High     | yes, live path <loc>   | bump to 1.2.4              |
| license: GPL-3.0  | bar @ 0.4       |          | transitive via baz     | replace baz / allow in deny.toml |
```
