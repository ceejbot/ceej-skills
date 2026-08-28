---
name: review-application-security
description: "Use when security-reviewing an application, service, architecture, or scoped change in any language: threat-model trust boundaries, injection, authorization, secrets or PHI, cryptography, abuse resistance, and dependency exposure. Pair with review-rust-security for Rust-specific implementation risks. Produces ranked, exploitable-first findings with attacker paths, CWE references, and the smallest fixes."
---

# Application Security Review

Review the system through the question: **what can the modeled attacker actually
do?** This skill owns application-level controls regardless of implementation
language. `review-rust-security` owns Rust- and Cargo-specific failure modes.

**Core principle:** every finding needs a concrete attacker path. A dangerous
API or missing best practice is not automatically a vulnerability. Show where
untrusted input enters, how it reaches the weakness, what asset or boundary is
affected, and the smallest change that closes the path.

## Scope and companion lens

Establish whether the review covers a whole application, an architecture, or a
diff/PR. For a diff, capture its stated intent and ask only whether the change
adds attacker-reachable surface, weakens a control, or handles a new asset.
Read full files around relevant hunks; controls often live outside the diff.

For a Rust implementation, also apply `review-rust-security` when the requested
scope includes implementation or supply-chain risk. Build one threat model and
return one deduplicated report: application findings first, then any distinct
Rust-specific findings. Do not make the user reconcile two reviews.

Review only. Do not implement fixes unless the user separately asks. Never
paste a real secret, credential, PII, or PHI into the report; name its location
and redact the value.

## How to run

1. Build the threat model before assigning severity.
2. Trace only inputs and controls reachable under that model.
3. Run relevant project-native security checks; report anything skipped.
4. Rank a small set of findings by exploitability and impact.
5. Give the smallest fix and a concrete verification method for each.

## Threat model

State these explicitly at the top of the review:

- **Trust boundaries:** HTTP/gRPC handlers, queues, file or object-store reads,
  CLI/env, browser messages, third-party webhooks, deserialization, and admin
  surfaces where untrusted data enters.
- **Assets:** secrets, auth tokens, PHI/PII, money, tenant isolation,
  availability, and integrity of audit or business records.
- **Attacker capabilities:** unauthenticated remote, authenticated
  cross-tenant, malicious upstream, compromised operator, or poisoned build
  dependency.
- **Existing controls:** typed parsing, authentication and object-level
  authorization, parameterized queries, KMS, rate limits, network policy, and
  audit logging.

## Application security lens

### Input and injection

- Parse untrusted input into a bounded, typed representation at the edge.
- Parameterize SQL and other query languages. Allow-list dynamic identifiers
  such as sort columns rather than treating them as bindable values (CWE-89).
- Trace user-controlled command arguments, paths, redirects, templates, and
  URLs for command injection, traversal, open redirects, and SSRF (CWE-22,
  CWE-78, CWE-918).
- Bound request bodies, collection sizes, recursion, decompression, and parser
  work. Treat zip/JSON bombs and unbounded allocation as availability paths.

### Authentication, authorization, and tenancy

- Authentication is not authorization. Check the caller may act on this
  object and tenant at every reachable operation (CWE-639, CWE-862).
- Tokens and sessions must be validated for issuer, audience, expiry, scope,
  and revocation as the design requires. Never put credentials in URLs or
  logs.
- Privileged or recovery paths need the same scrutiny as the happy path;
  background jobs must preserve the initiating tenant and authority.

### Secrets and sensitive data

- Look for hardcoded credentials, committed environment files, credentialed
  URLs, and secrets exposed by logs, errors, metrics, traces, or serialization
  (CWE-532, CWE-798).
- For PHI/PII, apply minimum necessary access, encryption in transit and at
  rest, and auditable access. PHI must not appear in logs, error bodies,
  metrics labels, trace attributes, or panic messages.
- Verify redaction survives error and fallback paths; a safe success response
  does not protect an exception handler that prints the whole object.

### Cryptography and transport

- Use vetted primitives and protocols; no homegrown crypto, MD5/SHA-1 for
  security, non-cryptographic randomness for tokens, or ordinary equality for
  secrets/MACs (CWE-208, CWE-327).
- TLS certificate and hostname verification must remain enabled. Key and nonce
  lifecycle, reuse, and rotation should match the primitive's requirements.

### Availability and abuse resistance

- Bound concurrency, queues, retries, timeouts, regex work, upload sizes, and
  expensive per-request operations.
- Distinguish an ordinary crash from an attacker-repeatable denial of service.
- Check rate limits and abuse controls at the resource being exhausted, not
  only at a distant global gateway.

### Dependencies and configuration

- Review dependency and lockfile churn, untrusted package sources, install or
  build scripts, and newly introduced transitive code.
- Check deployment defaults for debug endpoints, permissive CORS, disabled
  verification, broad credentials, and insecure fallback behavior.
- Use the ecosystem's configured advisory/license/source checks. Do not install
  extra scanners without the user's approval; say when a useful check was not
  available.

## Severity and evidence

- **Critical:** exploitable now with catastrophic impact such as RCE, auth
  bypass, tenant escape, or PHI exposure.
- **High:** serious impact with a meaningful precondition.
- **Medium:** constrained exploitability or significant defense-in-depth.
- **Low / Hardening:** no concrete attacker path today.

Attach a CWE to each finding. Use CVSS only when it helps compare a Critical or
High vulnerability; never invent an overall security score. Every finding
must cite a file and line (or an architecture boundary), state the attack path,
name the smallest fix, and explain how to verify it.

## Output

```markdown
## Scope & threat model
- Under review: ...
- Trust boundaries: ...
- Assets: ...
- Attacker assumed: ...
- Existing controls: ...

## What's solid
<One or two sentences on controls that are working.>

## Findings (ranked, exploitable-first)
**Critical / High / Medium / Low — hardening**
1. `<file:line>` — <vulnerability> (CWE-NNN[, CVSS x.x]).
   **Attack path:** ... **Fix:** ... **Verify:** ...

## Tooling
- <check>: <result or "not run — reason">

## Verdict
<Safe for the modeled exposure, or the must-fix boundary.>

## Recommended next action
<One concrete step, or none.>
```

## Project-specific posture

Read `AGENTS.md`, `CLAUDE.md`, and `docs/review-notes.md` when present. For
these projects, assume HIPAA-sensitive handling unless the repository or user
says otherwise: no PHI in observable telemetry, secrets come from the
configured secret store/KMS, and PHI access is auditable. This is a code and
architecture security review, not a HIPAA compliance certification.

## Anti-patterns

- Do not dump an OWASP/CWE checklist; report the reachable paths in this
  system.
- Do not inflate severity or manufacture findings on safe code.
- Do not rank a dangerous-looking function above an exploitable boundary
  without tracing both.
- Do not conflate a hardening opportunity with an exploitable vulnerability.
- Do not recommend a framework or rewrite when a narrow control closes the
  path.
