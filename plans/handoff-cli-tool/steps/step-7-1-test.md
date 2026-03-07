# Cycle 7.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

---

## Cycle 7.1: Status integration

**RED Phase:**

**Test:** `test_status_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Read `src/claudeutils/session/status/cli.py` — understand full pipeline from CLI entry

**Assertions:**
- Create `tmp_path` git repo with:
  - `agents/session.md` (realistic fixture with in-tree tasks, worktree tasks, reference files)
  - `plans/parser/` directory with design artifacts (triggers plan state inference)
  - At least one plan directory not referenced by any task (triggers unscheduled detection)
- CliRunner invokes `_session status`
- Output contains `Next:` section with correct task name and command
- Output contains `Pending:` section with plan status
- Output contains `Worktree:` section with slug markers
- Output contains `Unscheduled Plans:` section with orphan plan
- Exit code 0

**Expected failure:** Integration path not fully wired — individual components may work but full pipeline from CLI to output untested

**Why it fails:** End-to-end path through CliRunner exercises wiring gaps

**Verify RED:** `pytest tests/test_session_integration.py::test_status_integration -v`

---
