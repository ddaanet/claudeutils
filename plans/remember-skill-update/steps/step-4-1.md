# Cycle 4.1

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Rewrite Click command for one-arg syntax with batched recall.

**Files:** `src/claudeutils/when/cli.py`, `tests/test_when_cli.py`, `agent-core/bin/when-resolve.py`
**Baseline:** 5 existing tests, all passing. Resolver (`src/claudeutils/when/resolver.py`) signature unchanged — CLI parses operator, calls `resolve(operator, query, ...)` as before.

---

## Cycle 4.1: One-arg syntax replaces two-arg

**RED:**
- New test: `test_single_arg_query_parsed`
- Invoke: `["when", "when writing mock tests"]` (single arg with operator prefix)
- Assert: resolve() called with operator="when", query="writing mock tests"
- Expected failure: CLI expects separate operator arg, "when writing mock tests" is invalid Choice value

**Verify RED:** `just test tests/test_when_cli.py::test_single_arg_query_parsed -v`

**GREEN:**
- Rewrite Click command: remove `operator` argument, change `query` to variadic args each containing operator prefix, parse prefix from each query string
- Call resolve() with parsed operator and remaining query
- Update all 5 existing tests to new invocation syntax (same behavioral contract, new API surface)
- Update docstring comment in `agent-core/bin/when-resolve.py` to reflect new invocation: `Usage: when-resolve.py "when <query>" ["how <query>" ...]`. No code change needed — entry point delegates to Click, which handles all arg parsing.

**Verify GREEN:** `just test tests/test_when_cli.py -v`
**Verify no regression:** `just test -v`

**Stop/Error Conditions:**
- resolver.py signature must NOT change — CLI parses operator, calls resolve(operator, query, ...) as before
- If Click arg parsing conflicts with dot-prefix queries (e.g., "when .Section"), test dot-prefix in existing test migration

**Dependencies:** None (first cycle in Phase 4)

---
