# Lens: TypeScript

The TypeScript branch of `review-project`. `PROBES.md` holds the questions;
this file holds where to point them in a TypeScript tree, what the compiler
can and cannot witness, and the properties a healthy TypeScript project holds
beyond the General section of `HYGIENE.md`.

## Detect

`package.json` beside a `tsconfig.json`. Read `strict`, `noUncheckedIndexedAccess`,
and `exactOptionalPropertyTypes` from the config: they decide how much the
compiler witnesses. Then the dialect: Node service (`express`, `fastify`,
`hono`, `nest`), browser or React app, or a library; and the package manager
and workspace layout (`pnpm-workspace.yaml`, `workspaces` in `package.json`).

## Evidence model

Types are erased at runtime. The compiler witnesses what it is shown and
nothing that crosses a boundary: a `fetch` response, a parsed JSON body, an
environment variable, a database row. The witness for a boundary property is
a runtime schema at the edge or a test that sends the wrong shape. **A
property with no runtime witness is unwitnessed**, whatever the type says.

| Property                                  | Witness                                                   | Unwitnessed looks like                                            |
| ----------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------- |
| Exhaustive handling of a sum type         | compiler, on a discriminated union with `never` in `default` | a `switch` on a string with no `never` check                   |
| Input shape at an edge                    | `zod`/`valibot`/`io-ts` parse at the edge, plus a test posting malformed input | `as Foo` on a parsed body; `any` or `unknown` passed inward |
| Absence of null/undefined dereference     | compiler under `strict` and `noUncheckedIndexedAccess`    | `!` non-null assertions; array index used without a check        |
| Errors are handled                        | none from the compiler; `no-floating-promises` lint       | a `Promise` expression on its own line; `.then` with no `.catch`  |
| Exceptions typed                          | none; `catch (e: unknown)` and narrowing by convention    | `catch (e: any)` reading `e.message`                              |
| Secret never rendered                     | a redaction test, or a wrapper class with `toJSON`        | a plain object with the secret as a property                      |
| Behaviour under a timeout                 | a test with fake timers or `AbortSignal`                  | none; §1 carries the question                                     |
| Doc examples still compile                | `typedoc` with examples checked, or example tests         | code blocks in README only                                        |

## Partition unit

The workspace package, then the directory under `src/` by import graph:
entry points (server, CLI, pages), their internal modules, shared packages.

## Tooling gates

- `tsc --noEmit` with the project's config; if `strict` is off, say so in the
  gates table: the project has chosen not to witness nullability.
- `eslint` with `@typescript-eslint/no-floating-promises`,
  `no-misused-promises`, and `no-explicit-any` reported (read the config for
  what is disabled).
- `prettier --check`.
- Tests through the repo's recipe (`vitest`, `jest`, `node --test`), with
  coverage filtered to the irreversible-class modules and edge parsers.
- `npm audit` / `pnpm audit` / `yarn npm audit`; a lockfile committed.

## Probe instances

### §1 Bounds

`AbortSignal.timeout(`, `AbortController`, `setTimeout(` racing a promise,
`fetch(` with no `signal` (a bound of infinity), `axios` `timeout:`,
`server.timeout`, `keepAliveTimeout`, `headersTimeout`, pool `max` and
`idleTimeoutMillis` (`pg`), `maxRetries`, `retry`.

TypeScript consequence: aborting a `fetch` rejects the promise; the server on
the other end may still complete the request. A `Promise.race` against a
timer **leaves the loser running**, holding its connection until it settles
on its own.

### §2 Dual writes

`await tx.commit()` or an ORM `transaction(` followed by a `publish`,
`sendMessage`, `putObject`, `fs.writeFile`, an email, a webhook; a column
`published`, `sentAt`, `exported`; a metrics `.inc()` beside the publish it
counts.

### §3 Supervision

A `Promise` not awaited or returned (`void doWork()`, a bare call), `.then(`
without `.catch(`, `setInterval(`, `process.on('SIGTERM'`,
`server.close(`, worker threads (`new Worker(`), `queue.add(`,
`EventEmitter` handlers that are `async`.

TypeScript consequence: an unhandled rejection in Node 15+ **crashes the
process**; an `async` event handler's rejection goes nowhere the emitter can
see. A `setInterval` with no `clearInterval` at shutdown keeps the process
alive past `server.close()`.

### §4 Boundary symmetry

Every client module for one vendor, token refresh, `status === 401`, `429`
and `Retry-After`, `response.ok` checked at some call sites and not others,
error mappers for the same vendor in two modules.

### §5 Startup truth

`process.env.X`, `process.env.X ?? 'default'`, `Number(process.env.X)`,
`parseInt(` with no radix, `dotenv`, config libraries with defaults,
`JSON.parse(process.env.X)`.

TypeScript consequence: `process.env.X` is `string | undefined` and
`Number(undefined)` is `NaN`, which passes `if (n)` checks as falsy and
comparisons as false; `Number("")` is `0`. A `NaN` or `0` reaching a pool size
or a loop bound produces a healthy process that does no work.

### §6 The irreversible class

Every object type carrying PHI, credentials, money, or audit material.
Rendering sites: `JSON.stringify(obj)`, `console.log(obj)`, structured
loggers given the whole object (`logger.info({ req })`, `pino` without
`redact`), template literals `` `${obj}` ``, `util.inspect`, error messages
built from response bodies, `res.json(entity)` returning the whole row.
Passing sites: a `string` parameter that accepts a key, a label, and a
secret alike; spread (`...obj`) copying a secret into a log context.

### §7 Promises

README and `docs/` guarantees, runbooks, alert annotations, JSDoc on the
public surface, `CHANGELOG` entries, OpenAPI specs the handlers claim to
implement, ADRs.

## Hygiene

TypeScript-specific properties, applied on top of `HYGIENE.md` General.

### Strict, and typed at the edge

- `strict: true`; `noUncheckedIndexedAccess` where the codebase can bear it.
- Every external input parsed with a runtime schema at the edge; `as` casts
  on parsed data are findings; `any` confined to typed wrappers around
  untyped libraries.
- Discriminated unions with an exhaustiveness check (`never` in `default`).

### Promises are owned

- Every promise awaited, returned, or explicitly `void`ed with a comment;
  `no-floating-promises` on in lint.
- `catch (e: unknown)` with narrowing; errors re-thrown or converted, never
  swallowed.

### Modules are honest

- `index.ts` barrels only where they build a façade; no circular imports
  (`madge` or the bundler's warning).
- ESM/CJS choice consistent; `"type": "module"` and `tsconfig` `module`
  agree.

### Dependencies

- Lockfile committed; `npm audit` clean or each advisory triaged by
  reachability; no `postinstall` scripts in dependencies without a reason.

## Security

For a focused security pass (threat model, injection, authz, crypto, PHI
handling) use `review-application-security`. TypeScript-specific exposure to
carry into it: prototype pollution through recursive merges, `eval` and
`new Function`, `dangerouslySetInnerHTML`, SQL built by template literal,
`child_process.exec` with interpolated input, and the npm supply chain.
