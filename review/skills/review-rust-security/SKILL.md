---
name: review-rust-security
description: "Use when security-reviewing Rust code or a Rust diff for language- and ecosystem-specific risks: unsafe or FFI invariants, attacker-reachable panics and allocation, deserialization limits, concurrency and cancellation, secret-bearing debug output, cryptographic APIs, and Cargo supply-chain exposure. Pair with review-application-security for networked services or broad threat models. Produces ranked, exploitable-first findings with attacker paths and the smallest fixes."
---

# Rust Security Review

Rust's safe subset removes a large class of memory bugs; it does not remove
attacker-reachable panics, unbounded work, unsafe invariant failures, logic
bugs, or compromised build dependencies.

**Core principle:** trace hostile data to a Rust-specific failure mode. An
`unwrap` is not a security finding merely because it exists. It becomes one
when a modeled attacker can make it fail repeatedly and affect availability or
integrity.

## Boundary with application security

This skill owns Rust implementation and Cargo ecosystem risks. It does not
repeat broad injection, authorization, tenancy, PHI, or protocol findings;
`review-application-security` owns those. For a Rust service review, share its
threat model, apply both lenses, and return one deduplicated report.

For a Rust library or crate with no service boundary, establish who controls
its public inputs and what callers rely on, then apply this skill alone. For a
diff, capture intent and restrict findings to risks introduced or materially
worsened by the change. Read the full changed files and their nearby tests.

Review only. Do not implement fixes unless separately asked. Redact any secret
or sensitive value found in source, logs, fixtures, or generated output.

## Rust security lens

### Panics, arithmetic, and allocation

- Trace attacker-controlled values to `.unwrap()`, `.expect()`, indexing,
  assertions, `unreachable!`, integer arithmetic, and infallible conversions.
- Treat a panic as denial of service only when the attacker can reach and
  repeat it in a long-running process (CWE-248, CWE-400).
- Check attacker-influenced lengths before `Vec::with_capacity`, `read_to_end`,
  collection growth, decompression, and buffering. Use bounded reads and
  checked or saturating arithmetic where semantics permit.
- Watch release/debug differences in overflow and any cast that truncates a
  size, offset, duration, or identifier.

### Unsafe code and FFI

- Inventory `unsafe`, `unsafe fn`, `extern` blocks, raw pointers, `transmute`,
  manual allocation, and unchecked UTF-8 or indexing.
- A `// SAFETY:` comment is a claim to verify, not proof. Follow hostile input
  through every invariant: validity, alignment, provenance, aliasing,
  initialization, lifetime, thread safety, and unwind behavior.
- At FFI boundaries, validate lengths, nullability, ownership, callback
  lifetime, error conventions, and whether a foreign panic/exception can cross
  the boundary.
- Rank unreachable unsafe as hardening, below unsafe that consumes attacker
  bytes or crosses a live boundary.

### Parsing and deserialization

- Bound serde nesting, collection lengths, strings/bytes, decompression, and
  format-specific work before allocating from untrusted input.
- Check custom `Deserialize`, visitors, `deserialize_any`, untagged enums, and
  unchecked conversions for ambiguous or unexpectedly expensive inputs.
- Avoid parsing untrusted bytes by first allocating the size they claim. Fuzz
  parsers and state machines that sit on a real trust boundary when the
  project has a fuzzing setup.

### Async and concurrency

- Look for unbounded task spawning, channels, retry loops, and blocking work on
  an async runtime.
- Check locks held across `.await`, lock-order cycles, cancellation that leaves
  half-mutated state, and detached tasks that outlive authorization or tenant
  context.
- Verify `Send + Sync` assumptions around interior mutability and unsafe impls;
  prefer compiler-enforced ownership over comments and global mutable state.

### Secrets and cryptographic APIs

- Secret-bearing types should not derive or expose unsafe `Debug`, `Display`,
  serialization, or error output. Use redaction wrappers and `zeroize` only
  where the threat model justifies memory clearing.
- Use maintained Rust crypto/TLS crates and their high-level APIs. Check CSPRNG
  selection, nonce uniqueness, constant-time verification, key parsing, and
  certificate/hostname verification.
- Treat `dangerous_configuration`, custom verifiers, or disabled TLS checks as
  findings when reachable in a production configuration.

### Cargo and build-time supply chain

- Review `Cargo.lock` churn, new registries/git sources, similarly named
  crates, feature expansion, and unexpected duplicate security-sensitive
  dependencies.
- Treat `build.rs`, proc macros, and native build dependencies as code that
  executes on developer and CI machines (CWE-1357).
- Confirm dependencies are maintained and advisories are understood; determine
  whether an advisory is reachable and whether it affects runtime, build, or
  dev-only code.

## Tooling

Run only what is relevant and available, scoped to touched crates where
possible:

- `cargo audit` for RUSTSEC advisories.
- `cargo deny check` for advisories, bans, licenses, and sources when configured.
- `cargo geiger` for unsafe surface and `cargo vet` for supply-chain policy when
  already available.
- Existing fuzz, Miri, sanitizer, or loom tests when they cover the reachable
  boundary under review.

Do not install missing tools without approval. State what was not run and why.
Tool output becomes a finding only after reachability and impact are assessed.

## Findings and severity

Every finding cites a file and line, names the attacker-controlled input or
build-time capability, describes the Rust failure mode, gives the smallest
fix, and says how to verify it.

- **Critical:** exploitable memory unsafety/RCE or equivalent catastrophic
  compromise under the modeled attacker.
- **High:** serious attacker-reachable availability, integrity, secret, or
  build compromise with a meaningful precondition.
- **Medium:** constrained exploitability or significant defense-in-depth.
- **Low / Hardening:** no concrete attacker path today.

Attach a CWE where it clarifies the class. CVSS is optional on Critical/High;
never invent an overall security score.

## Output

```markdown
## Scope & threat model
- Rust scope: <crate / diff / boundary>
- Hostile inputs or build-time capabilities: ...
- Companion application review: <used / not needed / not requested>

## What's solid
<One or two sentences on Rust controls that hold.>

## Findings (ranked, exploitable-first)
1. `<file:line>` — <Rust-specific vulnerability> (CWE-NNN).
   **Attack path:** ... **Fix:** ... **Verify:** ...

## Tooling
- `cargo audit`: ...
- `cargo deny`: ...
- other relevant checks: ...

## Verdict
<Rust-specific readiness under the modeled inputs.>

## Recommended next action
<One concrete step, or none.>
```

## Project-specific posture

Check the repository's agent instructions (`AGENTS.md` or `CLAUDE.md`) and
`docs/review-notes.md` for lint, unsafe, dependency, MSRV, and testing rules.

## Anti-patterns

- Do not report every `unwrap` or unsafe block; prove attacker reachability.
- Do not repeat application-level findings from the companion review.
- Do not treat every advisory as runtime-exploitable; check reachability and
  dependency role.
- Do not recommend replacing a crate or rewriting unsafe code when a narrow
  bound, invariant check, or version update closes the path.
- Do not manufacture findings when Rust's types and bounds already make the
  modeled path impossible.
