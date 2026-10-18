# Lens: Rust

The Rust branch of `review-project`. `PROBES.md` holds the questions; this
file holds where to point them in a Rust tree, what the toolchain already
proves, and the properties a healthy Rust project holds beyond the General
section of `HYGIENE.md`.

## Detect

`Cargo.toml` at the root, or a `[workspace]` manifest with `members`. Dialect
notes that change the instances below: the async runtime (`tokio` almost
always; `async-std` or `smol` rarely), and whether the project is a service
(HTTP or gRPC surface) or a library (no §3 shutdown story, but `#[must_use]`
and doc examples matter more).

## Evidence model

The compiler is the strongest witness in this plugin. Lean on it: a property
the type system already holds needs no test, and the review's attention goes
to what the compiler cannot see.

| Property                                  | Witness                                        | Unwitnessed looks like                                   |
| ----------------------------------------- | ---------------------------------------------- | -------------------------------------------------------- |
| Exhaustive handling of a sum type         | compiler (`match`)                             | a `_ =>` arm on an enum the code owns                    |
| Absence of null and use-after-free        | compiler (ownership, `Option`)                 | n/a                                                      |
| Thread safety of shared state             | compiler (`Send`, `Sync`)                      | `unsafe impl Send`                                       |
| Errors are handled                        | compiler (`#[must_use]` on `Result`)           | `let _ =` on a `Result`; `.ok()` with no comment         |
| Input shape at an edge                    | a newtype or enum with `TryFrom`/`Deserialize` | a bare `String` or `serde_json::Value` past the edge     |
| Cancellation and shutdown behaviour       | a test with a fake transport or a paused clock | none; probe §1 and §3 carry the question                 |
| Secret never rendered                     | a redaction test on the type's `Debug`         | `derive(Debug)` on the type, and no test                 |
| Panic-freedom on attacker input           | fuzz target or property test                   | `unwrap()` on parsed input                               |
| Doc examples still compile                | `cargo test --doc`                             | a nextest-only recipe                                    |

**Where the witness question is asked:** at §6, and wherever untrusted
input crosses into the code: a response body in §4, a config parse in §5,
the edge *Types do work* names. Elsewhere the compiler answers it, and the
row's "unwitnessed" shape is the finding instead.

## Partition unit

The crate group: binaries, their direct library crates, shared libraries,
test and bench crates. A workspace of one crate partitions by top-level
module.

## Tooling checks

Run through the project's own recipes first, then the gaps the recipes leave:

- `cargo fmt --check`.
- `cargo clippy --all-targets -- -D warnings`. A new `#[allow(clippy::...)]`
  carries a comment saying why.
- `cargo test`, then `cargo test --doc` on its own: nextest-based recipes skip
  doctests, so a green `just test` says nothing about them.
- `cargo doc --no-deps`, warning-free.
- `cargo deny check` and `cargo audit`; `cargo machete` for unused deps.
- `actionlint` and `zizmor` when the repo carries their config.

## Probe instances

### §1 Bounds

`timeout(`, `timeout_at(`, `deadline`, `budget`, pool sizes
(`max_connections`, `max_size`), `retry`, `max_attempts`,
`message.timeout.ms` and its cousins in client config; `reqwest::Client`
builders (one without `.timeout()` is a bound of infinity).

Rust consequence: `tokio::time::timeout` **drops the future**. Name what that
future was in the middle of: a vendor call that may have committed, a write
half-done, a lock still held by a guard that will now drop early.

### §2 Dual writes

A `commit(` or `.execute(` followed by `send`, `publish`, `emit`,
`put_object`, or a file write; any column, flag, or label that records
"emitted", "sent", "published", "announced"; a metrics counter incremented
beside a publish.

### §3 Supervision

`tokio::spawn`, `spawn_blocking`, `JoinSet`, `TaskTracker`, `select!` arms
on a shutdown token, anything with a `drain()` or `wait()`.

Rust consequence: a `JoinHandle` that is dropped detaches the task; a join
that matches only `JoinError` discards `Ok(Err(_))`; a `select!` without
`biased;` may serve one more request after shutdown fired.

### §4 Boundary symmetry

Every client for one vendor or service; `invalidate`, `refresh`, `re-mint`,
backoff; 401, 403, 429 handling; status-to-error mappers (`impl From<StatusCode>`,
`match resp.status()`).

### §5 Startup truth

`env::var`, config structs, `.parse().ok()`, `unwrap_or(default)`,
`unwrap_or_default()` on anything that reaches a loop bound, a pool size, or a
feature switch; `#[serde(default)]` on a config field.

### §6 The irreversible class

Every type that carries the project's irreversible material: tokens, secrets,
transcripts, addresses, names, account numbers, raw request and response
bodies. Rendering sites: a derived `Debug`, a `Display`, `{e:?}` on an error
path, an `anyhow` wrapper around a response body, a log line with `{err}`,
`tracing::instrument` without `skip`. Passing sites: a bare `String` payload
accepts any `&str`, including a storage key or a metric label.

### §7 Promises

README guarantees, runbook steps and the observations they expect, alert
annotations, doc comments on `pub` items, ADRs and closed issues. Setup
artifacts: `docs/**/*.sql`, `migrations/`, `docker-compose.yml`, a Helm
chart; read each against the SQL and config the code actually requires.
Grep the docs for `always`, `never`, `within`, `guarantee`, and the
service's outcome words (`fails open`, `sheds`, `retries`).

## Hygiene

Rust-specific properties, each a yes-or-no question at a file:line, applied
on top of `HYGIENE.md` General.

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

## Security

For a focused security pass (threat model, injection, authz, crypto, PHI
handling) use `review-application-security`, with `review-rust-security` for
the Rust overlay: `unsafe` and FFI invariants, attacker-reachable panics,
deserialization limits, Cargo supply chain.
