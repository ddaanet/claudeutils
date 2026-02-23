# Cycle 4.2

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Rewrite Click command for one-arg syntax with batched recall.

**Files:** `src/claudeutils/when/cli.py`, `tests/test_when_cli.py`, `agent-core/bin/when-resolve.py`
**Baseline:** 5 existing tests, all passing. Resolver (`src/claudeutils/when/resolver.py`) signature unchanged — CLI parses operator, calls `resolve(operator, query, ...)` as before.

---

## Cycle 4.2: Batched recall

**RED:**
- New test: `test_batched_recall_multiple_queries`
- Invoke: `["when", "when writing mock tests", "how encode paths"]`
- Assert: resolve() called twice (once per query), output contains both results separated by `\n---\n`
- Expected failure: After 4.1, CLI processes first query only, ignores rest

**Verify RED:** `just test tests/test_when_cli.py::test_batched_recall_multiple_queries -v`

**GREEN:**
- Implement batch loop: iterate queries, collect results, join with separator
- Single query = no separator (backward compatible output)

**Verify GREEN:** `just test tests/test_when_cli.py -v`
**Verify no regression:** `just test -v`

**Stop/Error Conditions:**
- Batch separator must not appear in single-query output (backward compat)
- If resolve() raises ResolveError on one query, decide: fail fast or collect errors — fail fast (exit on first error)

**Dependencies:** Cycle 4.1 (batch iterates over single-arg queries)

---
