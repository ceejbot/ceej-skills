# Lens: Python

The Python branch of `review-project`. `PROBES.md` holds the questions; this
file holds where to point them in a Python tree, what the type checker can
and cannot witness, and the properties a healthy Python project holds beyond
the General section of `HYGIENE.md`.

## Detect

`pyproject.toml`, `setup.cfg`, `setup.py`, or `requirements*.txt`. Read the
Python version floor and the type-checker configuration (`[tool.mypy]`,
`pyrightconfig.json`, `strict = true` or not). Then the dialect, because it
decides §1 and §3: `asyncio` (`async def`, `await`, `create_task`), threads
(`threading`, `concurrent.futures`), a task queue (`celery`, `rq`, `dramatiq`),
or a request framework with its own lifecycle (`fastapi`, `django`, `flask`).

## Evidence model

Type hints are advisory. Nothing stops a caller passing the wrong shape, and
the checker sees only what is annotated and imported. The witness for a
boundary property is a runtime validator at the edge or a test that exercises
the wrong input. This is the bar: **a property with no runtime witness is
unwitnessed**, whatever the hints say. The review therefore measures test
coverage specifically over the irreversible class and the parse boundaries,
not over the tree.

| Property                                  | Witness                                                   | Unwitnessed looks like                                            |
| ----------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------- |
| Exhaustive handling of a sum type         | `mypy --strict` with `assert_never`, or a test per variant | an `if/elif` chain on a string with no `else`                    |
| Input shape at an edge                    | a `pydantic` model, `attrs` validator, or `marshmallow` schema, plus a test posting malformed input | a `dict` parameter with a type comment |
| Errors are handled                        | none; a test that triggers the failure                    | `except Exception: pass`; `except:` bare                          |
| Absence of None dereference               | `mypy --strict` (`Optional` narrowing), if the code is annotated | an unannotated function returning `None` on one path       |
| Thread safety of shared state             | none; a test with contention                              | a module-level `dict` mutated from a thread pool                  |
| Task survives its creator                 | a reference held to the task, or a `TaskGroup`            | `asyncio.create_task(...)` with the result discarded              |
| Secret never rendered                     | a redaction test on `__repr__`, or a `SecretStr`          | a `@dataclass` holding the secret with its generated `__repr__`   |
| Behaviour under a timeout                 | a test with a fake clock or a slow fake                   | none; §1 carries the question                                     |
| Doc examples still run                    | `doctest` or `pytest --doctest-modules`                   | code blocks in README only                                        |

## Partition unit

The package (a directory with `__init__.py` or a namespace package), grouped
by import graph: entry points (`__main__`, CLI commands, app factories),
their internal packages, shared libraries. A monorepo of several
`pyproject.toml` files partitions by distribution first.

## Tooling gates

- `ruff check` and `ruff format --check` (or `black --check` and `flake8`
  where the repo still uses them).
- The type checker **as a finding source, not a gate**: `mypy --strict` or
  `pyright --strict` on the scope, and read the errors. A project that runs
  the checker non-strict has told you which properties it has chosen not to
  witness; list them.
- `pytest` through the repo's recipe, then `pytest --cov` with the report
  filtered to the irreversible-class modules and the edge parsers Orient
  named. Whole-tree coverage is not the number; coverage of those paths is.
- `pip-audit` or `safety check`; a lockfile (`uv.lock`, `poetry.lock`,
  `requirements.txt` with hashes) present and current.
- `bandit` when the repo configures it.

## Probe instances

### §1 Bounds

`timeout=` on `requests.*`, `httpx.*`, `urllib3`, `socket.settimeout`,
`asyncio.wait_for`, `asyncio.timeout(`, `concurrent.futures ... .result(timeout=`,
`pool_size`, `max_overflow`, `pool_timeout` (SQLAlchemy), `max_retries`,
`Retry(` (urllib3), `celery` `soft_time_limit` / `time_limit`.

Python consequence: `requests.get(url)` with no `timeout=` **waits forever**;
this is the single most common bound of infinity in Python services.
`asyncio.wait_for` cancels the awaited coroutine, so name what it was in the
middle of; a `Future.result(timeout=)` on a thread pool returns to the caller
and leaves the thread running.

### §2 Dual writes

`session.commit()` or `transaction.atomic()` followed by a `publish`,
`send_task`, `.delay(`, `put_object`, a file write, an email; Django
`post_save` signals that call out; a column `published`, `sent_at`,
`exported`; a metrics `.inc()` beside the publish it counts.

### §3 Supervision

`asyncio.create_task`, `asyncio.ensure_future`, `loop.run_in_executor`,
`threading.Thread(`, `daemon=True`, `ThreadPoolExecutor.submit`,
`multiprocessing.Process`, `signal.signal`, `atexit`, `celery` task
registrations, `asyncio.TaskGroup`.

Python consequence: a task from `asyncio.create_task` whose result is not
stored **can be garbage-collected mid-flight**; the event loop holds only a
weak reference. A `daemon=True` thread is killed at interpreter exit with
whatever it holds half-written. A `submit` whose `Future` is never read
discards the exception. An exception in a `Thread.run` prints to stderr and
the thread ends; nothing restarts it.

### §4 Boundary symmetry

Every client module for one vendor, token refresh (`refresh_token`,
`oauth` session helpers), `status_code == 401`, `429` handling and
`Retry-After`, `raise_for_status()` present at some call sites and absent at
others, exception mappers for the same vendor in two modules.

### §5 Startup truth

`os.environ.get(`, `os.getenv(`, `int(os.getenv(...) or 0)`,
`config.get(..., default)`, `pydantic.BaseSettings` fields with defaults,
`argparse` defaults, `django.conf.settings` with `getattr` fallback.

Python consequence: `int("")` raises but `int(os.getenv("X") or 0)` yields
`0`; `bool("false")` is `True`. A `0` reaching a pool size or a worker count
starts a healthy process that does no work; a string "false" enabling a
feature switch is the inverse.

### §6 The irreversible class

Every class, dataclass, pydantic model, or `dict` carrying PHI, credentials,
money, or audit material. Rendering sites: the generated `__repr__` of a
`@dataclass` or `attrs` class, `pydantic` `.model_dump()` / `.dict()` /
`.json()` of the whole model, `str(obj)` and f-strings `f"... {obj}"` in a
log call, `logging.exception` carrying a response body in the exception
message, `print`, `pprint`, `json.dumps(vars(obj))`, Django admin `__str__`.
Passing sites: a `str` parameter that accepts a key, a label, and a secret
alike; `**kwargs` forwarding a payload into a logger.

### §7 Promises

README and `docs/` guarantees, runbooks, alert annotations, module and
function docstrings on the public surface, `CHANGELOG` entries, ADRs, and
the type hints themselves where they promise a shape the code does not
enforce.

## Hygiene

Python-specific properties, applied on top of `HYGIENE.md` General.

### Edges are typed at runtime

- Every external input (HTTP body, queue message, file, env) parsed into a
  `pydantic` model, `attrs` class, or `TypedDict` with a validator at the
  edge; interior code receives objects, not `dict`s.
- Type hints on the whole public surface; the checker runs in CI at the
  strictness the project has chosen, and that choice is written down.

### Exceptions are specific

- `except SomeError`, never bare `except:`; `except Exception` only at a
  top-level boundary that logs and re-raises or converts.
- No `pass` in an `except`; a swallowed exception carries a comment saying
  why the failure cannot matter.

### Defaults are immutable

- No mutable default arguments (`def f(x=[])`); `None` and construct inside,
  or `field(default_factory=...)`.
- Module-level state is constants or explicitly guarded singletons.

### Async discipline

- Every `create_task` result stored or run in a `TaskGroup`; `await`ed
  coroutines never left as bare expressions (a created-but-not-awaited
  coroutine is a warning the project should fail on).
- No blocking I/O inside `async def` without `run_in_executor`.

### Subprocess and filesystem

- `subprocess.run([...])` with a list, never `shell=True` with interpolated
  input; `check=True` or the return code read.
- `pathlib` over string paths; temp files via `tempfile`.

### Packaging hygiene

- One `pyproject.toml` source of truth; a lockfile committed; the Python floor
  declared and matched by CI.
- Dev dependencies separate; no `requirements.txt` drifting from the
  lockfile.

## Security

For a focused security pass (threat model, injection, authz, crypto, PHI
handling) use `review-application-security`. Python-specific exposure to
carry into it: `pickle` and `yaml.load` on untrusted bytes, `eval`/`exec`,
`subprocess` with `shell=True`, Jinja2 autoescape, SQL built by string
formatting, and the dependency tree's transitive surface.
