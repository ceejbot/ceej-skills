---
name: rust-project-review
description: Use when the user asks for a holistic / wholistic review of a Rust project, "is this codebase healthy", "review the project", "audit before sharing", or at a periodic checkpoint in a personal Rust project
---

# Rust Project Review

A holistic pass over a Rust codebase: first general code-quality concerns that apply to any project, then Rust-specific hygiene. The output should be concrete enough to act on — file references, not vibes.

**Core principle:** every finding cites a file and a reason. "The architecture could be cleaner" is not a finding; "`src/lib.rs:42` re-exports `internal::Inner` which is referenced in three other modules — exposing this as `pub use internal::Inner` would let callers stop reaching through" is.

## How to run

1. Walk Section A in order, noting findings with file references.
2. Walk Section B in order, noting findings with file references.
3. Run `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, `cargo test`, `cargo doc --no-deps` — record what's clean and what isn't.
4. Synthesize the **Summary** at the bottom: top 3 strengths, top 3 issues, recommended next action.

Findings should land in a single message. Don't fix anything in this pass — review only. Fixes come after the user picks priorities.

## Section A — General review

### Architecture
- Are module boundaries sensible? Could a new reader form a mental model from `main.rs` / `lib.rs` alone?
- Does each module own one concept, or has it become a junk drawer?
- Is the data flow obvious — where does input enter, where does output leave?

### README
- Does it answer **what is this**, **who is it for**, **should I use it**?
- For small projects: is there a 5-line example showing the happy path?
- For libraries: is there a one-line `Cargo.toml` snippet and a minimal call site?
- Are non-obvious build/run commands documented?

### Documentation
- Public items have `///` doc comments?
- Doc comments explain *why* and *when*, not just restate the signature?
- Examples in docs that actually compile (`cargo test --doc`)?

### Simplicity & modularity
- Each module / file doing one thing?
- Functions short enough to hold in your head?
- No deep inheritance-style trait hierarchies that could be data?

### Information hiding
- Things that might be swapped (storage backend, transport, serialization, time source) hidden behind a trait or module boundary?
- Or — if the abstraction is premature — is the concrete dependency at least quarantined to one place?

### DRY balance
- No copy-paste of three-plus lines that share a real concept (extract).
- No abstraction used in only one place (inline).
- Three similar lines beats a premature abstraction.

### Parse, don't validate
- Untrusted input converted to a strongly-typed representation at the *edge*?
- Interior code can assume validity — no re-checking the same invariants in every function?
- Are "stringly typed" parameters that could be enums, newtypes, or `NonEmpty<T>`?

### Cleanup
- Dead code (`#[allow(dead_code)]`, commented-out blocks, orphaned files)?
- TODOs older than the project — still relevant or stale?
- Stray `dbg!`, `eprintln!`, debug-only branches?
- Unused dependencies in `Cargo.toml`?

## Section B — Rust-specific review

### Types do work
- Newtype wrappers around primitives where the primitive is meaningful (`UserId(u64)`, `Millis(u64)`, `Email(String)`).
- `NonZeroU32`, `NonZeroUsize`, `NonEmpty<T>`, `OnceCell` / `OnceLock` used where they fit.
- Type-state for objects with phases (`Builder<Unconfigured> → Builder<Ready> → Built`).
- Enums for sum types, not stringly-typed match.

### Errors are typed
- Library code: `thiserror`-style enums per module or per crate; variants describe failure modes, not just sources.
- Binary / top-level: `anyhow` or `eyre` are fine; their `Context` extension is used to add per-call context.
- No `Box<dyn Error>` in public APIs.
- `impl std::error::Error` chains source errors via `#[source]` / `#[from]`.

### No casual panics
- `.unwrap()` and `.expect()` confined to:
  - tests (fine)
  - `main` returning `Result` from `?` (fine)
  - genuine type-system invariants (fine, but with a comment explaining why it can't fail)
- Index access (`arr[i]`) with bounds-checked alternatives where practical (`get`, `chunks`, `windows`).

### Idiomatic shape
- Iterators over manual `for i in 0..n` loops where natural.
- `?` over manual `match` on `Result`/`Option`.
- `if let`, `let else`, `let .. else { return }` where they cut nesting.
- `From` / `Into` impls for ergonomic conversions; `TryFrom` where conversion can fail.
- `Default` impls where there's a sensible default.
- `#[must_use]` on builders, query results, and types where ignoring the value is a bug.
- `Display` and `Debug` thoughtfully chosen — `Debug` derived, `Display` hand-written for user-facing output.

### Clones
- Every `.clone()` and `.to_string()` justified — could it be a borrow, a move, or a `Cow<'_, T>`?
- Particularly suspect: clones inside hot loops, clones of large structs, clones in trait impls.

### Lifetimes
- Elided where the compiler infers correctly.
- Explicit only when the relationship matters (struct holds a borrow; function returns one of multiple input borrows).
- No `'static` where it shouldn't be.

### Module hygiene
- `pub` is intentional, not just "the compiler asked for it".
- `pub(crate)` / `pub(super)` used to scope visibility.
- Re-exports via `pub use` build a clean public façade — callers shouldn't need to know about `internal::deeply::nested::Type`.
- `mod.rs` vs `name.rs + name/` — consistent across the project.

### Async hygiene (if applicable)
- No `block_on` deep in the call stack.
- `Send + 'static` bounds present only where the runtime requires them.
- Cancel-safe across `.await` points (no half-mutated state if the future drops mid-way).
- One async runtime, not three.

### Tooling
- `cargo fmt --check` clean.
- `cargo clippy --all-targets --all-features -- -D warnings` clean. No broad `#[allow(clippy::...)]` without a comment justifying it.
- `cargo test` clean, including doctests.
- `cargo doc --no-deps` warning-free.
- `cargo audit` reviewed (informational; not always blocking for personal projects).

### `Cargo.toml` hygiene
- Features documented (what does each feature gate?).
- `[dev-dependencies]` separate from `[dependencies]`.
- MSRV declared if it matters (`rust-version = "1.74"`).
- No unused dependencies (`cargo machete` or `cargo udeps`).
- Sensible `[profile.release]` settings if performance matters.

### `unsafe`
- Every `unsafe` block has a `// SAFETY:` comment justifying the invariants.
- Safer alternative not available?
- For most personal projects: zero `unsafe` is the target.

## Summary template

End the review with:

```
Strengths
  1. ...
  2. ...
  3. ...

Issues (in priority order)
  1. ... (file:line) — why this matters
  2. ...
  3. ...

Recommended next action
  ...
```

The "Recommended next action" should be a single concrete first step, not a plan. The user picks from the issue list and we work down it together.

## Anti-patterns in the review itself

| Don't | Why |
|---|---|
| Vague findings ("could be cleaner") | Useless without a file reference and a reason. |
| Ten "issues" of equal weight | Forces the user to do the prioritization. Top 3, then a long-tail list if needed. |
| Recommend rewrites | This is a review pass, not a redesign. Suggest the smallest move that improves the situation. |
| Score the project on a numeric scale | Numbers feel rigorous and aren't. Specific findings are more useful. |
| Skip Section A because it's "general" | The general issues are usually the ones that matter most. Don't only nitpick clippy lints. |
