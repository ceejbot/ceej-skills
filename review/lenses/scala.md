# Lens: Scala

The Scala branch of `review-project`. `PROBES.md` holds the questions; this
file holds where to point them in a Scala tree, what the compiler proves and
what it leaves to tests, and the properties a healthy Scala project holds
beyond the General section of `HYGIENE.md`.

## Detect

`build.sbt`, or a `pom.xml` whose plugins include `scala-maven-plugin`, or a
Bazel `scala_library`. Read the Scala version from the build (`2.12`, `2.13`,
`3.x`) and whether a crossbuild is in progress (`-Wconf`, a ready-list file, a
per-version source directory). Then the dialect, because it decides §1 and §3:

- **Effect system** (`cats.effect`, `zio`, `monix`): a timeout cancels the
  fiber and runs finalizers; supervision is a scope or a fiber tree.
- **Akka** (`akka.actor`, `akka.stream`): supervision is literal, a strategy
  on the parent; timeouts are `ask` patterns.
- **Plain JVM** (`java.util.concurrent`, `new Thread`, `scala.concurrent.Future`
  with an explicit `ExecutionContext`): a timeout returns to the caller and
  leaves the task running; nothing supervises a submitted task unless its
  `Future` is read.
- **Spark present** (`org.apache.spark`): executor-side code has its own
  bounds, its own connections, and no access to driver-side thread-locals.

State the dialect in one sentence in Orient. A monorepo may mix them by
module; name which modules use which.

## Evidence model

The compiler witnesses more than Java's and less than Rust's. Pattern matches
on sealed hierarchies are checked; nullability, exceptions, and thread-safety
are not. Java interop punches holes the type system cannot see.

| Property                                  | Witness                                                   | Unwitnessed looks like                                           |
| ----------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------- |
| Exhaustive handling of a sum type         | compiler, on a `sealed` hierarchy                         | a non-sealed trait matched with `case _`                         |
| Absence of null                           | `Option` at the Java boundary, by convention              | a Java getter's result used directly; `.get` on an `Option`      |
| Exceptions handled                        | none from the compiler; `Try`/`Either` by convention      | a `Future` or `Try` whose failure is never read                  |
| Thread safety of shared state             | none; `synchronized`, `@volatile`, `java.util.concurrent` by hand | a `var` or mutable collection reached from a pool thread  |
| Collection semantics across 2.12/2.13     | the crossbuild gate with warnings fatal                   | `Predef.Seq`, `asScala` results, `Stream` in a module not yet on the ready list |
| Input shape at an edge                    | a case class with a parser, or a test posting malformed input | a `Map[String, Any]` or `JsonNode` past the edge             |
| Secret never rendered                     | a redaction test, or a hand-written `toString`            | a case class holding the secret with its generated `toString`    |
| Per-request context on background threads | a test that runs the handler off-request                 | a scheduler callback that reaches a thread-local                 |

## Partition unit

The build module (Maven module, sbt project, Bazel target) within the named
system. Resolve the system first: the repo's own doc for it lists its modules
and key classes; otherwise grep the system's word across module names and
package paths. Spark jobs partition separately from the services that submit
them, because the probes answer differently on an executor.

## Tooling gates

- Formatting and lint: `scalafmt --check` and `scalafix --check` through the
  repo's recipes (`just fmt`, `just lint`, or the sbt/Maven plugin).
- Compile with warnings fatal if the build supports it (`-Xfatal-warnings`,
  `-Wconf:any:e`); on a crossbuild, run the ready-list check for the modules
  in scope.
- Tests through the recipe the repo names, scoped to the modules in scope
  (`mvn -pl <modules> test`, `sbt <project>/test`). Note the framework
  (TestNG, ScalaTest, munit, specs2) and what the fast recipe skips:
  integration tests behind a profile, Spark tests behind a flag.
- Dependency audit: `mvn dependency-check:check`, `sbt dependencyCheck`, or
  the organisation's scanner; `mvn dependency:analyze` for unused and
  undeclared dependencies.

## Probe instances

### §1 Bounds

`Await.result(`, `Await.ready(`, `Future.get(`, `awaitTermination(`,
`setQueryTimeout`, `setLoginTimeout`, `connectionTimeout`, `maxLifetime`,
`maximumPoolSize` (HikariCP), `socketTimeout` in JDBC URLs,
`spark.network.timeout`, `spark.sql.broadcastTimeout`, `spark.task.maxFailures`,
`maxRetries`, `retry`, any `Duration` or `Timeout` in a config class.

Scala consequence, plain JVM: `Future.get(timeout)` and `Await.result` return
to the caller and **leave the task running** on its pool thread, still
holding whatever it holds: a JDBC connection, a lock, a Spark session. The
caller may retry while the first attempt is still executing. Under an effect
system, ask instead whether the finalizer releases the resource.

### §2 Dual writes

`commit()` on a JDBC connection, `@Transactional` boundaries, `executeUpdate`
followed by a Kafka `send`, an S3 `putObject`, a `Files.write`, an email, a
webhook; Spark `.write` beside a metadata table update; a flag column such as
`published`, `sent_at`, `exported`.

### §3 Supervision

`ExecutorService.submit`, `.execute(`, `new Thread(`, `Thread.start`,
`ScheduledExecutorService.schedule*`, `Future {` with a global or implicit
`ExecutionContext`, `onComplete`, `recover`, `Runtime.addShutdownHook`,
`awaitTermination`, `shutdownNow`.

Scala consequence: a `submit` whose returned `Future` is never read discards
the task's exception silently; `execute` routes it to the thread's
uncaught-exception handler, which by default prints and moves on. A `new
Thread` with no handler dies quietly and health keeps reporting fine.
`Future.onComplete` with a global `ExecutionContext` runs on a thread the
code does not own. Background threads have none of the per-request context
the web framework sets on request threads (thread-locals, security context,
tenant); a handler that reaches one from a scheduler callback throws on the
first run, often an NPE with no tenant in the message.

### §4 Boundary symmetry

Every client class for one vendor or service (`*Client`, `*Service` wrapping
an HTTP or JDBC call), token refresh and retry wrappers, `case 401 | 403 |
429`, status-to-exception mappers, Jackson `ObjectMapper` configurations for
the same vendor (one `FAIL_ON_UNKNOWN_PROPERTIES` setting per vendor, not
per call site).

### §5 Startup truth

`System.getenv`, `sys.env`, `System.getProperty`, `ConfigFactory`,
`config.getInt`/`getString` with a default, `.toInt` on a string from config,
`Try(...).getOrElse(default)`, `Option(javaValue).getOrElse`, Spring
`@Value("${...:default}")`.

Scala consequence: a Java getter that returns null for a boxed primitive
unboxes to a Scala value without throwing in some 2.12 configurations and
throws on the first method call in others; a config default of `0` for a pool
size yields a worker that starts, reports healthy, and does nothing.

### §6 The irreversible class

Every case class, Java bean, or `Map` that carries PHI, credentials, money, or
audit material. Rendering sites: the **generated `toString` of every case
class** (every field, no opt-out short of overriding it), `s"$obj"` and
`log.info(s"... $request")`, `.toString` on a Java bean, Jackson or json4s
serializing the whole object, `Exception.getMessage` carrying a response
body, `e.printStackTrace`, a `derisk`- or `mask`-style helper that obscures
reversibly and is treated as redaction. Passing sites: a `String` parameter
that accepts a key, a label, and a secret alike.

### §7 Promises

README and `docs/` guarantees, runbooks, alert annotations, Scaladoc on
public methods, `@deprecated` messages that promise a replacement, ADRs, and
the agent docs (`CLAUDE.md`, `.claude/docs/`) that tell a reader what a
subsystem does. In a monorepo, the system doc Orient resolved is the first
source of promises for that system.

## Hygiene

Scala-specific properties, applied on top of `HYGIENE.md` General.

### Null stays in Java

- Nullable Java values wrapped in `Option` at the boundary; no `null` in
  Scala signatures. Java collections converted through a null-safe helper
  where the codebase has one.
- `.get` on an `Option` only with a comment saying why it holds; `.head` on
  a possibly-empty collection is a finding.

### Failure is a value

- `Try`, `Either`, or `Future` carry failure; a `catch` that logs and returns
  a default is a finding unless the default is the documented behaviour.
- `Future` failures are read: `onComplete`, `recover`, or a join. A fire-and-
  forget `Future` is probed under §3.
- `ExecutionContext` passed explicitly or injected; `Implicits.global` only in
  scripts and tests.

### Shared state is guarded

- Every `var` and mutable collection reached from more than one thread sits
  behind `synchronized`, an `Atomic*`, a `java.util.concurrent` collection, or
  an actor. A `@volatile` on a collection reference guards the reference, not
  the contents.

### Case classes are data

- Case classes for data, with no mutable fields; behaviour in companions or
  services. A case class in the irreversible class overrides `toString` or
  carries a redacting wrapper (§6).
- `sealed` on every trait that is matched on.

### Implicits are findable

- Implicit conversions and instances live in companions or one named import;
  no implicit that changes behaviour from a wildcard import.

### Crossbuild hygiene

Where the build spans Scala versions: collections built as the target's
default (`immutable.Seq`), `Predef` differences handled explicitly, the
version-specific APIs the project's agent docs list avoided, and the ready
list for the modules in scope still green.

### Build hygiene

- Module dependencies acyclic and declared; `mvn dependency:analyze` clean.
- Compiler flags consistent across modules; warnings fatal where the build
  allows.
- Framework stereotype rules the project documents (which annotation a
  resource takes versus an infrastructure bean) followed; mis-stereotyping is
  a runtime failure, not a style issue.

## Security

For a focused security pass (threat model, injection, authz, crypto, PHI
handling) use `review-application-security`. Scala-specific exposure to carry
into it: Java deserialization of untrusted bytes, Jackson polymorphic typing
(`enableDefaultTyping`), reflective Spark UDF loading, and the JVM dependency
tree's transitive surface.
