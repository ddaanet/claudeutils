# Cycle 3.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

**GREEN Phase:**

**Implementation:** Add `detect_parallel()` to `session/status/render.py`

**Behavior:**
- `detect_parallel(tasks: list[ParsedTask], blockers: list[list[str]]) -> list[str] | None`
- Build dependency graph: tasks with shared `plan_dir` are dependent. Tasks mentioned in blocker text are dependent on the blocker
- Find largest independent set (no shared plan_dir, no blocker references between them)
- Return task names if group has 2+ members, else None

**Approach:** Simple graph algorithm — build dependency edges (shared plan_dir, blocker reference), then find the largest independent set (no edges between members). For small task lists (<20), brute-force over subsets is fine: enumerate all subsets of pending tasks in descending size order, return first subset with no dependency edges between any pair.

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Add `detect_parallel()` function

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---
