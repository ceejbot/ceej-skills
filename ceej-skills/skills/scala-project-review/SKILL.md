---
name: scala-project-review
description: Use when the user asks for a holistic / wholistic review of a Scala project, "is this codebase healthy", "review the project", "audit before sharing", or at a periodic checkpoint in a personal Scala project
---

# Scala Project Review

A holistic pass over a Scala codebase: first general code-quality concerns that apply to any project, then Scala-specific hygiene. The output should be concrete enough to act on — file references, not vibes.

**Core principle:** every finding cites a file and a reason. "The architecture could be cleaner" is not a finding; "`core/src/main/scala/api/Routes.scala:42` exposes `internal.Repo` as a public type — narrowing the return to `trait UserStore` would let callers stop reaching through" is.

## How to run

1. Walk Section A in order, noting findings with file references.
2. Walk Section B in order, noting findings with file references.
3. Run the project's build-tool checks — record what's clean and what isn't:
   - **Maven** (current main project): `mvn spotless:check` (or `mvn scalafmt:check` depending on plugin), `mvn compile`, `mvn test`, `mvn scala:doc`. Strict compiler flags live in the `scala-maven-plugin` `<args>` block in `pom.xml`.
   - **sbt**: `sbt scalafmtCheckAll`, `sbt "scalafixAll --check"`, `sbt compile`, `sbt test`, `sbt doc`.
   - **Mill** (coming soon): `mill __.checkFormat`, `mill __.compile`, `mill __.test`, `mill __.docJar`.
4. Synthesize the **Summary** at the bottom: top 3 strengths, top 3 issues, recommended next action.

Findings should land in a single message. Don't fix anything in this pass — review only. Fixes come after the user picks priorities.

## Section A — General review

### Architecture
- Are package boundaries sensible? Could a new reader form a mental model from the top-level package and `Main` alone?
- Does each package own one concept, or has it become a junk drawer?
- Is the data flow obvious — where does input enter, where does output leave?

### README
- Does it answer **what is this**, **who is it for**, **should I use it**?
- For small projects: is there a 5-line example showing the happy path?
- For libraries: is there a minimal dependency snippet (Maven `<dependency>`, sbt `libraryDependencies`, or Mill `ivy"..."`) and a minimal call site?
- Are non-obvious build/run commands documented?

### Documentation
- Public items have Scaladoc comments?
- Doc comments explain *why* and *when*, not just restate the signature?
- Examples in docs that actually compile (mdoc, tut, or doctests)?

### Simplicity & modularity
- Each package / file doing one thing?
- Methods short enough to hold in your head?
- No deep trait hierarchies that could be ADTs (sealed traits + case classes) instead?
- No dense one-liners (`xs.flatMap(_.bar).groupBy(_._1).view.mapValues(_.size).toMap.filter(...)`) where two named intermediate `val`s would read better? **Idioms should serve readability, not show them off.**

### Information hiding
- Things that might be swapped (storage backend, transport, serialization, clock) hidden behind a trait or package boundary?
- Or — if the abstraction is premature — is the concrete dependency at least quarantined to one place?
- Implementation classes not leaking into public signatures (return `Map[K, V]`, not `mutable.HashMap[K, V]`; return `Seq[A]`, not `ArrayBuffer[A]`).

### DRY balance
- No copy-paste of three-plus lines that share a real concept (extract).
- No abstraction used in only one place (inline).
- Three similar lines beats a premature abstraction.

### Parse, don't validate
- Untrusted input converted to a strongly-typed representation at the *edge* (HTTP handler, queue consumer, file reader)?
- Interior code can assume validity — no re-checking the same invariants in every method?
- Are "stringly typed" parameters that could be `sealed trait` ADTs, opaque types (Scala 3), value classes (Scala 2), or refined types?
- Smart constructors return `Either[Error, T]` / `Validated[Error, T]` rather than throwing.

### Cleanup
- Dead code, commented-out blocks, orphaned files?
- TODOs older than the project — still relevant or stale?
- Stray `println`, `Console.err.println`, debug-only branches?
- Unused dependencies in `pom.xml` / `build.sbt` / `build.mill`?

## Section B — Scala-specific review

### Idioms in service of readability
- Scala idioms are used — `map` / `flatMap` / `for`-comprehensions / pattern matching / `Option` / `Either` — but **not so densely that the next reader has to parse the symbols before they can read the code**.
- A `for`-comprehension is preferred over deeply nested `flatMap`/`map` chains when the steps have meaningful names.
- Named intermediate `val`s used where they let the reader skim. A dense functional one-liner is not a virtue if a three-line version reads in a third of the time.
- Operator-heavy code (`|+|`, `>>`, `*>`, `<*`, `&>`, `|@|`) is scoped and explained — not sprinkled into general-purpose business logic for readers who don't know cats.

### Types do work
- Newtype wrappers around primitives where the primitive is meaningful — value classes (`final case class UserId(value: Long) extends AnyVal`) or Scala 3 opaque types (`opaque type UserId = Long`).
- `sealed trait` / `enum` (Scala 3) for sum types — **not strings**, **not `Int` constants**. If a value has a fixed set of cases, the compiler should enforce that.
- Java `enum` is acceptable on the Java boundary; Scala 3 `enum` or `sealed trait` + case objects is preferred inside Scala code.
- Type parameters used where they capture a real relationship. Project convention: response types carry a `data` field of a type that varies per endpoint — express that as `final case class Response[T](data: T, ...)` rather than `Response(data: Any)` or untyped JSON.
- Phantom types or path-dependent types where they prevent mixing of incompatible values (`Id[User]` vs `Id[Account]`).
- `Refined` / `iron` (Scala 3) or smart constructors for values like `NonEmptyString`, `PositiveInt`, `EmailAddress`.

### Inheritance, traits, and encapsulation
- **Inheritance of implementation breaks encapsulation.** Subclasses depend on the superclass's protected internals, so changes ripple. Prefer composition (hold a collaborator) or mixins of pure behavior.
- **Traits express behavior; classes express identity.** Mixing the two — a trait that has fields and constructor-like state, then extending it as if it were a class — works but tends to confuse the reader. Keep traits behavioral (methods, maybe abstract `def`s) and put state in classes.
- If a `trait` has more than one or two `var`s or non-trivial constructor parameters, ask whether it should be a `class` or an interface-style `trait` plus a class.
- `sealed` on traits that are meant to be exhaustively pattern-matched. The compiler can then warn on missing cases.
- `final` on classes that aren't designed to be extended. The default-open posture of Scala invites accidental inheritance.

### Errors and exceptions
- Library / domain code returns `Either[DomainError, A]`, `Validated[NonEmptyList[Error], A]`, or an effect type (`IO[A]`, `ZIO[R, E, A]`) — **not** throws.
- `Try` is used where a known-throwy Java API is called and the result is converted to `Either` or `Option` quickly.
- **Catch as specifically as possible.** `catch case NonFatal(_) =>` is the broadest acceptable form, and even that should usually log or rethrow. `catch case _: Throwable =>` is almost always wrong (it swallows `OutOfMemoryError`, `InterruptedException`, `ControlThrowable`).
- No `catch case e: Exception =>` that turns a typed failure mode into a generic one — match on the specific exception types you actually expect.
- Domain errors are an ADT (`sealed trait DomainError { case class NotFound(id: UserId) extends DomainError; ... }`), not strings.
- `recover` / `recoverWith` on `Future` / `IO` is specific about which failures it handles.

### Java/Scala boundary
- Every call into a Java API is reviewed for: **null return values** (wrap in `Option(...)` immediately), **checked or unchecked exceptions** (wrap in `Try` or catch the specific type), **mutable collections leaking in** (convert to immutable at the boundary).
- `null` does not appear in Scala code outside the boundary layer.
- Java collections (`java.util.List`, `java.util.Map`) converted at the boundary via `scala.jdk.CollectionConverters`; not passed into Scala interior code.
- `Optional` from Java converted to `Option` at the boundary.
- Time types: `java.time.*` is fine; `java.util.Date` should be quarantined.

### No casual runtime errors
- No `.get` on `Option` outside of tests or genuine invariants (with a comment).
- No `.head` / `.last` on a possibly-empty collection — use `.headOption` / `.lastOption`.
- No unchecked downcasts (`asInstanceOf[T]`) — if needed, route through a pattern match.
- Array / sequence indexing (`xs(i)`) avoided in favor of `lift`, `get`, pattern destructuring, or guards.
- No `???` left in committed code.
- No partial functions applied without checking `isDefinedAt`, unless the input is known total.

### Pattern matching
- Matches on `sealed` hierarchies are exhaustive. Compiler exhaustiveness warnings are on.
- No `case _ =>` that hides a missing case — use it only when you really mean "everything else."
- Guards are simple; complex predicates pulled into a named `def`.
- `@unchecked` annotations are justified by a comment.

### `var` / mutability
- `val` is the default; `var` is rare and contained.
- Mutable collections (`mutable.Map`, `ArrayBuffer`) are local — they don't escape the method they're built in. If they do, document why.
- Shared mutable state is behind a concurrency primitive (`Ref`, `AtomicReference`, `STM`), not raw `var`.

### Implicits / givens
- Scala 2 `implicit` and Scala 3 `given` instances are scoped tightly — top-level for typeclasses, locally in a method otherwise.
- Implicit conversions (`implicit def aToB`) are extremely rare. Prefer extension methods.
- No "magic" — a reader should be able to find the implicit / given without searching the whole project.
- `using` parameters (Scala 3) document what they are.

### Don't be clever
- Newer / fancier features (macro annotations, match types, complex type-level computation, given derivation chains) are used only when they pay for the cost they add to the reader.
- A clear `Map[String, UserSummary]` beats a `HMap[KeyOf, ValueOf]` for 99% of projects.
- Implicit derivation of typeclasses (e.g. circe, magnolia) is fine; derivation of business logic is a code smell.
- Macros and `inline` should have a comment naming the concrete win.

### Effects and concurrency
- One effect story per project — `Future`, cats-effect `IO`, or `ZIO`. Not a mix.
- If `Future`: `ExecutionContext` is threaded explicitly or via a clearly-named `given`; no `import scala.concurrent.ExecutionContext.Implicits.global` in library code.
- No blocking calls (`Await.result`, `.get` on `Future`, blocking JDBC) on a non-blocking pool. Use a dedicated blocking pool or `IO.blocking { ... }`.
- `Future` composition uses `for`-comprehensions or `flatMap` — not nested callbacks.
- Cancellation is considered for long-running effects.

### Equality
- `==` is used on case classes (structural equality works).
- Cross-type comparisons (`x == y` where types differ) are flagged by the compiler — strict-equality flags (`-Xfatal-warnings`, `-Wnonunit-statement`, or cats `Eq`) are enabled.
- No `eq` / `ne` outside performance-critical or identity-comparison contexts.

### Collections
- Return types are interface-level (`Seq`, `Set`, `Map`, `Iterable`) unless the concrete type matters.
- `List` vs `Vector` vs `ArraySeq` chosen with intent — `List` for head/tail access, `Vector` for random access and concatenation, `ArraySeq` for primitive arrays.
- `view` used where a chain of transformations would otherwise allocate intermediate collections.
- No `xs.size == 0` (use `isEmpty`) or `xs.length` on a `List` in a hot path.

### Build & tooling
- **Formatting clean.** **Run `scalafmt` before every commit.**
  - Maven: `mvn spotless:check` or `mvn scalafmt:check` (whichever plugin the `pom.xml` configures).
  - sbt: `sbt scalafmtCheckAll`.
  - Mill: `mill __.checkFormat`.
- Scalafix clean (if configured): `mvn scalafix:scalafix -Dscalafix.mode=check` / `sbt "scalafixAll --check"` / `mill __.fix --check`.
- Compiler flags are strict: `-Wunused:all`, `-Wvalue-discard`, `-Wnonunit-statement`, `-Xfatal-warnings`, `-deprecation`, `-feature`. In Maven these live in the `scala-maven-plugin` `<args>` block; in sbt, `sbt-tpolecat` is a reasonable default; in Mill, `scalacOptions`.
- Compile clean — no warnings (`mvn compile` / `sbt compile` / `mill __.compile`).
- Tests clean (`mvn test` / `sbt test` / `mill __.test`).
- Scaladoc warning-free (`mvn scala:doc` / `sbt doc` / `mill __.docJar`).
- Dependency versions pinned. Maven: no version ranges (`[1.0,)`) and no `LATEST` / `RELEASE`. sbt: no `latest.integration`.
- No unused dependencies. Maven: `mvn dependency:analyze`. sbt: `sbt-explicit-dependencies` or manual audit. Mill: manual audit.

### Project layout
- `src/main/scala` vs `src/main/java` consistent.
- Test-only utilities in `src/test/scala`, not `src/main`.
- Multi-module projects have a sensible dependency graph — leaf modules don't depend on roots, no cycles.
- Cross-builds (2.13 + 3) declared cleanly if used.

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
| Skip Section A because it's "general" | The general issues are usually the ones that matter most. Don't only nitpick compiler warnings. |
| Praise functional density for its own sake | The goal is code the next reader can absorb quickly, not a demo of typeclass derivation. |
