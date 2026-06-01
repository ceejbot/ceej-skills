---
name: rust-security-review
description: Use when reviewing code for security — threat-modeling a change or service, auditing untrusted-input handling, secrets or PHI exposure, injection, auth, crypto, panics-as-DoS, or supply-chain risk. Triggers on "security review", "is this safe to expose", "threat model this", "check for vulnerabilities", "audit before it takes untrusted input", "HIPAA review". Rust-shaped but applies to any language. Produces ranked, exploitable-first findings with an attacker path, a CWE reference, and the smallest fix.
---

# Rust Security Review

The security counterpart to `rust-project-review` and `rust-change-review`. Same evidence
discipline — file, line, smallest fix — but the lens is "what can an attacker do?" rather than
"is this clean code?". Can run over a whole service or a single diff; the threat surface scales
to the scope.

**Core principle:** every finding needs an **attacker path**, not a theory. "Uses `format!` in a
query" is not a finding; "`src/repo.rs:88` interpolates the user-supplied `tenant` into the SQL
string via `format!`, and `tenant` arrives unvalidated from the `/search` query param
(`handlers.rs:31`) — SQL injection, CWE-89" is. A vulnerability nobody can reach is, at most, a
defense-in-depth note — mark it as such and rank it below anything exploitable.

Security review drowns in theoretical findings if you let it. The job is to find the handful of
things an attacker can actually do, ranked, with the smallest fix for each — not to recite the
OWASP list.

## Determining scope

Establish what's under review and, crucially, **where the trust boundary sits**:

- **Whole service / project** — the attack surface is every place untrusted data enters: network
  handlers, file/blob reads, CLI args, env, message-queue payloads, deserialization, FFI.
- **Scoped diff / PR** — `gh pr diff` / `git diff`. Ask the narrower question: does this change
  *add* attacker-reachable surface, *weaken* an existing control, or *handle* a new asset (PHI,
  secrets, tokens)? A diff that touches none of those is a short review — say so.
- **Capture intent** (commit/PR text or the service's purpose) and **read the full files**, not
  just hunks — a control might live three functions away from the change.

## How to run

1. **Build the threat model first** (below). You cannot rank a finding without it.
2. Walk the **Security lens**, but only where the threat model says data is attacker-reachable.
3. Run the **Tooling** (supply-chain + unsafe surface). Failures are findings, not footnotes.
4. Synthesize a small, ranked list with the **Output template** — exploitable-first.

Review only. Don't fix in this pass. And **never paste a real secret or real PHI into the
findings** — reference the location, redact the value.

## Step 1 — Threat model (do this before the lens)

Four questions, answered explicitly at the top of the output:

- **Trust boundaries** — where does untrusted data cross into trusted code? (HTTP/gRPC handlers,
  Kafka/queue consumers, file/S3 reads, CLI/env, FFI, deserialization.)
- **Assets** — what's worth stealing or breaking here? Name them: **PHI/PII**, secrets/keys,
  auth tokens, money, availability, integrity of an audit record.
- **Attacker capabilities** — unauthenticated remote? Authenticated-but-other-tenant? A
  malicious upstream service? A poisoned dependency at build time?
- **Existing controls** — what already defends each boundary (typed parsing at the edge, authz
  middleware, parameterized queries, KMS)? A finding is "this control is missing/weak *here*".

## Step 2 — Security lens (only where the threat model points)

### Untrusted input & injection
- **Parse, don't validate, as security** — untrusted bytes converted to a typed representation at
  the edge, so interior code can't be confused. Re-validation scattered everywhere is a smell.
- **SQL** — parameterized only. `sqlx` bind params / query macros, never `format!`/`+` into SQL
  (CWE-89). Watch dynamic `ORDER BY`/identifiers — those need allow-listing, not binding.
- **Command / path / template** — `std::process::Command` with attacker args (CWE-78); path
  joins from user input without canonicalize + prefix check (path traversal, CWE-22); any
  user-controlled format/template string.
- **Deserialization & decompression** — `serde` over untrusted input with no size/shape limits;
  zip/gzip/JSON bombs; unbounded `Vec`/`String` allocation from a length field (CWE-502, CWE-400).

### Sensitive data — secrets & PHI (HIPAA)
- **Secrets** — no hardcoded tokens/keys/credentialed URLs; no committed `.env`; secrets not
  leaking through a derived `Debug`/`Display`, an error message, or a log line (CWE-532, CWE-798).
- **PHI / PII** — never in logs, error messages, metrics labels, span attributes, or panic
  messages (ties to the no-PHI-in-dimensions rule). Encrypted at rest (per-tenant KMS) and in
  transit (TLS). **Minimum necessary** — does this code read or move more PHI than it needs?
- **Audit** — is access to a sensitive asset recorded where it should be? (See the audit-log
  design thinking — PHI access is an auditable event.)

### Memory & availability (Rust-shaped)
- **Panics as DoS** — an attacker-reachable `.unwrap()`/`.expect()`/`arr[i]`/integer overflow in
  a server is a denial-of-service vector, not a style nit (CWE-248, CWE-400). Bounds-checked
  access, `checked_*`/`saturating_*` arithmetic on attacker-influenced numbers.
- **`unsafe` on attacker bytes** — any `unsafe` touching untrusted input is a top finding unless
  the `// SAFETY:` invariant provably holds for hostile input. `transmute` of attacker bytes is a
  red flag.
- **Resource limits** — request body caps, timeouts, connection/concurrency limits, regex with
  bounded backtracking. Unbounded anything reachable from the network is a finding.

### Authn / authz
- **Object-level authorization** — does every handler check the caller may act on *this*
  resource, not just that they're logged in? Missing per-object/per-tenant checks (IDOR, CWE-639,
  CWE-862) are the most common real vuln in CRUD services.
- **Tokens / sessions** — validated, expired, scoped; not logged; not in URLs.

### Crypto
- No homegrown crypto. Vetted crates (`ring`, `rustls`, `aws-lc-rs`); no MD5/SHA-1 for security
  (CWE-327); constant-time comparison for secrets/MACs (CWE-208); CSPRNG (`OsRng`) for keys/tokens,
  not a fast PRNG; TLS verification never disabled "to make it work" (CWE-295).

### Supply chain
- `cargo audit` (RUSTSEC advisories), `cargo deny check` (advisories + bans + licenses +
  sources). Eyeball `Cargo.lock` churn for unexpected new transitive deps; watch typosquatted
  crate names; treat a new `build.rs` or proc-macro dependency as code that runs on your machine
  (CWE-1357).

## Tooling

Run, scoped to the touched crate(s) where possible:

- `cargo audit` — RUSTSEC advisories. **Blocking** for anything network-facing or pre-release.
- `cargo deny check` — advisories + bans + licenses + sources in one gate.
- `cargo-geiger` (if available) — `unsafe` surface across the dependency tree.
- For web services, a quick `semgrep` / `cargo-vet` pass if configured.

If a tool isn't installed or the code won't build, say so explicitly — don't silently skip a
supply-chain gate.

## Severity

Use the standard security tiers, not the project-review ones:

- **Critical** — exploitable now by the modeled attacker; data loss, RCE, auth bypass, PHI
  exposure.
- **High** — exploitable with a precondition, or serious info leak.
- **Medium** — requires unlikely conditions, or meaningful defense-in-depth.
- **Low / Hardening** — good practice, no concrete attacker path today.

**CVSS is the one number allowed** — and only on Critical/High, because it's an external standard,
not a vibe. No invented "security score out of 10". Always attach a **CWE** id; it makes the
finding searchable and unambiguous.

## Output template

```
## Scope & threat model
- Under review: <service / diff / commit range>
- Trust boundaries: <where untrusted data enters>
- Assets: <PHI, secrets, tokens, availability, …>
- Attacker assumed: <unauth remote / cross-tenant / malicious upstream / build-time>

## What's solid
<One or two sentences on controls that are correctly in place — so the fixes land in context.>

## Findings (ranked, exploitable-first)

**Critical**
1. `<file:line>` — <vuln> (CWE-NNN[, CVSS x.x]). **Attack path:** <how it's reached>.
   **Fix:** <smallest change that closes it>. **Verify:** <how to confirm it's closed>.

**High** / **Medium** / **Low — hardening**
...

## Tooling
- `cargo audit`: ...
- `cargo deny check`: ...
(One line each. "Not run — <reason>" is acceptable.)

## Verdict
<"Safe to expose", "One critical must-fix before it takes untrusted input", etc.>

## Recommended next action
<Single concrete step, or "None — no exploitable issue found.">
```

## Anti-patterns in the review itself

| Don't | Why |
|---|---|
| List a vuln with no attacker path | If nothing can reach it, it's a hardening note at most. Rank it accordingly or cut it. |
| Dump the OWASP / CWE catalog | Recite-the-list isn't review. Find the few things reachable *here*. |
| Inflate severity to look thorough | Critical means exploitable now. Crying wolf gets the whole review ignored. |
| Recommend adopting a security framework | This is a review. Name the smallest fix for the concrete hole. |
| Paste the secret or PHI you found | Reference the location, redact the value — the finding shouldn't leak the asset. |
| Invent a numeric "security score" | Feels rigorous, isn't. CWE always, CVSS where it helps, no vibe grades. |
| Manufacture findings on safe code | If the attack surface is clean, "no exploitable issue found" *is* the review. |
| Conflate defense-in-depth with exploitable-now | Both are worth saying — but not at the same severity. Keep them in separate tiers. |

## Project-specific notes

Replace with notes for the repository under review. Default posture for these projects is
**HIPAA**, so unless told otherwise:

- PHI must never appear in logs, error bodies, metrics labels, trace attributes, or panic
  messages. Treat any path that could emit it as a finding.
- Untrusted input crossing a service boundary is parsed to a typed representation at the edge;
  flag anything that threads raw strings/bytes inward.
- Secrets come from the configured secret store + KMS, not source or `.env`; confirm they don't
  surface through a derived `Debug`.
- Access to PHI is an auditable event — note where an audit record is expected but missing.
- A panic reachable from the network is a DoS finding in a long-running service, not a style nit.
