# Cycle 7.2

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.2: Phase 1 pre-checks — THEIRS clean tree (strict, no session exemption)

**Objective:** Verify worktree and its submodule are clean (strict check prevents uncommitted state loss).

**RED Phase:**

**Test:** `test_merge_theirs_clean_tree`
**Assertions:**
- When worktree has ANY uncommitted changes (including session.md): exit 1 with message "Clean tree required for merge (worktree: uncommitted changes would be lost)"
- No exemption for session files in worktree (strict enforcement)
- When worktree submodule has uncommitted changes: exit 1 with message "Clean tree required for merge (worktree submodule)"
- Both worktree parent and submodule checked
- Error message mentions potential data loss

**Expected failure:** AssertionError: no worktree clean check, or session exemption applied to worktree

**Why it fails:** THEIRS check not implemented, or uses same exemption logic as OURS

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_theirs_clean_tree -v`

---

**GREEN Phase:**

**Implementation:** Add THEIRS clean tree check (strict, no exemptions)

**Behavior:**
- Get worktree path using `wt_path(slug)`
- Check worktree: run `git -C <wt-path> status --porcelain --untracked-files=no`
- If output non-empty: exit 1 with "Clean tree required for merge (worktree: uncommitted changes would be lost)"
- Check worktree submodule: run `git -C <wt-path>/agent-core status --porcelain --untracked-files=no`
- If output non-empty: exit 1 with "Clean tree required for merge (worktree submodule)"
- NO filtering (strict check on all files)

**Approach:** Same subprocess pattern as OURS, but without session file filtering

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add worktree path resolution in `merge` command
  Location hint: After OURS checks, use `wt_path(slug)`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add THEIRS clean tree check (strict, no filter)
  Location hint: After OURS checks, use `cwd=<wt-path>` for git status
- File: `src/claudeutils/worktree/cli.py`
  Action: Add THEIRS submodule check
  Location hint: After THEIRS parent check

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_theirs_clean_tree -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_merge_ours_clean_tree -v`
- Cycle 7.1 test still passes

---
