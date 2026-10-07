# Probes: where lints cannot see

A **probe** is a question asked of every instance of a mechanism. A property
check ("every spawn is joined or aborted") is satisfied on paper while the
consequence goes unexamined; a probe asks the consequence. Grep finds the
instances, the probe is answered per instance, and the step completes when
every instance is **accounted for**: answered with a file:line, or ruled out
with a reason. Probes are cross-cutting: run each across the whole tree, not
per crate.

Each probe names its instances, its questions, and the shape a finding takes.
A probe finding goes through the review's verify step like any other.

## 1. Bounds

**Instances:** `timeout(`, `timeout_at(`, `deadline`, `budget`, pool sizes
(`max_connections`, `max_size`), `retry`, `max_attempts`, `message.timeout.ms`
and its cousins in client config.

**Ask, per bound:**

- What does this bound release when it fires: the caller's wait, or the work
  itself? A `tokio::time::timeout` drops the future; name what that future was
  in the middle of.
- What still holds the resource after it fires, and who releases that?
- What is the next bound down the chain (upstream client timeout × retries,
  the broker's own timeout), and does this one sit inside it?
- Has the house hit this before? `git log --grep` the config key.

**Finding shape:** the timeout drops a future after the vendor committed but
before the local write; the new bound is wider than the upstream bound it
claims to protect; a retry count multiplies a timeout past the caller's own.

## 2. Dual writes

**Instances:** a `commit(` followed by `send`, `publish`, `emit`, `put_object`,
or a file write; any column, flag, or label that records "emitted", "sent",
"published", "announced".

**Ask, per pair:**

- Which side is authoritative, and does the code say so?
- What bridges a crash between the two: an outbox, retry-until-confirmed, or
  accepted loss? Is the chosen bridge implemented, or described in a comment?
- Does the metric or log for this step record the outcome, or the intention?

**Finding shape:** a flag with writers of only one value; a counter incremented
before the publish it counts; a comment promising a replay that has no code.

## 3. Supervision

**Instances:** `tokio::spawn`, `spawn_blocking`, `JoinSet`, `TaskTracker`,
`select!` arms on a shutdown token, anything with a `drain()` or `wait()`.

**Ask, per task:**

- When this task returns `Err`, who learns, and when? A join that matches only
  `JoinError` discards `Ok(Err(_))`.
- At shutdown, who waits for it, and what work can be mid-flight when the
  runtime drops it?
- While it is dead, what does health or readiness report?
- Was it spawned before the config it needs was validated?

**Finding shape:** a tracker whose `drain()` only tests call; a consumer that
fails on a missing env var while HTTP keeps serving; a join site that logs the
join error and swallows the task's own.

## 4. Boundary symmetry

**Instances:** every client for one vendor or service; `invalidate`, `refresh`,
`re-mint`, backoff; 401, 403, 429 handling; status-to-error mappers.

**Ask, per boundary:**

- Where does the self-healing live (retry on 401, re-mint, backoff), and does
  every caller of this boundary pass through it?
- Do the error mappers for the same vendor agree on the same status?
- When the healing fails, what does the user see, and does it prompt an action
  that makes the state worse (a re-link that rotates a token again)?

**Finding shape:** the control plane retries on 401 and the data plane sends
once; four mappers disagree on 403.

## 5. Startup truth

**Instances:** `env::var`, config structs, `.parse().ok()`, `unwrap_or(default)`,
`unwrap_or_default()` on anything that reaches a loop bound, a pool size, or a
feature switch.

**Ask, per parse:**

- What does garbage become? What does zero or empty become?
- Is the parsed value validated before the process serves or reports ready?
- If the value is wrong, what is the first observable symptom, and how long
  until someone sees it?

**Finding shape:** `"abc"` becomes 5; `0` is accepted and yields a healthy
worker that runs no jobs.

## 6. The irreversible class

**Instances:** the project's own rule, found in its `CLAUDE.md`, `AGENTS.md`,
or ADRs under a word like PHI, credentials, money, audit, or irreversible.
Then every type that carries it: tokens, secrets, transcripts, addresses,
names, account numbers, raw request and response bodies.

**Ask, per type:**

- Can it be rendered? A derived `Debug`, a `Display`, a `{e:?}` on an error
  path, an `anyhow` wrapper around a response body, a log line with `{err}`.
- Can it be passed where it does not belong? A bare `String` payload accepts
  any `&str` parameter, including a storage key or a metric label.
- Where is the redaction test, and does this type have one?

**Output:** a table of type, location, and whether `Debug` redacts. Every
type in the class gets a row, including the ones that pass.

**Finding shape:** `derive(Debug)` two lines under a comment saying never to
log the fields; the one PHI payload that is a bare `String` while its siblings
are newtypes.

## 7. Invent one

The six above are the mechanisms most Rust services share. Each project has one
more: the mechanism its docs are proudest of, or most worried about. Read the
repo's ADRs and agent docs for it, then write the seventh probe in the same
shape (instances, questions, finding shape) and run it. Name it in the review
so the next reviewer inherits it.
