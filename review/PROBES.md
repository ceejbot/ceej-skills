# Probes: where lints cannot see

A **probe** is a question asked of every instance of a mechanism. A property
check ("every spawn is joined or aborted") is satisfied on paper while the
consequence goes unexamined; a probe asks the consequence. Grep finds the
instances, the probe is answered per instance, and the step completes when
every instance is **accounted for**: answered with a file:line, or ruled out
with a reason. Probes are cross-cutting: run each across the whole tree, not
per module. Docs, runbooks, and chart files are part of the tree.

Each probe names the mechanism it asks about, its questions, and the shape a
finding takes. **Where to find the instances is the lens's job**: the
language file under `lenses/` lists, per probe number, the grep hints and the
consequence that language attaches to the mechanism. A probe finding goes
through the review's verify step like any other.

One more question rides along: **where is the witness?** A type, a lint, or
a test that would fail if the answer changed. "None" on an instance in the
irreversible class or at a parse boundary is a finding on its own, before
the probe's own questions are asked. The lens's evidence model says which
witnesses the language can offer and where the question is asked: of every
instance where the type checker is advisory; at the irreversible class and
the parse boundaries where the compiler is the witness.

Each probe run leaves a **ledger** line in the review: instances found,
instances accounted for, findings. `§1 Bounds: 9 instances, 9 accounted,
2 findings` is checkable. "Bounds are chained on purpose" is not, and a probe
summarized in prose is one whose instances nobody can count.

## 1. Bounds

**Mechanism:** every timeout, deadline, pool size, and retry count, in code
and in client config. Instances: the lens, §1.

**Ask, per bound:**

- What does this bound release when it fires: the caller's wait, or the work
  itself? Name what the work was in the middle of when the bound fired; the
  lens says whether the language cancels it or leaves it running.
- What still holds the resource after it fires, and who releases that?
- What is the next bound down the chain (upstream client timeout × retries,
  the broker's own timeout), and does this one sit inside it?
- Has the house hit this before? `git log --grep` the config key.

**Finding shape:** the timeout abandons work after the vendor committed but
before the local write; the new bound is wider than the upstream bound it
claims to protect; a retry count multiplies a timeout past the caller's own.

## 2. Dual writes

**Mechanism:** two durable writes that must agree, with no transaction
spanning them: a database commit beside a publish, an upload, or a file
write; any column, flag, or label that records "emitted", "sent",
"published", "announced". Instances: the lens, §2.

**Ask, per pair:**

- Which side is authoritative, and does the code say so?
- What bridges a crash between the two: an outbox, retry-until-confirmed, or
  accepted loss? Is the chosen bridge implemented, or described in a comment?
- Does the metric or log for this step record the outcome, or the intention?

**Finding shape:** a flag with writers of only one value; a counter incremented
before the publish it counts; a comment promising a replay that has no code.

## 3. Supervision

**Mechanism:** every unit of work that runs off the caller's thread of
control: spawned tasks, pool submissions, background threads, scheduled
jobs, and the shutdown path that is supposed to wait for them. Instances:
the lens, §3.

**Ask, per task:**

- When this task fails, who learns, and when? A join site that handles only
  the runtime's own failure discards the task's.
- At shutdown, who waits for it, and what work can be mid-flight when the
  runtime drops it?
- While it is dead, what does health or readiness report?
- Was it spawned before the config it needs was validated?

**Finding shape:** a shutdown wait that only tests call; a consumer that
fails on a missing env var while HTTP keeps serving; a join site that logs the
runtime's error and swallows the task's own.

## 4. Boundary symmetry

**Mechanism:** every client for one vendor or service, its token refresh
and backoff, its 401, 403, and 429 handling, and its status-to-error
mappers. Instances: the lens, §4.

**Ask, per boundary:**

- Where does the self-healing live (retry on 401, re-mint, backoff), and does
  every caller of this boundary pass through it?
- Do the error mappers for the same vendor agree on the same status?
- When the healing fails, what does the user see, and does it prompt an action
  that makes the state worse (a re-link that rotates a token again)?

**Finding shape:** the control plane retries on 401 and the data plane sends
once; four mappers disagree on 403.

## 5. Startup truth

**Mechanism:** every value read from the environment or a config file and
parsed with a default, where the result reaches a loop bound, a pool size, or
a feature switch. Instances: the lens, §5.

**Ask, per parse:**

- What does garbage become? What does zero or empty become?
- Is the parsed value validated before the process serves or reports ready?
- If the value is wrong, what is the first observable symptom, and how long
  until someone sees it?

**Finding shape:** `"abc"` becomes 5; `0` is accepted and yields a healthy
worker that runs no jobs.

## 6. The irreversible class

**Mechanism:** the project's own rule, found in its `CLAUDE.md`, `AGENTS.md`,
or ADRs under a word like PHI, credentials, money, audit, or irreversible.
Then every type that carries it: tokens, secrets, transcripts, addresses,
names, account numbers, raw request and response bodies. The lens, §6, names
the language's rendering sites: the places a whole value becomes a string
without anyone writing a formatter.

**Ask, per type:**

- Can it be rendered? A derived or auto-generated string form, a wrapped
  error that carries a response body, a log line that formats the whole
  value or the whole error.
- Can it be passed where it does not belong? A payload typed as the
  language's plain string accepts any string, including a storage key or a
  metric label.
- Where is the redaction test, and does this type have one?

**Output:** a table of type, location, and whether its rendering redacts.
Every type in the class gets a row, including the ones that pass.

**Finding shape:** an auto-generated string form two lines under a comment
saying never to log the fields; the one PHI payload that is a plain string
while its siblings are wrapped types.

## 7. Promises

**Mechanism:** every sentence that tells a reader what the system does. That
means README guarantees and "consequences" lists, runbook steps and the
observations they expect, alert descriptions and annotations, integration
contracts with callers, doc comments on public behaviour, and decisions
recorded in ADRs and closed issues. It also means every setup artifact the
docs tell an operator to apply: a schema or migration file, a compose file,
a chart; applying it is the promise that the system then works. Grep the
docs for `always`, `never`, `within`, `guarantee`, the outcome words the
service uses (`fails open`, `sheds`, `retries`), and each runbook's "you
should see". The lens, §7, adds the language's doc-comment and contract
conventions.

**Ask, per promise:**

- Does the code make it true under the production configuration: the
  timeouts, sizes, and log levels the chart or deployment actually sets?
- Who acts on it (a caller coding to the contract, on-call following the
  runbook), and what do they do when it is false?
- Where code and promise disagree, which one is right? The disagreement is the
  finding; the fix is whichever side was wrong.
- Has reality tested it? For an alert rule: the alert state series over the
  last week, and whether each firing was the condition the annotation
  describes. For a runbook: whether its first check would have explained the
  last real event. A promise that fired on something else is a finding.

**Finding shape:** a runbook lists a cause that the classifier routes
somewhere else; an alert says "sustained" over an expression that fires on one
sample; a closed issue records a decision that a later handler change made
unreachable.

## 8. Invent one

The seven above are the mechanisms most services share, in any language. Each project has
one more: the mechanism its docs are proudest of, or most worried about. Read
the repo's ADRs and agent docs for it, then write the eighth probe in the same
shape (instances, questions, finding shape) and run it. Its instances are call
sites you can grep: the calls that feed a liveness clock, every error an
acquire can return, every background thread that needs a per-request context
the framework only sets on request threads. A probe whose instances are the project's goals restates
§6 and §7. Name it in the review so the next reviewer inherits it.
