# Step 5

**Plan**: `plans/validator-consolidation/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Step 5: Port Tasks Validator + Tests

**Objective**: Port task key validation (FR-4: uniqueness, disjointness with learning keys, git history; C-1: merge commit handling).

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-tasks.py` (~275 lines)

**Implementation**:

1. Create `src/claudeutils/validation/tasks.py`:
   - Port all functions: `extract_task_names()`, `extract_learning_keys()`, `get_session_from_commit()`, `get_merge_parents()`, `get_staged_session()`, `get_new_tasks()`, `check_history()`, `validate()`
   - `validate(session_path: str, learnings_path: str, root: Path) -> list[str]`
   - Keep subprocess calls for git operations (git show, git rev-parse, git log -S)
   - Preserve merge commit logic (C-1): check all parents, task is "new" only if absent from ALL parents
   - Preserve octopus merge detection and error

2. Create `tests/test_validation_tasks.py`:
   - Test: task name extraction from session.md format
   - Test: duplicate task names within session.md → error
   - Test: task name conflicts with learning key → error
   - Test: new task found in git history → error
   - Test: merge commit checks all parents (mock both git rev-parse and git show)
   - Test: no session.md → no errors
   - Test: no learnings.md → still validates tasks
   - Mock `subprocess.run` for all git operations. Use `monkeypatch.setattr` or `unittest.mock.patch`.

**Expected Outcome**: Tasks validator identical behavior including merge commit handling.

**Success Criteria**: `pytest tests/test_validation_tasks.py -q` passes, C-1 merge logic tested.

---
