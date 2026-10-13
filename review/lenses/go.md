# Lens: Go

The Go branch of `review-project`. `PROBES.md` holds the questions; this file
holds where to point them in a Go tree, what the toolchain proves and what it
leaves to tests, and the properties a healthy Go project holds beyond the
General section of `HYGIENE.md`.

## Detect

`go.mod` at the root, or a `go.work` listing modules. Dialect notes that change
the instances: the HTTP framework (`net/http` alone, `chi`, `gin`, `echo`),
gRPC (`google.golang.org/grpc`), and whether the project ships a long-running
service (shutdown story in §3) or a CLI (startup truth in §5 dominates).

## Evidence model

The compiler witnesses types and little else. Errors are values the compiler
lets you drop; nil is a valid value of every pointer, map, slice, channel,
and interface; data races compile. The linters are the second witness, and a
project that does not run them has only its tests.

| Property                                  | Witness                                           | Unwitnessed looks like                                            |
| ----------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------- |
| Exhaustive handling of a sum type         | none; `exhaustive` linter on enum-like consts     | a `switch` on a const type with no `default`                      |
| Errors are handled                        | `errcheck`, `staticcheck`                         | `_ = f()`; `f()` on a line of its own                             |
| Absence of nil dereference                | none; `nilaway` partially                         | a map read into a pointer used without a check                    |
| Thread safety of shared state             | `go test -race` on a test that exercises the path | a map written from a goroutine with no mutex and no racing test   |
| Context propagated and honoured           | none; `contextcheck` partially                    | `context.Background()` deep in a call stack; a loop with no `ctx.Done()` select |
| Input shape at an edge                    | a struct with validation tags and a test posting malformed input | `map[string]interface{}` or `json.RawMessage` past the edge  |
| Secret never rendered                     | a redaction test on the type's `String()`         | a struct with the secret as an exported field and no `String()`   |
| Panic-freedom on attacker input           | fuzz target (`go test -fuzz`)                     | index arithmetic on request bytes                                 |
| Doc examples still compile                | `Example*` functions, run by `go test`            | code blocks in README only                                        |

## Partition unit

The package, grouped by import graph: `cmd/*` entry points, their internal
packages, shared `pkg/` libraries. A multi-module workspace partitions by
module first.

## Tooling gates

- `gofmt -l .` or `goimports -l .`; `go vet ./...`.
- `staticcheck ./...`, `errcheck ./...`, and `golangci-lint run` when the repo
  configures it (read `.golangci.yml` for what is disabled, and why).
- `go test ./...`, then `go test -race ./...` on its own: the race detector is
  off by default and a green plain run says nothing about races.
- `govulncheck ./...` for reachable vulnerabilities; `go mod verify`;
  `go mod tidy` with a clean diff.

## Probe instances

### §1 Bounds

`context.WithTimeout`, `context.WithDeadline`, `time.After`, `time.NewTimer`,
`http.Client{` (one without `Timeout:` is a bound of infinity), `http.Server{`
without `ReadTimeout`/`WriteTimeout`, `sql.DB.SetMaxOpenConns`,
`SetConnMaxLifetime`, `MaxRetries`, `backoff`, `Retry` in client config.

Go consequence: a context deadline **does not stop the goroutine**; it closes
`ctx.Done()`, and the work stops only where the code checks it. Name the
place between the deadline and the next `select` or `ctx.Err()` check, and
what the goroutine holds across it.

### §2 Dual writes

`tx.Commit()` followed by a producer `Send`/`Publish`, an S3 `PutObject`, an
`os.WriteFile`, a webhook; `UPDATE ... SET published`, `sent_at`, `exported`;
a metrics `Inc()` beside the publish it counts.

### §3 Supervision

`go func(`, `go worker(`, `errgroup.Group`, `sync.WaitGroup`, `select {` with
a `ctx.Done()` arm, `signal.NotifyContext`, `http.Server.Shutdown`, `defer
wg.Done()`.

Go consequence: a bare `go func()` with no `errgroup` or channel discards its
error and, if it panics, **crashes the whole process**: `recover` only works
in the goroutine that panicked. A `WaitGroup` with no `Wait` at shutdown
leaves work mid-flight when `main` returns.

### §4 Boundary symmetry

Every client package for one vendor, token refresh (`oauth2.TokenSource`,
`Refresh`), `case http.StatusUnauthorized`, `429` handling and `Retry-After`,
status-to-error mappers (`switch resp.StatusCode`), `errors.Is`/`errors.As`
targets for the same vendor across packages.

### §5 Startup truth

`os.Getenv`, `os.LookupEnv`, `strconv.Atoi` with the error dropped,
`flag.Int` defaults, `viper.GetInt`, `envconfig` tags with `default:`,
`time.ParseDuration` with the error dropped.

Go consequence: `os.Getenv` returns `""` for unset and empty alike, and
`strconv.Atoi("")` yields `0` with an error that is easy to drop; a `0`
reaching a pool size or a loop bound produces a healthy process that does
no work.

### §6 The irreversible class

Every struct carrying PHI, credentials, money, or audit material. Rendering
sites: `%v` and `%+v` on the struct or on an error wrapping it, `log.Printf`
and structured loggers given the whole struct (`zap.Any`, `slog.Any`),
`json.Marshal` of a struct whose secret field lacks `json:"-"`,
`fmt.Errorf("...: %w", err)` where `err` carries a response body,
`spew.Dump`. Passing sites: a `string` parameter that accepts a key, a
label, and a secret alike.

### §7 Promises

README and `docs/` guarantees, runbooks, alert annotations, package doc
comments (`// Package foo ...`), exported-function doc comments, `Example*`
tests that document behaviour, ADRs.

## Hygiene

Go-specific properties, applied on top of `HYGIENE.md` General.

### Errors are handled and wrapped

- Every error checked; `_ =` only with a comment saying why the error cannot
  matter.
- Wrapping with `%w` so `errors.Is`/`errors.As` work; sentinel errors
  exported where callers branch on them.
- No `panic` on a request path; `log.Fatal` only in `main`.

### Context is first

- `ctx context.Context` is the first parameter of anything that blocks, does
  I/O, or spawns; never stored in a struct.
- Loops that can run long select on `ctx.Done()`.

### Zero values mean something

- A struct's zero value is usable or its constructor is the only way to make
  one. A `nil` map is never written to.
- Pointers to structs only when nil is a meaningful state or the struct is
  large; no `*string` for optionality where a zero value would do.

### Interfaces at the consumer

- Small interfaces defined where they are used, not where they are
  implemented; no `interface{}` / `any` in a signature where a type would do.
- No `init()` with side effects beyond registration.

### Concurrency shape

- Goroutine lifetimes owned: every `go` has a corresponding wait or a
  documented reason it may outlive its caller.
- Channels closed by the sender only; buffered channel sizes justified.
- Shared state behind a mutex or confined to one goroutine; `-race` run in CI.

### Module hygiene

- `internal/` for packages that are not API; exported surface intentional.
- `go.mod` tidy, `replace` directives explained, major versions bumped with
  the import path.

## Security

For a focused security pass (threat model, injection, authz, crypto, PHI
handling) use `review-application-security`. Go-specific exposure to carry
into it: `unsafe` and `cgo` boundaries, `html/template` versus
`text/template` for HTML output, `database/sql` string concatenation,
`crypto/rand` versus `math/rand`, and `govulncheck` reachability.
